---
name: mf-cli
description: Use when driving Mechanical Finder (整形外科CT-FE商用ソフト, インストール先 C:\mfinder_ee130, V13 EE) from the command line WITHOUT its GUI — DICOM読込・骨セグメント・メッシュ生成・材料割当・ソルバを裏側のバックエンドexe(dicom_if/inferSend/FloatTetwild/mesher/to_exec/solver2)で直接叩いて自動化・バッチ化したいとき。MFのGUI(3D節点選択が本質でpywinauto不可)をコマンドラインで回避、Bessho型破断解析のヘッドレス実行、複数症例バッチ展開。トリガー: MFをCLIで/GUIなしで/バッチで/Mechanical Finder headless/破断解析を自動化。
---

# Mechanical Finder を CLI で駆動する

## Overview
MF は AVS/Express 製の GUI アプリで CLI 駆動の公式手段は無い（マニュアル219頁にコマンドライン手順なし、solv_cli/bat_solv/proj2text/img2proj は引数なしで GUI を開くだけ）。荷重・拘束は 3D OpenGL ビューでの**節点選択**が本質で pywinauto では届かない。**しかし GUI が裏で叩くバックエンド exe 群を直接起動すれば GUI を回避してパイプラインを組める。材料則・節点グループはテキスト**。

## 実行作法（最重要 — ここで必ずつまずく）
- **Bash ツール + `dangerouslyDisableSandbox: true`**。PowerShell の `Start-Process`（外部 spawn）は EPERM で不可。Bash の `timeout` 経由で MF exe を起動する。
- **exe 自体は POSIX パス** `/c/mfinder_ee130/bin/pc11_64/xxx.exe`（Windows 形式 `C:/...` だと `timeout` が exit 127 で見つけられない）。
- **exe に渡す引数は Windows パス** `D:\...`（シングルクォートで `\` を保持）＋ `MSYS_NO_PATHCONV=1`（Git Bash のパス変換を止める）。MF は POSIX パスを解さない。
- **CWD 依存が強い**: `inputs.json`/`ftet.mesh`/`EXEC.*`/`mf_tmp*` を相対名で読む exe が多い。**1コマンド内で `cd <workdir> && exe...` と連結**（Bash は呼出し間で cwd がリセットされる）。
- 作業ディレクトリ = `D:\mf_work\<case>`（C ドライブ逼迫回避）。長時間 exe（inferSend / FloatTetwild / solver）は `run_in_background: true`。
- 各 exe 冒頭でライセンスチェック（ノードロック `C:\mfinder_ee130\License.dat`）。GUI 系（mecha/matedit 等）はウィンドウを開くので無人ループに不向き。headless 確実なのは `dicom_if / inferSend / FloatTetwild_bin / SplitByInnerBoundary / mesher / to_exec / solver(2)`。

## パイプライン各段（bin = `C:\mfinder_ee130\bin\pc11_64`）
1. **DICOM読込 ✅実証済**: `dicom_if.exe <代表dcm1枚> <out_prefix> <mf_info> F256 <lst>` → `mf_tmp.ctm`(CTボリューム)/`.pai`/`.sys`。dcm1枚を渡すとそのディレクトリ全体を読む。**実引数の具体値**: 代表dcm=ディレクトリ内の任意1枚(`$(ls <dir>/slice0000.dcm)` 等); out_prefix=作業Dの `mf_tmp`; mf_info=**同梱の入力ファイル `C:\mfinder_ee130\mf_info`**(事前に存在、そのまま渡す); **F256=フィルタ/フォーマットトークン、症例に依らず固定でよい**; lst=dicom_if が書く出力DICOMリスト。実コマンド例は `C:\mfinder_ee130\temp\dicom_if.log` の1行目にも残る。⚠inferSend(段2)は別途 **非圧縮 mf_tmp.mhd** を要求する(dicom_ifの .ctm とは別物)。
2. **骨セグメント**: `inferSend.exe --mode Femur --gpu -1`（CPU。`temp\ai_segment.bat` の実例）。入力=**カレントの非圧縮 `mf_tmp.mhd`**（MET_SHORT, CompressedData=False。圧縮 .mhd は不可 → SimpleITK で `useCompression=False` 書き出し）、出力=`mf_tmp_label.mhd/raw`。⚠**既存の骨マスクがあればこの段は不要** — マスク→表面STLへ直行する。
3. **メッシュ**: `FloatTetwild_bin.exe -i <stl> -o ftet.msh -l <相対edge=目標mm/bbox対角> --epsa <0.1〜0.3> --max-threads 4 --stop-energy 12`（**単一STLでOK**、`--inputs json` は複数用）。皮質シェルは続けて `SplitByInnerBoundary.exe ftet.msh ftet.msh__tracked_surface.stl out.FDNEUT 1e-5`（VTK 製、皮質シェル不要ならこの段はスキップ）。⚠marching cubes の生 STL は階段状で荒く、`epsa 0.1` だと四面体が爆発（例: 470万）→ **STL を Laplacian smoothing してから、edge を大きめ・envelope を緩め**に。
4. **FDNEUT→.geom**: `mesher.exe`（`temp\mesher.log`: FDNEUT読込→GEOM書出し。引数順は未確定）。
5. **材料（テキスト・GUI不要）🔑**: `data\props\*.dat` はテキスト。`Keyak Sample(Eq).dat` の弾性率式が Keyak 区分則（`33900ρ^2.2 / 5307ρ+469 / 10200ρ^2.01`）で、**プロジェクトの `fe/hu_to_E.py` と完全一致**。形式=`<density閾値> <flag> <coef> <exp> <const>`（val = coef·ρ^exp + const）。均質材料=`basicdata_en.mat`（name/ν/E/density/critical/yield/…）。
6. **ソルバ**: `to_exec.exe [EXEC.BINP] [EXEC.INP] (LOG)` が BINP→INP 変換（SOLVER-TYPE V1/V2 判定）→ `solver2.exe`（Intel Fortran + MKL Pardiso, EXEC.INP を読む）→ 結果 `.Bdsp`(変位)/`.Bstr`(応力)。solver.log の SOLUTION PARAMS: DRUCKER-PRAGER ALPHA=0.07(Bessho降伏)。プロジェクト→EXEC.BINP は `solv_cli`/`bat_solv`（GUI だが `CMfilesData::WriteInputData` を持つ）。

## プロジェクトファイル形式
バイナリ（独自ヘッダ）: `.geom`(GEO130)/`.mesh`(MES8.0)/`.prop`(PRP130材料)/`.cond`(CND110拘束)/`.forc`(FOC110荷重)/`.roi`/`.pai`/`.phan`(校正)/`.ctm`(CT)/`.set`/`.sys`。`data\sample.*` がテンプレ。`proj2text.exe`(GUI) でテキスト化可（読み出しのみ）。
テキスト: 材料 `.dat/.mat`、節点グループ `#MFgroup-points`、メッシュ `inputs.json`。

## 未確定（触る前に実機確認）
- `solver2`/`mesher` の直接引数順。GUI系（proj2text/matdbase/matedit/img2proj/proj_man）の無人実行可否（MFC GUI、headless 不可の可能性大 → 材料割当・BC・結果出力の一部は GUI 自動化に頼る恐れ）。材料割当(.prop)・荷重拘束(.cond/.forc)・EXEC.BINP 生成の GUI 回避経路が最難関。
- 一次資料 `doc\mf_man.pdf`（219頁）。pdftoppm は無いので **pypdf でテキスト抽出**して読む。

## Common Mistakes
- PowerShell で MF exe 起動 → EPERM。必ず Bash + `dangerouslyDisableSandbox`。
- exe を Windows パスで `timeout` に渡す → exit 127。exe は POSIX パス。
- 圧縮 .mhd を inferSend に渡す → FileNotFoundError（.mhd を探す）。非圧縮で書き出す。
- marching cubes STL を直接 FloatTetwild → 四面体爆発。smoothing 必須。
- 絶対破断荷重を臨床値扱い → BC/校正が未閉。**相対ランキング・破断部位・energy で見る**。破断部位が頸部かは**骨マスク重ね画像でユーザー（整形外科医）が目視**。MFメッシュ(tet+shell)は我々の voxel-hex とは別系統なので絶対値比較しない。

## 関連
プロジェクト固有の詳細・実証ログは `<project>/.claude-memory/mf_cli_pipeline.md`。
