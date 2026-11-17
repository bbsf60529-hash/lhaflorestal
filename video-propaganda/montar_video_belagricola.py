#!/usr/bin/env python3
"""Vídeo de agradecimento à Belagrícola (antes e depois), mesmo layout 1080x1080.
Uso: montar_video_belagricola.py FOTO_ANTES.jpg FOTO_DEPOIS.jpg [saida.mp4]
A placa do veículo é borrada nas duas fotos antes da montagem."""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ANTES, DEPOIS = sys.argv[1], sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else "forest_truck_agradecimento_belagricola.mp4"
TMP = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_tmp")
os.makedirs(TMP, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, VID_TOP, VID_BOT = 1080, 140, 880
H = VID_BOT - VID_TOP
GREEN, DARK, YEL, LIGHT, RED = (27, 94, 26), (13, 50, 15), (255, 215, 0), (200, 255, 200), (200, 30, 30)

def font(s): return ImageFont.truetype(FONT, s)
def center(d, y, text, size, fill): d.text((W // 2, y), text, font=font(size), fill=fill, anchor="mm")

def blur_plate(src, box, name):
    im = Image.open(src).convert("RGB")
    x0, y0, x1, y1 = box
    x1, y1 = min(x1, im.width), min(y1, im.height)
    im.paste(im.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(14)), (x0, y0))
    p = f"{TMP}/{name}.jpg"; im.save(p, quality=95); return p

def overlay(name, footer, badge=None):
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, VID_TOP], fill=GREEN + (255,))
    center(d, 35, "FOREST TRUCK - LAVA JATO PESADO", 44, "white")
    center(d, 90, "AGRADECIMENTO - BELAGRÍCOLA", 23, YEL)
    d.rectangle([0, VID_BOT, W, W], fill=DARK + (255,))
    d.rectangle([5, VID_BOT + 5, W - 6, W - 6], outline=YEL, width=4)
    for i, (txt, size, col) in enumerate(footer):
        center(d, VID_BOT + 45 + i * 55 if len(footer) > 1 else VID_BOT + 100, txt, size, col)
    if badge:
        text, color = badge
        f = font(46); l, t, r, b = d.textbbox((160, VID_TOP + 55), text, font=f, anchor="mm")
        d.rounded_rectangle([l - 24, t - 12, r + 24, b + 12], radius=14, fill=color + (235,))
        d.text((160, VID_TOP + 55), text, font=f, fill="white", anchor="mm")
    p = f"{TMP}/{name}.png"; im.save(p); return p

# placas (coordenadas nas fotos 1280x960)
IMG_A = blur_plate(ANTES, (1225, 595, 1290, 690), "antes")
IMG_D = blur_plate(DEPOIS, (1150, 350, 1230, 430), "depois")

PHONE = ("PLANTÃO: (42) 99846-9325", 34, "white")
ADDR = ("Rua José Zampier Filho, 86 - Industrial", 24, "white")

def pan(i, dur, left_to_right):
    """foto -> janela 1080x740, com leve movimento horizontal (zoom de 12%)"""
    sw = int(W * 1.12); sh = int(sw * 960 / 1280)
    travel = sw - W
    x = f"{travel}*t/{dur}" if left_to_right else f"{travel}-{travel}*t/{dur}"
    return (f"[{i}:v]fps=30,scale={sw}:{sh},crop={W}:{H}:'{x}':'(ih-{H})/2',setsar=1")

args = ["ffmpeg", "-v", "error", "-y"]
filters, labels = [], []
inp = 0
def still(img, dur):
    global inp
    args.extend(["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", img]); inp += 1; return inp - 1
def ovl(path):
    global inp
    args.extend(["-i", path]); inp += 1; return inp - 1

scenes = []  # (rótulo de vídeo, dur)
def add_simple(k, img, dur, foot, badge, ltr):
    a = still(img, dur); o = ovl(overlay(f"o{k}", foot, badge))
    filters.append(f"{pan(a, dur, ltr)},pad={W}:{W}:0:{VID_TOP}:black[b{k}];"
                   f"[b{k}][{o}:v]overlay=0:0,fade=t=in:st=0:d=0.4,fade=t=out:st={dur-0.4}:d=0.4[s{k}]")
    scenes.append(dur)

add_simple(0, IMG_A, 4, [("ANTES: SUJA DE BARRO", 36, YEL), ("Barro e sujeira acumulados", 26, "white")], ("ANTES", RED), True)
add_simple(1, IMG_D, 4, [("DEPOIS: LIMPA E BRILHANDO", 33, YEL), ("Lavagem completa, do pneu ao teto", 26, "white")], ("DEPOIS", GREEN), False)
# comparação: antes -> depois com transição em cortina
a = still(IMG_A, 3); d_ = still(IMG_D, 3); o = ovl(overlay("o2", [("VEJA A DIFERENÇA", 38, YEL), ("Cada detalhe faz diferença", 26, "white")]))
filters.append(f"{pan(a, 3, True)}[pa];{pan(d_, 3, False)}[pd];"
               f"[pa][pd]xfade=transition=wipeleft:duration=2:offset=0.7,pad={W}:{W}:0:{VID_TOP}:black[b2];"
               f"[b2][{o}:v]overlay=0:0,fade=t=in:st=0:d=0.4,fade=t=out:st=3.6:d=0.4[s2]")
scenes.append(4)
add_simple(3, IMG_D, 4, [("OBRIGADO, BELAGRÍCOLA!", 40, YEL), ("Pela confiança e pela preferência", 27, "white")], None, True)
add_simple(4, IMG_D, 4, [("CHAME NO PLANTÃO!", 40, YEL), PHONE, ADDR], None, False)

for k, dur in enumerate(scenes):
    filters.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{dur}[a{k}]")
    labels.append(f"[s{k}][a{k}]")
filters.append("".join(labels) + f"concat=n={len(scenes)}:v=1:a=1[v][a]")
args += ["-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", OUT]
subprocess.run(args, check=True)
print("OK", OUT)
