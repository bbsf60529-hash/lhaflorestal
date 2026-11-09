#!/usr/bin/env python3
"""Vídeo de propaganda Forest Truck (caminhonete) no mesmo layout 1080x1080.
Uso: montar_video_caminhonete.py VIDEO.mov [saida.mp4]
Os trechos foram escolhidos para não mostrar a placa do veículo."""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "forest_truck_propaganda_caminhonete.mp4"
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
    center(d, 90, "LAVAGEM DE CAMINHONETES E VEÍCULOS LEVES", 23, YEL)
    d.rectangle([0, VID_BOT, W, W], fill=DARK + (255,))
    d.rectangle([5, VID_BOT + 5, W - 6, W - 6], outline=YEL, width=4)
    for i, (txt, size, col) in enumerate(footer):
        center(d, VID_BOT + 45 + i * 55 if len(footer) > 1 else VID_BOT + 100, txt, size, col)
    p = f"{TMP}/{name}.png"; im.save(p); return p

PHONE = ("PLANTÃO: (42) 99846-9325", 34, "white")
ADDR = ("Rua José Zampier Filho, 86 - Industrial", 24, "white")
# início, duração, rodapé
scenes = [
    (0,    3.5, [("LAVAGEM COMPLETA", 38, YEL), ("Sua caminhonete limpa e brilhando", 26, "white"), ADDR]),
    (9,    6,   [("DO BARRO AO BRILHO", 34, YEL), ("Carroceria, rodas e acabamento", 26, "white")]),
    (18,   3.5, [("CUIDADO EM CADA DETALHE", 31, LIGHT), ("Lavagem feita com capricho", 26, "white")]),
    (21.4, 3.5, [("CHAME NO PLANTÃO!", 40, YEL), PHONE, ADDR]),
]
args = ["ffmpeg", "-v", "error", "-y"]
filters, labels = [], []
for i, (ss, dur, foot) in enumerate(scenes):
    args += ["-ss", str(ss), "-t", str(dur), "-i", SRC, "-i", overlay(f"o{i}", foot)]
    v, o = 2 * i, 2 * i + 1
    filters.append(
        f"[{v}:v]fps=30,scale={W}:-2,crop={W}:{H}:0:250,pad={W}:{W}:0:{VID_TOP}:black,setsar=1[b{i}];"
        f"[b{i}][{o}:v]overlay=0:0,fade=t=in:st=0:d=0.4,fade=t=out:st={dur-0.4}:d=0.4[s{i}]")
    filters.append(f"[{v}:a]volume=0.5,afade=t=in:d=0.3,afade=t=out:st={dur-0.4}:d=0.4[a{i}]")
    labels.append(f"[s{i}][a{i}]")
filters.append("".join(labels) + f"concat=n={len(scenes)}:v=1:a=1[v][a]")
args += ["-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", OUT]
subprocess.run(args, check=True)
print("OK", OUT)
