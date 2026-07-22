---
name: cad-modeling
description: Use when the user wants to create, edit, or export a 3D CAD model or mechanical part — 3D CAD, CADモデル, STEP, STL, 3MF, メカ部品, ブラケット, エンクロージャ, ケース, ギア, 治具, フランジ, シャフト, マウント, 3Dプリント用モデル, build123d, OpenSCAD, CadQuery, パラメトリックモデリング, 寸法指定の部品, 既存STEPの修正. Do NOT use for 3D-looking images/video (use video-media-studio) or architectural floor plans.
---

# CAD Modeling (build123d / STEP-first)

## Overview

テキスト仕様から **build123d**（OpenCascade B-rep）でパラメトリックに 3D CAD を作る。
**Pythonソースコードがモデルの正本**（成果物 STEP/STL を直接編集しない）。
**STEP が第一エクスポート**（CAD互換・後編集可能）、STL/3MF は 3Dプリント等の用途別派生。
参考: earthtojake/text-to-cad（同思想: spec → parametric source → validate → snapshot）。

## 環境（この環境で実機検証済み 2026-07-22）

```bash
export LD_LIBRARY_PATH=   # anaconda libtinfo 汚染回避（必須）
/home/kita/.local/bin/uv run model.py   # PEP723 インラインスクリプト
```

- 依存は PEP723 で `build123d>=0.8` + `matplotlib`。**OCPホイールはuvキャッシュ済み → 2回目以降は数秒で起動**
- ヘッドレスOK（GUI/GL不要）。レンダは matplotlib Agg

## ワークフロー

1. **仕様シートを先に書く**: 寸法（単位は既定 mm）・座標系（既定: XY底面・+Z上）・
   穴（径/位置/貫通か止まりか）・フィレット/面取り・用途（3Dプリント/機械加工/嵌合相手）。
   **曖昧な寸法・穴位置・公差を勝手に補完しない** — ユーザーに確認する
   （人物画像の6要素確認と同じ規律）。確認できない文脈では仮定を明示的に列挙してから進める
2. **パラメータ定数ブロック → build123d コード**（下の実証済み例の形）。
   マジックナンバー禁止・全寸法を名前付き定数に
3. **幾何検証を必ず実行**（生成コード内で assert）:
   - `part.volume > 0` / `part.is_valid`（★**プロパティ。`is_valid()` と呼ぶと TypeError** — 実機で確認済み）
   - バウンディングボックス == 仕様値（`part.bounding_box().size`）
   - 体積の解析解チェック（板の和 − 穴の円筒: 誤差<1%）または断面/位相での穴数確認
4. **多視点PNGプレビュー → SendUserFile でユーザーに見せる**:
   ```bash
   uv run ~/.claude/skills/cad-modeling/scripts/render_views.py out/part.step out/preview.png
   ```
   プレビューはQC用途（寸法感・穴位置・向き）。承認前に次の工程へ進まない
5. **修正はソースを編集して再生成**（STEP/STLを直接いじらない。パラメータを変えて再実行）
6. **納品**: STEP（正本）+ 用途別（3Dプリント= STL or 3MF）。SendUserFile は display='attach'

## 実証済みコード例（Lブラケット・この形をテンプレートに）

```python
# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["build123d>=0.8"]
# ///
from build123d import (BuildPart, Box, Hole, Locations, export_step, export_stl)

# --- パラメータ（全寸法をここに集約） ---
T = 4.0          # 板厚
BASE_L, W = 50.0, 30.0
WALL_H = 30.0
HOLE_R = 2.25    # M4クリアランス φ4.5 / 2

with BuildPart() as bp:
    Box(BASE_L, W, T)                                  # 底板（原点=底板中心）
    with Locations((-BASE_L / 2 + T / 2, 0, WALL_H / 2)):
        Box(T, W, WALL_H)                              # 立ち上がり
    with Locations((BASE_L / 4, 0, 0)):
        Hole(radius=HOLE_R)                            # 貫通穴（BuildPart文脈で自動的に through-all）
part = bp.part

assert part.volume > 0 and part.is_valid               # is_valid はプロパティ
bb = part.bounding_box()
print(f"volume={part.volume:.1f}mm3 bbox=({bb.size.X:.1f},{bb.size.Y:.1f},{bb.size.Z:.1f})")
export_step(part, "out/bracket.step")
export_stl(part, "out/bracket.stl")
```

よく使うAPI: `fillet(edges, radius)` / `chamfer(edges, length)` / `Cylinder` /
`BuildSketch`+`extrude` / `RegularPolygon` / `Text`。エッジ選択は
`bp.edges().filter_by(Axis.Z)` 等。組立体は `Compound(children=[...])`。

## Quick Reference

| 用途 | 値/関数 |
|---|---|
| クリアランス穴(中級) | M3=φ3.4 / M4=φ4.5 / M5=φ5.5 / M6=φ6.6（半径で渡す） |
| セルフタップ下穴(3Dプリント) | M3=φ2.5 / M4=φ3.3 |
| エクスポート | `export_step` / `export_stl` / `export_gltf`（3MFは `Mesher().write`） |
| STEP読み込み(既存修正) | `import_step(path)` → 測定・ブーリアンで加工 |
| 3Dプリント検証 | STLは watertight 必須（`part.is_valid` + STL再読込確認） |

## Common Mistakes（ベースライン実測 2026-07-22 で観測）

| 間違い | 現実 |
|---|---|
| 「OCP/build123dは重いから trimesh+manifold3d で済ませる」 | **STEPが出せない**（メッシュCSGはCAD互換・後編集性ゼロ）。OCPはuvキャッシュ済みで数秒。STLだけ明示依頼された時以外、メッシュ工法を既定にしない |
| プレビューなしで納品 | ユーザーはSTLを開けない前提で動く。**render_views.py → SendUserFile が必須工程** |
| 曖昧な穴位置・公差を黙って補完 | 仕様シートで確認、できなければ仮定を明示列挙 |
| `part.is_valid()` と呼ぶ | プロパティ。`()`を付けると TypeError（実機確認済み） |
| 成果物STEP/STLを直接編集 | ソース（Pythonパラメータ）を直して再生成 |
| プレビューの大面の暗い三角形を形状不良と誤読 | matplotlib深度ソートの既知アーティファクト。形状判断はSTEP/検証値で |
| 穴位置検証に円筒面の `Face.center()` を使う | **面上の一点を返す（軸上ではない）** → 偽陽性で検証が落ちる（GREEN実測 2026-07-22）。穴の位置は円筒面の**軸**（`face.location` / 軸線）か断面スライスで検証する |

## 実装委譲ルールとの関係

CADモデル生成スクリプトは「モデルの記述＝成果物そのもの」であり、このスキルのワークフロー内で
直接書いてよい（2026-07-22 ユーザー依頼の趣旨。画像生成のプロンプトと同格）。ただし
CAD周辺の**アプリ/パイプライン/ツール開発**は通常どおり delegating-implementation-to-codex に従う。
