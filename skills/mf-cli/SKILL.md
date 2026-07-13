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

## 🎯 決め手 = solver2 の入力 EXEC.INP を自前生成する（メッシュ/材料/BCは自前、ソルバだけMF）
mesher/GUI authoring は親 GUI プロセス依存で CLI 不可（断念）。代わりに **`solver2.exe` の入力 `EXEC.INP` が完全に素直な人間可読テキスト（FIDAP風固定幅）と判明** → メッシュ・材料・BC を自前 Python で書いて EXEC.INP を生成し、`solver2.exe`（引数なし、cwd の固定名 EXEC.INP を読む）でFEAだけ回す。

**solver2 実行**: `cd <workdir> && solver2.exe`（引数なし）。cwd の `EXEC.INP` を読み `EXEC.Bdsp`/`EXEC.Bstr`/`EXEC.LOG` を書く。`##$$ExSv end 1 1`=正常終了。

**EXEC.INP 固定幅フォーマット（1バイトもズレ不可＝forrtl severe(64) input conversion error）**: 全キーワードで id 終端=col15。TITLE/CNTND/NODE/CNTEL/SOLID/SHELL/PROPT/CNTRL/CNTR2/CNTR3/PRPLT/PRPL2/CNTLP/CNTPR/KUKAN/NGLD/NLOAD/TBLLD/FORCE/DISP/NGLK/NPLNK/PLNK/END。制御ブロック(CNTR2/CNTR3/PRPLT/PRPL2/CNTLP/CNTPR)と拘束ヘッダ(NGLK/NPLNK)を欠くと STEP=0/access violation。

**解析種フラグ = CNTRL の末尾4桁コード**（行内の数値でない）: `CNTRL0000`=線形 / `CNTRL0110`=幾何+材料非線形 / `CNTRL0010`=材料非線形のみ(幾何OFF)。2桁目=幾何非線形, 3桁目=材料非線形。**薄肉シェル付き破断解析は CNTRL0010(幾何OFF) を使う**(幾何非線形ONだと薄膜シェルが数値発散)。GUI捕捉で確定。

**変位制御**: `NGLD 3` + 3グループ(x/y/z成分), 各グループ `NLOAD g 2 nL`/`TBLLD(0,0)(1.0,方向単位ベクトルのg成分)`/全荷重ノードの`DISP <id> <dx dy dz rx ry rz>`(g軸列に押込量mm)。**★拘束は NGLK 2 の2グループ必須**: 固定面 `PLNK <id>111111`(全固定) + 強制変位面 `PLNK <id>222000`(★DOFコード '2'=強制変位モード。これが無いとMFはDISP値を無視し全ゼロ解になる)。反力は cons枠に固定面(+)と強制変位面(-)が両方入り相殺→**強制変位ノードの反力だけ**が破断荷重。

## 🔴 材料 PROPT の書式・単位（最重要 — 間違えると9.8倍硬い材料になる）
**MFはCT値→密度→ヤング率を直接計算する**（密度をそのままKeyak則に入れる。ρ_ash変換を挟まない）:
```
CT値[HU] →[検量線]→ 密度[g/cm3] →[Keyak則]→ ヤング率[MPa]
```
- **PROPT列 = `PROPT00122(solid)/00121(shell)` + id(%10d) + ν・E・density・crit・yield・relax・0・Efloor・Ecap(各 E9.3=`%.3E`を%9s、間にスペース1)**。`relax`=応力緩和係数(骨0.05)、`Efloor/Ecap`=E下限/上限クリップ[kgf/mm2]。正確な桁位置は捕捉版(exec_capture_*)と1バイト照合すること(固定幅厳守)。
- 🔴**単位: E・crit・yield・Efloor・Ecap = [kgf/mm2](MPaでない！ MPa値÷9.80665)。density = [kg/mm3](g/cm3値×1e-6)**。GUI捕捉版がKeyak式+単位変換でピタリ一致して確定。MPaのまま書くとMFは9.8倍硬い材料と解釈し、特に薄肉シェルで応力が非物理発散する。
- **要素ID**: SHELLとSOLIDは**別系統の1始まり独立採番**(SOLID 1..M, SHELL 1..nSH)。PROPT00121もSHELL IDに対応し1始まり。
- **皮質シェル(Miura2017型)**: solid四面体の外表面三角形を`SHELL <id> <n1><n2><n3> 3 <厚み>`で重ねる。**厚み=0.001mm(=MF GUIデフォルト`0.100E-02`)。Miura論文の0.2mmを渡すとシェルが自己応力を持ちsolidを発散させる**(MFは薄膜シェルとして扱う設計)。シェル法線はsolid四面体の対向節点で外向き統一。シェル材料は1000HU相当をKeyak則で計算。

## CT値→密度の検量線（Keyak則の入力密度をどう作るか, mf_man.pdf第8章）
- **ファントム設定時**: 密度[mg/cm3] = CT値×a + b（a,bはファントム4ロッドで校正した値）。
- **ファントム未使用時 = 標準検量線**: `密度[g/cm3] = (CT値[H.U.] + 1.4246) × 0.001 / 1.0580` (CT値>-1), 0 (CT値≦-1)。⚠**X線管電圧125kVp前提**（マニュアル注記）。管電圧が違うCTでは系統誤差。
- この密度[g/cm3]を **そのままKeyak則**（E=33900ρ^2.2(ρ≤0.27)/5307ρ+469(0.27<ρ<0.6)/10200ρ^2.01(ρ≥0.6)[MPa]、`Keyak Sample(Eq).dat`と一致）に入れてヤング率を得る。降伏応力も密度から（Keyak S=137ρ^1.88 等）。

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
- 🔴**PROPT の E/応力を MPa のまま書く → MFは9.8倍硬い材料と解釈**（MFはkgf/mm2）。密度をg/cm3のまま書く→100万倍（MFはkg/mm3）。E÷9.80665、density×1e-6 で変換。solidは動くが破断荷重が全部間違い、薄肉シェルは非物理発散。
- 🔴**シェル厚みに Miura論文の0.2mm を渡す → シェルが自己応力を持ちsolid応力が数万〜数百万MPaに発散**。MFは薄膜シェルとして 0.001mm(GUIデフォルト)で扱う。
- **SHELL要素IDをSOLIDの続き(M+1〜)にする → ID衝突で材料割当が壊れる**。SHELLは1始まり独立採番。
- **変位制御で強制変位面を PLNK 222000 で拘束しない → DISP値が無視され全ゼロ解**。
- **CNTRLの行内数値を変えて非線形化しようとする → 効かない**。フラグはキーワード末尾4桁コード(CNTRL0110等)。
- 絶対破断荷重を臨床値扱い → BC/校正が未閉。**相対ランキング・破断部位・energy で見る**。破断部位が頸部かは**骨マスク重ね画像でユーザー（整形外科医）が目視**。MFメッシュ(tet+shell)は我々の voxel-hex とは別系統なので絶対値比較しない。

## 関連
プロジェクト固有の詳細・実証ログは `<project>/.claude-memory/mf_cli_pipeline.md`。
