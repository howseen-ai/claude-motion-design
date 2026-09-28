"""sync.py — build the deliverables from full-render frames in out/full/o_fNNNN.png.
  sync.py encode   -> out/remake_silent.mp4 (24 fps, h264 BT.709) and out/remake.mp4 (muxed with out/mix.wav if present)
  sync.py split    -> out/split_screen.mp4 : REF left | OURS right, labelled "original" / "opus 5.5 copy", white bg (the X post format)
  sync.py stacked  -> out/sync_check.mp4 : REF top / OURS bottom, frame-locked, for QA
"""
import subprocess, sys
from pathlib import Path
import imageio_ffmpeg
H = Path(__file__).parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
OUT = H / "out"; FULL = OUT / "full"; REF = H / "ref/reference.mp4"
ENC = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "slow", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart"]
mode = sys.argv[1]
if mode == "encode":
    subprocess.run([FF, "-v", "error", "-y", "-framerate", "24", "-i", str(FULL / "o_f%04d.png"), *ENC, str(OUT / "remake_silent.mp4")], check=True)
    mix = OUT / "mix.wav"
    if mix.exists():
        subprocess.run([FF, "-v", "error", "-y", "-i", str(OUT / "remake_silent.mp4"), "-i", str(mix), "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(OUT / "remake.mp4")], check=True)
    print("encoded")
elif mode == "split":
    font = "/System/Library/Fonts/Helvetica.ttc"
    lab = lambda txt, x: f"drawbox=x={x}:y=246:w={len(txt) * 13 + 24}:h=34:color=black@1:t=fill,drawtext=fontfile={font}:text='{txt}':x={x + 12}:y=253:fontsize=22:fontcolor=white"
    vf = ("[0:v]scale=880:-2,pad=920:496:0:0:0xF3F4F6[a];[1:v]scale=880:-2,pad=880:496:0:0:white[b];"
          "[a][b]hstack=inputs=2:shortest=1,pad=1920:1080:60:292:0xF3F4F6[s];"
          f"[s]{lab('original', 60)},{lab('opus 5.5 copy', 980)},setsar=1[v]")
    src = OUT / ("remake.mp4" if (OUT / "remake.mp4").exists() else "remake_silent.mp4")
    audio = ["-map", "1:a?"] if (OUT / "remake.mp4").exists() else []
    subprocess.run([FF, "-v", "error", "-y", "-i", str(REF), "-i", str(src), "-filter_complex", vf, "-map", "[v]", *audio, *ENC, "-c:a", "aac", "-b:a", "256k", str(OUT / "split_screen.mp4")], check=True)
    print("split ->", OUT / "split_screen.mp4")
elif mode == "stacked":
    src = OUT / "remake_silent.mp4"
    subprocess.run([FF, "-v", "error", "-y", "-i", str(REF), "-i", str(src), "-filter_complex", "[0:v]scale=960:540[a];[1:v]scale=960:540[b];[a][b]vstack=inputs=2:shortest=1[v]", "-map", "[v]", *ENC, str(OUT / "sync_check.mp4")], check=True)
    print("stacked ->", OUT / "sync_check.mp4")
