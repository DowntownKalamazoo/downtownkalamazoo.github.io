#!/usr/bin/env python3
"""Generates brand-derived assets for the site from the vector patterns in the brand guide.

Outputs (into ./assets_out, copied to out/ by build.py):
  pattern-<name>-sm.webp      small pattern swatches for footer, chips and patches
  downloads/phone-<name>.jpg  phone wallpapers
  downloads/call-<name>.jpg   video-call backgrounds with the logo
  downloads/*-thumb.webp      previews for the take-home page
  downloads/coloring-pages.pdf
Run once whenever the source art changes:  python3 make_assets.py
"""
import base64, io, os, re, shutil
import cairosvg
from PIL import Image
from pypdf import PdfWriter, PdfReader

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets_out')
DL = os.path.join(OUT, 'downloads')
SRC = open(os.path.join(HERE, 'data', 'brand', 'patterns-page.svg')).read()
INNER = SRC[SRC.index('>', SRC.index('<svg')) + 1: SRC.rindex('</svg>')]
LOGO_REV = os.path.join(HERE, 'logo-reverse.png')
LOGO_GREEN = os.path.join(HERE, 'dk-logo-green.png')
SITE = 'https://downtownkalamazoo.us/'
NAVY = '#121345'

_cols = [(518, 769), (784, 1035), (1049, 1302), (1316, 1567)]
_rows = [(165, 387), (402, 625), (641, 863)]
_names = [['squiggle', 'confetti', 'arcs', 'dots'], ['quilt', 'stripes', 'waves', 'speckle'], ['loops', 'maze', 'pinstripes', 'dashes']]
TILES = {}
for ri, (y0, y1) in enumerate(_rows):
    for ci, (x0, x1) in enumerate(_cols):
        TILES[_names[ri][ci]] = (x0 + 6, y0 + 6, x1 - x0 - 12, y1 - y0 - 12)
LIGHT = {'confetti', 'stripes', 'speckle', 'loops', 'pinstripes'}   # light patterns get the green K, the rest get the white K


def crop_box(name, aspect):
    """Largest box inside the tile with the given width/height aspect, centered."""
    x, y, w, h = TILES[name]
    if w / h > aspect:
        nw = h * aspect
        return x + (w - nw) / 2, y, nw, h
    nh = w / aspect
    return x, y + (h - nh) / 2, w, nh


def line_inner():
    return re.sub(r'fill="rgb\([^)]*\)"', f'fill="#ffffff" stroke="{NAVY}" stroke-width="0.7" stroke-linejoin="round"', INNER)


def nested(name, x, y, w, h, inner=INNER):
    bx, by, bw, bh = crop_box(name, w / h)
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{bx:.2f} {by:.2f} {bw:.2f} {bh:.2f}" preserveAspectRatio="xMidYMid slice">{inner}</svg>'


def doc(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'


def png_uri(path_or_img, width=None):
    im = Image.open(path_or_img) if isinstance(path_or_img, str) else path_or_img
    if width:
        im = im.copy(); im.thumbnail((width, width * 4))
    b = io.BytesIO(); im.save(b, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode(), im.size


def render(svg, w, h):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h))).convert('RGBA')


def smalls():
    for n in TILES:
        im = Image.open(os.path.join(HERE, f'pattern-{n}.webp')).convert('RGB')
        im.thumbnail((480, 480))
        im.save(os.path.join(OUT, f'pattern-{n}-sm.webp'), 'WEBP', quality=78, method=6)


from downloads_data import PHONE, CALL


def wallpapers():
    for n in PHONE:
        im = render(doc(1170, 2532, nested(n, 0, 0, 1170, 2532)), 1170, 2532).convert('RGB')
        im.save(os.path.join(DL, f'phone-{n}.jpg'), 'JPEG', quality=88, optimize=True)
        t = im.copy(); t.thumbnail((240, 520)); t.save(os.path.join(DL, f'phone-{n}-thumb.webp'), 'WEBP', quality=75)
    logo = Image.open(LOGO_REV).convert('RGBA')
    logo.thumbnail((340, 340))
    for n in CALL:
        im = render(doc(1920, 1080, nested(n, 0, 0, 1920, 1080)), 1920, 1080)
        im.alpha_composite(logo, (1920 - logo.width - 70, 1080 - logo.height - 60))
        im = im.convert('RGB')
        im.save(os.path.join(DL, f'call-{n}.jpg'), 'JPEG', quality=88, optimize=True)
        t = im.copy(); t.thumbnail((480, 270)); t.save(os.path.join(DL, f'call-{n}-thumb.webp'), 'WEBP', quality=75)


COLOR = [('squiggle', 'The squiggle'), ('confetti', 'Confetti'), ('loops', 'Loop-de-loops'),
         ('maze', 'The maze'), ('dots', 'Snowfall dots'), ('dashes', 'Dashes')]


def pdf_from_pages(pages, path):
    w = PdfWriter()
    for svg in pages:
        for p in PdfReader(io.BytesIO(cairosvg.svg2pdf(bytestring=svg.encode()))).pages:
            w.add_page(p)
    with open(path, 'wb') as f:
        w.write(f)


def coloring():
    li = line_inner()
    logo, (lw, lh) = png_uri(LOGO_GREEN, 300)
    pages = []
    for i, (n, label) in enumerate(COLOR):
        x, y, w, h = 42, 150, 528, 520
        body = (f'<rect width="612" height="792" fill="#fff"/>'
                f'<text x="42" y="70" font-family="Jost" font-weight="bold" font-size="12" fill="{NAVY}" letter-spacing="1.5">DOWNTOWN KALAMAZOO · COLORING PAGE {i + 1} OF {len(COLOR)}</text>'
                f'<text x="42" y="112" font-family="Unbounded" font-weight="900" font-size="30" fill="{NAVY}">COLOR YOUR DOWNTOWN</text>'
                f'<text x="42" y="136" font-family="Jost" font-size="14" fill="{NAVY}">{label}, from the patterns made for Downtown Kalamazoo.</text>'
                f'{nested(n, x, y, w, h, li)}'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="none" stroke="{NAVY}" stroke-width="2.5"/>'
                f'<text x="42" y="712" font-family="Jost" font-weight="bold" font-size="14" fill="{NAVY}">Show us your colors: #SomethingNewKalamazoo</text>'
                f'<text x="42" y="732" font-family="Jost" font-size="12" fill="{NAVY}">More to print and color at downtownkalamazoo.us</text>'
                f'<image x="{570 - 92}" y="690" width="92" height="{92 * lh / lw:.1f}" xlink:href="{logo}"/>')
        pages.append(doc(612, 792, body))
    pdf_from_pages(pages, os.path.join(DL, 'coloring-pages.pdf'))
    # preview of page 1 for the site
    prev = render(pages[0], 612 * 1, 792 * 1).convert('RGB')
    prev.thumbnail((360, 470)); prev.save(os.path.join(DL, 'coloring-thumb.webp'), 'WEBP', quality=78)


# ---------------------------------------------------------------- Holiday coloring & craft pack
def li_w(name, target_w, pt=1.3):
    """Line art for one pattern, with strokes about `pt` points wide at the size it will print."""
    bw = TILES[name][2]
    sw = pt * bw / max(target_w, 1)
    return re.sub(r'fill="rgb\([^)]*\)"', f'fill="#ffffff" stroke="{NAVY}" stroke-width="{sw:.3f}" stroke-linejoin="round"', INNER)


_UID = [0]


def clipped(name, shape, bbox, pt=1.3, outline=2.2):
    """Pattern line art cut to any SVG shape (in page coordinates), plus the shape's outline."""
    _UID[0] += 1
    cid = f'c{_UID[0]}'
    x, y, w, h = bbox
    return (f'<defs><clipPath id="{cid}">{shape}</clipPath></defs>'
            f'<g clip-path="url(#{cid})">{nested(name, x, y, w, h, li_w(name, w, pt))}</g>'
            f'<g fill="none" stroke="{NAVY}" stroke-width="{outline}" stroke-linejoin="round">{shape}</g>')


def page_frame(i, n, title, sub):
    logo, (lw, lh) = png_uri(LOGO_GREEN, 300)
    return (f'<rect width="612" height="792" fill="#fff"/>'
            f'<text x="42" y="66" font-family="Jost" font-weight="bold" font-size="12" fill="{NAVY}" letter-spacing="1.5">FIND THE HOLIDAYS DOWNTOWN · COLOR &amp; CRAFT {i} OF {n}</text>'
            f'<text x="42" y="106" font-family="Unbounded" font-weight="900" font-size="28" fill="{NAVY}">{title}</text>'
            f'<text x="42" y="130" font-family="Jost" font-size="14" fill="{NAVY}">{sub}</text>'
            f'<text x="42" y="742" font-family="Jost" font-weight="bold" font-size="13" fill="{NAVY}">Show us what you make: #SomethingNewKalamazoo</text>'
            f'<text x="42" y="760" font-family="Jost" font-size="11" fill="{NAVY}">More to print at downtownkalamazoo.us</text>'
            f'<image x="{570 - 80}" y="712" width="80" height="{80 * lh / lw:.1f}" xlink:href="{logo}"/>')


def k_shape_placed(x, y, w):
    ksvg = open(os.path.join(HERE, 'k-shape.svg')).read()
    vx, vy, vw, vh = [float(v) for v in re.search(r'viewBox="([^"]+)"', ksvg).group(1).split()]
    d = re.search(r' d="([^"]+)"', ksvg).group(1)
    sc = w / vw
    h = vh * sc
    return f'<path transform="translate({x - vx * sc:.2f} {y - vy * sc:.2f}) scale({sc:.5f})" d="{d}" vector-effect="non-scaling-stroke"/>', h


def holiday_pack():
    N = 7
    pages = []

    # 1. Color the K
    kshape, kh = k_shape_placed(96, 160, 420)
    body = page_frame(1, N, 'COLOR THE K', 'The brush-stroke K from the Downtown Kalamazoo logo, filled with the squiggle.')
    body += clipped('squiggle', kshape, (96, 160, 420, kh), pt=1.4, outline=3)
    pages.append(doc(612, 792, body))

    # 2. Deck the Mall: six ornaments
    body = page_frame(2, N, 'DECK THE MALL', 'Six ornaments, six downtown patterns. Color them, cut them out, hang them up.')
    pats = ['dots', 'confetti', 'squiggle', 'maze', 'arcs', 'dashes']
    for i, pat in enumerate(pats):
        cx = 140 + (i % 3) * 166
        cy = 290 + (i // 3) * 230
        r = 66
        body += f'<path d="M{cx} {cy - r - 34} q -14 -16 0 -30 q 14 14 0 30" fill="none" stroke="{NAVY}" stroke-width="1.6"/>'
        body += f'<line x1="{cx}" y1="{cy - r - 34}" x2="{cx}" y2="{cy - r - 14}" stroke="{NAVY}" stroke-width="1.6"/>'
        body += f'<rect x="{cx - 16}" y="{cy - r - 16}" width="32" height="20" rx="4" fill="#fff" stroke="{NAVY}" stroke-width="2"/>'
        body += clipped(pat, f'<circle cx="{cx}" cy="{cy}" r="{r}"/>', (cx - r, cy - r, 2 * r, 2 * r), pt=1.1)
    pages.append(doc(612, 792, body))

    # 3. A patchwork tree
    body = page_frame(3, N, 'A PATCHWORK TREE', 'Every band of this tree is a different pattern. Add a star on top.')
    top, base, cx, half = 190, 640, 306, 210
    bands = ['confetti', 'dots', 'squiggle', 'arcs', 'maze']
    hb = (base - top) / len(bands)
    for i, pat in enumerate(bands):
        y0, y1 = top + i * hb, top + (i + 1) * hb
        w0, w1 = half * (y0 - top) / (base - top), half * (y1 - top) / (base - top)
        poly = f'<polygon points="{cx - w0:.1f},{y0:.1f} {cx + w0:.1f},{y0:.1f} {cx + w1:.1f},{y1:.1f} {cx - w1:.1f},{y1:.1f}"/>'
        body += clipped(pat, poly, (cx - w1, y0, 2 * w1 + 1, hb + 1), pt=1.1, outline=2.4)
    body += clipped('stripes', f'<rect x="{cx - 34}" y="{base}" width="68" height="54" rx="4"/>', (cx - 34, base, 68, 54), pt=1)
    pts = ' '.join(f'{cx + (34 if k % 2 == 0 else 14) * __import__("math").sin(k * 3.14159 / 5):.1f},{top - 18 - (34 if k % 2 == 0 else 14) * __import__("math").cos(k * 3.14159 / 5):.1f}' for k in range(10))
    body += f'<polygon points="{pts}" fill="#fff" stroke="{NAVY}" stroke-width="2.4" stroke-linejoin="round"/>'
    pages.append(doc(612, 792, body))

    # 4. Mittens
    body = page_frame(4, N, 'A PAIR OF MITTENS', 'Make them match, or don’t. Downtown is a patchwork anyway.')
    def mitten(x, y, flip):
        # one outline: rounded fingers, a palm, and a thumb on the outside edge
        d = (f'M{x} {y + 290} L{x} {y + 105} Q{x} {y} {x + 100} {y} Q{x + 200} {y} {x + 200} {y + 105} L{x + 200} {y + 128} '
             f'C{x + 252} {y + 112} {x + 268} {y + 196} {x + 226} {y + 236} L{x + 200} {y + 258} L{x + 200} {y + 290} Z')
        t = f' transform="translate({2 * x + 200} 0) scale(-1 1)"' if flip else ''
        return f'<path d="{d}"{t}/>', (x - 70, y - 2, 340, 296)
    for flip, x, pat in [(True, 88, 'speckle'), (False, 324, 'loops')]:
        shape, bb = mitten(x, 196, flip)
        body += clipped(pat, shape, bb, pt=1.1)
        body += clipped('stripes', f'<rect x="{x - 8}" y="482" width="216" height="72" rx="12"/>', (x - 8, 482, 216, 72), pt=1)
    pages.append(doc(612, 792, body))

    # 5. Gift tags
    body = page_frame(5, N, 'GIFT TAGS', 'Color, cut out, punch a hole, and tie one on a gift from a downtown shop.')
    tpats = ['confetti', 'dots', 'squiggle', 'maze', 'arcs', 'speckle']
    for i, pat in enumerate(tpats):
        x = 52 + (i % 2) * 262
        y = 160 + (i // 2) * 182
        w, h = 246, 160
        tag = f'<path d="M{x + 40} {y} L{x + w} {y} L{x + w} {y + h} L{x + 40} {y + h} L{x} {y + h - 40} L{x} {y + 40} Z"/>'
        band = f'<path d="M{x + 40} {y} L{x + 96} {y} L{x + 96} {y + h} L{x + 40} {y + h} L{x} {y + h - 40} L{x} {y + 40} Z"/>'
        body += f'<g fill="none" stroke="{NAVY}" stroke-width="2.2" stroke-linejoin="round">{tag}</g>'
        body += clipped(pat, band, (x, y, 96, h), pt=1)
        body += f'<circle cx="{x + 24}" cy="{y + h / 2}" r="7" fill="#fff" stroke="{NAVY}" stroke-width="1.6"/>'
        body += (f'<text x="{x + 112}" y="{y + 52}" font-family="Jost" font-weight="bold" font-size="14" fill="{NAVY}">To:</text>'
                 f'<line x1="{x + 140}" y1="{y + 54}" x2="{x + w - 14}" y2="{y + 54}" stroke="{NAVY}" stroke-width="1"/>'
                 f'<text x="{x + 112}" y="{y + 98}" font-family="Jost" font-weight="bold" font-size="14" fill="{NAVY}">From:</text>'
                 f'<line x1="{x + 156}" y1="{y + 100}" x2="{x + w - 14}" y2="{y + 100}" stroke="{NAVY}" stroke-width="1"/>'
                 f'<text x="{x + 112}" y="{y + 138}" font-family="Jost" font-size="10" fill="{NAVY}">Found downtown · Kalamazoo</text>')
    pages.append(doc(612, 792, body))

    # 6. Patchwork quilt
    body = page_frame(6, N, 'THE DOWNTOWN QUILT', 'Nine squares, nine patterns, one downtown. Pick your colors square by square.')
    qp = ['squiggle', 'confetti', 'arcs', 'dots', 'quilt', 'loops', 'maze', 'speckle', 'dashes']
    S, gx, gy = 168, 54, 158
    for i, pat in enumerate(qp):
        x, y = gx + (i % 3) * S, gy + (i // 3) * S
        body += clipped(pat, f'<rect x="{x}" y="{y}" width="{S}" height="{S}"/>', (x, y, S, S), pt=1.1, outline=2.6)
    pages.append(doc(612, 792, body))

    # 7. Make your own
    body = page_frame(7, N, 'MAKE YOUR OWN PATTERN', 'Squiggles, dots, dashes, loops. Draw a pattern for your favorite downtown spot.')
    body += f'<rect x="54" y="160" width="504" height="430" rx="14" fill="#fff" stroke="{NAVY}" stroke-width="2.6"/>'
    for j, pat in enumerate(['squiggle', 'dots', 'dashes', 'loops']):
        x = 54 + j * 129
        body += clipped(pat, f'<rect x="{x}" y="610" width="117" height="70" rx="8"/>', (x, 610, 117, 70), pt=0.9, outline=1.6)
    body += f'<text x="54" y="702" font-family="Jost" font-size="11" fill="{NAVY}">Need ideas? These four are from the Downtown Kalamazoo pattern library.</text>'
    body += f'<text x="70" y="186" font-family="Jost" font-size="12" fill="{NAVY}">My pattern is for: ______________________________</text>'
    pages.append(doc(612, 792, body))

    pdf_from_pages(pages, os.path.join(DL, 'holiday-color-craft-pack.pdf'))
    im = render(pages[0], 612, 792).convert('RGB')
    im.thumbnail((360, 470)); im.save(os.path.join(DL, 'craft-pack-thumb.webp'), 'WEBP', quality=78)


def social_and_icon():
    # Share image for links posted on social media (1200 x 630)
    im = render(doc(1200, 630, nested('squiggle', 0, 0, 1200, 630)), 1200, 630)
    logo = Image.open(LOGO_REV).convert('RGBA'); logo.thumbnail((560, 560))
    im.alpha_composite(logo, ((1200 - logo.width) // 2, (630 - logo.height) // 2))
    im.convert('RGB').save(os.path.join(OUT, 'og-image.png'), optimize=True)
    # Browser tab icon: the green K on its own
    ksvg = open(os.path.join(HERE, 'k-shape.svg')).read().replace('fill="#000"', 'fill="#38a669"')
    ic = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=ksvg.encode(), output_width=180, output_height=180))).convert('RGBA')
    ic.save(os.path.join(OUT, 'favicon.png'), optimize=True)


if __name__ == '__main__':
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(DL)
    smalls(); print('swatches')
    wallpapers(); print('wallpapers')
    coloring(); print('coloring')
    social_and_icon(); print('share image and icon')
    holiday_pack(); print('holiday color & craft pack')
    for root, _, fs in os.walk(OUT):
        for f in sorted(fs):
            p = os.path.join(root, f); print(f'{os.path.relpath(p, OUT):42s} {os.path.getsize(p) // 1024:6d} KB')
