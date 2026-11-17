#!/usr/bin/env python3
"""Vídeo de agradecimento à Laboro Transportes, mesmo layout 1080x1080.
Uso: montar_video_agradecimento.py VIDEO_A.mov VIDEO_B.mov [saida.mp4]
Os trechos foram escolhidos para não mostrar a placa do caminhão.
Os vídeos são verticais e de baixa resolução: o vídeo fica nítido no centro da janela
sobre uma cópia desfocada dele mesmo."""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

A, Bv = sys.argv[1], sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else "forest_truck_agradecimento_laboro.mp4"
TMP = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_tmp")
os.makedirs(TMP, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, VID_TOP, VID_BOT = 1080, 140, 880
H = VID_BOT - VID_TOP
GREEN, DARK, YEL, LIGHT = (27, 94, 26), (13, 50, 15), (255, 215, 0), (200, 255, 200)

def font(s): return ImageFont.truetype(FONT, s)
def center(d, y, text, size, fill): d.text((W // 2, y), text, font=font(size), fill=fill, anchor="mm")

def overlay(name, footer):
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, VID_TOP], fill=GREEN + (255,))
    center(d, 35, "FOREST TRUCK - LAVA JATO PESADO", 44, "white")
    center(d, 90, "AGRADECIMENTO - LABORO TRANSPORTES", 23, YEL)
    d.rectangle([0, VID_BOT, W, W], fill=DARK + (255,))
    d.rectangle([5, VID_BOT + 5, W - 6, W - 6], outline=YEL, width=4)
    for i, (txt, size, col) in enumerate(footer):
        center(d, VID_BOT + 45 + i * 55 if len(footer) > 1 else VID_BOT + 100, txt, size, col)
    p = f"{TMP}/{name}.png"; im.save(p); return p

PHONE = ("PLANTÃO: (42) 99846-9325", 34, "white")
ADDR = ("Rua José Zampier Filho, 86 - Industrial", 24, "white")
# arquivo, início, duração, rodapé
scenes = [
    (A,  0,    3.5, [("OBRIGADO, LABORO TRANSPORTES!", 33, YEL), ("Pela parceria e pela preferência", 27, "white")]),
    (A,  3.5,  3.5, [("SEUS CAMINHÕES, NOSSO CUIDADO", 31, LIGHT), ("Cabine, chassi e carreta bem lavados", 26, "white")]),
    (A,  7,    3,   [("ORGULHO DE ATENDER A LABORO", 32, YEL), ("Confiança que nos move", 26, "white")]),
    (Bv, 6.5,  4,   [("PARCERIA QUE MOVE A FLORESTA", 32, LIGHT), ("Seu caminhão pronto para a estrada", 26, "white")]),
    (Bv, 10.5, 3.5, [("CONTE SEMPRE COM A FOREST TRUCK", 30, YEL), ("Lavagem completa com jato pesado", 26, "white")]),
    (Bv, 13.8, 3.5, [("MUITO OBRIGADO, LABORO!", 36, YEL), PHONE, ADDR]),
]
args = ["ffmpeg", "-v", "error", "-y"]
filters, labels = [], []
for i, (src, ss, dur, foot) in enumerate(scenes):
    args += ["-ss", str(ss), "-t", str(dur), "-i", src, "-i", overlay(f"o{i}", foot)]
    v, o = 2 * i, 2 * i + 1
    filters.append(
        f"[{v}:v]fps=30,split[x][y];"
        f"[x]scale={W}:-2,crop={W}:{H}:0:(ih-{H})/2,boxblur=30:5,eq=brightness=-0.12[bg];"
        f"[y]scale=-2:{H}[fg];[bg][fg]overlay=(W-w)/2:0,pad={W}:{W}:0:{VID_TOP}:black,setsar=1[b{i}];"
        f"[b{i}][{o}:v]overlay=0:0,fade=t=in:st=0:d=0.4,fade=t=out:st={dur-0.4}:d=0.4[s{i}]")
    filters.append(f"[{v}:a]volume=0.5,afade=t=in:d=0.3,afade=t=out:st={dur-0.4}:d=0.4[a{i}]")
    labels.append(f"[s{i}][a{i}]")
filters.append("".join(labels) + f"concat=n={len(scenes)}:v=1:a=1[v][a]")
args += ["-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", OUT]
subprocess.run(args, check=True)
print("OK", OUT)
