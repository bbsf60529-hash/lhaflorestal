#!/usr/bin/env python3
"""Vídeo de propaganda Forest Truck (Tigercat) no mesmo layout 1080x1080.
Uso: montar_video_tigercat.py VIDEO.mov FOTO.jpg [saida.mp4]"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

SRC, PHOTO = sys.argv[1], sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else "forest_truck_propaganda_tigercat.mp4"
TMP = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_tmp")
os.makedirs(TMP, exist_ok=True)
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, VID_TOP, VID_BOT = 1080, 140, 880
H = VID_BOT - VID_TOP
GREEN, DARK, YEL, LIGHT = (27, 94, 26), (13, 50, 15), (255, 215, 0), (200, 255, 200)

def font(s): return ImageFont.truetype(B, s)
def center(d, y, text, size, fill): d.text((W // 2, y), text, font=font(size), fill=fill, anchor="mm")

def overlay(name, footer):
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, VID_TOP], fill=GREEN + (255,))
    center(d, 35, "FOREST TRUCK - LAVA JATO PESADO", 44, "white")
    center(d, 90, "LAVAGEM DE MÁQUINAS FLORESTAIS - TIGERCAT", 23, YEL)
    d.rectangle([0, VID_BOT, W, W], fill=DARK + (255,))
    d.rectangle([5, VID_BOT + 5, W - 6, W - 6], outline=YEL, width=4)
    for i, (txt, size, col) in enumerate(footer):
        center(d, VID_BOT + 45 + i * 55 if len(footer) > 1 else VID_BOT + 100, txt, size, col)
    p = f"{TMP}/{name}.png"; im.save(p); return p

PHONE = ("PLANTÃO: (42) 99846-9325", 34, "white")
ADDR = ("Rua José Zampier Filho, 86 - Industrial", 24, "white")
DUR = 5
# tipo, início no vídeo, rodapé
scenes = [
    ("photo", 0, [("MÁQUINA FLORESTAL TAMBÉM SE LAVA!", 31, YEL), ("Jato pesado tirando barro e resíduo", 26, "white"), ADDR]),
    ("video", 1, [("CHEGOU PARA O SERVIÇO PESADO", 31, YEL), ("Cavalo e carreta prontos para a lavagem", 25, "white")]),
    ("video", 12, [("TIGERCAT • ESTEIRAS • CHASSI", 30, LIGHT), ("Limpeza completa de ponta a ponta", 26, "white")]),
    ("video", 19, [("BRAÇO, CABINE E CABEÇOTE", 31, YEL), ("Sem deixar barro escondido", 26, "white")]),
    ("video", 23.5, [("ESTRUTURA PARA ATENDER SUA FROTA", 29, LIGHT), ("Forest Truck cuida do seu equipamento", 25, "white")]),
    ("photo", 0, [("CHAME NO PLANTÃO!", 40, YEL), PHONE, ADDR]),
]
args = ["ffmpeg", "-v", "error", "-y"]
filters, labels = [], []
for i, (kind, ss, foot) in enumerate(scenes):
    ov = overlay(f"o{i}", foot)
    fade = f"fade=t=in:st=0:d=0.4,fade=t=out:st={DUR-0.4}:d=0.4"
    if kind == "video":
        args += ["-ss", str(ss), "-t", str(DUR), "-i", SRC, "-i", ov]
        v, o = 2 * i, 2 * i + 1  # índices só funcionam se todas as cenas tiverem 2 entradas
        base = f"[{v}:v]fps=30,scale={W}:-2,crop={W}:{H}:0:330,pad={W}:{W}:0:{VID_TOP}:black,setsar=1"
        aud = f"[{v}:a]volume=0.5,afade=t=in:d=0.3,afade=t=out:st={DUR-0.4}:d=0.4[a{i}]"
    else:
        args += ["-loop", "1", "-framerate", "30", "-t", str(DUR), "-i", PHOTO, "-i", ov]
        v, o = 2 * i, 2 * i + 1
        pan = 430 + (60 if i == 0 else 0)  # leve movimento vertical sobre a máquina
        y = f"{pan}+t*12" if i == 0 else f"{pan+60}-t*12"
        base = (f"[{v}:v]scale={W}:-2,crop={W}:{H}:0:'{y}',"
                f"pad={W}:{W}:0:{VID_TOP}:black,setsar=1,format=yuv420p")
        aud = f"anullsrc=r=48000:cl=stereo,atrim=0:{DUR}[a{i}]"
    filters.append(f"{base}[b{i}];[b{i}][{o}:v]overlay=0:0,{fade}[s{i}]")
    filters.append(aud)
    labels.append(f"[s{i}][a{i}]")
filters.append("".join(labels) + f"concat=n={len(scenes)}:v=1:a=1[v][a]")
args += ["-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", OUT]
subprocess.run(args, check=True)
print("OK", OUT)
