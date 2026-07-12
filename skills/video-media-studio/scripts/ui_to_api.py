#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests",
# ]
# ///
"""ui_to_api.py — convert a ComfyUI *UI-format* workflow JSON (nodes[]+links[])
into the *API-format* dict (node_id -> {class_type, inputs}) that POST /prompt
accepts, WITHOUT a browser.

ComfyUI's official UI->API conversion lives in the frontend (JS) and can't be
called from Python. But the conversion is mechanical if you know each node's
input *ordering*, which the headless server exposes at GET /object_info. This
script:
  1. reads the UI JSON,
  2. queries /object_info for every node's input name order,
  3. maps each node's widgets_values[] onto its widget input names,
  4. resolves node-to-node connections from links[] into inputs = [from_id, slot],
  5. emits API-format JSON.

Widget order is taken from the LIVE server (version-independent within the
installed node set), so Kijai-wrapper updates are absorbed as long as the server
is running the same nodes.

Output contract: WHY logs to stderr; API JSON to stdout (or --out file).
--dry-post validates the result against the server (/prompt with no execution
side effects is not possible, so we POST and immediately note prompt_id; use a
throwaway short job or --dry-post only when you accept a queued run).

Usage:
  ui_to_api.py --ui sample_ui.json --server http://127.0.0.1:8189 [--out api.json]
  ui_to_api.py --ui sample_ui.json --server ... --dry-post   # POST to validate
"""
import argparse
import copy
import json
import sys
from collections import defaultdict

import requests

PREFIX = "[ui_to_api]"


def log(msg: str) -> None:
    print(f"{PREFIX} {msg}", file=sys.stderr, flush=True)


def fetch_object_info(server: str) -> dict:
    r = requests.get(f"{server}/object_info", timeout=60)
    r.raise_for_status()
    return r.json()


def input_order(obj_info: dict, class_type: str):
    """Return the ordered list of (name, spec) for a node's inputs, required then
    optional, matching the order ComfyUI's frontend assigns widgets_values."""
    node_def = obj_info.get(class_type)
    if not node_def:
        return None
    inp = node_def.get("input", {})
    order = []
    # ComfyUI preserves insertion order of the required/optional dicts, which is
    # the same order the frontend uses to lay out widgets.
    for section in ("required", "optional"):
        for name, spec in inp.get(section, {}).items():
            order.append((name, spec))
    return order


# These render as widgets in the frontend and therefore occupy a slot in
# widgets_values. Newer ComfyUI expresses a dropdown as the literal string
# "COMBO" (with choices in spec[1]); older builds express it as a list of
# choices. Both are widgets. Every other declared type (IMAGE, LATENT, MODEL,
# MASK, and custom node-output types like COMFY_MATCHTYPE_V3, HYVIDEMBEDS) is a
# *connection* input fed by a link and must NOT consume a widgets_values slot —
# otherwise every later widget shifts by one.
_WIDGET_SCALAR_TYPES = {"INT", "FLOAT", "STRING", "BOOLEAN", "BOOL", "COMBO"}


def is_link_input(spec) -> bool:
    """True if this input is a node-to-node connection (not a widget).
    Widget inputs are the scalar types in _WIDGET_SCALAR_TYPES or a combo
    (type given as the string "COMBO" or as a list of choices). Anything else —
    including unknown custom types — is treated as a connection."""
    if not isinstance(spec, (list, tuple)) or not spec:
        return True  # malformed => assume connection (safer: don't eat a widget slot)
    t = spec[0]
    if isinstance(t, list):
        return False  # combo-as-list => widget
    return t not in _WIDGET_SCALAR_TYPES


_CONTROL_VALUES = {"fixed", "increment", "decrement", "randomize"}


# Widget names that ComfyUI's frontend always pairs with a control_after_generate
# token in widgets_values, even when /object_info doesn't flag them.
_CONTROL_WIDGET_NAMES = {"seed", "noise_seed", "rand_seed"}


def _has_control_after_generate(name, spec) -> bool:
    if name in _CONTROL_WIDGET_NAMES:
        return True
    if not isinstance(spec, (list, tuple)) or len(spec) < 2:
        return False
    meta = spec[1]
    return isinstance(meta, dict) and bool(meta.get("control_after_generate"))


def _strip_control_values(order, widget_names, widgets):
    """ComfyUI's frontend appends a control token ('fixed'/'randomize'/...) to
    widgets_values right after any widget that declares control_after_generate.
    That token is NOT a server input, so drop it. We walk the ordered widget
    specs; when a control-bearing widget is consumed, skip the following value if
    it looks like a control token."""
    spec_by_name = {name: spec for name, spec in order}
    out = []
    it = iter(widgets)
    for name in widget_names:
        try:
            val = next(it)
        except StopIteration:
            break
        out.append(val)
        if _has_control_after_generate(name, spec_by_name.get(name)):
            # peek: if the next value is a control token, consume+drop it.
            try:
                nxt = next(it)
            except StopIteration:
                break
            if nxt not in _CONTROL_VALUES:
                # not a control token after all; keep it for the next widget by
                # prepending back via a fresh chained iterator.
                import itertools
                it = itertools.chain([nxt], it)
    return out


# ---------------------------------------------------------------------------
# Flattening pre-pass: expand subgraphs, resolve KJNodes Get/Set, bypass Reroute.
# ComfyUI's frontend does this before sending /prompt; we replicate it headless.
# (algorithm per Codex consult 2026-07-13; link output kept ARRAY-format for convert)
# ---------------------------------------------------------------------------
SUBGRAPH_INPUT_ID = -10
SUBGRAPH_OUTPUT_ID = -20
_SET_TYPES = {"SetNode", "SetNode (KJNodes)", "SetNode_KJ"}
_GET_TYPES = {"GetNode", "GetNode (KJNodes)", "GetNode_KJ"}
_REROUTE_TYPES = {"Reroute", "rgthree Reroute", "Reroute (rgthree)"}


def _norm_link(l):
    if isinstance(l, (list, tuple)):
        return {"id": l[0], "origin_id": l[1], "origin_slot": l[2],
                "target_id": l[3], "target_slot": l[4], "type": l[5] if len(l) > 5 else "*"}
    return dict(l)


def _denorm_link(l):  # ARRAY format, matches convert()'s expectation
    return [l["id"], l["origin_id"], l["origin_slot"], l["target_id"], l["target_slot"], l.get("type", "*")]


def _max_id(items, key):
    vals = []
    for x in items:
        try:
            vals.append(int(key(x)))
        except Exception:
            pass
    return max(vals, default=0)


def _channel(n):
    props = n.get("properties") or {}
    for k in ("channel", "name", "key", "Name"):
        if props.get(k) not in (None, ""):
            return str(props[k])
    w = n.get("widgets_values")
    if isinstance(w, list) and w:
        return str(w[0])
    raise ValueError(f"cannot read channel for node id={n.get('id')} type={n.get('type')}")


def bypass_reroutes(ui):
    ui = copy.deepcopy(ui)
    nodes = ui.get("nodes", [])
    links = [_norm_link(l) for l in ui.get("links", [])]
    changed = True
    while changed:
        changed = False
        for n in list(nodes):
            if n.get("type") not in _REROUTE_TYPES:
                continue
            incoming = [l for l in links if l["target_id"] == n["id"]]
            if len(incoming) != 1:
                continue
            src = incoming[0]
            for out in links:
                if out["origin_id"] == n["id"]:
                    out["origin_id"] = src["origin_id"]
                    out["origin_slot"] = src["origin_slot"]
                    out["type"] = out.get("type") or src.get("type", "*")
            links = [l for l in links if l["id"] != src["id"] and l["target_id"] != n["id"]]
            nodes = [x for x in nodes if x["id"] != n["id"]]
            changed = True
            break
    ui["nodes"] = nodes
    ui["links"] = [_denorm_link(l) for l in links]
    return ui


def resolve_get_set(ui):
    ui = copy.deepcopy(ui)
    nodes = ui.get("nodes", [])
    if not any(n.get("type") in _SET_TYPES or n.get("type") in _GET_TYPES for n in nodes):
        return ui
    links = [_norm_link(l) for l in ui.get("links", [])]
    links_by_id = {l["id"]: l for l in links}

    set_source = {}
    for n in nodes:
        if n.get("type") not in _SET_TYPES:
            continue
        ch = _channel(n)
        incoming = []
        for inp in n.get("inputs", []) or []:
            lid = inp.get("link")
            if lid is not None and lid in links_by_id:
                incoming.append(links_by_id[lid])
        if not incoming:
            incoming = [l for l in links if l["target_id"] == n["id"]]
        if len(incoming) != 1:
            raise ValueError(f"SetNode channel={ch}: input link not unique ({len(incoming)})")
        l = incoming[0]
        set_source[ch] = (l["origin_id"], l["origin_slot"], l.get("type", "*"))

    remove_nodes, remove_links, rewired = set(), set(), []
    for n in nodes:
        if n.get("type") not in _GET_TYPES:
            continue
        ch = _channel(n)
        if ch not in set_source:
            raise ValueError(f"GetNode channel={ch}: no matching SetNode")
        src_id, src_slot, typ = set_source[ch]
        remove_nodes.add(n["id"])
        for l in links:
            if l["origin_id"] == n["id"]:
                nl = copy.deepcopy(l)
                remove_links.add(l["id"])
                nl["origin_id"] = src_id
                nl["origin_slot"] = src_slot
                nl["type"] = l.get("type") or typ
                rewired.append(nl)
    for n in nodes:
        if n.get("type") in _SET_TYPES:
            remove_nodes.add(n["id"])
            for l in links:
                if l["target_id"] == n["id"] or l["origin_id"] == n["id"]:
                    remove_links.add(l["id"])

    ui["nodes"] = [n for n in nodes if n["id"] not in remove_nodes]
    ui["links"] = [_denorm_link(l) for l in links
                   if l["id"] not in remove_links
                   and l["origin_id"] not in remove_nodes
                   and l["target_id"] not in remove_nodes] + [_denorm_link(l) for l in rewired]
    return ui


def _slot_link_ids(io_slot):
    return set(io_slot.get("linkIds") or io_slot.get("links") or [])


def inline_subgraphs(ui):
    ui = copy.deepcopy(ui)
    sub_defs = {sg["id"]: sg for sg in ui.get("definitions", {}).get("subgraphs", [])}
    if not sub_defs:
        return ui
    changed = True
    while changed:
        changed = False
        nodes = ui.get("nodes", [])
        links = [_norm_link(l) for l in ui.get("links", [])]
        inst = next((n for n in nodes if n.get("type") in sub_defs), None)
        if not inst:
            break
        changed = True
        sg = sub_defs[inst["type"]]
        inst_id = inst["id"]
        parent_in, parent_out = defaultdict(list), defaultdict(list)
        for l in links:
            if l["target_id"] == inst_id:
                parent_in[l["target_slot"]].append(l)
            if l["origin_id"] == inst_id:
                parent_out[l["origin_slot"]].append(l)
        next_nid = _max_id(nodes, lambda n: n["id"]) + 1
        next_lid = _max_id(links, lambda l: l["id"]) + 1
        in_node_id = (sg.get("inputNode") or {}).get("id", SUBGRAPH_INPUT_ID)
        out_node_id = (sg.get("outputNode") or {}).get("id", SUBGRAPH_OUTPUT_ID)
        idmap, inner_nodes = {}, []
        for n in sg.get("nodes", []):
            if n["id"] in (in_node_id, out_node_id, SUBGRAPH_INPUT_ID, SUBGRAPH_OUTPUT_ID):
                continue
            nn = copy.deepcopy(n)
            idmap[n["id"]] = next_nid
            nn["id"] = next_nid
            next_nid += 1
            inner_nodes.append(nn)
        inner_links = [_norm_link(l) for l in sg.get("links", [])]
        in_link_to_slot = {}
        for i, s in enumerate(sg.get("inputs", []) or []):
            for lid in _slot_link_ids(s):
                in_link_to_slot[lid] = i
        out_link_to_slot = {}
        for i, s in enumerate(sg.get("outputs", []) or []):
            for lid in _slot_link_ids(s):
                out_link_to_slot[lid] = i
        new_links, internal_out_src = [], {}
        for l in inner_links:
            oid, tid = l["origin_id"], l["target_id"]
            if oid in (in_node_id, SUBGRAPH_INPUT_ID) or l["id"] in in_link_to_slot:
                slot = in_link_to_slot.get(l["id"], l["origin_slot"])
                if l["target_id"] not in idmap:
                    continue
                for pl in parent_in.get(slot, []):
                    nl = copy.deepcopy(l)
                    nl["id"] = next_lid; next_lid += 1
                    nl["origin_id"] = pl["origin_id"]; nl["origin_slot"] = pl["origin_slot"]
                    nl["target_id"] = idmap[l["target_id"]]; nl["target_slot"] = l["target_slot"]
                    nl["type"] = pl.get("type") or l.get("type", "*")
                    new_links.append(nl)
                continue
            if tid in (out_node_id, SUBGRAPH_OUTPUT_ID) or l["id"] in out_link_to_slot:
                slot = out_link_to_slot.get(l["id"], l["target_slot"])
                if l["origin_id"] in idmap:
                    internal_out_src[slot] = (idmap[l["origin_id"]], l["origin_slot"], l.get("type", "*"))
                continue
            if oid in idmap and tid in idmap:
                nl = copy.deepcopy(l)
                nl["id"] = next_lid; next_lid += 1
                nl["origin_id"] = idmap[oid]; nl["target_id"] = idmap[tid]
                new_links.append(nl)
        for slot, outs in parent_out.items():
            src = internal_out_src.get(slot)
            if not src:
                continue
            src_id, src_slot, typ = src
            for pl in outs:
                nl = copy.deepcopy(pl)
                nl["id"] = next_lid; next_lid += 1
                nl["origin_id"] = src_id; nl["origin_slot"] = src_slot
                nl["type"] = pl.get("type") or typ
                new_links.append(nl)
        ui["nodes"] = [n for n in nodes if n["id"] != inst_id] + inner_nodes
        ui["links"] = [_denorm_link(l) for l in links
                       if l["origin_id"] != inst_id and l["target_id"] != inst_id] + \
                      [_denorm_link(l) for l in new_links]
    return ui


def flatten_ui(ui):
    """Expand subgraphs + resolve Get/Set + bypass Reroute (idempotent for flat graphs)."""
    ui = inline_subgraphs(ui)      # expose subgraph internals to top level first
    ui = resolve_get_set(ui)       # then resolve named Get/Set channels
    ui = bypass_reroutes(ui)
    # second pass in case inlining exposed nested subgraphs/Get-Set
    ui = inline_subgraphs(ui)
    ui = resolve_get_set(ui)
    return ui


def convert(ui: dict, obj_info: dict) -> dict:
    ui = flatten_ui(ui)
    nodes = ui["nodes"]
    links = ui.get("links", [])
    # link format: [link_id, from_node, from_slot, to_node, to_slot, type]
    # Build: (to_node, to_input_index) -> [from_node, from_slot]
    link_by_dest = {}
    for lk in links:
        if not isinstance(lk, (list, tuple)) or len(lk) < 5:
            continue
        _lid, from_node, from_slot, to_node, to_slot = lk[0], lk[1], lk[2], lk[3], lk[4]
        # ComfyUI's API format keys nodes by STRING id and resolves link sources
        # via prompt[from_node]; the from_node must therefore be a string or the
        # server raises KeyError during validation.
        link_by_dest[(to_node, to_slot)] = [str(from_node), from_slot]

    api = {}
    for n in nodes:
        nid = n["id"]
        ctype = n["type"]
        # Skip pure-frontend nodes with no server class (e.g. Note, Reroute UI).
        if ctype not in obj_info:
            log(f"skip node id={nid} type={ctype} (not in object_info; likely UI-only)")
            continue
        order = input_order(obj_info, ctype)
        if order is None:
            log(f"WARN node id={nid} type={ctype}: no input order; emitting empty inputs")
            api[str(nid)] = {"class_type": ctype, "inputs": {}, "_meta": {"title": n.get("title") or ctype}}
            continue

        # The node's declared *input slots* (connection inputs) appear in n["inputs"].
        # Map slot index -> input name for connection resolution, and collect the
        # set of input names that are actually wired via a link.
        node_input_slots = n.get("inputs", []) or []
        slot_name_by_index = {i: s.get("name") for i, s in enumerate(node_input_slots)}
        linked_input_names = set()
        for slot_idx, iname in slot_name_by_index.items():
            if iname and link_by_dest.get((nid, slot_idx)) is not None:
                linked_input_names.add(iname)

        widgets = n.get("widgets_values")
        inputs = {}
        # widgets_values is positioned against the FULL widget-eligible input
        # order (every non-connection-typed input), REGARDLESS of whether that
        # input is currently promoted to a link slot — ComfyUI keeps the stored
        # value even when the input is wired. So zip against all widget-eligible
        # names, then let links overwrite the ones that are actually connected.
        all_widget_names = [name for name, spec in order if not is_link_input(spec)]

        if isinstance(widgets, dict):
            # Named widgets (VHS_VideoCombine): use as-is for widget names.
            for name in all_widget_names:
                if name in widgets:
                    inputs[name] = widgets[name]
        elif isinstance(widgets, list):
            # Positional: zip against the full widget order. ComfyUI inserts a
            # trailing control value after any INT/COMBO widget that declares
            # control_after_generate; filter those extra values out of the stream.
            vals = _strip_control_values(order, all_widget_names, widgets)
            for name, val in zip(all_widget_names, vals):
                inputs[name] = val
        # Drop widget values for inputs that are actually wired (the link is
        # authoritative), then set the connection inputs from links.
        for iname in linked_input_names:
            inputs.pop(iname, None)
        for slot_idx, iname in slot_name_by_index.items():
            src = link_by_dest.get((nid, slot_idx))
            if src is not None and iname:
                inputs[iname] = src  # [from_node_id, from_output_slot]

        api[str(nid)] = {
            "class_type": ctype,
            "inputs": inputs,
            "_meta": {"title": n.get("title") or ctype},
        }
    return api


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ui", required=True, help="UI-format workflow JSON")
    ap.add_argument("--server", default="http://127.0.0.1:8189")
    ap.add_argument("--out", help="write API JSON here (default stdout)")
    ap.add_argument("--dry-post", action="store_true",
                    help="POST /prompt to validate (queues a run!)")
    args = ap.parse_args()

    ui = json.load(open(args.ui))
    log(f"loaded UI json: {len(ui.get('nodes', []))} nodes, {len(ui.get('links', []))} links")
    obj_info = fetch_object_info(args.server)
    log(f"object_info: {len(obj_info)} node classes")

    api = convert(ui, obj_info)
    out_json = json.dumps(api, indent=2, ensure_ascii=False)
    if args.out:
        open(args.out, "w").write(out_json)
        log(f"wrote {args.out}")
    else:
        print(out_json)

    if args.dry_post:
        log("dry-post: POST /prompt to validate ...")
        r = requests.post(f"{args.server}/prompt", json={"prompt": api}, timeout=60)
        if r.status_code == 200:
            log(f"VALID: prompt_id={r.json().get('prompt_id')}")
        else:
            log(f"INVALID ({r.status_code}): {r.text[:800]}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
