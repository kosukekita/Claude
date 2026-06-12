---
name: slide-making-skill-v2
description: slide-making skill rewritten 2026-06-12 — ask HTML-or-PPTX first; PPTX is native python-pptx (not HTML); GPT Image = parts only
metadata: 
  node_type: memory
  type: project
  originSessionId: 5abc3f9a-6807-4887-a828-d7f17f8a2012
---

The `slide-making` skill (`~/.claude/skills/slide-making/`) was fully rewritten 2026-06-12 (commit fde130c). Design decisions the user locked in:

- **STEP 0: always ask "HTML か PPTX か" up front** when the user doesn't specify. PNG/PDF are HTML-path derivatives.
- **PPTX path is NATIVE python-pptx, never via HTML.** `scripts/build_pptx.py` is a spec-driven generator: Claude writes a JSON spec (title/subtitle/bullets/body/images/table/emphasis), the script does the EMU/run/border mechanics. Run: `uv run --with python-pptx scripts/build_pptx.py --spec deck.json --out deck.pptx`. The old external paid API (html2pptx.app) was dropped.
- **GPT Image = PARTS ONLY** (icons/figures), never whole slides, never baked text (Japanese garbles). Text is always real text in HTML/python-pptx. Codex built-in `image_gen` tool (no OPENAI_API_KEY); transparency = generate on flat chroma-key bg then `~/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py --auto-key border --soft-matte --despill`.
- **HTML path**: `scripts/render_slide.py` (kept) now has a `--pdf` mode (Playwright `page.pdf`, 1920x1080, `emulate_media("screen")`, multi-slide merged via pypdf).
- Deleted: html2pptx-guide.md, png-crop-icon.md, powerpoint-handoff.md, export_to_pptx.py. Added: build_pptx.py, references/pptx-guide.md.

**python-pptx specifics that work** (verified end-to-end with a real generated icon): slide size via `prs.slide_width/height = Inches(13.333)/Inches(7.5)`; blank layout = `slide_layouts[6]`; horizontal-only tables need table style `{2D5ABB26-0587-4C30-8999-92F81FD0307C}` ("No Style, No Grid") PLUS per-cell `<a:lnB>` solid / `<a:lnL/R/T>` noFill; **partial (span-level) emphasis requires splitting the paragraph into separate runs** — setting `run.font.color` colors the whole run (first attempt colored the entire bullet line; fixed by rebuilding the paragraph, one run per token). Set `<a:ea>` typeface too or PowerPoint swaps the CJK font. python-pptx can't embed fonts → Noto Sans JP must be installed on the opener or swap the `FONT` constant.

**Environment gotcha (this Linux box):** anaconda pollutes `LD_LIBRARY_PATH`, which crashes LibreOffice (`soffice`) and can break other native tools with symbol-lookup errors (libcurl/libdconf). Always run them with `env -u LD_LIBRARY_PATH ...` (e.g. `env -u LD_LIBRARY_PATH soffice --headless --convert-to png ...`). Same family as the Playwright glib pollution noted elsewhere.

**Skill-rewrite lesson (TDD/writing-skills):** RED baseline showed the bare model ALREADY asks format and ALREADY refuses to bake text into images — so those rules didn't need heavy enforcement. The real value was the PPTX-native flow and the correct Codex imagegen invocation (the model otherwise guesses a stale `gpt-5.5` model and assumes an API key). Don't over-document what the model does right by default; spend the skill on what it gets wrong.
