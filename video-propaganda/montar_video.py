#!/usr/bin/env python3
"""Monta o vídeo de propaganda Forest Truck (1080x1080) no layout da arte original."""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "forest_truck_propaganda.mp4"
TMP = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_tmp")
os.makedirs(TMP, exist_ok=True)
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W = 1080
VID_TOP, VID_BOT = 140, 880
GREEN, DARK, YEL, LIGHT = (27, 94, 26), (13, 50, 15), (255, 215, 0), (200, 255, 200)

def font(s): return ImageFont.truetype(B, s)
def center(d, y, text, size, fill):
    d.text((W // 2, y), text, font=font(size), fill=fill, anchor="mm")

def overlay(name, footer):
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, VID_TOP], fill=GREEN + (255,))
    center(d, 35, "FOREST TRUCK - LAVA JATO PESADO", 44, "white")
    center(d, 90, "LABORO TRANSPORTES - MERCEDES ACTROS", 23, YEL)
    d.rectangle([0, VID_BOT, W, W], fill=DARK + (255,))
    d.rectangle([5, VID_BOT + 5, W - 6, W - 6], outline=YEL, width=4)
    for i, (txt, size, col) in enumerate(footer):
        center(d, VID_BOT + 45 + i * 55 if len(footer) > 1 else VID_BOT + 100, txt, size, col)
    p = f"{TMP}/{name}.png"; im.save(p); return p

PHONE = ("PLANTÃO: (42) 99846-9325", 34, "white")
ADDR = ("Rua José Zampier Filho, 86 - Industrial", 24, "white")
scenes = [  # (início no vídeo origem, rodapé)
    (0,   [("BRILHANDO NA CHUVA!", 38, YEL), ("LAVAGEM COMPLETA", 32, YEL), ADDR]),
    (24,  [("CABINE • CHASSI • CARRETA FLORESTAL", 29, LIGHT), ("Seu caminhão limpo de ponta a ponta", 26, "white")]),
    (40,  [("JATO PESADO PARA SERVIÇO PESADO", 30, YEL), ("Chuva não é desculpa para caminhão sujo", 25, "white")]),
    (100, [("PARA O PESO DA FLORESTA", 32, YEL), ("Pronto para a próxima carga", 26, "white")]),
    (122, [("CAMINHÃO LIMPO TRABALHA MELHOR", 30, LIGHT), ("Forest Truck cuida da sua frota", 25, "white")]),
    (142, [("CHAME NO PLANTÃO!", 40, YEL), PHONE, ADDR]),
]
DUR = 5
args = ["ffmpeg", "-v", "error", "-y"]
filters, labels = [], []
for i, (ss, foot) in enumerate(scenes):
    args += ["-ss", str(ss), "-t", str(DUR), "-i", SRC, "-i", overlay(f"o{i}", foot)]
    v, o = 2 * i, 2 * i + 1
    filters.append(
        f"[{v}:v]fps=30,scale=-2:{VID_BOT-VID_TOP},crop={W}:{VID_BOT-VID_TOP}:(iw-{W})/2-60:0,"
        f"pad={W}:{W}:0:{VID_TOP}:black,setsar=1[b{i}];"
        f"[b{i}][{o}:v]overlay=0:0,fade=t=in:st=0:d=0.4,fade=t=out:st={DUR-0.4}:d=0.4[s{i}]")
    filters.append(f"[{v}:a]volume=0.5,afade=t=in:d=0.3,afade=t=out:st={DUR-0.4}:d=0.4[a{i}]")
    labels.append(f"[s{i}][a{i}]")
filters.append("".join(labels) + f"concat=n={len(scenes)}:v=1:a=1[v][a]")
args += ["-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", OUT]
subprocess.run(args, check=True)
print("OK", OUT)
