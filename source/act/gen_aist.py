"""Original ACT-style Math items modelled on the topics and difficulty of the ACT International Subject Test (AIST) Math 1:
geometry (triangles, similarity, special right triangles, circles, polygons, solids, cross-sections, transformations, logic),
coordinate geometry, algebra, functions, sequences, statistics and multi-step word problems.
Every answer is computed exactly; every item has step-by-step reasoning. Correct choice first (the build shuffles).
Usage: python3 source/act/gen_aist.py  -> source/act/aist_math.json"""
import json, os, random, math
from fractions import Fraction as F

M = "−"
def n(v):
    v = F(v); s = str(abs(v.numerator)) if v.denominator == 1 else f"{abs(v.numerator)}/{v.denominator}"
    return (M if v < 0 else "") + s
def d1(x, k=1): return f"{x:.{k}f}"
def pt(x, y): return f"({n(x)}, {n(y)})"
def uniq(c, wrongs):
    out = [c]
    for w in wrongs:
        if w not in out: out.append(w)
        if len(out) == 4: return out
    return None
def sq(k):  # simplified radical sqrt(k)
    a, b = 1, k
    for f in range(int(math.isqrt(k)), 1, -1):
        if k % (f * f) == 0: a, b = f, k // (f * f); break
    if b == 1: return str(a)
    return ("" if a == 1 else str(a)) + "√" + str(b)

# ---------------- SVG figures (inherit text colour, so they work in light and dark themes)
def svg(body, w=300, h=190):
    return f'<svg viewBox="0 0 {w} {h}" class="qsvg" role="img" aria-label="Figure"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">{body}</g></svg>'
def T(x, y, s, a="middle"): return f'<text x="{x}" y="{y}" text-anchor="{a}" fill="currentColor" stroke="none" font-size="13" font-family="inherit">{s}</text>'
def fig_trap():
    return svg('<path d="M60 40 L220 40 L270 160 L30 160 Z"/><path d="M60 40 L270 160 M220 40 L30 160"/>' + T(56, 32, "A") + T(224, 32, "B") + T(276, 176, "C") + T(24, 176, "D") + T(143, 92, "E"))
def fig_right(lbl_hyp, lbl_opp, lbl_adj, ang):
    return svg('<path d="M40 160 L260 160 L260 40 Z"/><path d="M248 160 L248 148 L260 148"/><path d="M78 160 A38 38 0 0 0 74 145"/>' +
               T(150, 92, lbl_hyp) + T(276, 104, lbl_opp, "start") + T(150, 180, lbl_adj) + T(92, 152, ang, "start"))
def fig_inscribed_circle_tri():
    return svg('<path d="M150 20 L270 175 L30 175 Z"/><circle cx="150" cy="123" r="52"/><path d="M150 123 L150 175"/>' + T(160, 152, "r", "start"))

# ---------------- generators: (function, ACT category, difficulty range)
def trapezoid(r, d):
    ec = r.choice([5, 6, 7, 8, 9]); ae = r.choice([x for x in range(3, 13) if x != ec]); k = F(r.choice([3, 4, 5, 6]), 2)
    cd = ec * k; ab = ae * k; ac = ae + ec
    return dict(stem=f"In trapezoid ABCD shown, AB ∥ CD and the diagonals meet at E. If AE = {ae}, AC = {ac}, and CD = {n(cd)}, what is the length of AB?",
        svg=fig_trap(), choices=uniq(n(ab), [n(cd * F(ec, ae)), n(ac - cd if ac > cd else cd - ae), n(cd - ae + ec), n(ab + 1)]),
        steps=[f"Because AB ∥ CD, triangles ABE and CDE are similar (alternate interior angles are equal).", f"EC = AC − AE = {ac} − {ae} = {ec}.",
               f"Corresponding sides are proportional: AB/CD = AE/EC, so AB/{n(cd)} = {ae}/{ec}.", f"AB = {n(cd)} × {ae}/{ec} = {n(ab)}."],
        key="Parallel sides in a trapezoid create similar triangles at the intersection of the diagonals.")
def obtuse(r, d):
    kind = r.choice(["obtuse", "acute", "right"])
    def cls(a, b, c):
        a, b, c = sorted((a, b, c)); s = a * a + b * b - c * c
        return None if a + b <= c else ("right" if s == 0 else "acute" if s > 0 else "obtuse")
    sets = {"right": [(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17), (7, 24, 25), (9, 12, 15)], "acute": [(4, 5, 6), (5, 6, 7), (6, 8, 9), (7, 8, 9), (3, 4, 4), (5, 5, 6)],
            "obtuse": [(6, 7, 12), (4, 5, 7), (5, 6, 9), (3, 5, 7), (7, 9, 13), (4, 6, 8)]}
    good = r.choice(sets[kind]); others = [s for k in sets if k != kind for s in sets[k]]; r.shuffle(others)
    fmt = lambda s: ", ".join(str(x) for x in s)
    a, b, c = good
    return dict(stem=f"Which set of side lengths, in inches, could be the sides of a {'n' if kind[0] in 'aeiou' else ''} {kind} triangle?".replace("a n ", "an ").replace("a  ", "a "),
        choices=uniq(fmt(good), [fmt(o) for o in others[:3]]), steps=[f"Compare a² + b² with c², where c is the longest side.",
        "a² + b² > c² → acute; a² + b² = c² → right; a² + b² < c² → obtuse (and a + b > c so a triangle exists).",
        f"For {fmt(good)}: {a}² + {b}² = {a*a+b*b} and {c}² = {c*c}, so the triangle is {kind}."],
        key="Classify triangles by comparing a² + b² with c².")
def perim_possible(r, d):
    a, b = r.randint(2, 9), r.randint(5, 14)
    lo, hi = a + b + abs(a - b), 2 * (a + b)  # perimeter strictly between
    good = r.randint(lo + 1, hi - 1); wrong = [lo, hi, hi + r.randint(1, 4), max(1, lo - r.randint(1, 3))]
    return dict(stem=f"Two sides of a triangle have lengths {a} and {b}. Which of the following could be the perimeter of the triangle?",
        choices=uniq(str(good), [str(w) for w in wrong]), steps=[f"Triangle inequality: the third side c satisfies {abs(a-b)} < c < {a+b}.",
        f"So the perimeter {a} + {b} + c is between {lo} and {hi}, not including either end.", f"Only {good} lies strictly between {lo} and {hi}."],
        key="The third side is between the difference and the sum of the other two sides.")
def int_triangle(r, d):
    P, s = r.choice([(30, 7), (24, 5), (28, 6), (32, 8), (36, 9), (26, 6)])
    longs = set()
    for x in range(s, P):
        y = P - s - x
        if y < x or x < s: continue
        if s + x > y: longs.add(y)
    v = len(longs)
    return dict(stem=f"A triangle has a perimeter of {P} cm. All three sides are whole numbers of centimeters, and the shortest side is {s} cm. How many different lengths are possible for the longest side?",
        choices=uniq(str(v), [str(v + 1), str(max(1, v - 1)), str(v + 2)]),
        steps=[f"The other two sides add to {P} − {s} = {P - s}.", f"Let the longest side be L. Then the middle side is {P - s} − L, which must be at least {s} and at most L.",
               f"Triangle inequality: {s} + ({P - s} − L) > L.", f"Checking the whole numbers, the possible longest sides are {', '.join(str(x) for x in sorted(longs))}: {v} lengths."],
        key="List the cases systematically and test the triangle inequality.")
def special(r, d):
    t = r.choice(["30", "45"]); k = r.randint(2, 12)
    if t == "30":
        h = 2 * k; which = r.choice(["short", "long"]); v = str(k) if which == "short" else sq(3 * k * k)
        return dict(stem=f"In a right triangle, one acute angle measures 30° and the hypotenuse is {h} units long. What is the length of the leg {'opposite' if which == 'short' else 'adjacent to'} the 30° angle?",
            svg=fig_right(str(h), "?", "", "30°") if which == "short" else fig_right(str(h), "", "?", "30°"),
            choices=uniq(v, [sq(3 * k * k) if which == "short" else str(k), sq(2 * k * k), str(h // 2 + 1) if which == "short" else str(2 * h)]),
            steps=["In a 30°-60°-90° triangle the sides are in the ratio x : x√3 : 2x.", f"The hypotenuse 2x = {h}, so x = {k}.",
                   f"The leg opposite 30° is x = {k}; the leg adjacent to 30° is x√3 = {sq(3*k*k)}.", f"Answer: {v}."], key="30-60-90: x, x√3, 2x.")
    leg = k
    return dict(stem=f"An isosceles right triangle has legs of length {leg}. What is the length of its hypotenuse?",
        choices=uniq(sq(2 * leg * leg), [str(2 * leg), sq(3 * leg * leg), str(leg)]),
        steps=["In a 45°-45°-90° triangle the sides are in the ratio x : x : x√2.", f"x = {leg}, so the hypotenuse is {leg}√2 = {sq(2*leg*leg)}."], key="45-45-90: x, x, x√2.")
def ramp(r, d):
    L = r.choice([20, 24, 30, 36, 40, 50, 60]); a = r.choice([18, 22, 25, 28, 32, 35, 40])
    h = L * math.sin(math.radians(a)); wrong = [L * math.cos(math.radians(a)), L * math.tan(math.radians(a)), L / math.sin(math.radians(a))]
    return dict(stem=f"A ramp is {L} ft long and rises at an angle of {a}° to the level ground. To the nearest tenth of a foot, how high is the top of the ramp above the ground?",
        svg=fig_right(f"{L} ft", "h", "", f"{a}°"), choices=uniq(d1(h), [d1(w) for w in wrong] + [d1(h + 2)]),
        steps=["The ramp is the hypotenuse; the height is the side opposite the angle.", f"sin {a}° = h / {L}.", f"h = {L} × sin {a}° ≈ {L} × {math.sin(math.radians(a)):.4f} ≈ {d1(h)} ft."],
        key="SOH-CAH-TOA: opposite = hypotenuse × sine.")
def elevation(r, d):
    dist = r.choice([20, 25, 30, 40, 50]); a1, a2 = r.choice([(40, 55), (35, 50), (50, 65), (30, 45), (45, 60)])
    h1, h2 = dist * math.tan(math.radians(a1)), dist * math.tan(math.radians(a2)); v = round(h2 - h1)
    return dict(stem=f"A drone hovers directly above a point that is {dist} m from an observer on level ground. The angle of elevation from the observer to the drone changes from {a1}° to {a2}° as the drone rises straight up. To the nearest meter, how much higher is the drone?",
        choices=uniq(str(v), [str(round(h2)), str(round(dist * (math.sin(math.radians(a2)) - math.sin(math.radians(a1))))), str(v + 6)]),
        steps=[f"Height = horizontal distance × tan(angle).", f"First height: {dist} × tan {a1}° ≈ {h1:.2f} m.", f"Second height: {dist} × tan {a2}° ≈ {h2:.2f} m.", f"Difference ≈ {h2 - h1:.2f} ≈ {v} m."],
        key="Use tangent when you know the adjacent side and need the opposite side.")
def polygon(r, d):
    k = r.choice([5, 6, 8, 9, 10, 12, 15, 18, 20])
    inner = F(180 * (k - 2), k)
    if r.random() < 0.5:
        return dict(stem=f"What is the measure of each interior angle of a regular polygon with {k} sides?",
            choices=uniq(n(inner) + "°", [n(F(360, k)) + "°", n(180 * (k - 2)) + "°", n(inner + 10) + "°"]),
            steps=[f"Sum of interior angles = (n − 2) × 180° = ({k} − 2) × 180° = {180*(k-2)}°.", f"Each angle = {180*(k-2)}° ÷ {k} = {n(inner)}°."], key="Interior sum (n − 2)·180°; exterior angles sum to 360°.")
    return dict(stem=f"Each interior angle of a regular polygon measures {n(inner)}°. How many sides does the polygon have?",
        choices=uniq(str(k), [str(k + 1), str(k - 1), str(k + 2)]), steps=[f"Each exterior angle = 180° − {n(inner)}° = {n(180 - inner)}°.", f"Exterior angles sum to 360°, so n = 360 ÷ {n(180 - inner)} = {k}."],
        key="Work with exterior angles: n = 360 ÷ exterior angle.")
def inscribed(r, d):
    a = r.choice([20, 25, 28, 32, 35, 40, 48, 55]); b = r.choice([x for x in [22, 30, 36, 40, 44, 50] if x + a < 90 and x != a])
    return dict(stem=f"Quadrilateral ABCD is inscribed in a circle, and AC is a diameter. If m∠DAC = {a}° and m∠BCA = {b}°, what are m∠BAD and m∠BCD?",
        choices=uniq(f"{(90-b)+a}° and {(90-a)+b}°", [f"{90+a-b+10}° and {90-a+b-10}°", f"90° and 90°", f"{a+b}° and {180-a-b}°", f"{180-a}° and {a}°"]),
        steps=["An angle inscribed in a semicircle is a right angle, so ∠ABC = ∠ADC = 90°.", f"In △ABC: ∠BAC = 90° − {b}° = {90-b}°.", f"∠BAD = ∠BAC + ∠DAC = {90-b}° + {a}° = {90-b+a}°.",
               f"Opposite angles of an inscribed quadrilateral are supplementary: ∠BCD = 180° − {90-b+a}° = {90+b-a}°."], key="Inscribed angle on a diameter = 90°; opposite angles of a cyclic quadrilateral sum to 180°.")
def circle_point(r, d):
    a, b, c = r.choice([(5, 12, 13), (3, 4, 5), (8, 15, 17), (6, 8, 10), (7, 24, 25), (9, 12, 15)])
    R2 = c * c; x = r.choice([1, 2, 3, 4, 6, 7, 8, 9, 10, 11]); x = x if x < c else 1
    y2 = R2 - x * x; good = f"({x}, {sq(y2)})"
    wr = [f"({x}, {sq(y2+1)})", f"({c - 1}, {sq(R2 - (c-1)**2 + 3)})", f"({a + 1}, {b + 1})"]
    return dict(stem=f"A circle centered at the origin passes through the point ({M}{a}, {b}). Which of the following points also lies on the circle?",
        choices=uniq(good, wr), steps=[f"r² = ({M}{a})² + {b}² = {a*a} + {b*b} = {R2}.", f"A point (x, y) is on the circle when x² + y² = {R2}.", f"Check {good}: {x}² + ({sq(y2)})² = {x*x} + {y2} = {R2} ✓."],
        key="On the circle ⇔ x² + y² equals r².")
def dist_line(r, d):
    a, b, c = r.choice([(5, 12, 13), (3, 4, 5), (8, 15, 17), (6, 8, 10)])
    x0, y0 = r.randint(-3, 9), r.randint(-3, 9); yl = y0 - b if r.random() < .5 else y0 + b
    v = x0 - a
    return dict(stem=f"Point P lies on the line y = {n(yl)}. The distance from P to ({n(x0)}, {n(y0)}) is {c} units. If the x-coordinate of P is less than {n(x0)}, what is it?",
        choices=uniq(n(v), [n(x0 + a), n(x0 - b), n(x0 - c)]), steps=[f"Let P = (x, {n(yl)}). Vertical distance: |{n(y0)} − {n(yl)}| = {b}.", f"Distance formula: (x − {n(x0)})² + {b}² = {c}², so (x − {n(x0)})² = {a*a}.",
        f"x − {n(x0)} = ±{a}. Since x < {n(x0)}, x = {n(x0)} − {a} = {n(v)}."], key="Use the distance formula, or spot a Pythagorean triple.")
def section(r, d):
    m, k = r.choice([(1, 3), (1, 2), (2, 3), (1, 4), (3, 1), (2, 1)]); t = F(m, m + k)
    P = (r.randint(-9, 2), r.randint(-9, 2)); Q = (P[0] + (m + k) * r.randint(1, 3), P[1] + (m + k) * r.randint(1, 3))
    A = (P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])); mid = (F(P[0] + Q[0], 2), F(P[1] + Q[1], 2)); B = (P[0] + (1 - t) * (Q[0] - P[0]), P[1] + (1 - t) * (Q[1] - P[1]))
    return dict(stem=f"Directed segment PQ has endpoints P{pt(*P)} and Q{pt(*Q)}. What are the coordinates of the point A on PQ that divides PQ in the ratio {m}:{k}?",
        choices=uniq(pt(*A), [pt(*B), pt(*mid), pt(A[0] + 1, A[1] - 1)]), steps=[f"A is {m}/{m+k} of the way from P to Q.", f"x: {n(P[0])} + {n(t)}({n(Q[0])} − {n(P[0])}) = {n(A[0])}.", f"y: {n(P[1])} + {n(t)}({n(Q[1])} − {n(P[1])}) = {n(A[1])}."],
        key="Partition a segment: P + (m/(m+n))·(Q − P).")
def locus(r, d):
    x1, x2, y = r.randint(-6, 3), r.randint(4, 9), r.randint(-3, 5)
    if (x1 + x2) % 2: x2 += 1
    mx = F(x1 + x2, 2); good = pt(mx, r.randint(-6, 8)); wr = [pt(mx + 1, y), pt(y, mx), pt(mx - 2, y + 1)]
    return dict(stem=f"Which point lies on the set of all points equidistant from ({x1}, {y}) and ({x2}, {y})?",
        choices=uniq(good, wr), steps=["Points equidistant from two points lie on the perpendicular bisector of the segment joining them.", f"The segment is horizontal (both y = {y}), with midpoint x = ({x1} + {x2})/2 = {n(mx)}.",
        f"The perpendicular bisector is the vertical line x = {n(mx)}; only {good} has x = {n(mx)}."], key="Equidistant from two points ⇒ perpendicular bisector.")
def solids(r, d):
    kind = r.choice(["cone_half", "box_ratio", "sphere", "scale", "cyl"])
    if kind == "cone_half":
        h, dia = r.choice([4, 6, 8, 10]), r.choice([3, 4, 6]); rr = F(dia, 4); hh = F(h, 2); v = float(F(1, 3) * rr * rr * hh) * math.pi
        full = float(F(1, 3) * F(dia, 2) ** 2 * h) * math.pi
        return dict(stem=f"A cone-shaped cup (point at the bottom) has height {h} in and a top diameter of {dia} in. It is filled with water to half its height. To the nearest tenth of a cubic inch, what is the volume of the water?",
            choices=uniq(d1(v), [d1(full / 2), d1(full), d1(v * 2)]), steps=["The water forms a smaller cone similar to the cup.", f"At half the height, the radius is also halved: r = {n(F(dia,2))} ÷ 2 = {n(rr)} in, h = {n(hh)} in.",
            f"V = (1/3)πr²h = (1/3)π({n(rr)})²({n(hh)}) ≈ {d1(v)} in³.", "Note: half the height gives only 1/8 of the cup's volume."], key="Scaling lengths by k scales volume by k³.")
    if kind == "box_ratio":
        a, b, c = r.choice([(1, 2, 4), (2, 3, 4), (1, 3, 5), (2, 4, 8)]); x = r.randint(1, 3); V = a * b * c * x ** 3
        return dict(stem=f"The edges of a rectangular solid are in the ratio {a}:{b}:{c}, and its volume is {V} cubic meters. What is the length of the longest edge?",
            choices=uniq(f"{c*x} m", [f"{b*x} m", f"{c} m", f"{c*x*2} m"]), steps=[f"Let the edges be {a}x, {b}x, {c}x.", f"Volume: {a*b*c}x³ = {V}, so x³ = {x**3} and x = {x}.", f"Longest edge = {c}x = {c*x} m."], key="Write the dimensions with one variable from the ratio.")
    if kind == "sphere":
        k = r.choice([4, 9, 16, 25, 36]); rr = math.isqrt(k)
        return dict(stem=f"The largest cross section of a sphere has an area of {k}π square units. What is the surface area of the sphere?",
            choices=uniq(f"{4*k}π", [f"{k}π", f"{n(F(4,3)*rr**3)}π", f"{2*k}π"]), steps=["The largest cross section is a great circle with area πr².", f"πr² = {k}π, so r² = {k}.", f"Surface area = 4πr² = 4π × {k} = {4*k}π."], key="Sphere: SA = 4πr², V = (4/3)πr³.")
    if kind == "scale":
        k = r.choice([2, 3, 4]); V = r.choice([10, 12, 15, 20])
        return dict(stem=f"Two similar cylinders have radii in the ratio 1:{k}. The smaller cylinder has a volume of {V} cm³. What is the volume of the larger cylinder?",
            choices=uniq(f"{V*k**3} cm³", [f"{V*k} cm³", f"{V*k*k} cm³", f"{V*k**3*2} cm³"]), steps=[f"For similar solids, the ratio of volumes is the cube of the ratio of lengths.", f"Length ratio 1:{k} → volume ratio 1:{k**3}.", f"Larger volume = {V} × {k**3} = {V*k**3} cm³."], key="Similar solids: lengths k, areas k², volumes k³.")
    rr, h = r.randint(2, 6), r.randint(3, 10)
    return dict(stem=f"What is the volume, in cubic units, of a right circular cylinder with radius {rr} and height {h}?",
        choices=uniq(f"{rr*rr*h}π", [f"{2*rr*h}π", f"{n(F(rr*rr*h,3))}π", f"{rr*h}π"]), steps=["V = πr²h.", f"V = π({rr})²({h}) = {rr*rr*h}π."], key="Cylinder: V = πr²h.")
def cross(r, d):
    rows = [("a hexagonal prism", "perpendicular to the base", "a rectangle", ["a hexagon", "a triangle", "a trapezoid"]),
            ("a hexagonal prism", "parallel to the base", "a hexagon", ["a rectangle", "a triangle", "a circle"]),
            ("a right circular cylinder", "perpendicular to the base, through its center", "a rectangle", ["a circle", "an ellipse", "a triangle"]),
            ("a right circular cone", "perpendicular to the base, through its vertex", "a triangle", ["a circle", "a rectangle", "a trapezoid"]),
            ("a right circular cone", "parallel to the base", "a circle", ["a triangle", "an ellipse", "a rectangle"]),
            ("a square pyramid", "parallel to the base", "a square", ["a triangle", "a rectangle that is not a square", "a pentagon"]),
            ("a sphere", "through any point inside it", "a circle", ["an ellipse", "a square", "a semicircle"])]
    s, p, good, wr = r.choice(rows)
    return dict(stem=f"A plane intersects {s}. The plane is {p}. What is the shape of the cross section?", choices=uniq(good, wr),
        steps=[f"Picture slicing {s} {p}.", f"The cut surface is {good}."], key="Visualise the slice: parallel to the base copies the base shape.")
def composite(r, d):
    kind = r.choice(["semis", "square_circle", "rect_diag"])
    if kind == "semis":
        k = r.choice([8, 12, 16, 20]); s = F(k, 2)
        return dict(stem=f"A garden is made by attaching a semicircle to each of the four sides of a square, with each side as a diameter. If the perimeter of the garden is {k}π feet, what is its area in square feet?",
            choices=uniq(f"{n(s*s)} + {n(s*s/2)}π", [f"{n(s*s)} + {n(s*s)}π", f"{n(s*s)} + {n(s*s/4)}π", f"{n(4*s*s)} + {n(s*s/2)}π"]),
            steps=["The perimeter is made of 4 semicircular arcs, each with diameter s (the side of the square).", f"4 × (πs/2) = 2πs = {k}π, so s = {n(s)}.",
                   f"Area = square + 4 semicircles = s² + 2 × π(s/2)² = {n(s*s)} + {n(s*s/2)}π."], key="4 semicircles = 2 full circles.")
    if kind == "square_circle":
        A = r.choice([12, 16, 20, 24, 28])
        return dict(stem=f"The perimeter of a square equals the circumference of a circle whose area is {A} square inches. What is the area of the square, in square inches?",
            choices=uniq(f"{n(F(A,4))}π", [f"{A}", f"{A}π", f"{n(F(A,4))}"]), steps=[f"Circle: πr² = {A}.", "Square side s: 4s = 2πr, so s = πr/2.", f"Square area s² = π²r²/4 = π(πr²)/4 = π × {A}/4 = {n(F(A,4))}π."],
            key="Express everything in terms of r, then substitute πr².")
    a, b, c = r.choice([(5, 12, 13), (8, 15, 17), (6, 8, 10), (9, 12, 15), (7, 24, 25)])
    return dict(stem=f"A rectangle has a perimeter of {2*(a+b)} and an area of {a*b}. What is the length of its diagonal?",
        choices=uniq(str(c), [str(c * c), str(a + b), str(c + 1)]), steps=[f"Let the sides be x and y: x + y = {a+b}, xy = {a*b}.", f"The numbers are {a} and {b}.", f"Diagonal = √({a}² + {b}²) = √{c*c} = {c}."],
        key="Find the sides from sum and product, then use Pythagoras.")
def transform(r, d):
    x, y = r.choice([v for v in range(-7, 8) if v]), r.choice([v for v in range(-7, 8) if v])
    ops = [("reflected across the x-axis", (x, -y)), ("reflected across the y-axis", (-x, y)), ("reflected across the line y = x", (y, x)),
           ("rotated 90° counterclockwise about the origin", (-y, x)), ("rotated 180° about the origin", (-x, -y)), ("rotated 90° clockwise about the origin", (y, -x))]
    name, res = r.choice(ops); others = [o[1] for o in ops if o[1] != res]
    rule = {"reflected across the x-axis": "(x, y) → (x, −y)", "reflected across the y-axis": "(x, y) → (−x, y)", "reflected across the line y = x": "(x, y) → (y, x)",
            "rotated 90° counterclockwise about the origin": "(x, y) → (−y, x)", "rotated 180° about the origin": "(x, y) → (−x, −y)", "rotated 90° clockwise about the origin": "(x, y) → (y, −x)"}[name]
    return dict(stem=f"Point P{pt(x, y)} is {name}. What are the coordinates of its image?", choices=uniq(pt(*res), [pt(*o) for o in r.sample(others, len(others))]),
        steps=[f"Rule: {rule}.", f"Apply it to {pt(x, y)}: the image is {pt(*res)}."], key="Memorise the reflection and rotation rules.")
LOGIC = [  # statement, converse, inverse, contrapositive, plus one non-equivalent distractor (all written out in full)
    ("If two angles are vertical angles, then they are congruent.", "If two angles are congruent, then they are vertical angles.",
     "If two angles are not vertical angles, then they are not congruent.", "If two angles are not congruent, then they are not vertical angles.",
     "If two angles are vertical angles, then they are not congruent."),
    ("If a quadrilateral is a square, then it is a rectangle.", "If a quadrilateral is a rectangle, then it is a square.",
     "If a quadrilateral is not a square, then it is not a rectangle.", "If a quadrilateral is not a rectangle, then it is not a square.",
     "If a quadrilateral is a square, then it is not a rectangle."),
    ("If a number is divisible by 6, then it is divisible by 3.", "If a number is divisible by 3, then it is divisible by 6.",
     "If a number is not divisible by 6, then it is not divisible by 3.", "If a number is not divisible by 3, then it is not divisible by 6.",
     "If a number is divisible by 6, then it is not divisible by 3."),
    ("If an angle measures 30°, then it is acute.", "If an angle is acute, then it measures 30°.",
     "If an angle does not measure 30°, then it is not acute.", "If an angle is not acute, then it does not measure 30°.",
     "If an angle measures 30°, then it is not acute."),
    ("If a triangle is equilateral, then it is isosceles.", "If a triangle is isosceles, then it is equilateral.",
     "If a triangle is not equilateral, then it is not isosceles.", "If a triangle is not isosceles, then it is not equilateral.",
     "If a triangle is equilateral, then it is not isosceles."),
    ("If it is raining, then the ground is wet.", "If the ground is wet, then it is raining.",
     "If it is not raining, then the ground is not wet.", "If the ground is not wet, then it is not raining.",
     "If it is raining, then the ground is not wet."),
    ("If x = 4, then x² = 16.", "If x² = 16, then x = 4.", "If x ≠ 4, then x² ≠ 16.", "If x² ≠ 16, then x ≠ 4.", "If x = 4, then x² ≠ 16.")]
def logic(r, d):
    orig, conv, inv, contra, other = r.choice(LOGIC); form = r.choice(["converse", "inverse", "contrapositive"])
    st = {"converse": conv, "inverse": inv, "contrapositive": contra}
    return dict(stem=f"What is the {form} of the statement “{orig[:-1]}”?", choices=uniq(st[form], [st[k] for k in st if k != form] + [other]),
        steps=["Conditional: If p, then q.", "Converse: If q, then p. Inverse: If not p, then not q. Contrapositive: If not q, then not p.", f"So the {form} is: {st[form]}",
               "Only the contrapositive always has the same truth value as the original statement."], key="Contrapositive ≡ original; converse ≡ inverse.")
def midseg(r, d):
    a, b = sorted(r.sample(range(6, 30), 2))
    if r.random() < 0.5:
        return dict(stem=f"The bases of a trapezoid are {a} and {b}. What is the length of the segment joining the midpoints of the legs?",
            choices=uniq(n(F(a + b, 2)), [n(b - a), n(a + b), n(F(b - a, 2))]), steps=["The midsegment of a trapezoid is parallel to the bases.", f"Its length is the average of the bases: ({a} + {b})/2 = {n(F(a+b,2))}."], key="Trapezoid midsegment = (b₁ + b₂)/2.")
    return dict(stem=f"In triangle ABC, M and N are the midpoints of AB and AC. If BC = {2*a}, what is MN?", choices=uniq(str(a), [str(2 * a), str(4 * a), str(a + 2)]),
        steps=["The segment joining the midpoints of two sides of a triangle is parallel to the third side and half as long.", f"MN = {2*a}/2 = {a}."], key="Triangle midsegment = ½ × third side.")
def altitude_gm(r, d):
    p, q = r.choice([(4, 9), (2, 8), (3, 12), (1, 9), (4, 16), (9, 16), (2, 18)]); h = int(math.isqrt(p * q))
    return dict(stem=f"In right triangle ABC, the altitude from the right angle C meets hypotenuse AB at D. If AD = {p} and DB = {q}, what is CD?",
        choices=uniq(str(h), [n(F(p + q, 2)), str(q - p), sq(p * p + q * q)]), steps=["The altitude to the hypotenuse is the geometric mean of the two segments it creates.", f"CD² = AD × DB = {p} × {q} = {p*q}.", f"CD = √{p*q} = {h}."],
        key="Altitude on hypotenuse: CD² = AD·DB.")
def incircle_tri(r, d):
    k = r.choice([2, 3, 4, 5, 6]); rad = f"{k}√3"; side = 6 * k; spacing = r.choice([x for x in [2, 3, 6] if side % x == 0])
    bushes = 3 * side // spacing
    return dict(stem=f"A circular flower bed of radius {rad} ft is inscribed in an equilateral triangle (each side is tangent to the circle). Bushes are planted at each vertex and every {spacing} ft along the sides. How many bushes are planted?",
        svg=fig_inscribed_circle_tri(), choices=uniq(str(bushes), [str(bushes + 3), str(side // spacing), str(bushes * 2)]),
        steps=["For an equilateral triangle, inradius r = side/(2√3), so side = 2√3·r.", f"side = 2√3 × {rad} = 2 × 3 × {k} = {side} ft; perimeter = {3*side} ft.", f"Bushes every {spacing} ft around a closed loop: {3*side} ÷ {spacing} = {bushes} (the vertices are included)."],
        key="In an equilateral triangle the inradius is side/(2√3).")
def expo(r, d):
    a = r.choice([2, 3, 4, 5, 8, 10]); b = r.choice([F(1, 2), F(1, 4), F(1, 3), 2, 3])
    x2 = 2; y2 = a * b ** x2
    good = f"The y-intercept is (0, {a})."
    wr = [f"The x-intercept is ({n(b)}, 0).", "The asymptote is the line x = 0.", f"The graph passes through (2, {n(y2 + 1)})."]
    return dict(stem=f"Which statement about the graph of y = {a}({n(b)})ˣ is true?", choices=uniq(good, wr),
        steps=[f"At x = 0: y = {a}({n(b)})⁰ = {a}, so the y-intercept is (0, {a}).", "An exponential function a·bˣ (a > 0) is always positive, so there is no x-intercept.",
               "Its horizontal asymptote is y = 0, not x = 0.", f"At x = 2: y = {a}({n(b)})² = {n(y2)}, not {n(y2+1)}."], key="y = a·bˣ: y-intercept a, asymptote y = 0.")
def fshift(r, d):
    a, b, c = r.randint(2, 4), r.randint(-6, 6), r.randint(-9, 5); k = r.choice([1, 2, -1])
    # g(x - k) = a x^2 + b x + c  =>  g(t) = a (t+k)^2 + b (t+k) + c
    A, B, C = a, 2 * a * k + b, a * k * k + b * k + c
    def poly(A, B, C): return f"{A}x²" + (f" + {B}x" if B >= 0 else f" {M} {-B}x") + (f" + {C}" if C >= 0 else f" {M} {-C}")
    lhs = "x − 1" if k == 1 else "x − 2" if k == 2 else "x + 1"
    return dict(stem=f"If g({lhs}) = {poly(a, b, c)} for all real x, which expression defines g(x)?",
        choices=uniq(f"g(x) = {poly(A, B, C)}", [f"g(x) = {poly(a, b - 2*a*k, a*k*k - b*k + c)}", f"g(x) = {poly(a, b, c + k)}", f"g(x) = {poly(a, B, c)}"]),
        steps=[f"Let t = {lhs}, so x = t {'+' if k > 0 else M} {abs(k)}.", f"g(t) = {a}(t {'+' if k > 0 else M} {abs(k)})² + {b}(t {'+' if k > 0 else M} {abs(k)}) + {c}.".replace("+ -", f"{M} "),
               f"Expand and collect: g(t) = {poly(A, B, C).replace('x', 't')}.", f"So g(x) = {poly(A, B, C)}."], key="Substitute to undo the inside expression.")
def poly_root(r, d):
    a = r.randint(-6, 6); c1 = r.randint(1, 3); rt = r.choice([-3, -2, 2, 3])
    # p(x) = c1 x^2 + a x - 4x - 2a ; find a given p(rt)=0  -> c1 rt^2 + a rt - 4 rt - 2a = 0 -> a(rt - 2) = 4rt - c1 rt^2
    if rt == 2: rt = -2
    av = F(4 * rt - c1 * rt * rt, rt - 2)
    return dict(stem=f"The polynomial p(x) = {c1 if c1 > 1 else ''}x² + ax − 4x − 2a satisfies p({n(rt)}) = 0. What is the value of a?",
        choices=uniq(n(av), [n(-av), n(av + 2), n(av * 2 if av else 3)]), steps=[f"Substitute x = {n(rt)}: {c1}({n(rt)})² + a({n(rt)}) − 4({n(rt)}) − 2a = 0.",
        f"{c1*rt*rt} + ({n(rt)})a − ({n(4*rt)}) − 2a = 0 → a({n(rt)} − 2) = {n(4*rt - c1*rt*rt)}.", f"a = {n(4*rt - c1*rt*rt)} ÷ ({n(rt - 2)}) = {n(av)}."], key="A root makes the polynomial equal zero: substitute and solve.")
def ineq_area(r, d):
    m = r.choice([2, 3, 4]); k = r.choice([F(1, 2), F(1, 3), 1]); c = r.choice([3, 4, 6])
    xi = F(c) / (m + k); yi = m * xi; base = F(c) / k; A = F(1, 2) * base * yi
    def mixed(v): return n(v) if v.denominator == 1 else f"{v.numerator // v.denominator} {v.numerator % v.denominator}/{v.denominator}"
    ks = "" if k == 1 else n(k)
    return dict(stem=f"The solutions of the system y ≤ {m}x, y ≤ {M}{ks}x + {c}, y ≥ 0 form a triangular region. What is its area, in square units?",
        choices=uniq(mixed(A), [mixed(A * 2), mixed(A / 2), mixed(base * yi)]), steps=[f"Vertices: (0, 0); where y = {M}{ks}x + {c} meets y = 0: x = {n(base)}; where the two lines meet: {m}x = {M}{ks}x + {c}.",
        f"So x = {n(xi)}, y = {n(yi)}: the triangle's height is {n(yi)}.", f"Area = ½ × base × height = ½ × {n(base)} × {n(yi)} = {mixed(A)}."], key="Find the vertices by intersecting the boundary lines.")
def factor_signs(r, d):
    m_pos, n_neg = r.choice([(True, True), (True, False), (False, True), (False, False)])
    ab = "ab < 0" if n_neg else "ab > 0"; s = "a + b > 0" if m_pos else "a + b < 0"
    opts = [f"{x} and {y}" for x in ("ab > 0", "ab < 0") for y in ("a + b > 0", "a + b < 0")]
    good = f"{ab} and {s}"
    return dict(stem=f"If a, b, m, and n are integers with m {'>' if m_pos else '<'} 0 and n {'<' if n_neg else '>'} 0, and x² + mx + n = (x + a)(x + b), what must be true?",
        choices=uniq(good, [o for o in opts if o != good]), steps=["Expand: (x + a)(x + b) = x² + (a + b)x + ab.", "So a + b = m and ab = n.", f"m {'>' if m_pos else '<'} 0 gives {s}; n {'<' if n_neg else '>'} 0 gives {ab}."],
        key="Match coefficients: sum of roots-terms = m, product = n.")
def ratio_minmax(r, d):
    x1, x2 = r.choice([(F(2, 1000), F(2, 10)), (F(1, 100), F(5, 10)), (F(3, 100), F(6, 10))]); y1, y2 = r.choice([(5, 25), (4, 20), (2, 10)])
    v = x2 / y1
    return dict(stem=f"If {float(x1):g} ≤ x ≤ {float(x2):g} and {y1} ≤ y ≤ {y2}, what is the maximum value of x/y?",
        choices=uniq(f"{float(v):g}", [f"{float(x2/y2):g}", f"{float(x1/y1):g}", f"{float(v*10):g}"]), steps=["A fraction is largest when the numerator is as large as possible and the denominator as small as possible.", f"x = {float(x2):g}, y = {y1}.", f"x/y = {float(x2):g} ÷ {y1} = {float(v):g}."], key="Maximise a quotient: biggest top, smallest bottom.")
def rationalize(r, d):
    k = r.choice([8, 12, 18, 20, 27, 32, 45, 50]); num = r.choice([6, 10, 12, 15, 20, 24, 30]); v = F(num, k)
    # num/sqrt(k) = num*sqrt(k)/k
    a = 1; b = k
    for f in range(int(math.isqrt(k)), 1, -1):
        if k % (f * f) == 0: a, b = f, k // (f * f); break
    coef = F(num, a * b)  # num/(a sqrt b) = num sqrt b /(a b)
    def rad(c): return (f"{n(c)}√{b}" if c.denominator == 1 else f"{c.numerator}√{b}/{c.denominator}") if c != 1 else f"√{b}"
    return dict(stem=f"Which expression is equal to {num}/√{k} with a rational denominator?", choices=uniq(rad(coef), [rad(coef * 2), rad(coef / 2) if coef / 2 != coef * 2 else rad(coef + 1), f"{n(F(num, a))}"]),
        steps=[f"Simplify √{k} = {a}√{b}." if a > 1 else f"√{k} cannot be simplified.", f"{num}/({a}√{b}) × (√{b}/√{b}) = {num}√{b}/{a*b}.".replace("(1√", "(√"), f"Reduce: {rad(coef)}."], key="Multiply top and bottom by the radical.")
def arith_formula(r, d):
    a1 = r.randint(-15, 5); dd = r.choice([3, 4, 5, 6, 7]); terms = [a1 + i * dd for i in range(2, 7)]
    good = f"aₙ = {dd}n {M} {-(a1 - dd)}" if a1 - dd < 0 else f"aₙ = {dd}n + {a1 - dd}"
    w = [f"aₙ = {M}{dd}n + {abs(a1 - dd)}", f"aₙ = {n(a1 - dd)}n + {dd}", f"aₙ = {dd}n + {a1}".replace("+ -", f"{M} ")]
    return dict(stem=f"In a sequence, a₃ = {terms[0]}, a₄ = {terms[1]}, a₅ = {terms[2]}, a₆ = {terms[3]}, and a₇ = {terms[4]}. Which formula gives the nth term?".replace("-", M),
        choices=uniq(good, w), steps=[f"The common difference is d = {dd}.", f"Work back: a₁ = a₃ − 2d = {terms[0]} − {2*dd} = {a1}.", f"aₙ = a₁ + (n − 1)d = {a1} + {dd}(n − 1) = {dd}n {('+ ' + str(a1 - dd)) if a1 - dd >= 0 else (M + ' ' + str(-(a1 - dd)))}."],
        key="Arithmetic sequence: aₙ = a₁ + (n − 1)d.")
def geo_mean(r, d):
    a, b = r.choice([(16, 36), (4, 25), (9, 49), (8, 18), (12, 27), (5, 20), (3, 48)]); g = int(math.isqrt(a * b))
    return dict(stem=f"In the geometric sequence {a}, x, {b}, … with positive terms, what is the value of x?", choices=uniq(str(g), [n(F(a + b, 2)), str(g + 1), str(b - a)]),
        steps=["In a geometric sequence, x/a = b/x, so x² = ab.", f"x² = {a} × {b} = {a*b}.", f"x = √{a*b} = {g}."], key="The middle term is the geometric mean √(ab).")
def word_share(r, d):
    prize, coach, frac, players = r.choice([(500, 20, 3, 5), (620, 20, 4, 4), (900, 60, 3, 5), (760, 40, 4, 4)])
    left = prize - coach; cap = F(left, frac); rest = left - cap; each = rest / (players - 1)
    return dict(stem=f"A team wins a ${prize} prize. The coach receives ${coach}. The captain receives one-{['', '', 'half', 'third', 'fourth'][frac]} of what is left, and the remainder is shared equally by the other {players - 1} players. How much does each of those players receive?",
        choices=uniq(f"${n(each)}", [f"${n(cap)}", f"${n(F(prize, players))}", f"${n(rest)}"]), steps=[f"After the coach: ${prize} − ${coach} = ${left}.", f"Captain: ${left} ÷ {frac} = ${n(cap)}.", f"Remaining: ${left} − ${n(cap)} = ${n(rest)}.", f"Each of {players-1} players: ${n(rest)} ÷ {players-1} = ${n(each)}."], key="Follow each step in order and track what is left.")
def discount(r, d):
    p1, p2 = r.choice([(20, 10), (25, 20), (30, 10), (40, 25), (10, 10), (20, 15)]); f = F(100 - p1, 100) * F(100 - p2, 100)
    return dict(stem=f"A store sells items at {p1}% off the list price. During a sale, that discounted price is reduced by another {p2}%. The final price is what percent of the list price?",
        choices=uniq(f"{n(f*100)}%", [f"{100 - p1 - p2}%", f"{n((1 - f) * 100)}%", f"{100 - p1}%"]), steps=[f"After {p1}% off: {100-p1}% of the list price.", f"After another {p2}% off: {100-p2}% of that.", f"{n(F(100-p1,100))} × {n(F(100-p2,100))} = {n(f)} = {n(f*100)}%."], key="Successive percent changes multiply; they do not add.")
def avg_consec(r, d):
    k, avg = r.choice([(5, 12), (7, 20), (5, 31), (9, 15), (3, 41)])
    return dict(stem=f"The average of {k} consecutive whole numbers is {avg}. What is the largest of these numbers?", choices=uniq(str(avg + (k - 1) // 2), [str(avg + k - 1), str(avg), str(avg + k)]),
        steps=["For an odd number of consecutive integers, the average is the middle number.", f"The middle number is {avg}, with {(k-1)//2} numbers above it.", f"Largest = {avg} + {(k-1)//2} = {avg + (k-1)//2}."], key="Consecutive integers: average = middle value.")
def avg_maxval(r, d):
    k, avg, mn, first = r.choice([(5, 27, 23, 31), (4, 20, 15, 22), (6, 30, 24, 33), (5, 40, 35, 44)])
    mx = k * avg - first - (k - 2) * mn
    return dict(stem=f"Over {k} days, a commute averaged {avg} minutes. The shortest possible commute is {mn} minutes, and on the first day it took {first} minutes. What is the longest possible commute on any one of the other days?",
        choices=uniq(f"{mx} minutes", [f"{mx - 2} minutes", f"{first} minutes", f"{mx + 4} minutes"]), steps=[f"Total time = {k} × {avg} = {k*avg} minutes.", f"Without day 1: {k*avg} − {first} = {k*avg - first} for {k-1} days.",
        f"To make one day as long as possible, make the other {k-2} days as short as possible: {k-2} × {mn} = {(k-2)*mn}.", f"Longest = {k*avg - first} − {(k-2)*mn} = {mx} minutes."], key="Maximise one value by minimising the others.")
def remainder(r, d):
    dv, q, rm = r.choice([(17, 25, 1), (13, 30, 5), (19, 12, 7), (23, 15, 4)]); A = dv * q + rm; B = dv * (q + 1)
    return dict(stem=f"When A is divided by {dv}, the quotient is {q} and the remainder is {rm}. When B is divided by {dv}, the quotient is {q+1} and the remainder is 0. What is B − A?",
        choices=uniq(str(B - A), [str(dv), str(rm), str(B - A + 2)]), steps=[f"A = {dv} × {q} + {rm} = {A}.", f"B = {dv} × {q+1} = {B}.", f"B − A = {B} − {A} = {B-A}."], key="Dividend = divisor × quotient + remainder.")
def piano(r, d):
    fb, fg, mult, tot = r.choice([(8, 4, 3, 100), (6, 3, 2, 90), (10, 5, 4, 120), (5, 2, 2, 45)])
    # B/fb boys play, G/fg girls play, G/fg = mult*B/fb, B+G=tot
    # G = mult*fg*B/fb ; B(1 + mult*fg/fb) = tot
    Bv = F(tot) / (1 + F(mult * fg, fb)); bp = Bv / fb
    if bp.denominator != 1 or Bv.denominator != 1: return None
    return dict(stem=f"In a class, 1/{fb} of the boys and 1/{fg} of the girls play the piano, and {mult} times as many girls as boys play. If the class has {tot} students, how many boys play the piano?",
        choices=uniq(n(bp), [n(bp * mult), n(Bv), n(bp + 2)]), steps=[f"Let B boys and G girls: G/{fg} = {mult} × B/{fb}.", f"So G = {n(F(mult*fg, fb))}B, and B + {n(F(mult*fg, fb))}B = {tot}.", f"B = {n(Bv)}; boys who play = {n(Bv)} ÷ {fb} = {n(bp)}."], key="Translate each sentence into an equation.")
def sets_q(r, d):
    rows = [("whole numbers", "nonzero integers", "the positive integers", ["the empty set", "{0}", "the negative integers"]),
            ("integers", "natural numbers (1, 2, 3, …)", "the natural numbers", ["the integers", "the whole numbers", "the empty set"]),
            ("even integers", "prime numbers", "{2}", ["the empty set", "the odd primes", "the even integers"]),
            ("positive integers", "negative integers", "the empty set", ["{0}", "the integers", "the whole numbers"])]
    a, b, good, wr = r.choice(rows)
    return dict(stem=f"What is the intersection of the set of {a} and the set of {b}?", choices=uniq(good[0].upper() + good[1:] if good[0].isalpha() else good, [w[0].upper() + w[1:] if w[0].isalpha() else w for w in wr]),
        steps=["The intersection contains the numbers that belong to both sets.", f"Numbers that are both {a} and {b}: {good}."], key="Intersection = common elements.")
def age_eq(r, d):
    x = r.randint(8, 16); k = r.choice([2, 3]); diff = r.choice([4, 6, 8, 10]); yrs = r.choice([3, 4, 5, 6])
    father = k * x - diff; m2 = 2; add = (father + yrs) - m2 * (x + yrs)
    if add <= 0: return None
    good = f"{k}x {M} {diff} + {yrs} = 2(x + {yrs}) + {add}"
    return dict(stem=f"A father is {diff} years younger than {k} times his daughter's age, x. In {yrs} years, his age will be {add} more than twice her age then. Which equation can be used to find x?",
        choices=uniq(good, [f"{k}x + {diff} + {yrs} = 2(x + {yrs}) + {add}", f"{k}x {M} {diff} = 2x + {add}", f"{k}(x {M} {diff}) + {yrs} = 2x + {yrs} + {add}"]),
        steps=[f"Father's age now: {k}x − {diff}.", f"In {yrs} years: father {k}x − {diff} + {yrs}; daughter x + {yrs}.", f"Condition: {k}x − {diff} + {yrs} = 2(x + {yrs}) + {add}.", f"(Solving gives x = {x}.)"], key="Write each age now and later, then translate the sentence.")
def mean_median(r, d):
    data = sorted(r.sample(range(10, 60), 6)); k = r.randint(3, 9)
    newd = [x + k for x in data]
    return dict(stem=f"Each value in a data set is increased by {k}. Which statement is true about the new data set?", choices=uniq("The mean and median increase by " + str(k) + "; the range is unchanged.",
        ["The mean, median, and range all increase by " + str(k) + ".", "The mean increases by " + str(k) + "; the median is unchanged.", "The range increases by " + str(k) + "; the mean is unchanged."]),
        steps=["Adding a constant shifts every value by that amount.", f"Centre measures (mean, median, mode) increase by {k}.", "Spread measures (range, standard deviation) stay the same, because every distance between values is unchanged."], key="Shift: centre moves, spread stays.")

GENS = [(trapezoid, "Geometry", 2, 3), (obtuse, "Geometry", 2, 3), (perim_possible, "Geometry", 2, 3), (int_triangle, "Geometry", 3, 3), (special, "Geometry", 1, 2),
        (ramp, "Geometry", 2, 2), (elevation, "Geometry", 3, 3), (polygon, "Geometry", 1, 2), (inscribed, "Geometry", 3, 3), (circle_point, "Geometry", 2, 3),
        (dist_line, "Geometry", 2, 3), (section, "Geometry", 2, 3), (locus, "Geometry", 2, 3), (solids, "Geometry", 2, 3), (cross, "Geometry", 1, 2),
        (composite, "Geometry", 2, 3), (transform, "Geometry", 1, 2), (logic, "Integrating Essential Skills", 2, 2), (midseg, "Geometry", 1, 2),
        (altitude_gm, "Geometry", 2, 3), (incircle_tri, "Geometry", 3, 3), (expo, "Functions", 2, 2), (fshift, "Functions", 3, 3), (poly_root, "Algebra", 2, 2),
        (ineq_area, "Algebra", 3, 3), (factor_signs, "Algebra", 3, 3), (ratio_minmax, "Number and Quantity", 2, 2), (rationalize, "Number and Quantity", 1, 2),
        (arith_formula, "Functions", 2, 2), (geo_mean, "Functions", 1, 2), (word_share, "Integrating Essential Skills", 2, 2), (discount, "Integrating Essential Skills", 1, 2),
        (avg_consec, "Statistics and Probability", 1, 2), (avg_maxval, "Statistics and Probability", 3, 3), (remainder, "Number and Quantity", 1, 2),
        (piano, "Integrating Essential Skills", 3, 3), (sets_q, "Number and Quantity", 1, 1), (age_eq, "Algebra", 2, 2), (mean_median, "Statistics and Probability", 1, 2)]

def main(per=22, seed=31415):
    r = random.Random(seed); out = []; seen = set()
    for fn, cat, dlo, dhi in GENS:
        got = tries = 0
        while got < per and tries < 1500:
            tries += 1; dd = r.randint(dlo, dhi)
            try: q = fn(r, dd)
            except (ValueError, ZeroDivisionError): q = None
            if not q or not q.get("choices") or len(set(q["choices"])) != 4 or q["stem"] in seen: continue
            seen.add(q["stem"]); got += 1
            q.update(id=f"ai-{fn.__name__}-{got:03d}", cat=cat, difficulty=dd, answer=0, aist=True, source="SAT AIS original item (AIST Math 1 style)")
            out.append(q)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "aist_math.json"), "w"), ensure_ascii=False)
    print(len(out), "AIST-style items")
if __name__ == "__main__": main()
