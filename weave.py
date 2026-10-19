"""Builds the hero's weaving pink lines: organic, looping strokes in the spirit of the Downtown Kalamazoo squiggle pattern."""
import math, random

W, H = 1600, 760


def turtle(rng, x, y, ang, n=150, step=34):
    pts = [(x, y)]
    curv, left = 0.0, 0
    for _ in range(n):
        if left <= 0:
            r = rng.random()
            if r < .55:
                curv, left = rng.uniform(-.05, .05), rng.randint(4, 8)          # lazy drift
            elif r < .87:
                curv, left = rng.choice([-1, 1]) * rng.uniform(.25, .4), rng.randint(3, 5)  # a turn
            else:
                curv, left = rng.choice([-1, 1]) * rng.uniform(.38, .46), rng.randint(14, 16)  # a loop
        # steer back toward the canvas when wandering off
        cx, cy = W / 2 - x, H / 2 - y
        if len(pts) < 45 and (x < -60 or x > W + 60 or y < -60 or y > H + 60):
            target = math.atan2(cy, cx)
            diff = (target - ang + math.pi) % (2 * math.pi) - math.pi
            ang += max(-.35, min(.35, diff))
        ang += curv
        left -= 1
        x += math.cos(ang) * step
        y += math.sin(ang) * step
        pts.append((x, y))
        if len(pts) > 45 and (x < -90 or x > W + 90 or y < -90 or y > H + 90):
            break
    return pts


def smooth(pts):
    d = [f'M{pts[0][0]:.0f} {pts[0][1]:.0f}']
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f'C{c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} {p2[0]:.0f} {p2[1]:.0f}')
    return ''.join(d)


def weave_svg(seed=7):
    rng = random.Random(seed)
    starts = [(-40, 170, 0.15), (W + 40, 120, math.pi - .1), (420, H + 40, -math.pi / 2 + .2),
              (1200, -40, math.pi / 2 + .1), (-40, 620, -0.25), (W + 40, 600, math.pi + .25)]
    groups = {0: [], 1: []}
    for i, (x, y, a) in enumerate(starts):
        d = smooth(turtle(rng, x, y, a))
        groups[i % 2].append(f'<path d="{d}" pathLength="1" style="--i:{i}"/>')
    g = ''.join(f'<g class="drift drift-{k}">{"".join(v)}</g>' for k, v in groups.items())
    return (f'<svg class="weave" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
            f'<g fill="none" stroke="#f5b8d1" stroke-width="36" stroke-linecap="round" stroke-linejoin="round">{g}</g></svg>')


if __name__ == '__main__':
    s = weave_svg()
    print(len(s))
    open('/tmp/claude-0/-home-claude/b6957ddf-dd05-5f0b-a592-5a298989a4a1/scratchpad/weave.svg', 'w').write(
        s.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" style="background:#38a669" ', 1))
