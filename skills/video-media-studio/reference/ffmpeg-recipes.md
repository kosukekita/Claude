================================================================================
FFMPEG RECIPES — Video Editing Toolkit Reference
================================================================================

Heavy reference for the `video-media-studio` skill's editing flow. Loaded only
when the user is editing existing video. The wrapper script
`scripts/edit_video.py` injects the safe defaults below for the common ops;
fall back to this cookbook for exotic cases. All commands run through the
anaconda-clean environment (`source scripts/env.sh` first) so ffmpeg's libs are
not polluted by conda's libtinfo.

Conventions used below:
  in.mp4 / in2.mp4 ... input files
  out.mp4          ... output file
  Replace codecs/values to taste. Verified against ffmpeg 6.1.1 on this rig
  (libx264, libx265, libfreetype/fontconfig=drawtext, libass, xfade,
   acrossfade, sidechaincompress, setpts/atempo, overlay, scale/pad/crop,
   fps, fade/afade all present).
  -hide_banner -y can be added to every command (suppress banner / overwrite).
    -y = overwrite output without asking.  -n = never overwrite.

Timestamp formats accepted everywhere (-ss / -to / -t):
  SECONDS         e.g. 90.5
  HH:MM:SS.mmm    e.g. 00:01:30.500
  MM:SS           e.g. 01:30

GLOBAL GOTCHAS (read once, applies throughout)
  * yuv420p: For QuickTime / Safari / iOS / most web players and PowerPoint,
    always add  -pix_fmt yuv420p  when re-encoding. Without it, x264 may emit
    yuv444p/yuv422p which many players show as black/garbage.
  * EVEN DIMENSIONS: H.264/H.265 with yuv420p require width AND height to be
    even. Scaling to an odd size errors out with "width not divisible by 2".
    Use -2 in scale to auto-round, or force_divisible_by=2 / trunc(x/2)*2.
  * -shortest: When you combine streams of different lengths (e.g. video + a
    longer/looping audio track), add -shortest so output ends with the shortest
    input instead of running on.
  * -c copy (stream copy) is instant and lossless but cannot apply filters and
    requires compatible cut points / identical codecs. Filters force re-encode.
  * Filtergraph: use -vf / -af for a single in→single out chain. Use
    -filter_complex when there are multiple inputs/outputs or labels [a][v].
    You cannot use -vf and -filter_complex on the same stream.
  * Map: with -filter_complex, ffmpeg won't auto-pick streams. Use -map "[v]"
    -map "[a]" (or -map 0:a) to choose what goes to the output.


================================================================================
1. TRIM / CUT BY TIMESTAMP
================================================================================

Fast, lossless cut (stream copy). -ss BEFORE -i = fast input seek.
Cuts land on the nearest preceding keyframe, so start may be slightly off.
  ffmpeg -ss 00:00:30 -to 00:01:45 -i in.mp4 -c copy out.mp4

Cut by start + DURATION instead of end time (-t = duration, not end):
  ffmpeg -ss 00:00:30 -t 00:00:75 -i in.mp4 -c copy out.mp4

Frame-accurate cut (re-encode; -ss after -i decodes up to the point):
  ffmpeg -i in.mp4 -ss 00:00:30 -to 00:01:45 -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k -pix_fmt yuv420p out.mp4

Best of both — accurate AND reasonably fast (input seek + output seek):
  ffmpeg -ss 00:00:28 -i in.mp4 -ss 00:00:02 -to 00:01:17 -c:v libx264 -crf 18 -preset medium -c:a aac out.mp4
  (seek to ~2s before target on input, then trim the rest accurately on output)

Cut and KEEP only video (drop audio): add  -an
Cut and KEEP only audio: add  -vn


================================================================================
2. CONCATENATE CLIPS
================================================================================

--- 2a. concat DEMUXER — same codec/params, lossless, no re-encode (fast) ---
Requires identical codec, resolution, pix_fmt, timebase, sample rate, etc.
Make a list file (paths relative to the list file's location):

  list.txt:
    file 'clip1.mp4'
    file 'clip2.mp4'
    file 'clip3.mp4'

  ffmpeg -f concat -safe 0 -i list.txt -c copy out.mp4

  -safe 0 allows absolute/relative paths with special chars. Quote paths with
  apostrophes by doubling: file 'it''s.mp4'. Generate the list quickly:
    for f in *.mp4; do echo "file '$PWD/$f'"; done > list.txt

--- 2b. concat FILTER — different codecs/resolutions, re-encodes (robust) ---
Handles mismatched inputs; normalize first so frames line up.
Two inputs with audio (n=2 segments, v=1 video stream, a=1 audio stream each):

  ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
    "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0]; \
     [1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v1]; \
     [0:a]aresample=48000[a0];[1:a]aresample=48000[a1]; \
     [v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" \
    -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k -pix_fmt yuv420p out.mp4

  Video-only concat (no audio), 3 clips:
  ffmpeg -i a.mp4 -i b.mp4 -i c.mp4 -filter_complex \
    "[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]" -map "[v]" -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

  GOTCHA: concat filter requires ALL segments share the same resolution, SAR,
  pix_fmt and (for audio) sample rate/layout — hence the scale/pad/fps/aresample
  normalization above. Mismatches cause errors or only the first clip playing.

--- 2c. Concatenate when audio is missing on some clips ---
Add silent audio to clips lacking it before concat, e.g. with anullsrc:
  ffmpeg -i silent.mp4 -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 \
    -shortest -c:v copy -c:a aac withaudio.mp4


================================================================================
3. CHANGE SPEED (setpts for video, atempo for audio)
================================================================================

Video speed = multiply by 1/factor in setpts.
  2x faster (half PTS):       setpts=0.5*PTS
  4x faster:                  setpts=0.25*PTS
  0.5x slower (double PTS):   setpts=2.0*PTS

--- 3a. Speed up video only (drops audio) ---
  ffmpeg -i in.mp4 -filter:v "setpts=0.5*PTS" -an out.mp4

--- 3b. Speed up video AND audio together (2x) ---
  atempo accepts 0.5–2.0 per instance; chain for larger factors.
  ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" \
    -map "[v]" -map "[a]" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac out.mp4

--- 3c. Slow down 0.5x (video + audio) ---
  ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]" \
    -map "[v]" -map "[a]" out.mp4

--- 3d. 4x speed (chain atempo, each factor 0.5–2.0; 2.0*2.0=4) ---
  ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=0.25*PTS[v];[0:a]atempo=2.0,atempo=2.0[a]" \
    -map "[v]" -map "[a]" out.mp4
  (e.g. 3x = atempo=1.5,atempo=2.0 → 3.0 ; 8x = atempo=2,atempo=2,atempo=2)

--- 3e. Smooth slow-motion with frame interpolation (optical flow) ---
  Plain setpts just repeats/holds frames. minterpolate synthesizes new frames:
  ffmpeg -i in.mp4 -filter:v "setpts=2.0*PTS,minterpolate=fps=60:mi_mode=mci" -an slowmo.mp4
  (slow; mci = motion-compensated interpolation. Drop audio or speed-match it.)


================================================================================
4. ADD / BURN SUBTITLES
================================================================================

--- 4a. SOFT subtitles (muxed, toggleable, NOT burned in) ---
  ffmpeg -i in.mp4 -i subs.srt -c copy -c:s mov_text -metadata:s:s:0 language=eng out.mp4
    (mov_text = subtitle codec for MP4/MOV. For MKV use -c:s srt or copy.)

--- 4b. BURN IN .srt (hardsub, re-encodes; uses libass) ---
  ffmpeg -i in.mp4 -vf "subtitles=subs.srt" -c:a copy -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

  Style the burned SRT (font, size, colours; BGR hex, &H00BBGGRR, AA=alpha):
  ffmpeg -i in.mp4 -vf "subtitles=subs.srt:force_style='FontName=DejaVu Sans,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,MarginV=40'" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4

  Burn an .ass file (carries its own styling):
  ffmpeg -i in.mp4 -vf "ass=subs.ass" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4

  GOTCHA — paths in filter args: special chars (Windows drives, spaces, colons)
  must be escaped inside the filtergraph. On Windows:
    -vf "subtitles='C\:/path/subs.srt'"
  Safest: cd to the file's directory and reference by bare filename.

--- 4c. Pick a subtitle stream embedded in the source ---
  ffmpeg -i in.mkv -vf "subtitles=in.mkv:si=0" -c:v libx264 -pix_fmt yuv420p out.mp4
    (si = subtitle stream index, 0-based among subtitle streams.)

--- 4d. drawtext — single styled caption / lower-third (no SRT needed) ---
  ffmpeg -i in.mp4 -vf "drawtext=text='Hello World':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=48:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-100" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4

  drawtext only between 5s and 10s (enable expression):
    drawtext=...:enable='between(t,5,10)'

  Read text from a file (good for long/multiline/unicode text):
    drawtext=textfile=caption.txt:reload=1:...
    (reload=1 re-reads the file each frame — useful for live/changing text)

  Common drawtext position presets (x:y):
    top-left:        x=20:y=20
    top-right:       x=w-text_w-20:y=20
    bottom-center:   x=(w-text_w)/2:y=h-text_h-20
    dead center:     x=(w-text_w)/2:y=(h-text_h)/2
  Semi-transparent box behind text: add  box=1:boxcolor=black@0.5:boxborderw=10


================================================================================
5. OVERLAY TEXT / WATERMARK (image logo)
================================================================================

--- 5a. PNG logo, top-right with 20px margin ---
  ffmpeg -i in.mp4 -i logo.png -filter_complex "overlay=W-w-20:20" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4
  overlay position shorthands (W,H=main; w,h=overlay):
    top-left      0:0
    top-right     W-w:0          (use W-w-20:20 for margin)
    bottom-left   0:H-h
    bottom-right  W-w:H-h        (use W-w-20:H-h-20 for margin)
    centered      (W-w)/2:(H-h)/2

--- 5b. Scale the logo first, then overlay ---
  ffmpeg -i in.mp4 -i logo.png -filter_complex \
    "[1:v]scale=160:-1[wm];[0:v][wm]overlay=W-w-20:20" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4

--- 5c. Semi-transparent watermark (lower opacity of the logo) ---
  ffmpeg -i in.mp4 -i logo.png -filter_complex \
    "[1:v]format=rgba,colorchannelmixer=aa=0.4[wm];[0:v][wm]overlay=W-w-20:H-h-20" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4

--- 5d. Watermark only during 0–10s ---
  ...overlay=W-w-20:20:enable='between(t,0,10)'

--- 5e. Animated scrolling text ticker (drawtext with t in x) ---
  ffmpeg -i in.mp4 -vf "drawtext=text='Breaking news ticker':fontcolor=white:fontsize=36:y=h-60:x=w-mod(t*200\,w+text_w)" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4


================================================================================
6. AUDIO: EXTRACT / REPLACE / MIX / BACKGROUND MUSIC + DUCKING
================================================================================

--- 6a. Extract audio (copy original codec, no re-encode) ---
  ffmpeg -i in.mp4 -vn -acodec copy out.m4a       (AAC stays .m4a/.aac)
  ffmpeg -i in.mp4 -vn -acodec copy out.mp3       (only if source is MP3)

--- 6b. Extract & convert audio to MP3 / WAV ---
  ffmpeg -i in.mp4 -vn -c:a libmp3lame -q:a 2 out.mp3      (q 0=best..9)
  ffmpeg -i in.mp4 -vn -c:a pcm_s16le out.wav             (uncompressed WAV)

--- 6c. Strip audio (mute video) ---
  ffmpeg -i in.mp4 -an -c:v copy muted.mp4

--- 6d. REPLACE the audio track entirely with a new file ---
  ffmpeg -i in.mp4 -i newaudio.m4a -map 0:v:0 -map 1:a:0 \
    -c:v copy -c:a aac -b:a 192k -shortest out.mp4
  -map 0:v:0 = video from input0, -map 1:a:0 = audio from input1.
  -shortest stops at whichever is shorter (prevents trailing silence/freeze).

--- 6e. MIX two audio tracks together (e.g. voice + music), equal level ---
  ffmpeg -i voice.wav -i music.mp3 -filter_complex \
    "[0:a][1:a]amix=inputs=2:duration=longest:dropout_transition=2[a]" \
    -map "[a]" out.m4a
  duration=longest|shortest|first ; normalize=0 keeps original loudness
  (amix divides volume by inputs by default; add ,volume=2 or normalize=0).

--- 6f. Add background music UNDER existing video audio, music quieter ---
  ffmpeg -i in.mp4 -i music.mp3 -filter_complex \
    "[1:a]volume=0.25[bg];[0:a][bg]amix=inputs=2:duration=first[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest out.mp4
  duration=first = end with the video's original audio length.

--- 6g. Add background music to a SILENT video, looped to fill ---
  ffmpeg -i silent.mp4 -stream_loop -1 -i music.mp3 \
    -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out.mp4
  -stream_loop -1 before that -i loops the music; -shortest ends at video end.

--- 6h. SIDECHAIN DUCKING — auto-lower music when voice is present ---
  Music volume dips whenever the voice (sidechain key) is loud. Pro result.
  ffmpeg -i voice.wav -i music.mp3 -filter_complex \
    "[1:a]volume=0.8[music]; \
     [music][0:a]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300:makeup=1[ducked]; \
     [0:a][ducked]amix=inputs=2:duration=longest:normalize=0[a]" \
    -map "[a]" out.m4a
  Tuning: lower threshold = ducks more easily; higher ratio = deeper dip;
  attack(ms)=how fast it ducks; release(ms)=how fast music returns.
  To duck music under a VIDEO's own audio, replace [0:a]/voice.wav with the
  video's audio stream and -map 0:v for the picture.

--- 6i. Normalize loudness to broadcast/streaming standard (EBU R128) ---
  ffmpeg -i in.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v copy out.mp4
  (I=-16 LUFS suits web/podcast; -14 for many streaming platforms.)


================================================================================
7. RESIZE / SCALE / CROP / PAD TO TARGET ASPECT
================================================================================

--- 7a. Scale to exact size (may distort if AR differs) ---
  ffmpeg -i in.mp4 -vf "scale=1920:1080" -c:a copy -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

--- 7b. Scale keeping aspect, set ONE dimension, auto the other (even) ---
  ffmpeg -i in.mp4 -vf "scale=1280:-2" -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4
    -2 = compute to preserve AR and round to a multiple of 2 (avoids odd-size
    error). Use -1 to not round, but that can yield odd height → error.

--- 7c. FIT inside 16:9 1920x1080 with LETTERBOX/PILLARBOX (no crop, pad bars) ---
  ffmpeg -i in.mp4 -vf \
    "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4

--- 7d. FILL 16:9 1920x1080 by CROPPING overflow (no bars, edges cut) ---
  ffmpeg -i in.mp4 -vf \
    "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4

--- 7e. Vertical 9:16 1080x1920 (e.g. landscape → Reels/Shorts/TikTok) ---
  Letterboxed (whole frame visible, black bars top/bottom):
  ffmpeg -i in.mp4 -vf \
    "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4

  Center-cropped fill (fills 9:16, sides of a landscape video are cut):
  ffmpeg -i in.mp4 -vf \
    "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4

  Blurred-background fill (landscape centered over a blurred zoomed copy):
  ffmpeg -i in.mp4 -filter_complex \
    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40[bg]; \
     [0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4

--- 7f. Plain crop a region (w:h:x:y; x,y = top-left of crop) ---
  ffmpeg -i in.mp4 -vf "crop=1280:720:100:50" -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4
  Center crop to a size (omit x,y → centered automatically):
  ffmpeg -i in.mp4 -vf "crop=1280:720" -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

  Detect content crop (find black borders to remove), then apply:
  ffmpeg -i in.mp4 -vf cropdetect -f null - 2>&1 | grep -o "crop=[0-9:]*" | tail -1
  ffmpeg -i in.mp4 -vf "crop=1920:800:0:140" ... out.mp4   (use detected values)

  GOTCHA: setsar=1 forces square pixels — without it some scaled/padded outputs
  display stretched because the source had a non-1 sample aspect ratio.


================================================================================
8. FPS CONVERSION
================================================================================

--- 8a. Simple constant fps (duplicate/drop frames) ---
  ffmpeg -i in.mp4 -vf "fps=30" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy out.mp4
  (Alternatively  -r 30  as an output option does similar but fps filter is
  more predictable inside a filtergraph.)

--- 8b. To 24 fps (cinematic): ---
  ffmpeg -i in.mp4 -vf "fps=24" -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

--- 8c. Smooth fps change with motion interpolation (no judder, slow) ---
  ffmpeg -i in.mp4 -vf "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsr_mode=obmc" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

--- 8d. Force constant frame rate (CFR) from variable (VFR) source ---
  Fixes A/V sync issues from phone/screen recordings:
  ffmpeg -i in.mp4 -vsync cfr -r 30 -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac out.mp4

  NOTE: generated clips have fixed family fps — Wan exports at 16fps, LTX/LTX-2
  at ~24–25fps. Convert to a common fps BEFORE concat/xfade so timelines align.


================================================================================
9. IMAGE SEQUENCE <-> VIDEO ; VIDEO -> FRAMES
================================================================================

--- 9a. Image sequence -> video (numbered frame_0001.png ...) ---
  ffmpeg -framerate 30 -i frame_%04d.png \
    -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p out.mp4
  %04d = 4-digit zero-padded index. -framerate BEFORE -i sets input fps.
  Start at a given number: add  -start_number 100  before -i.

  From arbitrary filenames via glob (Linux/Mac):
  ffmpeg -framerate 30 -pattern_type glob -i 'shots/*.png' \
    -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

  Odd-sized PNGs → force even dimensions to avoid yuv420p error:
  ... -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -pix_fmt yuv420p out.mp4

  Single still image -> N-second video (e.g. 5s) with silent/looping use later:
  ffmpeg -loop 1 -i photo.jpg -t 5 -vf "scale=1920:1080,fps=30" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

--- 9b. Video -> frames (every frame as PNG) ---
  ffmpeg -i in.mp4 frames/frame_%04d.png

  Extract 1 frame per second:
  ffmpeg -i in.mp4 -vf "fps=1" frames/frame_%04d.png

  Extract at original quality JPEGs:
  ffmpeg -i in.mp4 -qscale:v 2 frames/frame_%04d.jpg   (2=best..31)

  Extract N evenly-spaced thumbnails (scene-agnostic, e.g. 1 every 10s):
  ffmpeg -i in.mp4 -vf "fps=1/10,scale=320:-1" thumbs/thumb_%03d.png

  Extract only scene-change keyframes:
  ffmpeg -i in.mp4 -vf "select='gt(scene,0.4)',showinfo" -vsync vfr scene_%03d.png

  Extract the LAST frame (i2v chaining — feed as next clip's seed image):
  ffmpeg -sseof -0.1 -i in.mp4 -frames:v 1 -y last.png
  (-sseof -0.1 seeks to 0.1s before EOF; this is the chain_video.py primitive.)


================================================================================
10. CROSSFADE / XFADE TRANSITIONS BETWEEN CLIPS
================================================================================

xfade needs BOTH inputs same resolution, pix_fmt, fps, SAR. offset = time in
the FIRST clip where the transition starts (= clip1_duration - transition_dur).

--- 10a. Video crossfade, 1s dissolve. clip1 is 10s long → offset=9 ---
  ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
    "[0:v][1:v]xfade=transition=fade:duration=1:offset=9[v]" \
    -map "[v]" -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

--- 10b. Crossfade BOTH video and audio together ---
  ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
    "[0:v][1:v]xfade=transition=fade:duration=1:offset=9[v]; \
     [0:a][1:a]acrossfade=d=1[a]" \
    -map "[v]" -map "[a]" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac out.mp4

--- 10c. Normalize first if clips differ (recommended before xfade) ---
  ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex \
    "[0:v]scale=1920:1080,setsar=1,fps=30,format=yuv420p[v0]; \
     [1:v]scale=1920:1080,setsar=1,fps=30,format=yuv420p[v1]; \
     [v0][v1]xfade=transition=wipeleft:duration=1:offset=9[v]" \
    -map "[v]" -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

  Useful transition names: fade, fadeblack, fadewhite, wipeleft/right/up/down,
  slideleft/right/up/down, circleopen, circleclose, dissolve, pixelize,
  smoothleft, radial, distance. (ffmpeg -h filter=xfade lists all.)

--- 10d. Chain 3 clips (each 10s, 1s transitions) ---
  Offsets are CUMULATIVE on the running output timeline:
    1st xfade offset = 10-1 = 9
    after it, combined length = 10+10-1 = 19; 2nd offset = 19-1 = 18
  ffmpeg -i a.mp4 -i b.mp4 -i c.mp4 -filter_complex \
    "[0:v][1:v]xfade=transition=fade:duration=1:offset=9[v01]; \
     [v01][2:v]xfade=transition=fade:duration=1:offset=18[v]" \
    -map "[v]" -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

--- 10e. Simple fade-IN / fade-OUT on a single clip (not between clips) ---
  Fade in over first 2s, fade out over last 2s (clip = 30s → st=28):
  ffmpeg -i in.mp4 -vf "fade=t=in:st=0:d=2,fade=t=out:st=28:d=2" \
    -af "afade=t=in:st=0:d=2,afade=t=out:st=28:d=2" \
    -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4


================================================================================
11. LOOP A CLIP
================================================================================

--- 11a. Loop whole input file N extra times via stream copy (fast) ---
  ffmpeg -stream_loop 3 -i in.mp4 -c copy out.mp4   (plays 4x total: 1+3)
  -stream_loop -1 = infinite (combine with -t to cap length):
  ffmpeg -stream_loop -1 -i in.mp4 -t 60 -c copy out.mp4

--- 11b. Loop to reach an exact duration with re-encode ---
  ffmpeg -stream_loop -1 -i loop.mp4 -t 30 \
    -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

--- 11c. Loop a short video as background for a longer audio track ---
  ffmpeg -stream_loop -1 -i bg.mp4 -i song.mp3 \
    -map 0:v -map 1:a -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -shortest out.mp4

--- 11d. Boomerang (forward then reversed) loop ---
  ffmpeg -i in.mp4 -filter_complex \
    "[0:v]split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[v]" \
    -map "[v]" -an -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4

  (Handy for seamless looping b-roll generated by Wan/LTX — a 5s clip becomes a
  10s ping-pong that returns to its start frame.)


================================================================================
12. GIF / ANIMATED WEBP EXPORT
================================================================================

--- 12a. High-quality GIF (two-pass palette = far better colors/size) ---
  Pass 1 — generate optimal palette:
  ffmpeg -i in.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,palettegen" -y palette.png
  Pass 2 — apply palette:
  ffmpeg -i in.mp4 -i palette.png -lavfi "fps=15,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse" -y out.gif

--- 12b. One-liner GIF (single chain, decent quality) ---
  ffmpeg -i in.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" out.gif

--- 12c. GIF from a sub-section (5s clip starting at 0:30) ---
  ffmpeg -ss 30 -t 5 -i in.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" out.gif

--- 12d. Animated WebP (smaller + more colors than GIF) ---
  ffmpeg -i in.mp4 -vf "fps=15,scale=480:-1:flags=lanczos" \
    -c:v libwebp -loop 0 -q:v 70 -preset default out.webp
  -loop 0 = loop forever ; -q:v 0..100 quality.

  GOTCHA: GIFs are capped at 256 colors — always go through palettegen/paletteuse
  for acceptable quality. Keep fps low (10–15) and width small to limit size.


================================================================================
13. THUMBNAIL / POSTER FRAME
================================================================================

--- 13a. Single frame at a timestamp ---
  ffmpeg -ss 00:00:05 -i in.mp4 -frames:v 1 -q:v 2 thumb.jpg
  (-ss before -i = fast seek; -frames:v 1 grabs one frame.)

--- 13b. PNG poster frame at exact time (lossless) ---
  ffmpeg -ss 00:01:00 -i in.mp4 -frames:v 1 poster.png

--- 13c. "Best" representative frame (thumbnail filter scans a window) ---
  ffmpeg -i in.mp4 -vf "thumbnail=300" -frames:v 1 thumb.jpg
  (picks the most representative frame out of every 300; ignores -ss timing.)

--- 13d. Scaled thumbnail at a time ---
  ffmpeg -ss 00:00:10 -i in.mp4 -frames:v 1 -vf "scale=640:-1" thumb.jpg

--- 13e. Contact sheet / storyboard (4x3 grid of stills) ---
  ffmpeg -i in.mp4 -vf "fps=1/10,scale=320:-1,tile=4x3" -frames:v 1 contact.png

--- 13f. Embed a poster/cover into an MP4 (shows as file thumbnail) ---
  ffmpeg -i in.mp4 -i poster.png -map 0 -map 1 -c copy -c:v:1 png \
    -disposition:v:1 attached_pic out.mp4


================================================================================
14. RE-ENCODE WITH SANE H.264 / H.265 SETTINGS
================================================================================

Key knobs:
  -crf      Quality. LOWER = better/larger. H.264 sane range 18–28 (23 default,
            18 ~ visually lossless). H.265 sane range 24–30 (28 default); H.265
            CRF values are NOT comparable to H.264 — ~+6 for similar quality.
  -preset   Speed/compression tradeoff: ultrafast, superfast, veryfast, faster,
            fast, medium(default), slow, slower, veryslow. Slower = smaller file
            at same CRF, more CPU time. "slow" is a good quality default.
  -pix_fmt yuv420p   Compatibility (see global gotchas). Almost always include.
  -movflags +faststart   Moves the moov atom to the front so web playback can
            start before the whole file downloads. Always add for web MP4s.

--- 14a. H.264 — solid general-purpose web/share default ---
  ffmpeg -i in.mp4 -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p \
    -c:a aac -b:a 192k -movflags +faststart out.mp4

--- 14b. H.264 — visually lossless archival ---
  ffmpeg -i in.mp4 -c:v libx264 -crf 18 -preset veryslow -pix_fmt yuv420p \
    -c:a aac -b:a 256k -movflags +faststart out.mp4

--- 14c. H.265 / HEVC — ~half the size at similar quality ---
  ffmpeg -i in.mp4 -c:v libx265 -crf 26 -preset medium -pix_fmt yuv420p \
    -tag:v hvc1 -c:a aac -b:a 192k -movflags +faststart out.mp4
  -tag:v hvc1 is REQUIRED for Apple/QuickTime/Safari to play HEVC in MP4.
  (10-bit HEVC: -pix_fmt yuv420p10le — better gradients, less compatible.)

--- 14d. Target a specific FILE SIZE (two-pass, bitrate-controlled) ---
  Compute video bitrate ≈ (target_MB*8192)/duration_s - audio_kbps.
  ffmpeg -y -i in.mp4 -c:v libx264 -b:v 2500k -preset slow -pass 1 -an -f mp4 /dev/null
  ffmpeg -i in.mp4 -c:v libx264 -b:v 2500k -preset slow -pass 2 \
    -c:a aac -b:a 128k -pix_fmt yuv420p -movflags +faststart out.mp4
  (On Windows use NUL instead of /dev/null. Two-pass = accurate size target.)

--- 14e. Fast, compatible "fix-it" re-encode (force even, yuv420p) ---
  ffmpeg -i weird.mov -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" \
    -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 160k -movflags +faststart out.mp4

--- 14f. Web-optimized 1080p H.264 social upload preset ---
  ffmpeg -i in.mp4 -vf "scale=-2:1080,fps=30,format=yuv420p" \
    -c:v libx264 -crf 21 -preset slow -profile:v high -level 4.0 \
    -c:a aac -b:a 192k -ar 48000 -movflags +faststart out.mp4

--- 14g. Hardware-accelerated encode (NVIDIA NVENC — much faster, lower quality/bit) ---
  ffmpeg -i in.mp4 -c:v h264_nvenc -preset p5 -cq 23 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -movflags +faststart out.mp4
  (This rig has 2x RTX A6000 → h264_nvenc / hevc_nvenc available for fast batch
  transcodes. Apple: -c:v h264_videotoolbox ; Intel: -c:v h264_qsv ; quality
  per-bit is below x264 at the same size, so prefer libx264 for final masters.)


================================================================================
QUICK-REFERENCE GOTCHA CHECKLIST
================================================================================
  [ ] Re-encoding for web/QuickTime/PPT?      → add  -pix_fmt yuv420p
  [ ] Web MP4 that should stream immediately?  → add  -movflags +faststart
  [ ] H.265 in MP4 for Apple?                  → add  -tag:v hvc1
  [ ] Odd width/height error?                  → scale -2 or trunc(iw/2)*2
  [ ] Combining streams of different lengths?  → add  -shortest
  [ ] concat filter / xfade misbehaving?       → normalize scale+fps+sar+pix_fmt
  [ ] Just trimming, no edits?                 → -c copy (instant, lossless)
  [ ] atempo factor > 2 or < 0.5?              → chain multiple atempo filters
  [ ] Subtitle path has spaces/colons?         → cd to dir, use bare filename
  [ ] GIF looks dithered/huge?                 → palettegen + paletteuse, low fps
  [ ] Stretched output after scale/pad?        → append  setsar=1
  [ ] Mixing Wan(16fps)+LTX(24fps) clips?      → fps-normalize before concat/xfade
  [ ] ffmpeg libs broken by conda?             → source scripts/env.sh first
================================================================================
