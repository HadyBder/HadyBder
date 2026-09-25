"""Generate the profile's original vector artwork using Python's standard library.

Run from any directory: python3 scripts/generate_art.py
Artwork is decorative, not operational telemetry or a system architecture.
"""
from pathlib import Path
from math import sin, cos, pi
from html import escape

OUT = Path(__file__).resolve().parents[1] / 'assets'
OUT.mkdir(exist_ok=True)
INK, PAPER, MINT, GOLD, MUTED = '#101d25', '#f4f0e6', '#8ee2c0', '#e9bb7b', '#a5b7bb'

def text(x, y, value, size=20, color=PAPER, weight=400, spacing=0, font='Arial, Helvetica, sans-serif'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}">{escape(value)}</text>'

def path(d, color=MINT, width=1, extra=''):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" {extra}/>'

def circle(x, y, r, color=MINT, extra=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" {extra}/>'

def svg(name, w, h, title, body):
    content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">Original geometric artwork connecting signals, software, and physical systems.</desc>
<style>@keyframes orbit{{to{{transform:rotate(360deg)}}}} @keyframes flow{{to{{stroke-dashoffset:-120}}}} .orbit{{transform-origin:914px 229px;animation:orbit 48s linear infinite}} .flow{{animation:flow 14s linear infinite}} @media(prefers-reduced-motion:reduce){{.orbit,.flow{{animation:none!important}}}}</style>
{body}
</svg>'''
    (OUT / name).write_text(content)

# A bespoke signal sculpture: a woven torus, with moving markers and flowing traces.
b = f'<rect width="1200" height="500" rx="18" fill="{INK}"/>'
b += '<defs><radialGradient id="halo"><stop stop-color="#244439" stop-opacity=".7"/><stop offset="1" stop-color="#101d25" stop-opacity="0"/></radialGradient><clipPath id="bounds"><rect width="1200" height="500" rx="18"/></clipPath></defs>'
b += '<g clip-path="url(#bounds)"><circle cx="914" cy="229" r="255" fill="url(#halo)"/>'
for x in range(690, 1190, 28):
    for y in range(45, 422, 28):
        b += circle(x, y, .8, '#47615e', 'opacity=".48"')
b += path('M56 85H1144', '#34434a')
b += text(56, 55, 'HB / ENGINEERING', 16, MINT, 500, 3)
b += text(925, 55, 'SIGNAL → SOFTWARE', 13, MUTED, 400, 1)
b += text(52, 192, 'Hady', 105, PAPER, 700, -5)
b += text(50, 295, 'Bdeir.', 105, PAPER, 700, -5)
b += text(57, 347, 'Software engineer. Systems thinker.', 25, PAPER)
b += text(57, 383, 'Building useful things across code and the physical world.', 18, MUTED)
for i in range(32):
    a = i * 2*pi/32
    pts = []
    for j in range(161):
        t = j * 2*pi/160
        # Surface of a torus rotated into an isometric perspective.
        x = (133 + 47*cos(t))*cos(a)
        yy = (133 + 47*cos(t))*sin(a)
        z = 47*sin(t)
        sx, sy = 914+x, 229+yy*.56+z*.83
        pts.append(f'{sx:.2f},{sy:.2f}')
    b += path('M'+' L'.join(pts)+' Z', MINT if i % 4 else GOLD, .9, 'opacity=".66"')
b += '<g class="orbit">'
b += '<ellipse cx="914" cy="229" rx="207" ry="207" fill="none" stroke="#59756d" stroke-width="1" stroke-dasharray="2 12"/>'
b += circle(914, 22, 4, GOLD) + circle(914, 436, 4, MINT)
b += '</g>'
b += path('M696 229H756 M1072 229H1133 M914 109V138 M914 320V350','#60857a')
b += circle(914, 229, 4, PAPER)
b += text(825, 394, 'FORM FOLLOWS FUNCTION', 12, MUTED, 400, 2)
b += f'<rect y="432" width="1200" height="68" fill="{PAPER}"/>'
b += text(56, 474, '01 / BACKEND', 16, INK, 700, 1)
b += text(440, 474, '02 / APPLIED AI', 16, INK, 700, 1)
b += text(865, 474, '03 / SYSTEMS', 16, INK, 700, 1)
b += '</g>'
svg('signal-header.svg',1200,500,'Hady Bdeir — Software engineer. Systems thinker.',b)

# Small editorial illustrations, paired with real, selectable project descriptions.
def card_base(label, n, color):
    return f'<rect width="580" height="206" rx="10" fill="{INK}"/>'+text(26,36,label,14,color,500,1.5)+text(525,36,n,14,MUTED)+path('M26 53H554','#33454b')

b = card_base('INDUSTRIAL INTELLIGENCE','01',MINT)
for k in range(3):
    pts=[f'{26+j*2.8:.1f},{93+k*32+sin(j*.2+k)*9:.1f}' for j in range(60)]
    b += path('M'+' L'.join(pts),MINT if k!=1 else GOLD,1.7)
b += path('M204 115L236 115L262 133 M204 154L236 154L262 133', '#6b8c83',1.5)
b += '<rect x="262" y="91" width="70" height="84" rx="8" fill="#213c35" stroke="#8ee2c0"/>'
b += text(279,141,'{ }',27,MINT,500)
b += path('M332 133H380',MINT,2,'class="flow" stroke-dasharray="6 8"')
for i,w in enumerate([150,106,126]):
    b += f'<rect x="393" y="{98+i*28}" width="{w}" height="8" rx="4" fill="{MINT if i==0 else "#405c55"}"/>'
svg('project-ccr.svg',580,206,'Industrial intelligence — signals into structured knowledge',b)

b = card_base('BACKEND ENGINEERING','02',GOLD)
for i,(verb,route) in enumerate([('GET','/applications'),('POST','/applications'),('GET','/applications/{id}')]):
    yy=91+i*35
    b+=f'<rect x="26" y="{yy-16}" width="61" height="25" rx="4" fill="#354132"/>'
    b+=text(33,yy+2,verb,13,GOLD,700)+text(101,yy+2,route,16,PAPER,font='monospace')
b += '<ellipse cx="490" cy="94" rx="39" ry="13" fill="#283a38" stroke="#e9bb7b"/>'
b += path('M451 94V155C451 173 529 173 529 155V94 M451 124C451 142 529 142 529 124',GOLD,1.5)
b += path('M368 129H430',GOLD,1.5,'class="flow" stroke-dasharray="5 7"')
svg('project-api.svg',580,206,'Backend engineering — Java APIs and persistence',b)

b=card_base('EVERYDAY SOFTWARE','03',MINT)
for i in range(4):
    x=28+i*74
    b+=f'<rect x="{x}" y="80" width="60" height="61" rx="5" fill="#243c35" stroke="#47665a"/>'
    b+=circle(x+30,107,12,MINT if i%2==0 else GOLD)
    b+=path(f'M{x+14} 129H{x+46}',MUTED)
b+=path('M29 165H314','#47665a',4)
b+='<path d="M382 72H530V183L520 177L510 183L500 177L490 183L480 177L470 183L460 177L450 183L440 177L430 183L420 177L410 183L400 177L390 183L382 177Z" fill="#f4f0e6"/>'
for y in [94,110,126]:
    b+=path(f'M398 {y}H458 M489 {y}H513','#67817a',2)
b+=path('M398 141H513','#67817a')
b+=text(398,164,'LOCAL / FIRST',12,INK,700)
svg('project-pos.svg',580,206,'Everyday software — checkout, inventory, and local storage',b)

b=card_base('FAULT-TOLERANT SYSTEMS','04',GOLD)
for i in range(3):
    y=88+i*40
    b+=circle(64,y,17,'#294136')+text(53,y+5,f'S{i+1}',13,MINT,700)
    b+=path(f'M82 {y}H170L232 128',MINT if i<2 else '#778582',1.5)
b+='<rect x="232" y="93" width="114" height="70" rx="9" fill="#293d36" stroke="#e9bb7b"/>'
b+=text(253,137,'2 / 3',25,GOLD,700)
b+=path('M346 128H409',GOLD,2,'class="flow" stroke-dasharray="5 7"')
b+='<circle cx="469" cy="128" r="36" fill="none" stroke="#698f7d" stroke-width="2"/>'
b+=path('M448 128L463 143L490 114',MINT,3)
svg('project-control.svg',580,206,'Fault-tolerant pressure control — two-out-of-three sensor validation',b)

b=f'<rect width="1200" height="134" rx="12" fill="{INK}"/>'
b+=text(38,49,'LET’S BUILD SOMETHING USEFUL.',15,MINT,500,2)
b+=text(37,94,'Good questions. Clear thinking. Working software.',27,PAPER,500)
b+=path('M1091 66H1155 M1136 47L1155 66L1136 85',MINT,2)
svg('footer.svg',1200,134,'Let’s build something useful. Good questions. Clear thinking. Working software.',b)
