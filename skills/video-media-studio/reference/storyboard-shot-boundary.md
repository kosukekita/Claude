# Storyboard Shot Boundary Guard

動画生成前のストーリーボードは、**1ストーリーボード=1連続ショット=1 i2v クリップ**で固定する。承認しやすさ、見栄え、同じ作品内の流れ、同じ登場人物、同じ音楽、同じロケーションは、複数カットを1枚のストーリーボードに束ねる理由にならない。

## 1連続ショットの定義

**1連続ショット**とは、1つのカメラ/視点/時間軸が途切れず、i2v の開始画像から終了画像まで自然に補間できる単一の映像区間のこと。

次のどれかが1回でも起きたら、そこでショットを分け、別ストーリーボード・別クリップにする。

- カメラのカット: 画角、レンズ感、カメラ位置、被写体サイズ、視点高さ、向きが瞬間的に切り替わる。
- 場面転換: 場所、背景、照明条件、天候、時間帯、セット、群衆/小物の配置が別シーンになる。
- 時間ジャンプ: 連続動作では説明できない時刻移動、数秒以上の省略、巻き戻し/早送り、別時点への飛び。
- 構図ジャンプ: フルショットからバストアップ、屋上俯瞰からローアングル、正面から背面など、連続カメラ移動だけでは届かない変化。
- アクションの非連続: 同じ人物でも、姿勢・向き・髪/衣装状態・持ち物・位置関係が途中で飛ぶ。

**同じ作品として連続して見せたい**ことと、**1つの i2v クリップとして連続補間できる**ことは別。前者は編集で作る。後者だけが1ストーリーボードに入る。

## i2v start/end 補間としての技術的理由

i2v の start/end 指定は、開始画像と終了画像の間を「同一ショット内の連続運動」として補間する。途中にカット、場面転換、時間ジャンプを入れる制御点はない。

そのため、1枚のストーリーボードに複数カットを束ねると、モデルは次のどれかで破綻しやすい。

- 別カットの開始/終了を連続変形として解釈し、背景・顔・服・カメラ位置が溶ける。
- 本来は編集点で切るべき瞬間を、モーフィング、ワープ、スロー、疑似 freeze で埋める。
- クリップ内に存在しない中間キーフレームをエージェントが脳内補完し、実生成時に再現不能になる。
- 承認済みの見た目と実際の start/end 入力がずれ、ユーザー承認が意味を失う。

よって、**ストーリーボード画像1枚に含める実画像は開始キーフレームと終了キーフレームの2枚だけ**にする。複数ショットの一覧をユーザーに見せたい場合は、各ショットの個別ストーリーボードを別ファイルとして作り、メッセージ上で複数ファイルを並べて提示する。

## Rationalization table

| 言い訳(rationalization) | 判定 | 正しい処理 |
|---|---|---|
| 「承認しやすいから1枚にまとめる」 | 禁止。承認効率はショット境界を破る理由にならない。 | `storyboard_<shot>_001.png/txt` をショットごとに作り、一覧として提示する。 |
| 「1つの連続した流れだから1ボードでよい」 | 禁止。流れと連続ショットは別概念。カットがあれば別ボード。 | カットごとに別 i2v クリップを作り、編集段階で concat する。 |
| 「同じ登場人物・同じ街だから1ショット扱い」 | 禁止。被写体や世界観が同じでも、画角/時間/場所が飛べば別ショット。 | ファイル名と `shot_id` を分ける。 |
| 「txtには C1/C2/C3 と書いてあるから大丈夫」 | 禁止。1つの txt に複数クリップを含めた時点で違反。 | 1 txt = 1 clip。C1/C2/C3 は別ファイルにする。 |
| 「1枚の大きな画像に3行で並べるだけなら生成入力は分ける」 | 禁止。承認対象と生成入力が分離し、確認が壊れる。 | 承認画像そのものをショット単位に分ける。 |
| 「雰囲気確認用のまとめボードだから例外」 | 禁止。動画生成前の storyboard 名を持つ成果物はすべてこの不変条件に従う。 | 雰囲気用は `moodboard_*.png` と命名し、生成承認用 storyboard と混同しない。 |

## Red flags

次の語や構造が出たら STOP し、作る前に分割する。

- `C1/C2/C3`, `cut 1`, `shot 1/2/3`, `3 rows`, `3行`, `sequence`, `montage` が1つの `storyboard_*.txt` に出る。
- `start/end` の組が2組以上ある。
- `duration` が複数ある。
- `scene`, `location`, `camera`, `time` が途中で変わる。
- 「承認しやすい」「一覧性」「同じ流れ」「まとめて見せる」「1枚で確認」のために束ねようとしている。
- 1枚の画像に複数行・複数カット・複数クリップを配置しようとしている。

## 機械的にチェックできる不変条件

`storyboard_*.txt` は、最低限次のヘッダを持つ strict 形式にする。

```text
storyboard_id: storyboard_rewind_city_c1_001
shot_id: rewind_city_c1
clip_id: 001
model: kling_i2v
duration_sec: 5
start_keyframe: keyframes/rewind_city_c1_001_start.png
end_keyframe: keyframes/rewind_city_c1_001_end.png
continuity: single_continuous_shot
cut_count: 0
scene_changes: none
time_jumps: none
camera: neon rooftop wide shot, slow push-in only
content: one continuous rooftop shot; no cut; no time jump
```

不変条件:

- `storyboard_id` はファイル basename と一致する。
- basename は `storyboard_<shot>_NN`。例: `storyboard_rewind_city_c1_001.txt`。
- 同 basename の `.png` が存在する。
- 1 txt に `duration_sec` は1つだけ。`start_keyframe` と `end_keyframe` も1つずつだけ。
- `duration_sec` は使用バックエンドの生成可能尺内。Kling i2v は 3-15 秒、Seedance i2v は 4-15 秒。
- `continuity` は `single_continuous_shot`。
- `cut_count` は `0`。
- `scene_changes` は `none`。
- `time_jumps` は `none`。
- `start_keyframe` と `end_keyframe` は別ファイルで、実在する。
- 1つの txt に `C1/C2/C3`、複数の `shot_id`、複数の `clip_id`、複数の `duration_sec` が出てはいけない。
- `camera` や `content` に「cut」「scene change」「time jump」「montage」「別カット」「場面転換」など、ショット分割を示す語が出てはいけない。

チェック:

```bash
source scripts/env.sh
"$UV" run scripts/check_storyboards.py /path/to/project/storyboards
```

## 命名とディレクトリ構成

推奨:

```text
project/
  storyboards/
    storyboard_<shot>_001.png
    storyboard_<shot>_001.txt
  keyframes/
    <shot>_001_start.png
    <shot>_001_end.png
  clips/
    <shot>_001.mp4
  edit/
    concat.txt
    final.mp4
```

`<shot>` は作品内のカット単位で固定する。1つの作品に3カットあるなら、`c1`, `c2`, `c3` を同じファイルに押し込まず、3つの `shot_id` に分ける。

## REWIND CITY の正しい分割例

誤り: `REWIND CITY` の C1 ネオン屋上5s / C2 ローアングル歩み寄り6s / C3 バストアップ・ヘアフリップ4s を、3行x開始/終了の1枚 `storyboard_rewind_city.png` にまとめる。

正解: 3カットなので、3つのストーリーボード、3つの i2v クリップ、最後に ffmpeg concat。

```text
rewind-city/
  storyboards/
    storyboard_rewind_city_c1_001.png / .txt
    storyboard_rewind_city_c2_001.png / .txt
    storyboard_rewind_city_c3_001.png / .txt
  keyframes/
    rewind_city_c1_001_start.png / _end.png
    rewind_city_c2_001_start.png / _end.png
    rewind_city_c3_001_start.png / _end.png
  clips/  rewind_city_c1_001.mp4 / c2 / c3
  edit/   concat.txt / rewind_city_final.mp4
```

concat:

```text
# rewind-city/edit/concat.txt
file '../clips/rewind_city_c1_001.mp4'
file '../clips/rewind_city_c2_001.mp4'
file '../clips/rewind_city_c3_001.mp4'
```

```bash
cd rewind-city/edit
ffmpeg -hide_banner -y -f concat -safe 0 -i concat.txt -c copy rewind_city_final.mp4
```

コーデック/解像度/fps が揃わない場合は `reference/ffmpeg-recipes.md` の concat filter で正規化してから結合する。
