"""Animate a growing snake over the real contribution cells from Platane/snk.

The snake follows a non-intersecting sweep from recent to older weeks. Each
nonempty day adds exactly one cell of body length; empty days do not grow it.
Python standard library only. Run after snk generation, before publishing.
"""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


def build(source):
    root = ET.fromstring(source)
    css = ''.join(e.text or '' for e in root if e.tag.endswith('style'))
    variables = re.search(r':root\{([^}]+)\}', css).group(1)
    levels = dict(re.findall(r'\.c\.(c[0-9a-z]+)\{fill:var\(--(c[1-4])\)', css))
    cells = {}
    for node in root.iter():
        classes = node.get('class', '').split()
        if node.tag.endswith('rect') and 'c' in classes:
            point = (int(float(node.get('x'))) + 6, int(float(node.get('y'))) + 6)
            level = next((levels[c] for c in classes if c in levels), None)
            cells[point] = level
    if not cells:
        raise ValueError('No contribution cells found; refusing to replace artwork')

    xs = sorted({x for x, _ in cells}, reverse=True)
    ys = sorted({y for _, y in cells})
    assert all(a-b == 16 for a,b in zip(xs,xs[1:]))
    assert all(b-a == 16 for a,b in zip(ys,ys[1:]))
    start_y = ys[0] - 16
    route = [(xs[0]-48, start_y), (xs[0]-32, start_y),
             (xs[0]-16, start_y), (xs[0], start_y)]
    for i,x in enumerate(xs):
        route.extend((x,y) for y in (ys if i % 2 == 0 else ys[::-1]))
    food_count = sum(level is not None for level in cells.values())
    # Exit left far enough for the whole grown tail to leave before reset.
    x,y = route[-1]
    route.extend((x-16*i,y) for i in range(1,food_count+8))
    assert len(set(route)) == len(route), 'Route must never cross itself'
    assert all(abs(a[0]-b[0])+abs(a[1]-b[1]) == 16 for a,b in zip(route,route[1:]))

    length, distance, clock = 48, 48, 800
    frames = [(0, length, 0), (clock,length,0)]
    eaten = {}
    for point in route[4:]:
        meal = cells.get(point) is not None
        clock += 150 if meal else 40
        distance += 16
        if meal:
            length += 16
            eaten[point] = clock
        frames.append((clock,length,distance-length))
    duration = clock+800
    frames.append((duration,length,distance-length))
    assert len(eaten) == food_count
    assert length == 48 + 16*food_count
    assert all(b[1]-a[1] in (0,16) for a,b in zip(frames,frames[1:]))
    assert all(b[2]>=a[2] for a,b in zip(frames,frames[1:]))
    gap = len(route)*16+100
    percent = lambda ms: f'{ms/duration*100:.6f}'
    styles = [f':root{{{variables}}}',
              '.cell{stroke:var(--cb);stroke-width:1}',
              f'.snake{{fill:none;stroke:var(--cs);stroke-width:12;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:48 {gap};animation:grow {duration}ms linear infinite}}',
              '@keyframes grow{'+''.join(f'{percent(t)}%{{stroke-dasharray:{size} {gap};stroke-dashoffset:{-tail}}}' for t,size,tail in frames)+'}']
    rects = []
    for i,((x,y),level) in enumerate(sorted(cells.items())):
        color = f'var(--{level})' if level else 'var(--ce)'
        if level:
            t = percent(eaten[(x,y)])
            styles.append(f'.food{i}{{animation:eat{i} {duration}ms steps(1,end) infinite}}'
                          f'@keyframes eat{i}{{0%{{fill:{color}}}{t}%,100%{{fill:var(--ce)}}}}')
        rects.append(f'<rect class="cell food{i}" x="{x-6}" y="{y-6}" width="12" height="12" rx="2" fill="{color}"/>')
    styles.append('@media(prefers-reduced-motion:reduce){*{animation:none!important}}')
    path = 'M'+' L'.join(f'{x},{y}' for x,y in route)
    vb = root.get('viewBox').split()
    title = 'A snake that grows as it eats GitHub contribution squares'
    result = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]} {vb[1]} {vb[2]} 160" width="{root.get("width")}" height="160" role="img" aria-labelledby="title">'
              f'<title id="title">{title}</title><desc>Contribution data and colors from Platane/snk. Each nonempty day adds one body section. The animation resets after the tail leaves.</desc>'
              '<style>'+''.join(styles)+'</style>'+''.join(rects)+f'<path class="snake" d="{path}"/></svg>')
    ET.fromstring(result)
    return result, {'food':food_count,'initial_length':48,'final_length':length,'duration_ms':duration}


if __name__ == '__main__':
    for name in sys.argv[1:]:
        path = Path(name)
        result,stats = build(path.read_text())
        path.write_text(result)
        print(f'{path.name}: {stats}')
