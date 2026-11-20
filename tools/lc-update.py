#!/usr/bin/env python3
"""LIVING CANVAS · one-command updater.
Puts the newest site code (from GitHub) into the LIVING CANVAS file in ~/Downloads,
keeping everything inside it: photos, videos, music, settings, fonts. A backup is kept."""
import glob, os, re, shutil, sys, time, urllib.request

NAME = "LIVING CANVAS — Sculpted Celebrations · Houston.html"
CODE = "https://raw.githubusercontent.com/mrjnexus-netizen/living-canvas/main/tools/site-code.html"
D = os.path.expanduser("~/Downloads")

def find():
    p = os.path.join(D, NAME)
    if os.path.exists(p): return p
    L = [f for f in glob.glob(os.path.join(D, "LIVING CANVAS*Houston*.html")) if "online" not in f.lower()]
    return max(L, key=os.path.getmtime) if L else None

src_path = find()
if not src_path: sys.exit("✕ The LIVING CANVAS file was not found in Downloads.")
print("· file:", os.path.basename(src_path))
src = open(src_path, encoding="utf-8").read()
print("· downloading the newest site code …")
tpl = urllib.request.urlopen(urllib.request.Request(CODE + "?t=%d" % time.time(), headers={"Cache-Control": "no-cache"}), timeout=120).read().decode("utf-8")

def pick(rx, req=True):
    m = re.search(rx, src)
    if not m and req: sys.exit("✕ This file does not look like a LIVING CANVAS file (missing part).")
    return m.group(1) if m else None

fonts = pick(r'<style>\s*((?:@font-face\{[^}]*\})+)')
data = pick(r'const DATA = ([\s\S]*?);\nconst FONTCSS = ')
fcss = pick(r'\nconst FONTCSS = ("(?:[^"\\]|\\.)*");')
vid = pick(r'src="(data:video/mp4;base64,[^"]+)"')
pos = pick(r'poster="(data:image/[a-z]+;base64,[^"]+)"')
ph = pick(r'id="lcPhotos">([\s\S]*?)</script>', False)
med = pick(r'id="lcMedia">([\s\S]*?)</script>', False)
adm = pick(r'id="lcAdmin">([\s\S]*?)</script>', False)

out = (tpl.replace("__FONTS__", fonts, 1)
          .replace("const DATA = __DATA__;", "const DATA = " + data + ";\nconst FONTCSS = " + fcss + ";", 1)
          .replace("__VIDEO__", vid, 1).replace("__POSTER__", pos, 1)
          .replace("__MEDIA__", med.strip() if med and med.strip() else "{}", 1))
T = '<script type="application/json" id="lcPhotos">{}</script>'
if ph and ph.strip() not in ("", "{}"): out = out.replace(T, T.replace("{}", ph), 1)
A = '<script type="application/json" id="lcAdmin">null</script>'
if adm and adm.strip() not in ("", "null"): out = out.replace(A, A.replace("null", adm), 1)
if re.search(r"__FONTS__|__DATA__|__VIDEO__|__POSTER__|__MEDIA__", out): sys.exit("✕ Update stopped — nothing was changed.")

bk = os.path.join(D, "LIVING CANVAS backups"); os.makedirs(bk, exist_ok=True)
shutil.copy2(src_path, os.path.join(bk, time.strftime("%Y-%m-%d %H.%M ") + os.path.basename(src_path)))
tmp = src_path + ".new"; open(tmp, "w", encoding="utf-8").write(out); os.replace(tmp, src_path)
print("✓ done — open the file again:", os.path.basename(src_path))
