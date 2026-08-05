#!/usr/bin/env python3
"""Reconstruct nectar-mockup.png as a clean SVG by measurement + fitting."""
import math, json

W = H = 1024
data = open('original.rgb', 'rb').read()

def px(x, y):
    i = (y * W + x) * 3
    return data[i], data[i+1], data[i+2]

def is_white(c, thr=225):
    return c[0] > thr and c[1] > thr and c[2] > thr

def whiteness(x, y):
    r, g, b = px(x, y)
    return min(1.0, max(0.0, (min(r, g, b) - 140) / 100.0))

# ---------- constants from trace ----------
XL   = 309.85   # left edge of left stem
XRS  = 416.38   # right edge of left stem
XLS  = 605.55   # left edge of right stem
XR   = 712.42   # right edge of right stem

# ---------- seam refinement ----------
def refine_seam(xs, prior, lo=-14, hi=14, mode='edge'):
    """for each x: mode 'edge' = max vertical color gradient; 'trough' = darkness minimum"""
    pts = []
    for x in xs:
        y0 = int(round(prior(x)))
        best, besty = -1, None
        resp = {}
        for y in range(y0 + lo, y0 + hi):
            if mode == 'trough':
                c = px(x, y)
                if is_white(c, 200): continue
                d = 765 - (c[0] + c[1] + c[2])
            else:
                a, b = px(x, y - 2), px(x, y + 2)
                if is_white(a, 200) or is_white(b, 200):
                    continue
                d = abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])
            resp[y] = d
            if d > best:
                best, besty = d, y
        if besty is None or (mode == 'edge' and best < 45):
            continue
        # parabolic subpixel refine
        dm = resp.get(besty - 1, best); dp = resp.get(besty + 1, best)
        denom = (dm - 2 * best + dp)
        off = 0.5 * (dm - dp) / denom if denom != 0 else 0
        off = max(-1, min(1, off))
        pts.append((x, besty + off))
    return pts

def polyfit(pts, deg):
    # least squares polynomial y(x)
    n = deg + 1
    A = [[0.0]*n for _ in range(n)]
    B = [0.0]*n
    for x, y in pts:
        xs = [x**i for i in range(2*n-1)]
        for i in range(n):
            B[i] += y * xs[i]
            for j in range(n):
                A[i][j] += xs[i+j]
    # gaussian elim
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(A[r][i]))
        A[i], A[p] = A[p], A[i]; B[i], B[p] = B[p], B[i]
        for r in range(i+1, n):
            f = A[r][i] / A[i][i]
            for c in range(i, n):
                A[r][c] -= f * A[i][c]
            B[r] -= f * B[i]
    coef = [0.0]*n
    for i in range(n-1, -1, -1):
        s = B[i] - sum(A[i][j]*coef[j] for j in range(i+1, n))
        coef[i] = s / A[i][i]
    return coef  # y = sum coef[i] x^i

def peval(coef, x):
    return sum(c * x**i for i, c in enumerate(coef))

def peval_safe(coef, x, x0, x1):
    """poly inside [x0,x1]; linear extension outside (poly extrapolation swings)"""
    if x < x0:
        y0 = peval(coef, x0); s = (peval(coef, x0+2) - y0) / 2
        return y0 + s * (x - x0)
    if x > x1:
        y1 = peval(coef, x1); s = (y1 - peval(coef, x1-2)) / 2
        return y1 + s * (x - x1)
    return peval(coef, x)

# priors from coarse detection
def priorA(x):  # arch fold seam, left
    p = [(310,429),(316,418),(322,406),(328,399),(334,394),(340,390),(346,388),(352,386),(358,386),(364,386),(370,386),(376,388),(382,391),(388,395),(394,400),(400,407),(406,415),(412,425),(417,432)]
    return interp(p, x)
def priorB(x):  # left stem second fold seam
    p = [(310,652),(322,630),(328,617),(334,604),(340,593),(346,583),(352,575),(358,567),(364,561),(370,554),(376,548),(382,543),(388,538),(394,535),(400,531),(406,527),(412,524),(417,521)]
    return interp(p, x)
def prior1(x):  # right stem: red top vs orange leaf
    p = [(606,472),(612,469),(622,463),(634,457),(646,446),(658,436),(670,422),(682,404),(694,381),(700,373),(706,367),(712,362)]
    return interp(p, x)
def prior2(x):  # orange leaf vs dark hook
    p = [(605,571),(610,577),(616,587),(628,603),(640,615),(652,617),(664,619),(676,616),(688,609),(700,597),(706,587),(712,576)]
    return interp(p, x)
def interp(p, x):
    if x <= p[0][0]: return p[0][1]
    for (x0,y0),(x1,y1) in zip(p, p[1:]):
        if x0 <= x <= x1:
            return y0 + (y1-y0)*(x-x0)/(x1-x0)
    return p[-1][1]

seams = {}
seamfits = {}
for name, prior, xr, deg, mode in [
    ('A', priorA, (312, 415), 6, 'edge'),
    ('B', priorB, (312, 415), 6, 'trough'),
    ('S1', prior1, (607, 711), 6, 'edge'),
    ('S2', prior2, (607, 711), 6, 'edge'),
]:
    # pass 1: wide window around rough prior, outlier-rejected; pass 2: tight window
    pts = refine_seam(range(xr[0], xr[1]), prior, lo=-24, hi=24, mode=mode)
    coef1 = polyfit(pts, deg)
    for cut in (6.0, 4.0):
        kept = [(x, y) for x, y in pts if abs(peval(coef1, x) - y) < cut]
        if len(kept) > 30:
            pts = kept; coef1 = polyfit(pts, deg)
    pts = refine_seam(range(xr[0], xr[1]), lambda x: peval(coef1, x), lo=-7, hi=8, mode=mode)
    coef = polyfit(pts, deg)
    for cut in (4.0, 3.0):
        kept = [(x, y) for x, y in pts if abs(peval(coef, x) - y) < cut]
        if len(kept) > 30:
            pts = kept; coef = polyfit(pts, deg)
    resid = max(abs(peval(coef, x) - y) for x, y in pts)
    seams[name] = pts
    seamfits[name] = coef
    print(f"seam {name}: {len(pts)} pts, poly deg {deg}, max resid {resid:.2f}, "
          f"ends ({xr[0]},{peval(coef,xr[0]):.1f}) ({xr[1]},{peval(coef,xr[1]):.1f})")

# ---------- contour samples ----------
def hedges(y, x0=295, x1=730):
    out = []
    prev = whiteness(x0, y)
    for x in range(x0+1, x1):
        w = whiteness(x, y)
        if (prev > .5) != (w > .5):
            t = (0.5-prev)/(w-prev) if w != prev else .5
            out.append(x-1+t)
        prev = w
    return out

def vedges(x, y0=282, y1=720):
    out = []
    prev = whiteness(x, y0)
    for y in range(y0+1, y1):
        w = whiteness(x, y)
        if (prev > .5) != (w > .5):
            t = (0.5-prev)/(w-prev) if w != prev else .5
            out.append(y-1+t)
        prev = w
    return out

# ---------- cubic fitting ----------
def fit_cubic(pts, t0, t1):
    """pts: ordered samples; endpoints fixed at pts[0], pts[-1]; unit tangents t0 (leaving start), t1 (arriving at end, i.e. direction INTO end). Solve alpha, beta >=0 least squares."""
    P0, P3 = pts[0], pts[-1]
    # chord-length parameterization
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + math.hypot(b[0]-a[0], b[1]-a[1]))
    total = d[-1]
    ts = [x / total for x in d]
    # B(t) = B0 P0 + B1 (P0 + a t0) + B2 (P3 - b t1) + B3 P3
    C11 = C12 = C22 = X1 = X2 = 0.0
    for (xp, yp), t in zip(pts, ts):
        b0 = (1-t)**3; b1 = 3*t*(1-t)**2; b2 = 3*t*t*(1-t); b3 = t**3
        base = (b0+b1)*P0[0] + (b2+b3)*P3[0], (b0+b1)*P0[1] + (b2+b3)*P3[1]
        a1 = (b1*t0[0], b1*t0[1])
        a2 = (-b2*t1[0], -b2*t1[1])
        r = (xp - base[0], yp - base[1])
        C11 += a1[0]*a1[0] + a1[1]*a1[1]
        C12 += a1[0]*a2[0] + a1[1]*a2[1]
        C22 += a2[0]*a2[0] + a2[1]*a2[1]
        X1 += r[0]*a1[0] + r[1]*a1[1]
        X2 += r[0]*a2[0] + r[1]*a2[1]
    det = C11*C22 - C12*C12
    if abs(det) < 1e-9:
        alpha = beta = total/3
    else:
        alpha = (X1*C22 - X2*C12)/det
        beta = (C11*X2 - C12*X1)/det
    if alpha <= 0: alpha = total/3
    if beta <= 0: beta = total/3
    P1 = (P0[0] + alpha*t0[0], P0[1] + alpha*t0[1])
    P2 = (P3[0] - beta*t1[0], P3[1] - beta*t1[1])
    # residual
    def B(t):
        b0=(1-t)**3; b1=3*t*(1-t)**2; b2=3*t*t*(1-t); b3=t**3
        return (b0*P0[0]+b1*P1[0]+b2*P2[0]+b3*P3[0], b0*P0[1]+b1*P1[1]+b2*P2[1]+b3*P3[1])
    err = max(min(math.hypot(B(t)[0]-xp, B(t)[1]-yp) for t in [tt/20 for tt in range(21)]) for (xp,yp) in pts[::max(1,len(pts)//15)])
    return P1, P2, err

def unit(v):
    n = math.hypot(*v)
    return (v[0]/n, v[1]/n)

# --- assemble arch samples (left edge -> apex -> shoulder -> straight) ---
arch = []
for y in range(391, 297, -1):
    e = hedges(y)
    if e: arch.append((e[0], y))
for x in range(378, 519):
    e = vedges(x)
    if e: arch.append((x, e[0]))
# keep ordered & dedup by advancing param; arch already roughly ordered (up left edge then across)
arch = [p for p in arch if p[1] < 403 or p[0] < 380 or p[0] > 370]

DIAG = 0.5122  # dx/dy of diagonal top edge
DIAG2 = 0.5233 # dx/dy of diagonal bottom edge

apex = min(arch, key=lambda p: p[1])
apex = (402.3, apex[1])
i_apex = next(i for i, p in enumerate(arch) if p[0] >= 402)
shoulder = next(p for p in arch if p[0] >= 462)
i_sh = arch.index(shoulder)
arch_end = (518.7, 402.0)
c1P1, c1P2, e1 = fit_cubic([ (XL,391.0) ] + arch[1:i_apex] + [apex], (0,-1), (1,0))
c2P1, c2P2, e2 = fit_cubic([apex] + arch[i_apex:i_sh] + [shoulder], (1,0), unit((8,6.8)))
c3P1, c3P2, e3 = fit_cubic([shoulder] + arch[i_sh:] + [arch_end], unit((8,6.8)), unit((DIAG,1)))
print(f"arch cubic errs: {e1:.2f} {e2:.2f} {e3:.2f}")

# --- top cut curve (right stem top) ---
topcut = []
for y in range(377, 293, -1):
    e = hedges(y)
    if len(e) >= 2: topcut.append((e[-2], y))
for x in range(678, 710):
    e = vedges(x)
    if e: topcut.append((x, e[0]))
tc_start = (XLS, 378.0)
tc_knee = next(p for p in topcut if p[0] >= 641)
i_knee = topcut.index(tc_knee)
tc_end = (709.0, 289.62)
t_knee = unit((641.57-628.38, -8))  # local direction at knee going up-right
t1P1, t1P2, te1 = fit_cubic([tc_start] + topcut[:i_knee] + [tc_knee], (0,-1), t_knee)
t2P1, t2P2, te2 = fit_cubic([tc_knee] + topcut[i_knee:] + [tc_end], t_knee, (1,0))
print(f"topcut cubic errs: {te1:.2f} {te2:.2f}")

# --- hook (bottom right big curve), right edge -> bottom apex -> straight ---
hook = []
for y in range(614, 711):
    e = hedges(y)
    if e: hook.append((e[-1], y))
for x in range(709, 605, -1):
    e = vedges(x)
    if e: hook.append((x, e[-1]))
for y in range(710, 649, -1):
    e = hedges(y)
    if len(e) >= 3 or (len(e) == 2 and y > 566):
        # lower-left edge of diagonal = third-from-last crossing region; take e[-2] when the tip run exists
        pass
# simpler: lower-left diagonal edge from hedges index 2 (after stem edges) for y 650..709
low = []
for y in range(709, 649, -1):
    e = hedges(y)
    if len(e) >= 2:
        # candidates between 500 and 640
        cands = [xx for xx in e if 500 < xx < 645]
        if cands: low.append((cands[0], y))
hook_start = (XR, 613.4)
bapex = (620.3, 710.35)
h_sh = (560.5, 688.8)  # mirror of shoulder
seg1 = [p for p in hook if p[1] > 616 and p[0] > 623]
seg1 = sorted(set(seg1), key=lambda p: math.atan2(p[1]-613, p[0]-620))
h1P1, h1P2, he1 = fit_cubic([hook_start] + seg1 + [bapex], (0,1), (-1,0))
# hook part2: apex -> h_sh ; part3: h_sh -> straight end
seg2 = [bapex] + [p for p in low if p[0] < 620 and p[0] >= 560]
seg2 = [seg2[0]] + sorted(seg2[1:], key=lambda p: -p[0])
h2P1, h2P2, he2 = fit_cubic(seg2 + [h_sh], (-1,0), unit((-8,-6.8)))
hook_endS = (503.6, 602.4)
seg3 = [h_sh] + sorted([p for p in low if 504 < p[0] < 560], key=lambda p: -p[0]) + [hook_endS]
h3P1, h3P2, he3 = fit_cubic(seg3, unit((-8,-6.8)), unit((-DIAG2,-1)))
print(f"hook cubic errs: {he1:.2f} {he2:.2f} {he3:.2f}")

# --- bottom cut (left stem bottom) ---
bot = []
for y in range(620, 711):
    e = hedges(y)
    if len(e) >= 2:
        cands = [xx for xx in e if 320 < xx < 418]
        if cands: bot.append((cands[-1], y))
for x in range(345, 312, -1):
    e = vedges(x)
    if e: bot.append((x, e[-1]))
bc_start = (XRS, 618.0)
bc_knee = next(p for p in bot if p[0] <= 384)
i_bknee = bot.index(bc_knee)
bc_end = (313.2, 714.62)
b_knee = unit((-13.19, 8))
b1P1, b1P2, be1 = fit_cubic([bc_start] + bot[:i_bknee] + [bc_knee], (0,1), b_knee)
b2P1, b2P2, be2 = fit_cubic([bc_knee] + bot[i_bknee:] + [bc_end], b_knee, (-1,0))
print(f"botcut cubic errs: {be1:.2f} {be2:.2f}")

# cusps
cuspL = (XRS, 432.3)
cuspR = (XLS + 0.05, 572.3)

def fmt(*vals):
    return ' '.join(f"{v:.2f}" for v in vals)

def C(P1, P2, P3):
    return f"C {fmt(P1[0],P1[1])} {fmt(P2[0],P2[1])} {fmt(P3[0],P3[1])}"

# ---------- outer path ----------
outer = ' '.join([
    f"M {fmt(XL, 703)}",
    f"L {fmt(XL, 391)}",
    C(c1P1, c1P2, apex),
    C(c2P1, c2P2, shoulder),
    C(c3P1, c3P2, arch_end),
    f"L {fmt(cuspR[0], cuspR[1])}",          # diagonal top edge into right cusp
    f"L {fmt(XLS, 378)}",                     # up right stem left edge
    C(t1P1, t1P2, tc_knee),
    C(t2P1, t2P2, tc_end),
    f"Q {fmt(XR, 289.6)} {fmt(XR, 293.6)}",  # top-right corner
    f"L {fmt(XR, 613.4)}",                    # down right edge
    C(h1P1, h1P2, bapex),
    C(h2P1, h2P2, h_sh),
    C(h3P1, h3P2, hook_endS),
    f"L {fmt(cuspL[0], cuspL[1])}",           # diagonal bottom edge into left cusp
    f"L {fmt(XRS, 618)}",                     # down left stem right edge
    C(b1P1, b1P2, bc_knee),
    C(b2P1, b2P2, bc_end),
    f"Q {fmt(XL, 714.7)} {fmt(XL, 710.6)}",  # bottom-left corner
    "Z",
])

# ---------- seam paths (as dense fitted polylines -> cubics) ----------
def seam_curve(name, x0, x1, rev=False):
    pts = [(x, seameval(name, x)) for x in [x0 + (x1-x0)*i/40 for i in range(41)]]
    if rev: pts = pts[::-1]
    # fit two cubics
    mid = len(pts)//2
    tA = unit((pts[1][0]-pts[0][0], pts[1][1]-pts[0][1]))
    tM = unit((pts[mid+1][0]-pts[mid-1][0], pts[mid+1][1]-pts[mid-1][1]))
    tB = unit((pts[-1][0]-pts[-2][0], pts[-1][1]-pts[-2][1]))
    P1a, P2a, _ = fit_cubic(pts[:mid+1], tA, tM)
    P1b, P2b, _ = fit_cubic(pts[mid:], tM, tB)
    return pts[0], C(P1a, P2a, pts[mid]) + ' ' + C(P1b, P2b, pts[-1])

SEAM_RANGE = {'A': (313, 414), 'B': (313, 414), 'S1': (608, 710), 'S2': (608, 710)}
def seameval(name, x):
    r = SEAM_RANGE[name]
    return peval_safe(seamfits[name], x, r[0], r[1])

# region overlays (will be clipped by outer path); overshoot beyond edges
sA0, sA_d = seam_curve('A', 306, XRS)          # left->right, ends at stem edge
sB0r, sB_dr = seam_curve('B', 306, XRS)
s10, s1_d = seam_curve('S1', XLS, 716)

yA_left = seameval('A', 306); yA_right = seameval('A', XRS)
yB_left = seameval('B', 306); yB_right = seameval('B', XRS)
y1_left = seameval('S1', XLS); y1_right = seameval('S1', 716)
y2_left = seameval('S2', XLS-1); y2_right = seameval('S2', 716)

# band1: seamA top, stem edge right, seamB bottom, left edge
band1 = (f"M {fmt(306, yA_left)} {sA_d} "                  # along seam A to stem edge
         f"L {fmt(XRS+2, yA_right)} L {fmt(XRS+2, yB_right)} ")  # down along (overshoot right)
# then seam B right->left: need reversed curve
_, sB_rev = seam_curve('B', XRS+0.0, 306)
band1 += f"{sB_rev} L {fmt(306, yA_left)} Z"

band2 = (f"M {fmt(306, yB_left)} {sB_dr} "                 # seam B left->right
         f"L {fmt(XRS+2, yB_right)} L {fmt(XRS+2, 720)} L {fmt(306, 720)} Z")

stemtop = (f"M {fmt(XLS-2, y1_left)} {s1_d} "              # seam1 left->right
           f"L {fmt(716, y1_right)} L {fmt(716, 285)} L {fmt(XLS-2, 285)} Z")

_, s2_rev = seam_curve('S2', 716, XLS-1)
leaf = (f"M {fmt(XLS-2, y1_left)} {s1_d} L {fmt(716, y2_right)} "
        f"{s2_rev} L {fmt(XLS-2, y1_left)} Z")

# ---------- region masks for gradient fitting ----------
def region_of(x, y):
    c = px(x, y)
    if is_white(c, 215): return None
    # near-boundary exclusion
    if whiteness(x, y) > 0.02: return None
    for dx, dy in ((4,0),(-4,0),(0,4),(0,-4),(3,3),(-3,3),(3,-3),(-3,-3)):
        if is_white(px(min(W-1,max(0,x+dx)), min(H-1,max(0,y+dy))), 215):
            return None
    if x <= XRS + 1:
        a = seameval('A', x); b = seameval('B', x)
        if y < a - 4: return 'face'
        if a + 4 < y < b - 4: return 'band1'
        if y > b + 4: return 'band2'
        return None
    if x >= XLS - 1:
        s1 = seameval('S1', x); s2 = seameval('S2', x)
        if y < s1 - 4: return 'stemtop'
        if s1 + 4 < y < s2 - 4: return 'leaf'
        if y > s2 + 4: return 'hook'
        return None
    return 'face'

# --- leaf brightness ridge (the leaf gradient reverses across it) ---
ridge_pts = []
for x in range(620, 709, 2):
    y0 = int(seameval('S1', x)) + 8
    y1 = int(seameval('S2', x)) - 8
    if y1 - y0 < 12: continue
    gs = {y: px(x, y)[1] for y in range(y0, y1)}
    ybest = max(gs, key=gs.get)
    if ybest <= y0 + 1 or ybest >= y1 - 2: continue
    dm, d0, dp = gs.get(ybest-1, gs[ybest]), gs[ybest], gs.get(ybest+1, gs[ybest])
    den = dm - 2*d0 + dp
    off = 0.5*(dm - dp)/den if den else 0
    ridge_pts.append((x, ybest + max(-1, min(1, off))))
ridge_coef = polyfit(ridge_pts, 2)
seamfits['R'] = ridge_coef
SEAM_RANGE['R'] = (622, 707)
# where the ridge meets seam1 (left of that, the leaf is single-gradient)
xcross = 616
for xx in range(700, 606, -1):
    if seameval('R', xx) <= seameval('S1', xx) + 2:
        xcross = xx; break
print(f"ridge: {len(ridge_pts)} pts, meets seam1 at x={xcross}")

samples = {'face': [], 'band1': [], 'band2': [], 'stemtop': [], 'leafL': [], 'leafU': [], 'hook': []}
for y in range(288, 716, 2):
    for x in range(306, 716, 2):
        r = region_of(x, y)
        if r == 'leaf':
            if x > xcross + 4 and y < seameval('R', x) - 3:
                r = 'leafU'
            elif abs(y - seameval('R', x)) <= 3 and x > xcross + 4:
                r = None
            else:
                r = 'leafL'
        if r: samples[r].append((x, y, px(x, y)))

def _binned(projs, cols, nbins):
    pmin, pmax = min(projs), max(projs)
    span = pmax - pmin or 1
    bins = [[0.0,0.0,0.0,0] for _ in range(nbins)]
    for p, c in zip(projs, cols):
        b = min(nbins-1, int((p-pmin)/span*nbins))
        bins[b][0]+=c[0]; bins[b][1]+=c[1]; bins[b][2]+=c[2]; bins[b][3]+=1
    means = [(b[0]/b[3], b[1]/b[3], b[2]/b[3]) if b[3] else None for b in bins]
    sse = 0.0
    for p, c in zip(projs, cols):
        b = min(nbins-1, int((p-pmin)/span*nbins))
        m = means[b]
        if m: sse += (c[0]-m[0])**2 + (c[1]-m[1])**2 + (c[2]-m[2])**2
    return sse, pmin, pmax, means

def fit_gradient(sam, nbins=12):
    """search linear angles AND radial centers; return ('lin',deg,...) or ('rad',cx,cy,...) spec"""
    sub = sam[::3] if len(sam) > 6000 else sam
    cols = [c for _, _, c in sub]
    best = None
    for deg in range(0, 180, 2):
        th = math.radians(deg)
        cth, sth = math.cos(th), math.sin(th)
        sse, pmin, pmax, _ = _binned([x*cth + y*sth for x, y, _ in sub], cols, nbins)
        if best is None or sse < best[0]:
            best = (sse, ('lin', deg))
    xs = [x for x, _, _ in sub]; ys = [y for _, y, _ in sub]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    for ccx in range(int(x0-200), int(x1+201), 25):
        for ccy in range(int(y0-200), int(y1+201), 25):
            if x0-20 < ccx < x1+20 and y0-20 < ccy < y1+20:
                continue  # center inside region -> degenerate circles
            sse, pmin, pmax, _ = _binned([math.hypot(x-ccx, y-ccy) for x, y, _ in sub], cols, nbins)
            if sse < best[0]:
                best = (sse, ('rad', ccx, ccy))
    _, spec = best
    # final stops from ALL samples
    cols = [c for _, _, c in sam]
    if spec[0] == 'lin':
        th = math.radians(spec[1])
        cth, sth = math.cos(th), math.sin(th)
        projs = [x*cth + y*sth for x, y, _ in sam]
    else:
        projs = [math.hypot(x-spec[1], y-spec[2]) for x, y, _ in sam]
    sse, pmin, pmax, means = _binned(projs, cols, nbins)
    rms = math.sqrt(sse / max(1, len(sam)) / 3)
    return spec + (pmin, pmax, means), rms

def grad_eval(g, x, y):
    """evaluate a fitted gradient the way SVG will render it (interp between stop centers)"""
    deg, pmin, pmax, means = g
    th = math.radians(deg)
    p = (x*math.cos(th) + y*math.sin(th) - pmin) / (pmax - pmin)
    n = len(means)
    centers = [(i+0.5)/n for i in range(n)]
    valid = [(c, m) for c, m in zip(centers, means) if m is not None]
    if p <= valid[0][0]: return valid[0][1]
    if p >= valid[-1][0]: return valid[-1][1]
    for (c0, m0), (c1, m1) in zip(valid, valid[1:]):
        if c0 <= p <= c1:
            t = (p-c0)/(c1-c0)
            return tuple(m0[i] + t*(m1[i]-m0[i]) for i in range(3))
    return valid[-1][1]

def profile_eval(p, stops):
    """p in [0,1] over the binned span; piecewise-linear between bin-center stops"""
    n = len(stops)
    centers = [(i+0.5)/n for i in range(n)]
    valid = [(c, m) for c, m in zip(centers, stops) if m is not None]
    if not valid: return (0, 0, 0)
    if p <= valid[0][0]: return valid[0][1]
    if p >= valid[-1][0]: return valid[-1][1]
    for (c0, m0), (c1, m1) in zip(valid, valid[1:]):
        if c0 <= p <= c1:
            t = (p-c0)/(c1-c0)
            return tuple(m0[i] + t*(m1[i]-m0[i]) for i in range(3))
    return valid[-1][1]

def fit_residual_overlay(sam, pred, alpha=0.55, nbins=16):
    """fit rgba overlay (linear over angles OR radial over centers) minimizing residual"""
    res = [(x, y, (c[0]-p[0], c[1]-p[1], c[2]-p[2])) for (x, y, c), p in zip(sam, pred)]
    xs = [x for x, y, _ in res]; ys = [y for x, y, _ in res]
    def binned_sse(projs):
        pmin, pmax = min(projs), max(projs)
        span = pmax - pmin or 1
        bins = [[0.0]*3 + [0] for _ in range(nbins)]
        for (x, y, r), p in zip(res, projs):
            b = min(nbins-1, int((p-pmin)/span*nbins))
            for i in range(3): bins[b][i] += r[i]
            bins[b][3] += 1
        means = [tuple(b[i]/b[3] for i in range(3)) if b[3] else None for b in bins]
        sse = 0.0
        for (x, y, r), p in zip(res, projs):
            b = min(nbins-1, int((p-pmin)/span*nbins))
            m = means[b] or (0,0,0)
            sse += sum((r[i]-m[i])**2 for i in range(3))
        return sse, pmin, pmax, means
    best = None
    for deg in range(0, 180, 3):
        th = math.radians(deg)
        cth, sth = math.cos(th), math.sin(th)
        sse, pmin, pmax, means = binned_sse([x*cth + y*sth for x, y, _ in res])
        if best is None or sse < best[0]:
            best = (sse, ('lin', deg, pmin, pmax), means)
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    for cx in range(int(x0-120), int(x1+121), 30):
        for cy in range(int(y0-120), int(y1+121), 30):
            sse, pmin, pmax, means = binned_sse([math.hypot(x-cx, y-cy) for x, y, _ in res])
            if sse < best[0]:
                best = (sse, ('rad', cx, cy, pmin, pmax), means)
    _, spec, rmeans = best
    # base color per bin -> stop colors o = base + res/alpha
    if spec[0] == 'lin':
        _, deg, pmin, pmax = spec
        th = math.radians(deg)
        proj = lambda x, y: x*math.cos(th) + y*math.sin(th)
    else:
        _, ccx, ccy, pmin, pmax = spec
        proj = lambda x, y: math.hypot(x-ccx, y-ccy)
    span = pmax - pmin or 1
    basebins = [[0.0]*3 + [0] for _ in range(nbins)]
    for (x, y, c), p in zip(sam, pred):
        b = min(nbins-1, int((proj(x, y)-pmin)/span*nbins))
        for i in range(3): basebins[b][i] += p[i]
        basebins[b][3] += 1
    stops = []
    for i in range(nbins):
        if rmeans[i] is None or not basebins[i][3]:
            stops.append(None); continue
        base = [basebins[i][j]/basebins[i][3] for j in range(3)]
        stops.append(tuple(max(0, min(255, base[j] + rmeans[i][j]/alpha)) for j in range(3)))
    g = spec + (stops,)   # ('lin', deg, pmin, pmax, stops) or ('rad', cx, cy, pmin, pmax, stops)
    ev = lambda x, y: profile_eval((proj(x, y) - pmin) / span, stops)
    newpred = []
    for (x, y, c), p in zip(sam, pred):
        o = ev(x, y)
        newpred.append(tuple((1-alpha)*p[i] + alpha*o[i] for i in range(3)))
    return g, newpred

def rms_of(sam, pred):
    sse = sum(sum((c[i]-p[i])**2 for i in range(3)) for (_, _, c), p in zip(sam, pred))
    return math.sqrt(sse / max(1, len(sam)) / 3)

grads = {}
for name, sam in samples.items():
    g, rms = fit_gradient(sam, nbins=24)
    grads[name] = g
    print(f"gradient {name}: {len(sam)} px, {g[0]} {g[1:3] if g[0]=='rad' else g[1]}, rms {rms:.1f}")

def gradient_def(gid, g):
    """g = ('lin', deg, pmin, pmax, means) or ('rad', cx, cy, pmin, pmax, means)"""
    kind = g[0]
    means = g[-1]
    n = len(means)
    if kind == 'lin':
        _, deg, pmin, pmax, _ = g
        th = math.radians(deg)
        cth, sth = math.cos(th), math.sin(th)
        stops = ''.join(
            f'<stop offset="{(i+0.5)/n:.4f}" stop-color="rgb({m[0]:.0f},{m[1]:.0f},{m[2]:.0f})"/>'
            for i, m in enumerate(means) if m is not None)
        return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
                f'x1="{pmin*cth:.1f}" y1="{pmin*sth:.1f}" x2="{pmax*cth:.1f}" y2="{pmax*sth:.1f}">{stops}</linearGradient>')
    _, ccx, ccy, pmin, pmax, _ = g
    stops = ''.join(
        f'<stop offset="{(pmin + (i+0.5)/n*(pmax-pmin))/pmax:.4f}" stop-color="rgb({m[0]:.0f},{m[1]:.0f},{m[2]:.0f})"/>'
        for i, m in enumerate(means) if m is not None)
    return (f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" '
            f'cx="{ccx}" cy="{ccy}" r="{pmax:.1f}">{stops}</radialGradient>')

# leafU: between seam1 and the ridge, from xcross rightward (painted over leafL)
_, s1_part = seam_curve('S1', xcross, 716)
_, ridge_rev = seam_curve('R', 716, xcross)
leafU = (f"M {fmt(xcross, seameval('S1', xcross))} {s1_part} "
         f"L {fmt(716, seameval('R', 716))} {ridge_rev} Z")

# hook: right-stem/diagonal area below seam2 (fold shadow, painted over face)
_, s2_fwd = seam_curve('S2', XLS-1, 716)
hookp = (f"M {fmt(XLS-1, y2_left)} {s2_fwd} "
         f"L {fmt(716, 725)} L {fmt(XLS-1, 725)} Z")

region_paths = [('face', outer), ('hook', hookp), ('band1', band1), ('band2', band2),
                ('stemtop', stemtop), ('leafL', leaf), ('leafU', leafU)]

# --- fold crease strokes: the original paints a ~3px darker line along the fold seams ---
def crease(name, x0, x1, nb=10):
    start, d = seam_curve(name, x0, x1)
    cols = []
    for i in range(nb):
        xa = x0 + (x1-x0)*(i+0.5)/nb
        ys = seameval(name, xa)
        cs = [px(int(xa), int(ys)+dy) for dy in (0, 1, 2)]
        cols.append(tuple(sum(c[j] for c in cs)/3 for j in range(3)))
    stops = ''.join(
        f'<stop offset="{(i+0.5)/nb:.3f}" stop-color="rgb({m[0]:.0f},{m[1]:.0f},{m[2]:.0f})"/>'
        for i, m in enumerate(cols))
    gid = f'crease_{name}'
    gdef = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
            f'x1="{x0}" y1="0" x2="{x1}" y2="0">{stops}</linearGradient>')
    path = (f'<path d="M {fmt(x0, seameval(name, x0))} {d}" transform="translate(0,1)" '
            f'fill="none" stroke="url(#{gid})" stroke-width="3" stroke-linecap="round"/>')
    return gdef, path

crease_defs, crease_paths = [], []
for cn, cx0, cx1 in [('S2', XLS+3, 710.5), ('B', 311.5, XRS-3)]:
    gd, cp = crease(cn, cx0, cx1)
    crease_defs.append(gd); crease_paths.append(cp)

# --- cusp shadows: soft dark feathering where the diagonal tucks behind each stem ---
cusp_defs = f'''
<radialGradient id="cuspR" gradientUnits="userSpaceOnUse" cx="{cuspR[0]:.1f}" cy="{cuspR[1]:.1f}" r="46">
  <stop offset="0" stop-color="rgb(150,5,14)" stop-opacity="0.5"/>
  <stop offset="0.45" stop-color="rgb(160,10,18)" stop-opacity="0.25"/>
  <stop offset="1" stop-color="rgb(170,15,22)" stop-opacity="0"/>
</radialGradient>
<radialGradient id="cuspL" gradientUnits="userSpaceOnUse" cx="{cuspL[0]:.1f}" cy="{cuspL[1]:.1f}" r="46">
  <stop offset="0" stop-color="rgb(150,5,14)" stop-opacity="0.5"/>
  <stop offset="0.45" stop-color="rgb(160,10,18)" stop-opacity="0.25"/>
  <stop offset="1" stop-color="rgb(170,15,22)" stop-opacity="0"/>
</radialGradient>'''
cusp_paths = (f'<circle cx="{cuspR[0]:.1f}" cy="{cuspR[1]:.1f}" r="46" fill="url(#cuspR)"/>'
              f'<circle cx="{cuspL[0]:.1f}" cy="{cuspL[1]:.1f}" r="46" fill="url(#cuspL)"/>')
defs = []
body = []
for name, d in region_paths:
    gid = 'g_' + name
    defs.append(gradient_def(gid, grads[name]))
    body.append(f'<path d="{d}" fill="url(#{gid})"/>')
defs.extend(crease_defs)
body.extend(crease_paths)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
  <defs>
    {''.join(defs)}
    <clipPath id="mark"><path d="{outer}"/></clipPath>
  </defs>
  <path d="{outer}" fill="url(#g_face)"/>
  <g clip-path="url(#mark)">
    {''.join(body)}
  </g>
</svg>
'''
open('nectar-n.svg', 'w').write(svg)
print("wrote nectar-n.svg")
