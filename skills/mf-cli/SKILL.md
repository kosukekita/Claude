---
name: mf-cli
description: Use when running Mechanical Finder (整形外科CT-FE商用ソフト V13 EE) FEA without its GUI — MFで非線形/線形FEAを回す、solver2 を叩く、EXEC.INP を生成する、破断解析をヘッドレス実行する、複数症例をバッチで回す、Linux(akitaken)やWineでMFを動かす、DICOM読込・骨セグメント・メッシュ生成・材料割当を裏側のバックエンドexeで自動化する、いずれの場合も。トリガー: MFで解く/MFのFEA/MFをCLIで/GUIなしで/バッチで/Mechanical Finder headless/破断解析を自動化/solver2/EXEC.INP/akitakenでFEA/LinuxでMF/Wineで動かす。
---

# Mechanical Finder を CLI で駆動する

## Overview
MF は AVS/Express 製の GUI アプリで CLI 駆動の公式手段は無い（マニュアル219頁にコマンドライン手順なし、solv_cli/bat_solv/proj2text/img2proj は引数なしで GUI を開くだけ）。荷重・拘束は 3D OpenGL ビューでの**節点選択**が本質で pywinauto では届かない。**しかし GUI が裏で叩くバックエンド exe 群を直接起動すれば GUI を回避してパイプラインを組める。材料則・節点グループはテキスト**。

## 🔴🔴 実行機は **akitaken（Linux + Wine）が既定**。Windows で FEA を回さない（★最上位の実行ルール）

**MF の FEA（solver2 = 線形・非線形・破断）は akitaken で実行する。Windows 機での実行は既定ではない。**
2026-07-23 に実機で全面検証済み（Windows 機は i9-14900KF、akitaken は AMD EPYC 7552 48c / 251GB RAM）。

```bash
# これ1行。EXEC.INP のあるディレクトリを渡すだけ
ssh akitaken '/data/kita/mf_work/mfrun.sh /data/kita/mf_work/<case> 12'
# 正常終了 = run_result.txt に rc=0 かつ ExSv_end_1_1=1
```

| 何 | どこ |
|---|---|
| MF 本体 | `/data/kita/mfinder_ee130/`（bin, runtime。897ファイル 1.8GB） |
| Wine | `/data/kita/wine/wine-11.13-staging-amd64-wow64/`（kron4ek portable。**root不要**） |
| WINEPREFIX | `/data/kita/wineprefix` |
| 実行ラッパ | `/data/kita/mf_work/mfrun.sh <workdir> [threads]` |
| 生成器一式 | `/data/kita/mf_work/gen_linux/`（`P:` シンボリックリンク済み） |
| Python | `/data/kita/UKA_FEA_PINN/.venv/bin/python`（numpy+SimpleITK。**uv は無い**） |

### なぜ akitaken か（実測。推測ではない）
- **ライセンス不要**: `solver2.exe`/`solver.exe`/`to_exec.exe` に**ライセンスチェックが存在しない**。
  `License.dat` と `mf_info` を両方消しても同一結果で完走することを対照実験で確認済み
  （文字列走査でも `LICVER|HOSTID|CUSTID` のヒット 0。GUI 系 `mecha.exe`=7件 / `mesher.exe`=6件 とは対照的）。
- **結果が同一**: 同一 EXEC.INP → 要素ステータス完全一致（スレッド数・並列度を変えた **17ラン全部**）。
  変位の最大相対差 1.19e-07（= float32 の機械イプシロン）、応力 9.5e-06、相対差>1e-4 は 0 件。
- **スループット 5.6倍**: 1本×24スレッド=135秒/本 に対し **8本×6スレッド=24.3秒/本**。
  ⚠**スレッドは8超で飽和する**（8th=154s / 24th=135s / 48th=146s）。
  👉 **教師データ生成は「1本を48スレッド」ではなく「多数本を6〜12スレッドで並列」**。
- **メモリ**: 251GB。PARDISO が in-core で回る（out-of-core 回避＝精度ではなく速度の話）。

### EXEC.INP の生成も akitaken でできる（Windows 不要）
`make_exec_inp.py` / `canonical_guard.py` / `mf_material_oracle.py` は **Windows 依存ゼロ**。
同一入力で **Windows と EXEC.INP がバイト完全一致**することを md5 で確認済み。正本ガードも Linux で作動する。
唯一の障害は絶対パス定数3つ（`CALIB_ROOT` / `SITE_CALIB_JSON` / `CANON_MD`）だが、
akitaken には pCloud が `/home/kita/pCloudDrive` にマウント済みなので、**cwd に symlink を置けばコード無改変で解決**する
（Linux では `P:\...` は「バックスラッシュを含む1個のファイル名」なので symlink 名にできる）:
```bash
cd /data/kita/mf_work/gen_linux   # 下記3本は設置済み
ln -sfn /home/kita/pCloudDrive "P:"
ln -sfn /home/kita/pCloudDrive/Data/NAIST/Uzumasa/Calibration 'P:\Data\NAIST\Uzumasa\Calibration'
ln -sfn /home/kita/pCloudDrive/Code/Research/PINN/UZUMASA_DATA_STRUCTURE.md 'P:\Code\Research\PINN\UZUMASA_DATA_STRUCTURE.md'
MF_TET_ORIENT=mf MF_LOAD_SENSE=compression /data/kita/UKA_FEA_PINN/.venv/bin/python make_exec_inp.py \
  <FDNEUT> <CT.mhd> <case> <out_dir> <load_N> matnl force 3.0 30 <none|auto>
```
CT・骨マスク・校正は `/data/kita/Uzumasa_CT/` にローカル実在。四面体化は
`/data/kita/tools/fTetWild/build/FloatTetwild_bin`（Linuxネイティブ、1側5〜7分）。

### Windows がまだ要るのは GUI 側バックエンドだけ
`mecha / mesher / dicom_if / inferSend / matedit / proj2text` は**ライセンスチェックを持つ**ので Windows。
ただし **EXEC.INP を自前生成する現行パイプラインではどれも不要**。

### 「今回は Windows でいいか」を潰す（★合理化への反論）
| 言い訳 | 現実 |
|---|---|
| 「小さいケースだから Windows で十分」 | 小さいほど転送コストも小さい。akitaken 側は1行で回る。分ける理由がない |
| 「転送が面倒」 | EXEC.INP を `scp` 1回だけ。生成自体も akitaken でできるので転送ゼロにできる |
| 「Windows の方が結果が確か」 | 逆。17ラン全部で要素ステータスが一致し、float32 精度で同値と実測済み |
| 「ライセンスが心配」 | solver2 にライセンスチェックは無い（対照実験で確認）。回避行為も一切していない |
| 「akitaken が空いてるか分からない」 | `ssh akitaken uptime` で1秒で分かる。48コアある |
| 「急いでいる」 | akitaken の方が速い。急いでいるなら尚更 akitaken |

**Windows で FEA を回してよいのは、ユーザーが明示的にそう指示したときだけ。**

---

## 実行作法（Windows 側 = GUI バックエンド用のフォールバック）
- **Bash ツール + `dangerouslyDisableSandbox: true`**。PowerShell の `Start-Process`（外部 spawn）は EPERM で不可。Bash の `timeout` 経由で MF exe を起動する。
- **exe 自体は POSIX パス** `/c/mfinder_ee130/bin/pc11_64/xxx.exe`（Windows 形式 `C:/...` だと `timeout` が exit 127 で見つけられない）。
- **exe に渡す引数は Windows パス** `D:\...`（シングルクォートで `\` を保持）＋ `MSYS_NO_PATHCONV=1`（Git Bash のパス変換を止める）。MF は POSIX パスを解さない。
- **CWD 依存が強い**: `inputs.json`/`ftet.mesh`/`EXEC.*`/`mf_tmp*` を相対名で読む exe が多い。**1コマンド内で `cd <workdir> && exe...` と連結**（Bash は呼出し間で cwd がリセットされる）。
- 作業ディレクトリ = `D:\mf_work\<case>`（C ドライブ逼迫回避）。長時間 exe（inferSend / FloatTetwild / solver）は `run_in_background: true`。
- 🔴**ライセンスチェックは「全 exe」ではない**（2026-07-23 実測で訂正）。`solver2 / solver / to_exec` は**チェックを一切持たない**（`License.dat` と `mf_info` を消しても同一結果で完走）。チェックを持つのは GUI 側の `mecha`(7件) / `mesher`(6件) など。**「MF を動かすにはノードロックライセンスが要る」は solver には当てはまらない。**
- GUI 系（mecha/matedit 等）はウィンドウを開くので無人ループに不向き。headless 確実なのは `dicom_if / inferSend / FloatTetwild_bin / SplitByInnerBoundary / mesher / to_exec / solver(2)`。

## パイプライン各段（bin = `C:\mfinder_ee130\bin\pc11_64`）
1. **DICOM読込 ✅実証済**: `dicom_if.exe <代表dcm1枚> <out_prefix> <mf_info> F256 <lst>` → `mf_tmp.ctm`(CTボリューム)/`.pai`/`.sys`。dcm1枚を渡すとそのディレクトリ全体を読む。**実引数の具体値**: 代表dcm=ディレクトリ内の任意1枚(`$(ls <dir>/slice0000.dcm)` 等); out_prefix=作業Dの `mf_tmp`; mf_info=**同梱の入力ファイル `C:\mfinder_ee130\mf_info`**(事前に存在、そのまま渡す); **F256=フィルタ/フォーマットトークン、症例に依らず固定でよい**; lst=dicom_if が書く出力DICOMリスト。実コマンド例は `C:\mfinder_ee130\temp\dicom_if.log` の1行目にも残る。⚠inferSend(段2)は別途 **非圧縮 mf_tmp.mhd** を要求する(dicom_ifの .ctm とは別物)。
2. **骨セグメント**: `inferSend.exe --mode Femur --gpu -1`（CPU。`temp\ai_segment.bat` の実例）。入力=**カレントの非圧縮 `mf_tmp.mhd`**（MET_SHORT, CompressedData=False。圧縮 .mhd は不可 → SimpleITK で `useCompression=False` 書き出し）、出力=`mf_tmp_label.mhd/raw`。⚠**既存の骨マスクがあればこの段は不要** — マスク→表面STLへ直行する。
3. **メッシュ**: `FloatTetwild_bin.exe -i <stl> -o ftet.msh -l <相対edge=目標mm/bbox対角> --epsa <0.1〜0.3> --max-threads 4 --stop-energy 12`（**単一STLでOK**、`--inputs json` は複数用）。皮質シェルは続けて `SplitByInnerBoundary.exe ftet.msh ftet.msh__tracked_surface.stl out.FDNEUT 1e-5`（VTK 製、皮質シェル不要ならこの段はスキップ）。⚠marching cubes の生 STL は階段状で荒く、`epsa 0.1` だと四面体が爆発（例: 470万）→ **STL を Laplacian smoothing してから、edge を大きめ・envelope を緩め**に。
4. **FDNEUT→.geom**: `mesher.exe`（`temp\mesher.log`: FDNEUT読込→GEOM書出し。引数順は未確定）。
5. **材料（テキスト・GUI不要）🔑**: `data\props\*.dat` はテキスト。`Keyak Sample(Eq).dat` の弾性率式が Keyak 区分則（`33900ρ^2.2 / 5307ρ+469 / 10200ρ^2.01`）で、**プロジェクトの `fe/hu_to_E.py` と完全一致**。形式=`<density閾値> <flag> <coef> <exp> <const>`（val = coef·ρ^exp + const）。均質材料=`basicdata_en.mat`（name/ν/E/density/critical/yield/…）。
6. **ソルバ**: `to_exec.exe [EXEC.BINP] [EXEC.INP] (LOG)` が BINP→INP 変換（SOLVER-TYPE V1/V2 判定）→ `solver2.exe`（Intel Fortran + MKL Pardiso, EXEC.INP を読む）→ 結果 `.Bdsp`(変位)/`.Bstr`(応力)。solver.log の SOLUTION PARAMS: DRUCKER-PRAGER ALPHA=0.07(Bessho降伏)。プロジェクト→EXEC.BINP は `solv_cli`/`bat_solv`（GUI だが `CMfilesData::WriteInputData` を持つ）。

## 🔴🔴 要素タイプの真実 = **Tet4 と tri3 しかない**（実機実験で確定・最重要）
**MF solver2 が扱える 3D 連続体要素は 4節点1次四面体(Tet4)ただ一種。SHELL は 3節点1次三角形ただ一種。六面体も二次要素も、入口(メッシャ)でも裏口(EXEC.INP直書き)でも不可能。**

- **パーサの実挙動**: `SOLID` 行の節点IDは**ちょうど4個しか読まれない**。行末の「節点数フィールド」(`... 4`)は分岐に使われず**読まれてすらいない**。
  実証: 健全な Tet4 パッチテスト(解析解と機械精度一致)の SOLID 行に実在IDを4個追記し節点数欄を `8` と詐称しても、`EXEC.Bdsp`/`EXEC.Bstr` が **MD5 バイト単位で完全一致**。→「節点数を8にすれば hex になる」抜け道は**存在しない**。SHELL も 3個固定。
- **hex8 を書くと**: `forrtl severe(157) access violation` で即死。ただし *hex として拒否された* のではない。hex の先頭4節点は必ず同一平面(底面)なので四面体として拾うと体積ゼロ → det(J)=0 → 発散。**先頭4IDだけを残した純 Tet4 ファイルが EXEC.LOG まで完全一致のクラッシュ**を起こす。節点順を変えても結果不変。
- 🔴**Tet10 を書くと＝最も危険な失敗様式**: **エラーも警告も出さず `##$$ExSv end 1 1` で正常終了する。** しかし中間節点6個は黙って捨てられ、結果は角4節点のみの Tet4 版と **MD5 完全一致**。
  → **「2次要素で精度を上げたつもりが、無言で1次に落ちている」事故が起こりうる。** EXEC.INP 生成コードには **「SOLID の節点IDはちょうど4個 / SHELL は3個」の fail-loud アサーションを必ず入れる**こと。
- **バイナリ証拠**: solver2.exe/solver.exe に `HEXA/HEX8/BRICK/TETRA/TET4/TET10/PENTA/WEDGE/PRISM/C3D4/C3D8/C3D10` は ASCII・UTF-16LE 両方で**出現数ゼロ**。要素ラベル表は `SOLID(BONE)/SOLID/SHELL(BONE)/SHELL/RUBBER` の5つのみ。`to_exec.exe` の書式文字列は `SOLID` 直後に `    4`、`mesher.exe` は `SHELL%5d%5d%5d%5d    3 ...` と**節点数がリテラル定数で焼き込まれている**。
- **マニュアル**: 付録4.4「使用要素」は【4節点ソリッド】【3節点シェル】【ギャップ】のみ。「**要素内の歪みは一定となります**」と明記(＝定ひずみ四面体)。「六面体/8節点/10節点/中間節点/高次要素」はマニュアル4冊すべてで**0ヒット**。
- **メッシャ側も四面体固定**: バックエンドは ICEM CFD に `TETRA_4` / `TRI_3` を明示指定して FIDAP(FDNEUT) 出力させている。fTetWild も四面体専用。
- **外部メッシュの取り込みは不可**: MF が読めるのは STL/IMP の**表面形状のみ**。他ソルバの FE メッシュ(節点・要素)をインポートする機能は無い。相互運用は MF→他ソルバの一方向のみ。
- 👉 **含意: MF で精度を上げる手段は p細分(要素次数)ではなく h細分(メッシュ細分)だけ。** 査読で問われるメッシュ収束性は h細分で示すしかない。「Tet10 にして精度を上げる」は**原理的に不可能**なので検討時間を使わないこと。

## 🎯 決め手 = solver2 の入力 EXEC.INP を自前生成する（メッシュ/材料/BCは自前、ソルバだけMF）
mesher/GUI authoring は親 GUI プロセス依存で CLI 不可（断念）。代わりに **`solver2.exe` の入力 `EXEC.INP` が完全に素直な人間可読テキスト（FIDAP風固定幅）と判明** → メッシュ・材料・BC を自前 Python で書いて EXEC.INP を生成し、`solver2.exe`（引数なし、cwd の固定名 EXEC.INP を読む）でFEAだけ回す。

**solver2 実行**: 🔴**既定は akitaken** — `ssh akitaken '/data/kita/mf_work/mfrun.sh <workdir> 12'`（上の実行機セクション参照）。
solver2 は引数なしで cwd の `EXEC.INP` を読み `EXEC.Bdsp`/`EXEC.Bstr`/`EXEC.LOG` を書く。`##$$ExSv end 1 1`（**stdout。EXEC.LOG ではない**）=正常終了。
Windows で直に叩く場合のみ `cd <workdir> && solver2.exe`。

**EXEC.INP 固定幅フォーマット（1バイトもズレ不可＝forrtl severe(64) input conversion error）**: 全キーワードで id 終端=col15。TITLE/CNTND/NODE/CNTEL/SOLID/SHELL/PROPT/CNTRL/CNTR2/CNTR3/PRPLT/PRPL2/CNTLP/CNTPR/KUKAN/NGLD/NLOAD/TBLLD/FORCE/DISP/NGLK/NPLNK/PLNK/END。制御ブロック(CNTR2/CNTR3/PRPLT/PRPL2/CNTLP/CNTPR)と拘束ヘッダ(NGLK/NPLNK)を欠くと STEP=0/access violation。

**解析種フラグ = CNTRL の末尾4桁コード**（行内の数値でない）: `CNTRL0000`=線形 / `CNTRL0110`=幾何+材料非線形 / `CNTRL0010`=材料非線形のみ(幾何OFF)。2桁目=幾何非線形, 3桁目=材料非線形。**薄肉シェル付き破断解析は CNTRL0010(幾何OFF) を使う**(幾何非線形ONだと薄膜シェルが数値発散)。GUI捕捉で確定。

**静解析 vs 動解析（mf_man.pdf 付録4.8）**: 静解析=静的荷重(準静的な圧縮破断荷重=Bessho/Miura型はこれ)。**動解析=慣性を考慮**。マニュアル明記「瞬間的な衝撃荷重を再現する場合、動解析でより現実に近い結果」。→ **インプラントの叩き込み(打ち込み)・転倒外傷など瞬間的衝撃/慣性が効く現象は動解析を使う**。動解析は構造減衰係数(付録4.8)＋総解析時間＋区間数の入力が要る(ソルバV2)。破断荷重(準静的圧縮)は静解析で十分。GUIの解析種で静/動を選ぶ→EXEC.INPのCNTRLコードに反映(動解析版のコードはGUI捕捉で確定する)。

**変位制御**: `NGLD 3` + 3グループ(x/y/z成分), 各グループ `NLOAD g 2 nL`/`TBLLD(0,0)(1.0,方向単位ベクトルのg成分)`/全荷重ノードの`DISP <id> <dx dy dz rx ry rz>`(g軸列に押込量mm)。**★拘束は NGLK 2 の2グループ必須**: 固定面 `PLNK <id>111111`(全固定) + 強制変位面 `PLNK <id>222000`(★DOFコード '2'=強制変位モード。これが無いとMFはDISP値を無視し全ゼロ解になる)。反力は cons枠に固定面(+)と強制変位面(-)が両方入り相殺→**強制変位ノードの反力だけ**が破断荷重。

## 🦴 プロトコルは「解こうとしている骨」の先行研究から取る（★転用禁止）
**脛骨を解くなら脛骨の先行研究。大腿骨(Bessho/Miura)の数値プロトコルを脛骨に持ち込んではならない。**

- **脛骨の参照先** = **HTO(高位脛骨骨切り術)の lateral hinge fracture 解析**: **Itou 2021 (PMID 33557809) / Kuwashima 2024 (PMID 38110736) / Özmen 2024 (PMID 39220812)**。
  MFで脛骨の骨折を実際に解いた研究。**シェル板厚・ν・要素サイズ・材料則・荷重条件はここから取る。**
  自然膝のMF研究(Watanabe 2020/2023, Fukaya 2021, Kozaki 2022)も脛骨を含む。
- ❌ **Bessho 2007 (PMID 17034798) / Miura 2017 (PMID 29246133) はどちらも proximal femur(大腿骨)**。
  **破壊則(DP + 方向性スメアードクラック + 圧壊、σt=0.8σy)の検証**としては引用してよいが、
  **シェル板厚・ν・要素サイズを脛骨に流用しない。**
- **なぜか**: MFのシェルは「**CTのボクセルでは薄すぎて解像できない皮質骨**」を補うためにある。板厚は
  **その骨のその部位の皮質がCTでどれだけ解像できないか**で決まる**部位固有の値**。大腿骨頸部の上外側皮質は
  極端に薄い(0.3〜1mm)のでシェル必須だが、近位脛骨は軟骨下骨プレート＋骨幹端皮質で構造も厚みも違う。
  **臓器が違えば「CTで見えない量」が違う。** ν・要素サイズ・材料則も同様
  (Keyak則の校正は「特定の骨・特定の要素サイズ・特定の破壊則」の組み合わせで屍体実験に合わせた**有効モデル**であり物理定数ではない)。
- 🔴 **プロトコル数値を採用するときは必ず原著本文を取得して直接引用で確認する。伝聞・二次情報・下請けエージェントの報告を数値の根拠にしない。**
  (実害: 2026-07-14、「Besshoのシェル板厚0.4mm」を原著未確認のまま脛骨プロトコルとして推奨し、
  ユーザーに「それは脛骨ですか？」と指摘されて発覚。Besshoは大腿骨だった。)

## 🔴 材料 PROPT の書式・単位（最重要 — 間違えると9.8倍硬い材料になる）
**MFはCT値→密度→ヤング率を直接計算する**（密度をそのままKeyak則に入れる。ρ_ash変換を挟まない）:
```
CT値[HU] →[検量線]→ 密度[g/cm3] →[Keyak則]→ ヤング率[MPa]
```
- 🔴**PROPT は4コードに分かれる（旧メモの「PROPT00122 が全要素数」は誤り）**:
  `PROPT00122`=**骨ソリッド(不均質・要素ごとに全部違う)**, `PROPT00012`=他材料ソリッド(全行同一値: ν=0.28, E=1.110E+04 kgf/mm2=108.9GPa, ρ=4.43 → Ti-6Al-4V),
  `PROPT10012`=他材料ソリッド2(全行同一: ν=0.34, E=196.1GPa, ρ=8.03 → CoCr/SUS), `PROPT00121`=**骨シェル(不均質)**。
  前3者の和 = SOLID 数、最後 = SHELL 数。**不均質なのは骨要素だけで、インプラントは均質材**。
- **材料の生成規則 = average-then-convert**: 要素内17点で CT値(ρ)をサンプル → **要素内で平均** → その後 Keyak 則 E=aρ^b に通す。
  GUI 生成モデルの全 314,260 骨要素で E=Keyak(ρ_element) が**相対誤差0.15%以内で一致**することを実測確認済み。
  👉 これは「MFは要素ごとに不均質なEを持つ」動かぬ証拠であると同時に、「**要素内の材料変化は原理的に表現不可**(定ひずみ四面体＋要素1材料)」という限界の証拠でもある。
  凸なべき則を平均後に通すため、**薄い高密度層＝皮質骨は系統的に軟らかく評価される**(皮質を体積比30%含む要素は Voigt 平均の0.373倍＝剛性を63%過小評価)。
- **PROPT列 = `PROPT00122(solid)/00121(shell)` + id(%10d) + ν・E・density・crit・yield・relax・0・Efloor・Ecap(各 E9.3=`%.3E`を%9s、間にスペース1)**。`relax`=応力緩和係数(骨0.05)、`Efloor/Ecap`=E下限/上限クリップ[kgf/mm2]。正確な桁位置は捕捉版(exec_capture_*)と1バイト照合すること(固定幅厳守)。
- 🔴**単位: E・crit・yield・Efloor・Ecap = [kgf/mm2](MPaでない！ MPa値÷9.80665)。density = [kg/mm3](g/cm3値×1e-6)**。GUI捕捉版がKeyak式+単位変換でピタリ一致して確定。MPaのまま書くとMFは9.8倍硬い材料と解釈し、特に薄肉シェルで応力が非物理発散する。
- **要素ID**: SHELLとSOLIDは**別系統の1始まり独立採番**(SOLID 1..M, SHELL 1..nSH)。PROPT00121もSHELL IDに対応し1始まり。
- **皮質シェル(Miura2017型)**: solid四面体の外表面三角形を`SHELL <id> <n1><n2><n3> 3 <厚み>`で重ねる。**厚み=0.001mm(=MF GUIデフォルト`0.100E-02`)。Miura論文の0.2mmを渡すとシェルが自己応力を持ちsolidを発散させる**(MFは薄膜シェルとして扱う設計)。シェル法線はsolid四面体の対向節点で外向き統一。シェル材料は1000HU相当をKeyak則で計算。

## 🔴🔴 MF の CT値→密度→材料 の内部仕様（実測で完全確定。ground truth = GUI生成 EXEC.INP 314,260要素の全数照合）

### ① 🔴🔴 rho の正体と ash変換 — **ここで重大な誤りを犯した。必ず読め**

#### MF内部の事実（実測。これは正しい）
- MF は **校正が返した密度を、変換を一切挟まずKeyak式に入れる**。
  実測: MF GUI 生成モデルの全314,260要素で E=Keyak(rho_PROPT) が max相対誤差 1.438e-03（0.5%超0件）。
- mf_man p.209:「RODと呼ばれる**ハイドロキシアパタイト相当**の物…既知の密度値」/ p.37:「ROD濃度値(mg/cm3)が既知」
- マニュアル219頁の全文検索: `ash`/`灰密度`/`apparent`/`K2HPO4`/`QCT` はすべて **0件**。

#### 🔴 しかし「ゆえに自前パイプラインでも ash変換を入れてはならない」は **【重大な誤り】**
**MFのash無しKeyakは、MF自身の【125kVp前提】の既定校正 `(HU+1.4246)/1058` とセットで初めて自己整合する。**
別の校正（別の管電圧・別のファントム）を使いながらMFの式だけを真似ると、**どちらの体系でもないハイブリッド**になる。

👉 **「MFに合わせる」とは、同じ骨に対してMFと同じEを出すことであって、違う量にMFの式を当てることではない。**

#### 🔴 Uzumasa プロジェクトの確定チェーン（正本 `P:\Code\Research\PINN\UZUMASA_DATA_STRUCTURE.md:123`）
```
HU --[B-MAS200 ファントム校正: rho_QCT[mg HA/cm3] = slope*HU + intercept]--> rho_HA [g/cm3]
    --[Eberle 2013 HAネイティブ式(★骨だけ): rho_ash = 0.079 + 0.877 * rho_HA]--> rho_ash
    --[Keyak 区分則]--> E, sigma_y

★★ash は【骨にのみ】適用する（正本の機械可読ブロック: ash.apply_to = bone_only）:
    rho_HA >  0 (骨)   : rho_ash = 0.079 + 0.877 * rho_HA
    rho_HA <= 0 (非骨) : rho_ash = 0.0  かつ  E = 0.001 MPa,  sigma_y = 137*0.01^1.88 = 0.0238 MPa
★降伏則(Keyak): sigma_y = 137*rho^1.88 (rho<0.317) / 114*rho^1.72 (rho>=0.317)、rho下限 0.01
   ⚠ `102*rho^1.80` は【極限圧縮強度】であって降伏式ではない。降伏式に使うな。
   sigma_t = 0.8 * sigma_y（★sigma_y が先。逆にするな）
```

#### 🔴🔴 2026-07-15 追記: ash を「非骨(骨髄・空気)」に外挿してはならない（bone_only）
上のチェーンで **ash変換を全要素に当てるのは誤り**。ash式の原典 Schileo 2008 の回帰は
**骨標本60本**に対する校正で、切片 +0.079 は「骨の密度域の回帰切片」であって
「灰分ゼロの組織の灰密度」ではない。`rho_HA=0`（＝ミネラル未検出＝骨髄・空気）へ外挿すると:

- `E = 33900 * 0.079^2.20 = 127.4 MPa` の **『存在しない骨』** が髄腔に生まれる
  （実測骨髄 E = 0.25–24.7 kPa の **5,200〜510,000倍**。Jansen 2015）
- `sigma_y = 1.16 MPa` なので **骨髄が圧壊までする**（実測: 192要素 failed / うち 169 CRUSHED）

**実測（UZU00001 右脛骨。同一メッシュ・BC・ステップで非骨規則だけを変えたA/B）:**

| 量 | ash を全要素に外挿（誤り） | bone_only（正本） |
|---|---|---|
| 非骨要素 | 9,249 / 96,578 = 9.58% | 同じ要素集合 |
| 非骨の E | 127.39 MPa | **0.001 MPa**（÷127,000） |
| 骨要素の E | — | **差 0.000e+00（1個も変わらない）** |
| 線形剛性 k | 6211.5 N/mm | 6155.3 N/mm（−0.905%） |
| 破断荷重 | 3617.8 N | 3552.3 N（−1.81%） |
| 骨髄の降伏・圧壊 | **192個 failed（169 CRUSHED）** | **0 個**（人工物が消えた） |

- 2.0mm メッシュでは非骨が **33,969 / 336,035 = 10.11%**（無視できない主経路）。
- 閾値 `rho_HA <= 0` は**校正密度そのもののゼロ点**であって、新しい閾値の発明ではない
  （MFマニュアル「密度が0.0以下であれば0.0にします」+ 全5材料則で「rho=0 → E=0.001」/
   Tawara 2010（B-MAS200 = Uzumasaと同一ファントム）/ Bonemat py_bonemat_abaqus も同じ）。
- 👉 **`rho_ash >= 0.079 が保証される` と書いてあるコメント・ドキュメントは全て古い。**
  現行チェーンでは `rho_ash` は **「0」か「>=0.079」の二択**（0 < rho < 0.079 は1個も出ない）。

👉 **材料則に触る前に `D:\mf_work\canonical_guard.py` が正本と照合する。コードだけ直しても通らない。**
- 正本 line 123 原文:「出力は **rho_HA（HA等価密度）**。rho_HA→rho_ash は**必ず**HAネイティブ式
  （Eberle2013: rho_ash=0.079+0.877·rho_HA）を使う（K2HPO4用係数1.22に直接入れない）」「HU→E主則 = Keyak区分則」
- 正本 line 107: **MFの標準検量線は125kVp前提。Uzumasa CTは全例100kVp（GE）** で管電圧ミスマッチ→密度過大。
  hold-out実測: 実校正 428.7 vs 施設標準式 442.5（差3%）vs **MF標準式 288.8（33%差）**。
- 🔴 **MF標準検量線を Uzumasa に使ってはならない。**

#### 🔴 やらかした実害（2026-07-14。二度と繰り返すな）
Claudeが「MFにash変換が無いから我々のash変換はバグ」と誤断定して `ASH_A, ASH_B = 0.079, 0.877` を削除。
- 破断荷重が **3,365 N → 1,359 N（半減）**
- 海綿骨（破壊が集中する帯）の sigma_y が **4.13 → 1.39 MPa（1/3）**、E が **562 → 157 MPa（1/3.6）**
- さらに「独立オラクル」を作って**その誤りを正解として固定**し、ash検出でエラー停止するガードまで入れた
  ＝**検証機構が誤った的を撃つ**状態を作った
- **根本原因: `UZUMASA_DATA_STRUCTURE.md` を一度も読まずにMFをリバースエンジニアリングして正本を上書きした。**
  CLAUDE.md は「Uzumasaデータを扱う作業に着手する前に**必ずこれを見る**」と明示している。

👉 **Uzumasa/PINN プロジェクトで材料則に触る前に、必ず `UZUMASA_DATA_STRUCTURE.md` を読む。**
👉 **MFのリバースエンジニアリング結果が、プロジェクト正本と食い違ったら、正本が勝つ。**
   （MF内部の観測は「MFがMF自身の校正で何をしているか」であって、「我々が我々の校正で何をすべきか」ではない）

### ② CT値 → 密度（3経路。途中に物理変換なし）
- **ファントム/ユーザー定義**: `rho[mg/cm3] = CT値 × a + b`、**0以下は0にクリップ**（p.176）→ 材料則へ渡す前に **÷1000** で g/cm3
- **ファントム未使用＝工場出荷既定**: `rho[g/cm3] = (CT値+1.4246)×0.001/1.0580` (CT値>-1) / 0.0 (CT値<=-1)。**125kVp前提**（p.177）
- 👉 **我々の B-MAS200 校正 (rho[mg/cm3]=slope*HU+intercept) は、MFのユーザー定義換算式と定義・単位・関数形・0クリップまで完全に同一。
  これを使うこと自体が MF準拠**（MFはファントム経路を一級機能として持つ）。
- ⚠️ `exec_capture`（GUI捕捉 ground truth）は **125kVp標準検量線（ファントム未使用）**で作られている。

### ③ 要素内のCT値サンプリング（average-then-convert）
要素内 **17点**（要素中心＋各頂点方向へ5分割した各4点、頂点は除く）を取り、各点のCT値を**その点を含むセルの8頂点から補間**して求め、**17点を平均**（mf_tut2 §14.3）。
→ 要素平均CT値 → 密度 → 材料則。**単純な最近傍でも重心1点でもない。**（我々は重心1点だった＝要修正）

### ④ 密度 → ヤング率 E [MPa]（Keyak）
```
rho = 0        -> E = 0.001        ★特別扱い（付録3の全5材料則に共通で明記）
0 < rho <= 0.27 -> E = 33900*rho^2.20
0.27 < rho < 0.6 -> E = 5307*rho + 469
rho >= 0.6      -> E = 10200*rho^2.01     （マニュアルの「10.200」は誤植。実測で10200と確定）
```
- 🔴 **`rho=0 -> E=0.001` を実装し忘れると `33900*0^2.2 = 0` になり剛性行列が特異化してソルバが落ちる。**
  MFが極小の非ゼロ値を使うのはまさにこれを避けるため。実測でも E=0.0010003 MPa の要素が **14,210個**（= n(rho==0)）実在。
- **E に密度クランプは無い。** 上下限クリップ機能はあるが **既定OFF**（捕捉モデルの PROPT: Efloor=1.000E-06 / Ecap=1.000E+04 kgf/mm2
  ＝実質無効。MF自身が 0.001〜**28,076 MPa** を素通ししている）。**自前で floor=10 / cap=20000 MPa を掛けてはならない。**

### ⑤ 密度 → 圧縮降伏応力 sigma_y [MPa]（Keyak）
```
rho <- max(rho, 0.01)          ★★密度に下限0.01のクランプ（マニュアル全219頁に記載なし。実測でのみ判明）
rho < 0.317  -> sigma_y = 137*rho^1.88
rho >= 0.317 -> sigma_y = 114*rho^1.72
sigma_t (引張臨界応力) = 0.8 * sigma_y   （実測 median=0.800000）
```
- 実測: max相対誤差 **1.270e-03**（0.5%超0件）。クランプ無しだと rho=0 で sigma_y=0 になり破綻。
  rho=0 の 14,210要素は一意に **sigma_y = 137*0.01^1.88 = 0.0238105 MPa**。
- 🔴 **E には 0.01クランプが掛からない（rho=0→0.001 の特別扱い、0<rho<0.01 は素の 33900rho^2.20）。この非対称は実測で確定。**

### ⑥ 🔴「弾性要素」トグル（rho<=0.2 を降伏させない）は **既定 OFF**
- mf_man **p.95 原文**:「降伏応力には上記トグルもあり（**初期ではOFF状態**）、密度値**200mg/cm3以下**を弾性要素とするかを選択できます。」
- マニュアル p.178 は Keyak の降伏表を**2つ併記**（1e20あり版 / 「弾性要素無しの場合」版）。props も2ファイル
  （`Keyak Sample(Eq).dat`=1e20なし / `Keyak Sample(Val).dat`=250点テーブルで rho=0〜0.20 が 1e20）。**矛盾ではなくトグルの2態。**
- 🔴 **実データが決着**: GUI捕捉 314,260要素で **sigma_y >= 1e6 MPa の要素は 0個**（最大 271 MPa）。
  **rho <= 0.2 の 103,967要素(33.08%) すべてが有限の sigma_y**（min 0.0238 / median 1.41 / max 6.65 MPa）。
  👉 **MF既定は 1e20 を使わない。rho<=0.2 にも 137rho^1.88 を延長する。**「rho<=0.2 に有限強度を与えるのはバグ」は**誤り**。
- ただしこのトグルは **v11.0 で初期値が変更された GUI永続設定**（版履歴に「初期値設定は以前のバージョンから引き継がれません」）。
  **MFが常にOFFとは限らない。**捕捉モデル(TITLE=V11.0, 圧壊ひずみ=10000)は v11.0既定と整合。

### ⑦ 単位の独立検証（骨もKeyakも使わずに証明できる）
捕捉モデルの `PROPT00012` = (0.28 / 11100 / 4.43e-6 / …) と `PROPT10012` = (0.34 / 20000 / 8.03e-6 / …) が、
`C:\mfinder_ee130\data\props\basicdata_en.mat` の **Titanium_alloy / Stainless_steel の行と完全一致**。
11100 kgf/mm2 × 9.80665 = **108.9 GPa**（Ti-6Al-4V 教科書値 110-114 GPa）、20000 → **196.1 GPa**（SUS316L 193-200 GPa）。
→ **E・応力 = kgf/mm2、密度 = kg/mm3 が確定**（MPaと読むとTiが11.1 GPaになり成立しない）。

### ⑧ PROPT の列（実測確定）
`[要素ID, ν, E, 密度, σt(引張臨界), σy(圧縮降伏), 応力緩和係数, ?, Efloor, Ecap]`（末尾に圧壊ひずみ）
捕捉モデルの骨: **ν=0.4 / 応力緩和係数=0.05 / 圧壊ひずみ=10000**（いずれも全要素一定）。

## CT値→密度の検量線（Keyak則の入力密度をどう作るか, mf_man.pdf第8章）
- **ファントム設定時**: 密度[mg/cm3] = CT値×a + b（a,bはファントム4ロッドで校正した値）。
- **ファントム未使用時 = 標準検量線**: `密度[g/cm3] = (CT値[H.U.] + 1.4246) × 0.001 / 1.0580` (CT値>-1), 0 (CT値≦-1)。⚠**X線管電圧125kVp前提**（マニュアル注記）。管電圧が違うCTでは系統誤差。
- この密度[g/cm3]を **そのままKeyak則**（E=33900ρ^2.2(ρ≤0.27)/5307ρ+469(0.27<ρ<0.6)/10200ρ^2.01(ρ≥0.6)[MPa]、`Keyak Sample(Eq).dat`と一致）に入れてヤング率を得る。降伏応力も密度から（Keyak S=137ρ^1.88 等）。

## プロジェクトファイル形式
バイナリ（独自ヘッダ）: `.geom`(GEO130)/`.mesh`(MES8.0)/`.prop`(PRP130材料)/`.cond`(CND110拘束)/`.forc`(FOC110荷重)/`.roi`/`.pai`/`.phan`(校正)/`.ctm`(CT)/`.set`/`.sys`。`data\sample.*` がテンプレ。`proj2text.exe`(GUI) でテキスト化可（読み出しのみ）。
テキスト: 材料 `.dat/.mat`、節点グループ `#MFgroup-points`、メッシュ `inputs.json`。

## 未確定（触る前に実機確認）
- 🔴**変位制御(DISP + PLNK 222)の荷重符号**。荷重制御(FORCE)では「負の fz → 引張」が確定したが、変位制御でも同じ符号反転が起きるかは未実験。**本番の破断解析は変位制御が主経路なので必ず埋めること**。単位立方体の一軸パッチテストを回帰テストとして常設し「圧縮を指示したら σ3=−P/A になる」を assert するのが確実。
- **シェル板厚**。GUI 捕捉モデルは SHELL 全 34,384 枚が **0.001mm ＝ 膜剛性∝t・曲げ剛性∝t^3 で構造寄与ゼロ**(接触面 CSURF/CBODY 用)で、Bessho/Miura 型の 0.2〜0.4mm 皮質シェルではない。**このモデルでは皮質を四面体だけが担っている**。先行研究プロトコル再現を主張するなら板厚設定を必ず確認する。
- **ポアソン比**。捕捉モデルは ν=0.4(全骨要素一定)。Miura 2017 は ν=0.3。どの先行研究プロトコルを再現すると主張するかで決まる。
- **CNTEL 第3〜5スロットの意味**。RUBB カードの綴り・列レイアウト・専用 PROPT も不明。使わない。
- `solver2`/`mesher` の直接引数順。GUI系（proj2text/matdbase/matedit/img2proj/proj_man）の無人実行可否（MFC GUI、headless 不可の可能性大 → 材料割当・BC・結果出力の一部は GUI 自動化に頼る恐れ）。材料割当(.prop)・荷重拘束(.cond/.forc)・EXEC.BINP 生成の GUI 回避経路が最難関。
- 一次資料 `doc\mf_man.pdf`（219頁）。pdftoppm は無いので **pypdf でテキスト抽出**して読む。

## Common Mistakes
- 🔴🔴**FEA を Windows で回す → 既定違反**。solver2 は akitaken で回す（ライセンス不要・結果同一・スループット5.6倍を実測済み）。「小さいから」「急いでいるから」は理由にならない（上の合理化表を読め）。
- 🔴**スレッドを48に上げる → 効かない**。8超で飽和（8th=154s / 24th=135s / 48th=146s）。**多数本を6〜12スレッドで並列**が正解。
- 🔴**`##$$ExSv end 1 1` を EXEC.LOG から grep する → 常に0件**。このマーカは **stdout** に出る。`run_stdout.txt` を見る。
- 🔴**EXEC.LOG は CRLF**。`grep -oE "[0-9]+$"` は `\r` で外れて「不一致」を誤検出する。必ず `tr -d "\r"` を噛ませる。
- **古い EXEC.INP と新生成物を比べて「Linux が壊れている」と誤断定する**。生成器はバージョンで出力が変わる（要素数・Efloor/Ecap・HUサンプリング法）。**プラットフォーム差を疑う前に、節点座標が一致するか＝同じメッシュかを見る**。
- 🔴🔴**「MFにash変換が無いから、自前パイプラインのash変換もバグだ」と考える → 【重大な誤り】。**
  MFのash無しKeyakはMF自身の125kVp校正とセットで自己整合する。別の校正を使うなら別の話。
  **Uzumasa の確定チェーンは rho_HA →[Eberle2013 ash]→ rho_ash → Keyak**（正本 UZUMASA_DATA_STRUCTURE.md:123）。
  実害: 削除して破断荷重が半減、海綿骨のsigma_yが1/3に。**材料則に触る前に必ず正本を読め。**
- 🔴**「Tet10 にすれば精度が上がる」と思って10節点を書く → MFは無言で中間節点を捨てて Tet4 として解き、正常終了する**。エラーも警告も出ない。精度が静かに落ちる。生成コードに「節点IDちょうど4個」の assert を入れる。
- 🔴**「節点数フィールドを8にすれば hex が通る」と考える → 通らない**。そのフィールドは読まれていない。hex は先頭4節点(同一平面)を四面体として拾って体積ゼロで死ぬだけ。
- 🔴**FORCE カードの符号が座標軸と逆**: 負の `fz` を書くと **+z へ変位し「引張」**になる。−z へ圧縮したければ**正の `fz`** を書く。線形弾性の応力符号で確定(負fz → σ1=+10 全要素＝引張 / 正fz → σ3=−10＝圧縮)。線形なら鏡像で実害ないが、**Drucker-Prager＋方向性クラックの非線形破断解析では引張/圧縮が非対称なので致命的**。※変位制御(DISP+PLNK 222)経路の符号は**未検証**。
- **CNTEL 第3スロットを RUBBER と思い込む → 違う**。第3に 16 を書くと LOG に「RUBBER: 0 / GAP: 48(=16×3)」と出る。**第1=SOLID・第2=SHELL のみ確定。第3以降は 0 のままにする**。
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
akitaken 実行環境の構築経緯・実測値の全数は `P:\Code\Research\PINN\.claude-memory\project_mf_solver2_on_linux_wine.md`。
