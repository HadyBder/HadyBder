"""Render four randomized, growing contribution-snake routes per SVG loop.

Backbite moves randomize a Hamiltonian path without crossing or missing cells.
New routes are generated on each workflow run; both themes share the same seed.
"""
from pathlib import Path
import random
import re
import sys
import xml.etree.ElementTree as ET


def random_route(xs, ys, rng):
    route = [(x, y) for i, x in enumerate(xs)
             for y in (ys if i % 2 == 0 else ys[::-1])]
    points = set(route)

    def mix():
        nonlocal route
        if rng.randrange(2):
            route.reverse()
        x, y = route[0]
        neighbors = [(x+16, y), (x-16, y), (x, y+16), (x, y-16)]
        options = [p for p in neighbors if p in points and p != route[1]]
        if options:
            i = route.index(rng.choice(options))
            route = route[:i][::-1] + route[i:]

    def outside(p):
        x, y = p
        choices = []
        if x == min(xs): choices.append((-16, 0))
        if x == max(xs): choices.append((16, 0))
        if y == min(ys): choices.append((0, -16))
        if y == max(ys): choices.append((0, 16))
        return rng.choice(choices) if choices else None

    for _ in range(len(route) * 30):
        mix()
    for _ in range(20000):
        a, b = outside(route[0]), outside(route[-1])
        if a and b:
            x, y = route[0]
            entry = [(x+a[0]*i, y+a[1]*i) for i in range(4, 0, -1)]
            x, y = route[-1]
            # Long enough for even a completely full calendar's tail to exit.
            exit_path = [(x+b[0]*i, y+b[1]*i) for i in range(1, len(route)+8)]
            result = entry + route + exit_path
            if len(set(result)) == len(result):
                assert all(abs(x-u)+abs(y-v) == 16
                           for (x,y),(u,v) in zip(result, result[1:]))
                return result
        mix()
    raise ValueError('Could not find a randomized route with clear entry and exit')


def build(source, seed=None, rounds=4):
    root = ET.fromstring(source)
    css = ''.join(e.text or '' for e in root if e.tag.endswith('style'))
    variables = re.search(r':root\{([^}]+)\}', css).group(1)
    levels = dict(re.findall(r'\.c\.(c[0-9a-z]+)\{fill:var\(--(c[1-4])\)', css))
    cells = {}
    for node in root.iter():
        classes = node.get('class', '').split()
        if node.tag.endswith('rect') and 'c' in classes:
            point = (int(float(node.get('x'))) + 6, int(float(node.get('y'))) + 6)
            cells[point] = next((levels[c] for c in classes if c in levels), None)
    if not cells:
        raise ValueError('No contribution cells found; refusing to replace artwork')
    xs = sorted({x for x, _ in cells})
    ys = sorted({y for _, y in cells})
    assert all(b-a == 16 for a,b in zip(xs,xs[1:]))
    assert all(b-a == 16 for a,b in zip(ys,ys[1:]))
    food_count = sum(level is not None for level in cells.values())
    rng = random.Random(seed)
    scenes, offset = [], 0
    for _ in range(rounds):
        route = random_route(xs, ys, rng)
        # Only keep the exit distance needed for this calendar's grown tail.
        route = route[:4 + len(xs)*len(ys) + food_count + 7]
        length, distance, clock = 48, 48, 500
        frames = [(0,length,0), (clock,length,0)]
        eaten = {}
        for point in route[4:]:
            meal = cells.get(point) is not None
            clock += 140 if meal else 45
            distance += 16
            if meal:
                length += 16
                eaten[point] = offset + clock
            frames.append((clock,length,distance-length))
        duration = clock + 500
        frames.append((duration,length,distance-length))
        assert len(eaten) == food_count
        assert length == 48 + 16*food_count
        assert all(b[1]-a[1] in (0,16) for a,b in zip(frames,frames[1:]))
        scenes.append((offset,duration,route,frames,eaten))
        offset += duration
    total = offset
    pct = lambda t: f'{t/total*100:.7f}'
    styles = [f':root{{{variables}}}', '.cell{stroke:var(--cb);stroke-width:1}',
              '.snake{fill:none;stroke:var(--cs);stroke-width:12;stroke-linecap:round;stroke-linejoin:round}']
    paths = []
    for i,(start,duration,route,frames,eaten) in enumerate(scenes):
        gap = len(route)*16 + 100
        keyframes = ''.join(f'{pct(start+t)}%{{stroke-dasharray:{size} {gap};stroke-dashoffset:{-tail}}}'
                            for t,size,tail in frames)
        styles.append(f'.snake{i}{{stroke-dasharray:48 {gap};animation:grow{i} {total}ms linear infinite}}'
                      f'@keyframes grow{i}{{{keyframes}}}')
        # Visibility switches instantaneously; movement stays smoothly interpolated.
        visibility = (f'0%{{opacity:0}}{pct(start)}%{{opacity:1}}'
                      f'{pct(start+duration)}%,100%{{opacity:0}}')
        styles.append(f'.scene{i}{{opacity:0;animation:show{i} {total}ms steps(1,end) infinite}}'
                      f'@keyframes show{i}{{{visibility}}}')
        d = 'M' + ' L'.join(f'{x},{y}' for x,y in route)
        paths.append(f'<g class="scene{i}"><path class="snake snake{i}" d="{d}"/></g>')
    rects = []
    for i,((x,y),level) in enumerate(sorted(cells.items())):
        color = f'var(--{level})' if level else 'var(--ce)'
        if level:
            keyframes = ''.join(f'{pct(start)}%{{fill:{color}}}{pct(eaten[(x,y)])}%{{fill:var(--ce)}}'
                                for start,duration,route,frames,eaten in scenes)
            styles.append(f'.food{i}{{animation:eat{i} {total}ms steps(1,end) infinite}}'
                          f'@keyframes eat{i}{{{keyframes}100%{{fill:var(--ce)}}}}')
        rects.append(f'<rect class="cell food{i}" x="{x-6}" y="{y-6}" width="12" height="12" rx="2" fill="{color}"/>')
    styles.append('@media(prefers-reduced-motion:reduce){*{animation:none!important}.scene0{opacity:1}}')
    vb = root.get('viewBox').split()
    result = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]} {vb[1]} {vb[2]} 160" width="{root.get("width")}" height="160" role="img" aria-labelledby="title">'
              '<title id="title">A growing snake exploring randomized contribution routes</title>'
              '<desc>Four different winding routes per loop, regenerated daily. Each eaten contribution adds one body section.</desc>'
              '<style>'+''.join(styles)+'</style>'+''.join(rects)+''.join(paths)+'</svg>')
    ET.fromstring(result)
    return result, {'food':food_count, 'rounds':rounds, 'final_length':48+16*food_count, 'duration_ms':total}


if __name__ == '__main__':
    seed = random.SystemRandom().getrandbits(64)
    for name in sys.argv[1:]:
        path = Path(name)
        result, stats = build(path.read_text(), seed=seed)
        path.write_text(result)
        print(f'{path.name}: {stats}')
