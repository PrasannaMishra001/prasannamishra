"""Image and video figures, shared by build.py and records.py."""

import html
import os
import re
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def esc(text):
    return html.escape(str(text), quote=True)


def image_size(path):
    with open(path, 'rb') as f:
        head = f.read(32)
        if head[:8] == b'\x89PNG\r\n\x1a\n':
            return struct.unpack('>II', head[16:24])
        f.seek(0)
        data = f.read()
    i = 2
    while i < len(data):  # jpeg: walk the segments to the frame header
        if data[i] != 0xFF:
            break
        marker = data[i + 1]
        size = struct.unpack('>H', data[i + 2:i + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack('>HH', data[i + 5:i + 9])
            return w, h
        i += 2 + size
    return 1200, 800



def fig(src, caption='', size='', extra_cls=''):
    path = os.path.join(ROOT, 'assets', src)
    w, h = image_size(path)
    if not size:
        size = 's' if w <= 520 else ('m' if w <= 900 else 'l')
    cap = f'<figcaption>{caption}</figcaption>' if caption else ''
    alt = esc(re.sub(r'<[^>]+>', '', caption)) if caption else ''
    return (f'<figure class="zoomable reveal {size} {extra_cls}"><img src="assets/{src}" alt="{alt}" '
            f'width="{w}" height="{h}" loading="lazy" decoding="async" />{cap}</figure>')


def vid(name, caption='', size='l'):
    poster = os.path.join(ROOT, 'assets', 'video', name + '.jpg')
    w, h = image_size(poster)
    cap = f'<figcaption>{caption}</figcaption>' if caption else ''
    return (f'<figure class="video reveal {size}"><video controls muted playsinline preload="none" '
            f'poster="assets/video/{name}.jpg" width="{w}" height="{h}">'
            f'<source src="assets/video/{name}.mp4" type="video/mp4" /></video>{cap}</figure>')
