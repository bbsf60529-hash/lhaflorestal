#!/usr/bin/env python3
"""Vídeo de propaganda Forest Truck - antes e depois, mesmo layout 1080x1080.
Uso: montar_video_antes_depois.py VIDEO.mp4 [saida.mp4]
O trecho "antes" (0-8,6s) tem quadros com efeito de falha colorida, que são removidos.
Os trechos do "depois" foram escolhidos para não mostrar a placa do veículo."""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "forest_truck_propaganda_antes_depois.mp4"
TMP = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_tmp")
os.makedirs(TMP, exist_ok=True)
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, VID_TOP, VID_BOT = 1080, 140, 880
H = VID_BOT - VID_TOP
GREEN, DARK, YEL, LIGHT, RED = (27, 94, 26), (13, 50, 15), (255, 215, 0), (200, 255, 200), (200, 30, 30)

def font(s): return ImageFont.truetype(B, s)
def center(d, y, text, size, fill): d.text((W // 2, y), text, font=font(size), fill=fill, anchor="mm")

def badge(d, cx, text, color):
    f = font(46); l, t, r, b = d.textbbox((cx, VID_TOP + 55), text, font=f, anchor="mm")
    d.rounded_rectangle([l - 24, t - 12, r + 24, b + 12], radius=14, fill=color + (235,))
    d.text((cx, VID_TOP + 55), text, font=f, fill="white", anchor="mm")

def overlay(name, footer, badges=()):
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, VID_TOP], fill=GREEN + (255,))
    center(d, 35, "FOREST TRUCK - LAVA JATO PESADO", 44, "white")
    center(d, 90, "LAVAGEM DE CAMINHONETES E VEÍCULOS LEVES", 23, YEL)
    d.rectangle([0, VID_BOT, W, W], fill=DARK + (255,))
    d.rectangle([5, VID_BOT + 5, W - 6, W - 6], outline=YEL, width=4)
    for i, (txt, size, col) in enumerate(footer):
        center(d, VID_BOT + 45 + i * 55 if len(footer) > 1 else VID_BOT + 100, txt, size, col)
    for cx, text, color in badges: badge(d, cx, text, color)
    p = f"{TMP}/{name}.png"; im.save(p); return p

# 1) "antes" limpo: recorta a faixa horizontal, remove os quadros de falha e borra a placa (câmera fixa)
glitch = [(0.88, 1.68), (2.22, 3.08), (3.98, 4.82), (5.95, 6.78), (7.65, 8.3)]
sel = "not(" + "+".join(f"between(t,{a},{b})" for a, b in glitch) + ")"
BEFORE = f"{TMP}/antes.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-t", "8.6", "-i", SRC, "-an",
                "-vf", f"crop=720:542:0:368,select='{sel}',setpts=N/30/TB,fps=30,"
                       "split[a][b];[b]crop=105:58:170:248,boxblur=14:4[bl];[a][bl]overlay=170:248",
                "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", BEFORE], check=True)
BEFORE_DUR = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                            "-of", "csv=p=0", BEFORE]))

PHONE = ("PLANTÃO: (42) 99846-9325", 34, "white")
ADDR = ("Rua José Zampier Filho, 86 - Industrial", 24, "white")
FB = f"scale={W}:-2,crop={W}:{H}:0:(ih-{H})/2"          # antes: preenche a janela
FA = lambda y: f"scale={W}:-2,crop={W}:{H}:0:{y}"        # depois: vertical -> janela
SPL = (f"[0:v]scale=-2:{H},crop=540:{H}:(iw-540)/2:0[l];"
       f"[1:v]scale=540:-2,crop=540:{H}:0:200[r];[l][r]hstack")
HALF = (f"[0:v]fps=30,scale=-2:{H},crop=540:{H}:(iw-540)/2:0[l];"
        f"[1:v]fps=30,scale=540:-2,crop=540:{H}:0:200[r];[l][r]hstack")

# (tipo, entradas [(arquivo, ss, dur)], filtro, áudio de, overlay)
scenes = [
    ("antes",  [(BEFORE, 0, BEFORE_DUR), (SRC, 0, BEFORE_DUR)], f"[0:v]fps=30,{FB}", 1,
     overlay("o0", [("ANTES: SUJA DE BARRO E POEIRA", 31, YEL), ("Estrada, obra e pátio deixam marcas", 25, "white")],
             [(150, "ANTES", RED)])),
    ("depois", [(SRC, 10.5, 3.5), (SRC, 10.5, 3.5)], f"[0:v]fps=30,{FA(200)}", 1,
     overlay("o1", [("DEPOIS: LIMPA E BRILHANDO", 33, YEL), ("Lavagem completa, do pneu ao teto", 26, "white")],
             [(160, "DEPOIS", GREEN)])),
    ("split",  [(BEFORE, 0.3, 3.5), (SRC, 20, 3.5)], None, 1,
     overlay("o2", [("VEJA A DIFERENÇA", 38, YEL), ("Cada detalhe faz diferença", 26, "white")],
             [(270, "ANTES", RED), (810, "DEPOIS", GREEN)])),
    ("cta",    [(SRC, 20, 3.6), (SRC, 20, 3.6)], f"[0:v]fps=30,{FA(300)}", 1,
     overlay("o3", [("DEIXE SUA CAMINHONETE ASSIM!", 33, YEL), PHONE, ADDR])),
]

args = ["ffmpeg", "-v", "error", "-y"]
filters, labels = [], []
for i, (kind, ins, flt, _, ov) in enumerate(scenes):
    dur = ins[0][2]
    for f, ss, d in ins: args += ["-ss", str(ss), "-t", str(d), "-i", f]
    args += ["-i", ov]
    a, b, o = 3 * i, 3 * i + 1, 3 * i + 2
    # reindexa os rótulos [0:v]/[1:v] do filtro para as entradas desta cena
    g = (HALF if kind == "split" else flt).replace("[0:v]", f"[{a}:v]").replace("[1:v]", f"[{b}:v]")
    filters.append(f"{g},pad={W}:{W}:0:{VID_TOP}:black,setsar=1[b{i}];"
                   f"[b{i}][{o}:v]overlay=0:0,fade=t=in:st=0:d=0.4,fade=t=out:st={dur-0.4}:d=0.4[s{i}]")
    # áudio sempre do vídeo original (entrada 1 da cena)
    filters.append(f"[{b}:a]volume=0.5,afade=t=in:d=0.3,afade=t=out:st={dur-0.4}:d=0.4[a{i}]")
    labels.append(f"[s{i}][a{i}]")
filters.append("".join(labels) + f"concat=n={len(scenes)}:v=1:a=1[v][a]")
args += ["-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", OUT]
subprocess.run(args, check=True)
print("OK", OUT)
