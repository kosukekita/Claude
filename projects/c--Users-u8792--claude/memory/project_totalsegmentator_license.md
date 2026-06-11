---
name: project_totalsegmentator_license
description: TotalSegmentatorアカデミックライセンス＋全ライセンスタスクのモデルDL作業。ローカルは中断、リモートGPU PCで再開予定
metadata: 
  node_type: memory
  type: project
  originSessionId: 213c11d7-5066-46e7-968c-ac34498cfd29
---

# TotalSegmentator ライセンス & ライセンスタスク・モデルDL

2026-06-02 にアカデミックライセンス取得（登録メール: kita.kosuke@naist.ac.jp）。非オープンの追加タスク（下記15）が利用可能。
**方針: ローカルPCはGPU無しでモデルDLが重いため中断。GPU搭載のリモートPCでDLを行う。** 本メモはリモートで再開するための完全手順。

## ライセンスと保存場所
- 有効化: `totalseg_set_license -l <ライセンス番号>`（番号は秘密情報。メモリ/Gitに置かない。取得元の登録メールを参照）
- 保存先: `~/.totalsegmentator/config.json` のJSONキー `"license_number"`（平文。Windowsなら %USERPROFILE%\.totalsegmentator\config.json、Linuxなら ~/.totalsegmentator/config.json）
- 既定パスは `Path.home()/.totalsegmentator`。環境変数 `TOTALSEG_HOME_DIR` で変更可（モデル重みもこの配下 `nnunet/results` に入る）
- ライセンスはマシンごとに設定が必要。リモートPCでも最初に `totalseg_set_license` を1回実行する

## インストール（リモートGPU PCで実施）
- 推奨: `uv tool install TotalSegmentator`（グローバルCLI。どのディレクトリからでもコマンド可）。導入済みバージョンは totalsegmentator 2.13.0
- GPU PCでは **CUDA版PyTorch** が入ることを確認（`python -c "import torch; print(torch.cuda.is_available())"` がTrue）。uvのデフォルトでCPU版torchが入る場合は、CUDA対応torchを別途指定して入れ直す（python-rules スキルのPyTorch CUDA選択を参照）
- 入る実行ファイル: TotalSegmentator, totalseg_download_weights, totalseg_set_license など11個

## モデルDLコマンド（推論不要でDLだけ）
- 1タスク: `totalseg_download_weights -t <task_name>`（タスク名で指定。整数IDではない）
- `-t all` は**ライセンスモデルも含めて全部**DLする（CLIのallは commercial を除外しない。総容量が巨大なので非推奨）
- DL前にライセンス設定が必須（`totalseg_set_license` を先に実行）

## ライセンスタスク全15（commercial_models, map_to_binary.py）
heartchambers_highres(301,CT) / appendicular_bones(304,CT) / appendicular_bones_mr(855,MR) / tissue_types(481,CT) / tissue_types_mr(925,MR) / tissue_4_types(485,CT) / vertebrae_body(305,CT) / face(303,CT) / face_mr(856,MR) / brain_structures(409) / thigh_shoulder_muscles(857,CT) / thigh_shoulder_muscles_mr(857,MR・**CTと同一ID857を共有=1回のDLで両方分**) / coronary_arteries(509,CT現行) / coronary_arteries_LEGACY(507,CT旧) / aortic_sinuses(920,CT)
- 注: READMEには brain_aneurysm も載るが、コード上は license gate(show_license_info)が無いのでライセンス対象外。
- 実質ユニークなDL対象は14モデル（857が共有のため）。

## ローカルPCの中断時点（2026-06-02）
DL済み（`~/.totalsegmentator/nnunet/results`、計約1.3GB）:
Dataset301(heart_highres) / Dataset304(appendicular_bones) / Dataset481(tissue) / Dataset485(tissue_4types) / Dataset925(MRI_tissue) ＝ 5モデル完了。vertebrae_body のDL中に中断。
→ **リモートで全15タスクを最初からDLし直す前提**（ローカル分は流用しない）。各モデルは概ね200MB台〜。

## 再開手順（リモートGPU PC）
1. `uv tool install TotalSegmentator`（CUDA torch確認）
2. `totalseg_set_license -l <番号>`
3. 下記ループで15タスクをDL（PowerShell例。bashなら適宜変換）:
   tasks = heartchambers_highres, appendicular_bones, appendicular_bones_mr, tissue_types, tissue_types_mr, tissue_4_types, vertebrae_body, face, face_mr, brain_structures, thigh_shoulder_muscles, thigh_shoulder_muscles_mr, coronary_arteries, coronary_arteries_LEGACY, aortic_sinuses
   各 `totalseg_download_weights -t <task>`
4. 検証: `~/.totalsegmentator/nnunet/results` に Dataset301/304/305/303/409/481/485/509/507/855/856/857/920/925 が揃うこと

**How to apply:** リモートGPU PCでTotalSegmentatorの追加タスクを使う際の作業再開ポイント。番号秘匿・CUDA torch確認・857共有・allは非推奨が要点。（python-rules スキル参照）

