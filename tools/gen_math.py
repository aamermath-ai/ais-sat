"""SAT AIS math question generator.
Each template builds an original SAT-style item from random parameters, computes the answer exactly
(Fractions), asserts it, and writes worked steps from the same numbers. Output: list of question dicts."""
import random, math, json, sys
from fractions import Fraction as Fr

SRC = "SAT AIS original item, generated from verified templates written to the College Board Digital SAT content specifications"

# ---------------------------------------------------------------- formatting
def S(v):
    v = Fr(v)
    if v < 0: return "−" + S(-v)
    if v.denominator == 1:
        n = v.numerator
        return f"{n:,}" if n >= 10000 else str(n)
    return f"{v.numerator}/{v.denominator}"
def A(v):  # SPR answer (ASCII)
    v = Fr(v)
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
def D(v, p=2):  # decimal display
    s = f"{float(v):,.{p}f}"
    return s
def money(v):
    v = Fr(v)
    return f"${v.numerator:,}" if v.denominator == 1 else f"${float(v):,.2f}"
def coef(a, var):
    a = Fr(a)
    if a == 1: return var
    if a == -1: return "−" + var
    return S(a) + var
def lin(a, b, var="x"):
    a, b = Fr(a), Fr(b)
    if a == 0: return S(b)
    s = coef(a, var)
    if b > 0: s += " + " + S(b)
    elif b < 0: s += " − " + S(-b)
    return s
def plus(b):  # " + 5" / " − 5"
    b = Fr(b)
    return (" + " + S(b)) if b >= 0 else (" − " + S(-b))
def quad(a, b, c, var="x"):
    s = coef(a, var + "²")
    if b: s += (" + " if b > 0 else " − ") + coef(abs(b), var)
    if c: s += plus(c)
    return s
def mp(v):  # always parenthesized, for multiplication like 3(5)
    return f"({S(v)})"
def sl(m):  # slope as a coefficient
    m = Fr(m)
    return f"({S(m)})" if m.denominator != 1 else S(m)
def D1(v):
    return D(v, 1).rstrip("0").rstrip(".") if "." in D(v, 1) else D(v, 1)
def par(v):  # value in parentheses if negative
    return f"({S(v)})" if Fr(v) < 0 else S(v)
SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
def pw(var, n):
    return var if n == 1 else (var + str(n).translate(SUP))
def xpow(n):
    if n == 0: return "1"
    if n < 0: return "1/" + pw("x", -n)
    return pw("x", n)
def pct(v):
    v = Fr(v)
    return (S(v) if v.denominator == 1 else D(v, 1)) + "%"

def pick4(correct, cands, pad):
    out = [correct]
    for c in list(cands) + list(pad):
        if c not in out: out.append(c)
        if len(out) == 4: return out
    raise ValueError("not enough distinct choices")
def numpad(v):
    v = Fr(v)
    return [S(v + 1), S(v - 1), S(v + 2), S(v * 2), S(v - 2), S(v + 3), S(-v)]

def MC(stem, choices, steps, key, table=None):
    q = dict(type="mc", stem=stem, choices=choices, answer=0, steps=steps, key=key)
    if table: q["table"] = table
    return q
def SPR(stem, ans, steps, key, table=None):
    q = dict(type="spr", stem=stem, answer=A(ans), steps=steps, key=key)
    if table: q["table"] = table
    return q
def nz(r, lo, hi):
    while True:
        v = r.randint(lo, hi)
        if v: return v

# ================================================================ ALGEBRA
def l1_basic(r, d):
    if d == 1:
        a = r.randint(2, 9); x = r.randint(-9, 12); b = nz(r, -15, 15); c = a * x + b
        op = (f"Subtract {S(b)} from both sides" if b > 0 else f"Add {S(-b)} to both sides")
        return MC(f"If {lin(a, b)} = {S(c)}, what is the value of x?",
                  pick4(S(x), [S(Fr(c + b, a)), S(c - b), S(Fr(c, a))], numpad(x)),
                  [f"Start: {lin(a, b)} = {S(c)}", f"{op}: {a}x = {S(c - b)}", f"Divide both sides by {a}: x = {S(x)}",
                   f"Check: {a}{mp(x)}{plus(b)} = {S(c)} ✓"],
                  "Undo operations in reverse order: first addition or subtraction, then multiplication or division.")
    if d == 2:
        a = r.randint(2, 6); p = nz(r, -8, 9); q = r.choice([k for k in range(1, 10) if k != a]); x = r.randint(-8, 12)
        rr = a * (x + p) - q * x
        lhs = f"{a}({lin(1, p)})"
        assert a * (x + p) == q * x + rr
        return SPR(f"{lhs} = {lin(q, rr)}\nWhat is the solution to the equation above?", x,
                   [f"Distribute: {lin(a, a * p)} = {lin(q, rr)}",
                    f"Collect x-terms on one side and constants on the other: {lin(a - q, 0)} = {S(rr - a * p)}",
                    *([f"Divide by {S(a - q)}: x = {S(x)}"] if a - q != 1 else []),
                    f"Check: {a}({S(x)}{plus(p)}) = {S(a * (x + p))} and {q}{mp(x)}{plus(rr)} = {S(q * x + rr)} ✓"],
                   "Distribute first, then collect the variable on one side and the constants on the other.")
    if r.random() < 0.5:
        m, n = r.sample([2, 3, 4, 5, 6], 2); L = m * n // math.gcd(m, n); x = L * r.randint(1, 6); c = Fr(x, m) + Fr(x, n)
        return SPR(f"x/{m} + x/{n} = {S(c)}\nWhat is the value of x?", x,
                   [f"Multiply every term by {L}, the least common denominator.",
                    f"{L}(x/{m}) + {L}(x/{n}) = {L}({S(c)}) gives {coef(L // m, 'x')} + {coef(L // n, 'x')} = {S(L * c)}.",
                    f"Combine: {L // m + L // n}x = {S(L * c)}.", f"Divide: x = {S(x)}.",
                    f"Check: {S(x)}/{m} + {S(x)}/{n} = {S(Fr(x, m))} + {S(Fr(x, n))} = {S(c)} ✓"],
                   "Multiply every term by the least common denominator to clear fractions in one step.")
    q = r.randint(2, 9); p = r.randint(1, 7); s = nz(r, -12, 12)
    while s == -q * p: s = nz(r, -12, 12)
    return MC(f"k(x − {p}) = {q}x{plus(s)}\nIn the equation above, k is a constant. For what value of k does the equation have no solution?",
              pick4(S(q), [S(-q), S(p), S(s), S(q * p)], numpad(q)),
              [f"Distribute: kx − {p}k = {lin(q, s)}.",
               "A linear equation has no solution when the x-coefficients on both sides match but the constants do not.",
               f"Match the x-coefficients: k = {q}.",
               f"Check the constants with k = {q}: left side −{p}({q}) = {S(-p * q)}, right side {S(s)}. They differ, so there is no solution."],
              "No solution: same coefficient of x on both sides, different constants. Infinitely many: both the same.")

WORD = [("A taxi company charges a flat fee of {f} plus {m} per mile. A ride cost {t} in total. How many miles long was the ride?", "miles"),
        ("A plumber charges a {f} visit fee plus {m} per hour of work. A repair cost {t} in total. How many hours did the plumber work?", "hours"),
        ("A gym charges a one-time sign-up fee of {f} plus {m} per month. A member has paid {t} in total. For how many months has the member paid?", "months"),
        ("A bike rental shop charges {f} plus {m} per hour. A rental cost {t} in total. For how many hours was the bike rented?", "hours"),
        ("An online course charges a {f} registration fee plus {m} per lesson. A student paid {t} in total. How many lessons did the student take?", "lessons"),
        ("A moving company charges {f} plus {m} per box moved. A customer was charged {t}. How many boxes were moved?", "boxes")]
def l1_word(r, d):
    tpl, unit = r.choice(WORD)
    if d == 1: f = r.randint(2, 12) * 5; m = r.randint(3, 15); n = r.randint(3, 15)
    else: f = Fr(r.randint(6, 40), 2); m = Fr(r.randint(5, 30), 4); n = r.randint(4, 16)
    t = f + m * n
    stem = tpl.format(f=money(f), m=money(m), t=money(t))
    return MC(stem, pick4(S(n), [S(t / m), S((t + f) / m), S(n + 1)], numpad(n)),
              [f"Write the equation: {money(f)} + {money(m)}n = {money(t)}, where n is the number of {unit}.",
               f"Subtract the fixed fee: {money(m)}n = {money(t - f)}.",
               f"Divide: n = {money(t - f)} ÷ {money(m)} = {S(n)}.",
               f"Check: {money(f)} + {money(m)} × {S(n)} = {money(t)} ✓",
               f"Trap: dividing the total by {money(m)} without removing the {money(f)} fee gives a wrong answer."],
              "Total = fixed fee + rate × quantity. Remove the fixed fee before dividing by the rate.")

def l2(r, d):
    if d == 1:
        if r.random() < 0.5:
            a, b = r.sample([2, 3, 4, 5, 6, 8], 2); k = r.randint(1, 6) * a * b // math.gcd(a, b); c = k
            yi, xi = Fr(c, b), Fr(c, a)
            return MC(f"In the xy-plane, what is the y-intercept of the graph of {a}x + {b}y = {c}?",
                      pick4(f"(0, {S(yi)})", [f"(0, {S(c)})", f"({S(xi)}, 0)", f"(0, {S(b)})", f"(0, {S(a)})"], [f"(0, {S(yi + 1)})", f"(0, {S(-yi)})"]),
                      ["The y-intercept is where the graph crosses the y-axis, so x = 0.", f"Substitute x = 0: {b}y = {c}.",
                       f"Divide: y = {S(yi)}.", f"The y-intercept is (0, {S(yi)}).", f"Trap: ({S(xi)}, 0) is the x-intercept (set y = 0)."],
                      "For the y-intercept set x = 0; for the x-intercept set y = 0.")
        m = nz(r, -5, 5); k = nz(r, -9, 9); x0 = r.randint(-3, 5); y0 = m * x0 + k
        wrong = [f"({x0}, {S(y0 + r.choice([-2, -1, 1, 2]))})", f"(0, {S(-k)})", f"({S(y0)}, {x0})", f"({x0 + 1}, {S(y0 + 2 * m + 1)})"]
        pt = f"({S(x0)}, {S(y0)})"
        ch = pick4(pt, [w for w in wrong if w != pt], [f"({x0}, {S(y0 + 3)})", f"({x0 - 1}, {S(y0 + 1)})"])
        return MC(f"Which point lies on the line y = {lin(m, k)}?", ch,
                  ["A point lies on the line if its coordinates make the equation true.",
                   f"Test {pt}: {S(m)}{mp(x0)}{plus(k)} = {S(y0)} ✓",
                   "Each other choice gives a y-value that does not match when its x-value is substituted."],
                  "Substitute the x-value and check whether you get the y-value.")
    if d == 2:
        x1 = r.randint(-6, 4); x2 = x1 + r.randint(1, 6); m = Fr(nz(r, -9, 9), r.choice([1, 1, 2, 3])); y1 = r.randint(-8, 8)
        y2 = y1 + m * (x2 - x1)
        if y2.denominator != 1: return None
        return SPR(f"A line in the xy-plane passes through the points ({S(x1)}, {S(y1)}) and ({S(x2)}, {S(y2)}). What is the slope of the line?", m,
                   ["Slope = (y₂ − y₁) ÷ (x₂ − x₁).", f"Change in y: {S(y2)} − {par(y1)} = {S(y2 - y1)}.",
                    f"Change in x: {S(x2)} − {par(x1)} = {S(x2 - x1)}.", f"Slope = {S(y2 - y1)} ÷ {S(x2 - x1)} = {S(m)}."],
                   "Subtract in the same order on top and bottom; watch the signs when subtracting a negative.")
    a = r.randint(1, 6); b = r.choice([2, 3, 4, 5, 6]); c = nz(r, -12, 12)
    m = Fr(-a, b); perp = r.random() < 0.5; ms = -1 / m if perp else m
    px = r.choice([k * b for k in range(-2, 3) if k]) if not perp else r.choice([k * a for k in range(-2, 3) if k]); py = r.randint(-6, 8)
    bb = py - ms * px
    rel = "perpendicular" if perp else "parallel"
    return SPR(f"Line k has the equation {coef(a, 'x')} + {b}y = {S(c)}. Line m is {rel} to line k and passes through the point ({S(px)}, {S(py)}). If the equation of line m is written as y = ax + b, what is the value of b?", bb,
               [f"Solve line k for y: {b}y = {lin(-a, c)}, so the slope of k is {S(m)}.",
                ("Perpendicular slopes are negative reciprocals" if perp else "Parallel lines have equal slopes") + f", so line m has slope {S(ms)}.",
                f"Substitute ({S(px)}, {S(py)}) into y = {coef(ms, 'x') if Fr(ms).denominator == 1 else sl(ms) + 'x'} + b: {S(py)} = {sl(ms)}{mp(px)} + b = {S(ms * px)} + b.",
                f"Solve: b = {S(py)} − {par(ms * px)} = {S(bb)}."],
               "Parallel lines share a slope; perpendicular slopes multiply to −1. Then use the point to find b.")

INTERP = [("C(m) = {a}m + {b} gives the total cost, in dollars, of a gym membership for m months", "month",
           "The cost increases by ${a} for each additional month", "A fixed charge of ${b} that does not depend on the number of months"),
          ("T(t) = {a}t + {b} gives the temperature, in degrees Fahrenheit, of an oven t minutes after it is turned on", "minute",
           "The temperature rises by {a} degrees each minute", "The temperature was {b} degrees when the oven was turned on"),
          ("W(t) = {b} − {a}t gives the amount of water, in liters, left in a tank t minutes after it begins draining", "minute",
           "The amount of water decreases by {a} liters each minute", "The tank held {b} liters when it began draining"),
          ("H(w) = {a}w + {b} gives the height, in centimeters, of a plant w weeks after it was first measured", "week",
           "The plant grows {a} centimeters each week", "The plant was {b} centimeters tall when first measured"),
          ("P(n) = {a}n + {b} gives a salesperson's weekly pay, in dollars, for selling n items", "item",
           "Pay increases by ${a} for each item sold", "The salesperson earns ${b} per week even when no items are sold"),
          ("D(h) = {a}h + {b} gives the distance, in miles, a train is from a station h hours after noon", "hour",
           "The train travels {a} miles each hour", "The train was {b} miles from the station at noon")]
def lf(r, d):
    if d == 1:
        a = nz(r, -7, 9); b = nz(r, -12, 12); k = r.randint(-4, 6); v = a * k + b
        return MC(f"The function f is defined by f(x) = {lin(a, b)}. What is the value of f({S(k)})?",
                  pick4(S(v), [S(a + k + b), S(a * k - b), S(a * (k + b))], numpad(v)),
                  [f"Substitute {S(k)} for x: f({S(k)}) = {S(a)}{mp(k)}{plus(b)}.", f"Multiply: {S(a * k)}{plus(b)}.", f"Result: {S(v)}."],
                  f"f({S(k)}) means: replace every x with {S(k)}.")
    if d == 2:
        if r.random() < 0.5:
            tpl, unit, ms, bs = r.choice(INTERP); a = r.randint(2, 25); b = r.randint(10, 90)
            if b == a: b += 7
            ask_slope = r.random() < 0.5; X = a if ask_slope else b
            corr = (ms if ask_slope else bs).format(a=a, b=b); other = (bs if ask_slope else ms).format(a=a, b=b)
            return MC(f"The function {tpl.format(a=a, b=b)}. What is the best interpretation of {X} in this context?",
                      pick4(corr, [other, f"The value of the function after {X} {unit}s", f"The number of {unit}s needed to reach {b + a}"], []),
                      [("The coefficient of the variable is the rate: how much the output changes for each 1-unit increase in the input." if ask_slope else
                        "The constant term is the output when the input is 0: the starting or fixed value."),
                       f"Here {X} is the {'coefficient of the variable' if ask_slope else 'constant term'}.",
                       f"So {X} means: {corr[0].lower() + corr[1:]}."],
                      "In a linear model, the coefficient is the rate of change and the constant is the starting value.")
        m = nz(r, -6, 6); b = r.randint(-10, 10); p = r.randint(-3, 3); q = p + r.randint(2, 5); s = q + r.randint(2, 6)
        g = lambda x: m * x + b
        return SPR(f"For the linear function g, g({S(p)}) = {S(g(p))} and g({S(q)}) = {S(g(q))}. What is the value of g({S(s)})?", g(s),
                   [f"Slope = ({S(g(q))} − {par(g(p))}) ÷ ({S(q)} − {par(p)}) = {S(g(q) - g(p))} ÷ {S(q - p)} = {S(m)}.",
                    f"Each increase of 1 in x changes g(x) by {S(m)}.",
                    f"From x = {S(q)} to x = {S(s)} is an increase of {S(s - q)}, so g changes by {S(s - q)} × {par(m)} = {S(m * (s - q))}.",
                    f"g({S(s)}) = {S(g(q))}{plus(m * (s - q))} = {S(g(s))}."],
                   "A linear function changes by the same amount for each equal step in x.")
    if r.random() < 0.5:
        m = nz(r, -6, 7); b = r.randint(-10, 10); k = r.randint(2, 6); x = r.randint(-5, 15); v = m * x + b
        return SPR(f"For the linear function h, h(0) = {S(b)} and h({k}) = {S(m * k + b)}. For what value of x is h(x) = {S(v)}?", x,
                   [f"h(0) = {S(b)} gives the y-intercept: b = {S(b)}.", f"Slope = ({S(m * k + b)} − {par(b)}) ÷ {k} = {S(m)}.",
                    f"So h(x) = {lin(m, b)}.", f"Set h(x) = {S(v)}: {lin(m, b)} = {S(v)}, so {coef(m, 'x')} = {S(v - b)}.", f"x = {S(x)}."],
                   "Build the function (slope and intercept) first, then solve h(x) = value.")
    m = nz(r, -5, 6); b = nz(r, -9, 12); xs = sorted(r.sample(range(-2, 8), 3)); ys = [m * x + b for x in xs]
    wrong = [lin(m, ys[0]), lin(ys[0] - b, b) if ys[0] - b != m else lin(m + 1, b - 1), lin(m * 2, b - m * xs[0])]
    return MC("The table shows three values of x and their corresponding values of y for a linear relationship. Which equation represents the relationship?",
              pick4("y = " + lin(m, b), ["y = " + w for w in wrong], ["y = " + lin(m, -b), "y = " + lin(-m, b), "y = " + lin(m + 1, b)]),
              [f"Slope = ({S(ys[1])} − {par(ys[0])}) ÷ ({S(xs[1])} − {par(xs[0])}) = {S(ys[1] - ys[0])} ÷ {S(xs[1] - xs[0])} = {S(m)}.",
               f"Use ({S(xs[0])}, {S(ys[0])}) in y = {S(m)}x + b: {S(ys[0])} = {S(m * xs[0])} + b, so b = {S(b)}.",
               f"Equation: y = {lin(m, b)}.", f"Check the third row: {S(m)}{mp(xs[2])}{plus(b)} = {S(ys[2])} ✓"],
              "Get the slope from two rows and the intercept from any row; always check a third row.",
              table={"caption": "", "head": ["x", "y"], "rows": [[S(x), S(y)] for x, y in zip(xs, ys)]})

def sy(r, d):
    if d == 1:
        if r.random() < 0.5:
            k = r.randint(2, 5); x = r.randint(2, 12); s = (k + 1) * x
            return SPR(f"y = {k}x\nx + y = {s}\nIf (x, y) is the solution to the system above, what is the value of x?", x,
                       [f"Substitute y = {k}x into the second equation: x + {k}x = {s}.", f"Combine: {k + 1}x = {s}.", f"Divide: x = {x}.",
                        f"(Then y = {k * x}. Check: {x} + {k * x} = {s} ✓)"], "Substitution works best when one equation is already solved for a variable.")
        p1 = r.randint(6, 15); p2 = r.randint(3, p1 - 2); a = r.randint(2, 9); c = r.randint(2, 9); n = a + c; t = p1 * a + p2 * c
        it = r.choice([("Adult tickets to a show cost ${p1} and child tickets cost ${p2}", "adult", "child", "tickets"),
                       ("Large notebooks cost ${p1} and small notebooks cost ${p2}", "large", "small", "notebooks"),
                       ("Hardcover books at a sale cost ${p1} and paperbacks cost ${p2}", "hardcover", "paperback", "books")])
        return MC(f"{it[0].format(p1=p1, p2=p2)}. A customer bought {n} {it[3]} for ${t}. How many {it[1]} {it[3]} did the customer buy?",
                  pick4(S(a), [S(c), S(a + 1), S(t // p1)], numpad(a)),
                  [f"Let a = {it[1]} {it[3]} and c = {it[2]} {it[3]}.", f"Count: a + c = {n}, so c = {n} − a.",
                   f"Cost: {p1}a + {p2}c = {t}. Substitute: {p1}a + {p2}({n} − a) = {t}.",
                   f"Simplify: {p1 - p2}a + {p2 * n} = {t}, so {p1 - p2}a = {t - p2 * n} and a = {a}.",
                   f"Check: {a} × ${p1} + {c} × ${p2} = ${t} ✓"], "Write one equation for the count and one for the value, then substitute.")
    if d == 2:
        x = r.randint(-5, 8); y = r.randint(-5, 8); a = r.randint(1, 6); b = r.randint(1, 5); dd = r.randint(1, 6)
        c = a * x + b * y; e = dd * x - b * y; ask = r.choice(["x", "y"]); ans = x if ask == "x" else y; oth = y if ask == "x" else x
        return MC(f"{lin(a, 0)} + {coef(b, 'y')} = {S(c)}\n{lin(dd, 0)} − {coef(b, 'y')} = {S(e)}\nIf (x, y) is the solution to the system above, what is the value of {ask}?",
                  pick4(S(ans), [S(oth), S(ans + 1), S(-ans)], numpad(ans)),
                  [f"The y-terms are +{coef(b, 'y')} and −{coef(b, 'y')}, so add the equations.",
                   f"{a + dd}x = {S(c + e)}, so x = {S(x)}.",
                   f"Substitute into the first equation: {S(a)}{mp(x)} + {coef(b, 'y')} = {S(c)}, so {coef(b, 'y')} = {S(c - a * x)}" + (f" and y = {S(y)}." if b != 1 else "."),
                   f"The question asks for {ask}: {S(ans)}."], "Add the equations when a variable has opposite coefficients, and answer for the variable asked.")
    a = r.randint(1, 6); b = r.randint(1, 6); c = nz(r, -10, 12); k = r.randint(2, 4); inf = r.random() < 0.5
    if inf:
        return MC(f"{coef(a, 'x')} + {coef(b, 'y')} = {S(c)}\n{coef(k * a, 'x')} + {coef(k * b, 'y')} = n\nIn the system above, n is a constant. For what value of n does the system have infinitely many solutions?",
                  pick4(S(k * c), [S(c), S(k), S(c + k)], numpad(k * c)),
                  ["Infinitely many solutions means both equations describe the same line.",
                   f"The second equation's coefficients are {k} times the first's ({k * a} = {k} × {a}, {k * b} = {k} × {b}).",
                   f"So the constant must also be multiplied by {k}: n = {k} × {par(c)} = {S(k * c)}.", "Any other value gives parallel lines and no solution."],
                  "Infinitely many solutions: one equation is an exact multiple of the other, constants included.")
    return MC(f"{coef(a, 'x')} + {coef(b, 'y')} = {S(c)}\npx + {coef(k * b, 'y')} = {S(k * c + r.choice([-3, -2, 2, 3, 5]))}\nIn the system above, p is a constant. For what value of p does the system have no solution?",
              pick4(S(k * a), [S(a), S(k), S(-k * a)], numpad(k * a)),
              ["No solution means the lines are parallel: same slope, different intercept.",
               f"The y-coefficients are in the ratio {k * b} ÷ {b} = {k}, so the x-coefficients must be too: p = {k} × {a} = {k * a}.",
               f"The constants are not in that ratio ({k} × {par(c)} = {S(k * c)} differs from the second constant), so the lines are distinct.",
               f"Answer: p = {k * a}."], "No solution: coefficients proportional, constants not.")

def li(r, d):
    if d == 1:
        a = r.randint(2, 7); B = r.randint(-3, 9); b = nz(r, -12, 12); c = a * B + b; lt = r.random() < 0.5
        if lt: corr, others = B - 1, [B, B + 1, B + 2]; sym, rel = "<", "less than"
        else: corr, others = B + 1, [B, B - 1, B - 2]; sym, rel = ">", "greater than"
        return MC(f"Which value of x satisfies the inequality {lin(a, b)} {sym} {S(c)}?", [S(corr)] + [S(o) for o in others],
                  [f"{'Subtract ' + S(b) + ' from' if b > 0 else 'Add ' + S(-b) + ' to'} both sides: {a}x {sym} {S(c - b)}.",
                   f"Divide by {a}: x {sym} {S(B)}.", f"Only {S(corr)} is {rel} {S(B)}.",
                   f"Trap: {S(B)} makes both sides equal, so it does not satisfy a strict inequality."],
                  "\"<\" and \">\" are strict: the boundary value itself is not a solution.")
    if d == 2:
        if r.random() < 0.5:
            p = r.randint(10, 40); q = r.randint(2, 6); rr = r.randint(-20, 5); bound = Fr(p - rr, q)
            g = bound - 1 if bound.denominator == 1 else Fr(math.floor(bound))
            return SPR(f"{p} − {q}x > {S(rr)}\nWhat is the greatest integer value of x that satisfies the inequality above?", g,
                       [f"Subtract {p} from both sides: −{q}x > {S(rr - p)}.", f"Divide by −{q} and flip the sign: x < {S(bound)}.",
                        f"The greatest integer less than {S(bound)} is {S(g)}.",
                        f"Check: {p} − {q}({S(g)}) = {S(p - q * g)}, which is greater than {S(rr)} ✓"],
                       "Dividing or multiplying an inequality by a negative number flips the sign.")
        cap = r.choice([800, 1000, 1200, 1500, 2000]); w = r.randint(150, 250); per = r.choice([30, 35, 40, 45, 50, 60]); mx = (cap - w) // per
        if (cap - w) % per == 0: return None
        return MC(f"A small elevator can carry at most {cap:,} pounds. An operator who weighs {w} pounds rides with the cargo, and each crate weighs {per} pounds. What is the maximum number of crates the elevator can carry on one trip?",
                  pick4(S(mx), [S(mx + 1), S(cap // per), S(mx - 2)], numpad(mx)),
                  [f"Total weight: {w} + {per}c ≤ {cap:,}.", f"Subtract {w}: {per}c ≤ {cap - w:,}.", f"Divide: c ≤ {D(Fr(cap - w, per), 2)}.",
                   f"Crates must be whole, so the maximum is {mx}.", f"Trap: {cap // per} ignores the operator's weight."],
                  "For \"at most\" problems, solve the inequality and round down to stay within the limit.")
    if r.random() < 0.5:
        goal = r.choice([500, 600, 750, 800, 1000]); have = r.randint(50, 200); price = r.randint(10, 20); cost = r.randint(2, price - 4); prof = price - cost
        n = -(-(goal - have) // prof)
        if (goal - have) % prof == 0: return None
        return SPR(f"A club needs to raise at least ${goal}. It already has ${have}. It sells T-shirts for ${price} each, and each shirt costs the club ${cost} to make. What is the minimum number of shirts the club must sell to reach its goal?", n,
                   [f"Profit per shirt: ${price} − ${cost} = ${prof}.", f"Inequality: {have} + {prof}s ≥ {goal}.",
                    f"Subtract {have}: {prof}s ≥ {goal - have}, so s ≥ {D(Fr(goal - have, prof))}.",
                    f"Shirts are whole and the goal must be reached, so round up: s = {n}.",
                    f"Check: {n - 1} shirts gives ${have + prof * (n - 1)} (not enough); {n} gives ${have + prof * n} ✓"],
                   "For \"at least\" goals, round up to the next whole number.")
    m1, b1, m2, b2 = nz(r, -3, 3), r.randint(-3, 3), nz(r, -3, 3), r.randint(2, 8)
    if m1 == m2: return None
    ok = lambda x, y: y > m1 * x + b1 and y <= m2 * x + b2
    pts = [(x, y) for x in range(-3, 5) for y in range(-6, 10)]
    good = [p for p in pts if ok(*p)]; bad = [p for p in pts if not ok(*p)]
    if not good or len(bad) < 3: return None
    g = r.choice(good); bs = r.sample(bad, 3); f = lambda p: f"({p[0]}, {p[1]})".replace("-", "−")
    return MC(f"y > {lin(m1, b1)}\ny ≤ {lin(m2, b2)}\nWhich point (x, y) is a solution to the system of inequalities above?",
              [f(g)] + [f(b) for b in bs],
              ["A solution must make both inequalities true.",
               f"Test {f(g)}: {g[1]} > {S(m1 * g[0] + b1)} ✓ and {g[1]} ≤ {S(m2 * g[0] + b2)} ✓.".replace("-", "−"),
               "Each other point fails at least one of the inequalities when its coordinates are substituted."],
              "Test each point in every inequality; one failure rules it out.")

# ================================================================ ADVANCED MATH
def ee(r, d):
    if d == 1:
        a = r.randint(2, 6); b = r.randint(2, 6); c = r.randint(1, 9); dd = r.randint(1, 12)
        if a * b == dd: dd += 1
        corr = lin(a * b - dd, -a * c)
        return MC(f"Which expression is equivalent to {a}({lin(b, -c)}) − {coef(dd, 'x')}?",
                  pick4(corr, [lin(a * b - dd, -c), lin(a * b + dd, -a * c), lin(b - dd, -a * c)], [lin(a * b - dd, a * c)]),
                  [f"Distribute the {a}: {lin(a * b, -a * c)} − {coef(dd, 'x')}.", f"Combine like terms: {a * b}x − {dd}x = {coef(a * b - dd, 'x')}.",
                   f"Result: {corr}.", f"Trap: {lin(a * b - dd, -c)} forgets to multiply {c} by {a}."],
                  "Distribute to every term inside the parentheses before combining.")
    if d == 2:
        if r.random() < 0.5:
            p = r.randint(1, 4); q = nz(r, -7, 7); rr = nz(r, -7, 7); B = p * rr + q
            if B == 0: return None
            corr = quad(p, B, q * rr)
            return MC(f"Which expression is equivalent to ({lin(p, q)})({lin(1, rr)})?",
                      pick4(corr, [quad(p, -B, q * rr) if B else quad(p, 1, q * rr), quad(p, 0, q * rr) if q * rr else quad(p, B + 1, 0), quad(p, p * rr - q, q * rr), quad(p, B, -q * rr)], [quad(p + 1, B, q * rr)]),
                      [f"Multiply each pair: {coef(p, 'x')}·x = {coef(p, 'x²')}, {coef(p, 'x')}·{par(rr)} = {coef(p * rr, 'x')}, {S(q)}·x = {coef(q, 'x')}, {S(q)}·{par(rr)} = {S(q * rr)}.",
                       f"Combine the middle terms: {S(p * rr)}x + {par(q)}x = {coef(B, 'x')}.", f"Result: {corr}."],
                      "Multiply every term by every term, then combine like terms.")
        k = r.randint(2, 12); s = r.choice([1, -1]); corr = f"(x {'+' if s > 0 else '−'} {k})²"
        return MC(f"Which expression is equivalent to {quad(1, 2 * k * s, k * k)}?",
                  [corr, f"(x {'−' if s > 0 else '+'} {k})²", f"(x − {k})(x + {k})", f"(x {'+' if s > 0 else '−'} {k * k})²"],
                  [f"x² = (x)² and {k * k} = ({k})², so check for a perfect square.",
                   f"The middle term {'+' if s > 0 else '−'}{2 * k}x equals {'+' if s > 0 else '−'}2(x)({k}).", f"So the expression is {corr}.",
                   f"(x − {k})(x + {k}) = x² − {k * k}, which has no middle term."],
                  "If the first and last terms are squares and the middle is twice their product, it's a perfect square.")
    if r.random() < 0.5:
        a, b, c = r.randint(2, 7), r.randint(-4, 3), r.randint(1, 8)
        if b == 0: b = -2
        n = a + b - c
        corr = xpow(n)
        wrongs = [xpow(a * b - c), xpow(a + b + c), xpow(a - b - c), xpow(n + 1), xpow(-n)]
        return MC(f"Which expression is equivalent to ({pw('x', a)} · {pw('x', b)}) / {pw('x', c)}, for x ≠ 0?", pick4(corr, wrongs, [xpow(n + 2), xpow(n - 1)]),
                  [f"Multiplying powers with the same base: add exponents. {pw('x', a)} · {pw('x', b)} = {pw('x', a + b)}.",
                   f"Dividing: subtract exponents. {pw('x', a + b)} / {pw('x', c)} = {pw('x', n)}.",
                   (f"A negative exponent means a reciprocal: {pw('x', n)} = {corr}." if n < 0 else f"Result: {corr}.")],
                  "Multiply → add exponents; divide → subtract exponents; negative exponent → reciprocal.")
    m, n = r.randint(2, 7), r.randint(1, 9)
    if math.gcd(m, n) != 1: return None
    corr = f"({m}x − {n})({m}x + {n})"
    return MC(f"Which expression is equivalent to {m * m}x² − {n * n}?",
              [corr, f"({m}x − {n})²", f"({m * m}x − {n})({m * m}x + {n})", f"({m}x − {n * n})({m}x + 1)"],
              [f"Both terms are perfect squares: {m * m}x² = ({m}x)² and {n * n} = ({n})².",
               "A difference of squares factors as a² − b² = (a − b)(a + b).", f"So {m * m}x² − {n * n} = {corr}.",
               f"Check: ({m}x)² − ({n})² = {m * m}x² − {n * n} ✓"], "a² − b² = (a − b)(a + b).")

def ne(r, d):
    if d == 1:
        if r.random() < 0.4:
            k = r.randint(3, 15)
            return SPR(f"x² = {k * k}\nIf x > 0, what is the value of x?", k,
                       [f"Take the square root of both sides: x = {k} or x = −{k}.", f"The condition x > 0 rules out −{k}.", f"Answer: {k}."],
                       "x² = k has two solutions, ±√k; use the given condition to pick one.")
        a, b = r.randint(1, 12), r.randint(1, 12)
        return MC(f"What are the solutions to (x − {a})(x + {b}) = 0?",
                  pick4(f"{a} and −{b}", [f"−{a} and {b}", f"{a} and {b}", f"−{a} and −{b}"], []),
                  ["A product is zero when at least one factor is zero.", f"x − {a} = 0 gives x = {a}.", f"x + {b} = 0 gives x = −{b}.",
                   "The signs flip from the factors."], "Zero-product property: set each factor equal to 0.")
    if d == 2:
        if r.random() < 0.5:
            a = nz(r, -9, 12); b = r.randint(2, 9); x = b * b - a
            return SPR(f"√(x{plus(a)}) = {b}\nWhat is the solution to the equation above?", x,
                       [f"Square both sides: x{plus(a)} = {b * b}.", f"Solve: x = {S(x)}.", f"Check: √({S(x)}{plus(a)}) = √{b * b} = {b} ✓",
                        "Always check radical equations; squaring can create false solutions."],
                       "Isolate the radical, square both sides, then check in the original.")
        p, q = r.randint(1, 12), r.randint(1, 12)
        if p == q: return None
        B, C = q - p, -p * q
        return SPR(f"{quad(1, B, C)} = 0\nWhat is the positive solution to the equation above?", p,
                   [f"Find two numbers that multiply to {S(C)} and add to {S(B)}: {S(-p)} and {S(q)}.", f"Factor: (x − {p})(x + {q}) = 0.",
                    f"Solutions: x = {p} or x = −{q}.", f"The positive solution is {p}."], "Factor by finding two numbers with product c and sum b.")
    if r.random() < 0.5:
        r1, r2 = r.sample([v for v in range(-5, 7) if v], 2); m, n = r1 + r2, -r1 * r2
        if m == 0: return None
        cand = [x for x in range(-6, 8) if x not in (r1, r2)]
        corr = r.choice([r1, r2])
        return MC(f"y = x²\ny = {lin(m, n)}\nThe graphs of the equations above intersect at two points. Which of the following is the x-coordinate of one of those points?",
                  [S(corr)] + [S(c) for c in r.sample(cand, 3)],
                  [f"At an intersection the y-values are equal: x² = {lin(m, n)}.", f"Rearrange: {quad(1, -m, -n)} = 0.",
                   f"Factor: (x{plus(-r1)})(x{plus(-r2)}) = 0, so x = {S(r1)} or x = {S(r2)}.",
                   f"Check x = {S(corr)}: x² = {S(corr * corr)} and {S(m)}{mp(corr)}{plus(n)} = {S(m * corr + n)} ✓"],
                  "To find intersections, set the expressions for y equal and solve.")
    a = r.randint(2, 5); p = r.randint(1, 6); s = r.randint(1, 9)
    if math.gcd(a, s) != 1: return None
    # (a x + s)(x − p) = a x² + (s − a p) x − s p
    B, C = s - a * p, -s * p
    return SPR(f"{quad(a, B, C)} = 0\nIf x > 0, what is the solution to the equation above?", p,
               [f"Look for two numbers that multiply to {a} × {par(C)} = {S(a * C)} and add to {S(B)}: {S(-a * p)} and {S(s)}.",
                f"Factor: ({lin(a, s)})(x − {p}) = 0.", f"Solutions: x = {S(Fr(-s, a))} or x = {p}.", f"With x > 0, x = {p}.",
                f"Check: {a}({p * p}){plus(B * p)}{plus(C)} = 0 ✓"],
               "For ax² + bx + c with a ≠ 1, split the middle term using two numbers that multiply to ac.")

CTX_EXP = [("the value, in dollars, of a car t years after it was bought", "value", "year"),
           ("the number of fish in a lake t years after a study began", "number of fish", "year"),
           ("the amount, in milligrams, of a medicine in a patient's bloodstream t hours after a dose", "amount", "hour"),
           ("the balance, in dollars, of a savings account t years after it was opened", "balance", "year"),
           ("the population of a town t years after 2020", "population", "year")]
def nf(r, d):
    if d == 1:
        if r.random() < 0.5:
            b, n = r.choice([(2, r.randint(3, 7)), (3, r.randint(2, 4)), (5, r.randint(2, 3)), (10, r.randint(2, 4))])
            v = b ** n
            return MC(f"The function f is defined by f(x) = {b}ˣ. What is the value of f({n})?", pick4(S(v), [S(b * n), S(n ** b), S(b + n)], numpad(v)),
                      [f"f({n}) = {pw(str(b), n)}.", f"Multiply {b} by itself {n} times: {v}.", f"Trap: {b * n} is {b} × {n}, which is multiplication, not an exponent."],
                      "bˣ means multiply b by itself x times.")
        b, c, k = nz(r, -6, 6), nz(r, -9, 9), r.randint(-4, 5); v = k * k + b * k + c
        return MC(f"The function g is defined by g(x) = {quad(1, b, c)}. What is the value of g({S(k)})?",
                  pick4(S(v), [S(-k * k + b * k + c), S(2 * k + b * k + c), S(k * k + b + c)], numpad(v)),
                  [f"Substitute {S(k)}: g({S(k)}) = {mp(k)}² {'+' if b > 0 else '−'} {'' if abs(b) == 1 else str(abs(b))}{mp(k)}{plus(c)}.",
                   f"Square first: {par(k)}² = {S(k * k)}.", f"Then: {S(k * k)}{plus(b * k)}{plus(c)} = {S(v)}."],
                  "Substitute, then follow the order of operations: exponents before multiplication.")
    if d == 2:
        ctx, noun, per = r.choice(CTX_EXP); rate = r.choice([5, 8, 10, 12, 15, 20, 25, 30]); up = r.random() < 0.5 and noun != "amount"
        P0 = r.choice([500, 1200, 2400, 8000, 15000, 24000]); fac = Fr(100 + rate, 100) if up else Fr(100 - rate, 100)
        corr = f"The {noun} {'increases' if up else 'decreases'} by {rate}% each {per}."
        return MC(f"The function f(t) = {P0:,}({D(fac, 2)})ᵗ models {ctx}. Which statement best describes how the {noun} changes?",
                  [corr, f"The {noun} {'increases' if up else 'decreases'} by {S(fac * 100)}% each {per}.",
                   f"The {noun} {'decreases' if up else 'increases'} by {rate}% each {per}.", f"The {noun} {'increases' if up else 'decreases'} by {rate} each {per}."],
                  [f"The form a(b)ᵗ is exponential with factor b = {D(fac, 2)}.",
                   f"Since {D(fac, 2)} is {'greater' if up else 'less'} than 1, the {noun} {'increases' if up else 'decreases'}.",
                   f"Each {per} the {noun} is multiplied by {D(fac, 2)}, which is {S(fac * 100)}% of the previous value: a {rate}% {'increase' if up else 'decrease'}.",
                   f"Trap: {S(fac * 100)}% is the {'new total' if up else 'amount kept'}, not the change."],
                  "In a(1 ± r)ᵗ, r is the percent change per period; the factor itself is the percent of the previous value.")
    if r.random() < 0.5:
        h = r.randint(-6, 7); k = r.randint(-9, 12); B, C = -2 * h, h * h + k
        if B == 0: return None
        return SPR(f"y = {quad(1, B, C)}\nWhat is the minimum value of y for the equation above?", k,
                   ["The parabola opens upward (positive x² term), so its vertex gives the minimum.",
                    f"Vertex x-coordinate: x = −b/(2a) = {S(-B)}/2 = {S(h)}.", f"Substitute x = {S(h)}: y = {S(h * h)}{plus(B * h)}{plus(C) if C else ''} = {S(k)}.",
                    f"Or complete the square: y = (x{plus(-h)})²{plus(k)}.", f"Minimum value: {S(k)}."],
                   "For an upward parabola, the minimum is the y-value at x = −b/(2a).")
    a = r.choice([2, 3, 4, 5, 6, 10]); b = r.choice([2, 3, 4]); n = r.randint(3, 4)
    return SPR(f"For the exponential function f, f(x) = a · bˣ, where a and b are positive constants. If f(0) = {a} and f(1) = {a * b}, what is the value of f({n})?", a * b ** n,
               [f"f(0) = a · b⁰ = a, so a = {a}.", f"f(1) = a · b = {a * b}, so b = {a * b} ÷ {a} = {b}.", f"f(x) = {a} · {b}ˣ.",
                f"f({n}) = {a} · {pw(str(b), n)} = {a} · {b ** n} = {a * b ** n}."], "f(0) gives the starting value a; f(1) ÷ f(0) gives the growth factor b.")

# ================================================================ PROBLEM-SOLVING & DATA
RATE = [("A car travels {a} miles in {t} hours at a constant speed. At this speed, how many miles will it travel in {u} hours?", "miles per hour"),
        ("A pump fills {a} liters in {t} minutes at a constant rate. At this rate, how many liters will it fill in {u} minutes?", "liters per minute"),
        ("A typist types {a} words in {t} minutes. At this rate, how many words will the typist type in {u} minutes?", "words per minute"),
        ("A machine packs {a} boxes in {t} hours. At this rate, how many boxes will it pack in {u} hours?", "boxes per hour")]
def rr_(r, d):
    if d == 1:
        tpl, unit = r.choice(RATE); rate = r.randint(4, 60); t = r.randint(2, 6); u = r.randint(2, 9)
        if u == t: u += 1
        return SPR(tpl.format(a=rate * t, t=t, u=u), rate * u,
                   [f"Find the unit rate: {rate * t} ÷ {t} = {rate} {unit}.", f"Multiply by {u}: {rate} × {u} = {rate * u}."], "Find the unit rate first, then scale it.")
    if d == 2:
        if r.random() < 0.5:
            conv = r.choice([("centimeters", "inches", Fr(254, 100), "2.54 centimeters in 1 inch"), ("kilograms", "pounds", None, None)])
            if conv[2]:
                cm = r.randint(10, 120); v = Fr(cm) / conv[2]
                return MC(f"There are {conv[3]}. Which of the following is closest to the number of inches in {cm} centimeters?",
                          pick4(D1(v), [D1(cm * conv[2]), D1(cm - Fr(254, 100)), D1(v * 2)], [D1(v + 1)]),
                          [f"Set up the conversion so centimeters cancel: {cm} cm × (1 in / 2.54 cm).", f"Compute: {cm} ÷ 2.54 ≈ {D(v, 1)} inches.",
                           "An inch is longer than a centimeter, so there must be fewer inches than centimeters."],
                          "Write units in the conversion factor so the unit you don't want cancels.")
            kg = r.randint(5, 90); lb = kg * Fr(22, 10)
            return MC(f"One kilogram is approximately 2.2 pounds. Which of the following is closest to the weight, in pounds, of a {kg}-kilogram package?",
                      pick4(D1(lb), [D1(Fr(kg) / Fr(22, 10)), D1(kg + Fr(22, 10)), D1(lb * 2)], [D1(lb + 1)]),
                      [f"Pounds = kilograms × 2.2.", f"{kg} × 2.2 = {D1(lb)} pounds.", "A kilogram is heavier than a pound, so the number of pounds must be larger."],
                      "Check that the converted number is larger when converting to a smaller unit.")
        sc = r.choice([5, 10, 20, 25, 40, 50]); dist = Fr(r.randint(12, 95), 10)
        return SPR(f"On a map, 1 centimeter represents {sc} kilometers. Two towns are {D(dist, 1)} centimeters apart on the map. What is the actual distance, in kilometers, between the towns?", dist * sc,
                   [f"Scale: 1 cm on the map = {sc} km.", f"Multiply: {D(dist, 1)} × {sc} = {S(dist * sc) if (dist * sc).denominator == 1 else D(dist * sc, 1)}."],
                   "Map distance × scale factor = actual distance.")
    if r.random() < 0.5:
        ppm = r.choice([12, 15, 18, 20, 24, 30, 36]); pages = Fr(ppm) * r.choice([Fr(1, 2), Fr(3, 2), Fr(5, 2), Fr(3, 4), Fr(5, 4), 2, 3])
        if pages.denominator != 1: return None
        sec = pages / ppm * 60
        return SPR(f"A printer prints {ppm} pages per minute. At this rate, how many seconds does it take to print {S(pages)} pages?", sec,
                   [f"Time in minutes: {S(pages)} ÷ {ppm} = {S(pages / ppm) if (pages / ppm).denominator == 1 else D(pages / ppm, 2)} minutes.",
                    f"Convert to seconds: × 60 = {S(sec)} seconds.", "Check the unit the question asks for."], "Check the units in the question; convert at the end.")
    cover = r.choice([250, 300, 350, 400]); hgt = r.randint(8, 12); ln = r.randint(20, 60); coats = r.choice([1, 2, 2, 3]); need = Fr(hgt * ln * coats, cover)
    g = math.ceil(need)
    if need.denominator == 1: return None
    return MC(f"One gallon of paint covers {cover} square feet. A wall is {hgt} feet high and {ln} feet long and needs {coats} coat{'s' if coats > 1 else ''} of paint. If paint is sold only in whole gallons, what is the minimum number of gallons needed?",
              pick4(S(g), [S(g - 1), S(math.ceil(Fr(hgt * ln, cover))), S(g + coats)], numpad(g)),
              [f"Wall area: {hgt} × {ln} = {hgt * ln} square feet.", f"For {coats} coat{'s' if coats > 1 else ''}: {hgt * ln} × {coats} = {hgt * ln * coats} square feet.",
               f"Gallons: {hgt * ln * coats} ÷ {cover} ≈ {D(need, 2)}.", f"Round up because only whole gallons are sold: {g}."],
              "Account for every factor (like the number of coats), then round up when you can't buy part of a unit.")

def pc(r, d):
    if d == 1:
        p = r.choice([5, 10, 15, 20, 25, 30, 40, 45, 60, 75]); n = r.randint(2, 30) * 20
        return SPR(f"What is {p}% of {n}?", Fr(p * n, 100), [f"Convert the percent: {p}% = {D(Fr(p, 100), 2)}.", f"Multiply: {D(Fr(p, 100), 2)} × {n} = {S(Fr(p * n, 100))}."],
                   "\"Percent of\" means multiply by the decimal form.")
    if d == 2:
        if r.random() < 0.5:
            a = r.randint(4, 40) * 50; ch = r.choice([10, 12, 15, 20, 25, 30, 40, 50, 60, 75]); up = r.random() < 0.5; b = a * (100 + ch) // 100 if up else a * (100 - ch) // 100
            if (a * ch) % 100: return None
            word = "increase" if up else "decrease"
            return MC(f"The number of visitors to a museum changed from {a:,} one year to {b:,} the next year. What was the percent {word}?",
                      pick4(f"{ch}%", [pct(Fr(abs(b - a) * 100, b)), f"{abs(b - a)}%", pct(Fr(b * 100, a))], [f"{ch + 5}%"]),
                      [f"Amount of change: {max(a, b):,} − {min(a, b):,} = {abs(b - a):,}.", f"Divide by the original value: {abs(b - a):,} ÷ {a:,} = {D(Fr(ch, 100), 2)}.",
                       f"{D(Fr(ch, 100), 2)} = {ch}%.", "Trap: dividing by the new value instead of the original gives a different, wrong percent."],
                      "Percent change always divides by the original (starting) value.")
        disc = r.choice([10, 15, 20, 25, 30, 40]); orig = r.randint(4, 40) * 20
        if (orig * disc) % 100: return None
        price = Fr(orig * (100 - disc), 100)
        return SPR(f"After a {disc}% discount, a jacket costs ${S(price)}. What was the original price, in dollars?", orig,
                   [f"After a {disc}% discount, the price is {100 - disc}% of the original: {D(Fr(100 - disc, 100), 2)}p = {S(price)}.",
                    f"Divide: p = {S(price)} ÷ {D(Fr(100 - disc, 100), 2)} = {orig}.", f"Check: {disc}% of ${orig} is ${S(Fr(orig * disc, 100))}, and ${orig} − ${S(Fr(orig * disc, 100))} = ${S(price)} ✓",
                    f"Trap: adding {disc}% of ${S(price)} back on gives the wrong answer, because the {disc}% was taken from the original price."],
                   "To undo a percent change, divide by the multiplier.")
    if r.random() < 0.5:
        a = r.choice([10, 20, 25, 30, 40, 50]); b = r.choice([10, 20, 25, 30, 40, 50]); f = Fr(100 + a, 100) * Fr(100 - b, 100); net = (f - 1) * 100
        if net == 0: return None
        desc = (pct(abs(net)) + (" less" if net < 0 else " more"))
        return MC(f"The price of an item is increased by {a}%. Later, the new price is decreased by {b}%. Compared with the original price, the final price is",
                  pick4(desc, [pct(abs(a - b)) + (" less" if a < b else " more") if a != b else "the same", "the same", pct(abs(net)) + (" more" if net < 0 else " less")],
                        [pct(abs(net) + 1) + " less"]),
                  [f"An increase of {a}% multiplies by {D(Fr(100 + a, 100), 2)}; a decrease of {b}% multiplies by {D(Fr(100 - b, 100), 2)}.",
                   f"Combined: {D(Fr(100 + a, 100), 2)} × {D(Fr(100 - b, 100), 2)} = {D(f, 4).rstrip('0').rstrip('.')}.",
                   f"So the final price is {pct(f * 100)} of the original: {desc}.", "Trap: successive percents multiply; you cannot just add or subtract them."],
                  "Successive percent changes multiply.")
    a = r.choice([10, 20, 25, 40, 50, 60, 75, 80]); b = r.choice([10, 20, 25, 40, 50, 60, 75, 80]); res = Fr(a * b, 100)
    return MC(f"The value of x is {a}% of y, and y is {b}% of z. The value of x is what percent of z?",
              pick4(pct(res), [f"{a + b}%", pct(Fr(a, b) * 100) if a != b else f"{abs(a - b) + 5}%", f"{abs(a - b)}%"], [pct(res + 5), pct(res * 2)]),
              [f"Write as equations: x = {D(Fr(a, 100), 2)}y and y = {D(Fr(b, 100), 2)}z.", f"Substitute: x = {D(Fr(a, 100), 2)} × {D(Fr(b, 100), 2)}z = {D(res / 100, 4).rstrip('0').rstrip('.')}z.",
               f"So x is {pct(res)} of z.", "Trap: adding the percents instead of multiplying them."], "A percent of a percent: multiply the decimals.")

def ov(r, d):
    if d == 1:
        if r.random() < 0.5:
            n = r.randint(4, 6); mean = r.randint(6, 40); vals = [r.randint(1, 60) for _ in range(n - 1)]; last = mean * n - sum(vals)
            if last < 1 or last > 99: return None
            vals.append(last); r.shuffle(vals)
            return SPR(f"What is the mean of the data set {', '.join(map(str, vals))}?", mean,
                       [f"Add the values: {' + '.join(map(str, vals))} = {sum(vals)}.", f"Divide by the number of values: {sum(vals)} ÷ {n} = {mean}."], "Mean = sum ÷ count.")
        vals = r.sample(range(1, 40), r.choice([5, 7])); srt = sorted(vals); med = srt[len(srt) // 2]; mean = Fr(sum(vals), len(vals))
        return MC(f"What is the median of the data set {', '.join(map(str, vals))}?",
                  pick4(S(med), [S(vals[len(vals) // 2]), D(mean, 1) if mean.denominator != 1 else S(mean), S(srt[-1] - srt[0])], numpad(med)),
                  [f"Order the values: {', '.join(map(str, srt))}.", f"There are {len(vals)} values, so the median is value number {len(vals) // 2 + 1}.", f"Median = {med}.",
                   "Trap: the middle of the unordered list is not the median."], "Always put the data in order before finding the median.")
    if d == 2:
        n = r.randint(4, 7); mean = r.randint(8, 30); known = [r.randint(2, 45) for _ in range(n - 1)]; miss = mean * n - sum(known)
        if miss < 0: return None
        return SPR(f"The mean of {n} numbers is {mean}. {n - 1} of the numbers are {', '.join(map(str, known[:-1]))}, and {known[-1]}. What is the remaining number?", miss,
                   [f"Sum of all {n} numbers = mean × count = {mean} × {n} = {mean * n}.", f"Sum of the known numbers: {sum(known)}.", f"Remaining number: {mean * n} − {sum(known)} = {miss}."],
                   "Mean × count gives the total; subtract what you know to find what's missing.")
    if r.random() < 0.5:
        n = r.randint(12, 30); m = r.randint(65, 85); new = r.randint(60, 100); tot = n * m + new
        if tot % (n + 1): return None
        nm = tot // (n + 1)
        return MC(f"The mean score of {n} students on a test is {m}. A new student takes the test and scores {new}. What is the mean score of all {n + 1} students?",
                  pick4(S(nm), [D(Fr(m + new, 2), 1) if (m + new) % 2 else S(Fr(m + new, 2)), S(m), S(nm + 1)], numpad(nm)),
                  [f"Total of the {n} scores: {n} × {m} = {n * m}.", f"Add the new score: {n * m} + {new} = {tot}.", f"New mean: {tot} ÷ {n + 1} = {nm}.",
                   f"Trap: averaging {m} and {new} treats one student as equal to {n} students."], "To update a mean, work with totals: new total ÷ new count.")
    c = r.randint(20, 60); s1, s2 = r.choice([(10, 2), (8, 1), (12, 3), (15, 2), (6, 1)])
    A_ = [c - 2 * s1, c - s1, c, c + s1, c + 2 * s1]; B_ = [c - 2 * s2, c - s2, c, c + s2, c + 2 * s2]
    sw = r.random() < 0.5
    X, Y = (B_, A_) if sw else (A_, B_)
    small = "A" if sw else "B"; big = "B" if sw else "A"
    return MC(f"Data set A: {', '.join(map(str, X))}\nData set B: {', '.join(map(str, Y))}\nWhich statement correctly compares the two data sets?",
              [f"They have the same mean, and data set {small} has a smaller standard deviation.", f"They have the same mean, and data set {big} has a smaller standard deviation.",
               f"Data set {small} has a greater mean than data set {big}.", "They have the same standard deviation."],
              [f"Mean of each set: {5 * c} ÷ 5 = {c}. The means are equal.", "Standard deviation measures how spread out the values are around the mean.",
               f"Data set {small}'s values are much closer to {c} than data set {big}'s.", f"So data set {small} has the smaller standard deviation."],
              "Standard deviation is about spread around the mean; compare it without calculating.")

ASSOC = [("hours of practice", "number of errors", -1), ("outdoor temperature", "ice cream sales", 1), ("age of a car", "its resale value", -1),
         ("hours studied", "test score", 1), ("distance from the city center", "monthly rent", -1), ("number of trees on a street", "shade coverage", 1),
         ("altitude", "air temperature", -1), ("height of students", "number of siblings", 0), ("shoe size of adults", "favorite number", 0)]
MODEL = [("y is the predicted height, in centimeters, of a plant x weeks after planting", "The predicted height increases by {m} centimeters each week", "The plant was {b} centimeters tall when planted", "week"),
         ("y is the predicted number of visitors to a website x days after launch", "The predicted number of visitors increases by {m} each day", "There were {b} predicted visitors at launch", "day"),
         ("y is the predicted price, in dollars, of a used laptop that is x years old", "The predicted price decreases by ${m} for each additional year of age", "A new laptop (0 years old) is predicted to cost ${b}", "year")]
def tv(r, d):
    if d == 1:
        a, b_, s = r.choice(ASSOC)
        stem = (f"A scatterplot shows that as {a} increased, {b_} tended to {'increase' if s > 0 else 'decrease'}." if s else
                f"A scatterplot of {a} and {b_} for a group of people shows points scattered with no upward or downward trend.")
        corr = {1: "Positive association", -1: "Negative association", 0: "No association"}[s]
        return MC(stem + f" Which best describes the association between {a} and {b_}?", pick4(corr, ["Positive association", "Negative association", "No association", "Exponential growth"], []),
                  ["Positive: both variables tend to increase together.", "Negative: one tends to decrease as the other increases.", "No association: no clear trend.", f"Here: {corr.lower()}."],
                  "Read the direction of the trend, not the size of the numbers.")
    if d == 2:
        if r.random() < 0.5:
            tpl, ms, bs, unit = r.choice(MODEL); m = Fr(r.randint(5, 60), 2); b = r.randint(10, 300) * (5 if "price" in tpl else 1)
            neg = "price" in tpl
            eq = f"y = {D1(-m if neg else m).replace('-', '−')}x + {b}"
            corr = ms.format(m=D(m, 1).rstrip('0').rstrip('.'), b=b)
            return MC(f"A line of best fit for a scatterplot is {eq}, where {tpl}. What is the best interpretation of {D(-m if neg else m, 1).replace('-', '−').rstrip('0').rstrip('.')} in this context?",
                      pick4(corr, [bs.format(m=D(m, 1), b=b), f"The predicted value after {D(m, 1).rstrip('0').rstrip('.')} {unit}s", f"The actual value is always {D(m, 1).rstrip('0').rstrip('.')} more than predicted"], []),
                      ["In y = mx + b, the slope m is the change in y for each 1-unit increase in x.", f"Here x is measured in {unit}s.", f"So the slope means: {corr[0].lower() + corr[1:]}."],
                      "Slope = change in y per 1 unit of x; intercept = y when x = 0.")
        m = nz(r, -8, 8); b = r.randint(20, 150); x = r.randint(3, 15); v = m * x + b
        return SPR(f"The model y = {lin(m, b)} predicts the number of tickets, y, still available x hours after a concert's tickets go on sale. According to the model, how many tickets are still available {x} hours after tickets go on sale?", v,
                   [f"Substitute x = {x}: y = {S(m)}({x}){plus(b)}.", f"Compute: {S(m * x)}{plus(b)} = {S(v)}."], "To use a model, substitute the given input and evaluate.") if m < 0 and v > 0 else None
    if r.random() < 0.5:
        m = Fr(r.choice([k for k in range(2, 16) if k != 10]), 10); b = Fr(r.randint(5, 50), 10); x = r.randint(2, 7); pred = m * x + b; act = pred + Fr(r.choice([-18, -12, -8, -5, 4, 6, 9, 14]), 10)
        if act < 0 or act > 10: return None
        return SPR(f"The line of best fit y = {D(m, 1)}x + {D(b, 1)} models the quiz score y, out of 10, for a student who studied x hours. One student studied {x} hours and scored {D(act, 1).rstrip('0').rstrip('.')}. What is the student's actual score minus the score predicted by the model?", act - pred,
                   [f"Predicted score: {D(m, 1)}({x}) + {D(b, 1)} = {D(pred, 1)}.", f"Actual score: {D(act, 1)}.", f"Actual − predicted = {D(act, 1)} − {D(pred, 1)} = {D(act - pred, 1).replace('-', '−')}.",
                    f"A {'positive' if act > pred else 'negative'} difference means the point lies {'above' if act > pred else 'below'} the line."],
                   "Residual = actual − predicted. Positive means above the line; negative means below.")
    expo = r.random() < 0.5; a0 = r.choice([100, 200, 400, 500, 800]); g = r.choice([Fr(11, 10), Fr(12, 10), Fr(3, 2), 2])
    if expo:
        ys = [a0 * g ** k for k in range(4)]
        if any(y.denominator != 1 for y in ys): return None
        corr = f"y = {a0}({D(g, 1) if g.denominator != 1 else S(g)})ˣ"; lin_ = f"y = {a0} + {S(ys[1] - ys[0])}x"
    else:
        step = r.choice([20, 40, 50, 60]); ys = [a0 + step * k for k in range(4)]; corr = f"y = {a0} + {step}x"; lin_ = f"y = {a0}({D(Fr(a0 + step, a0), 2)})ˣ"
    return MC(f"The table shows the number of members in a club at the start of each year. Which function best models the number of members, y, x years after year 0?",
              pick4(corr, [lin_, f"y = {a0}(0.9)ˣ", f"y = {S(ys[1])}x"], []),
              [f"Differences: {', '.join(S(ys[k + 1] - ys[k]) for k in range(3))}. " + ("Not constant, so not linear." if expo else "Constant, so linear."),
               f"Ratios: {', '.join(D(Fr(ys[k + 1], ys[k]), 2) for k in range(3))}. " + ("Constant, so exponential." if expo else "Not constant, so not exponential."),
               f"Starting value {a0} gives {corr}.", "y = 0.9ˣ would mean a decrease, and a model of the form y = kx gives 0 members at year 0."],
              "Constant differences → linear. Constant ratios → exponential.",
              table={"caption": "Club members", "head": ["Year", "Members"], "rows": [[str(k), S(y)] for k, y in enumerate(ys)]})

def pr(r, d):
    if d == 1:
        if r.random() < 0.5:
            cols = r.sample(["red", "blue", "green", "yellow", "white", "black"], 3); n = [r.randint(2, 12) for _ in cols]; t = sum(n); k = r.randrange(3); p = Fr(n[k], t)
            return MC(f"A bag contains {n[0]} {cols[0]}, {n[1]} {cols[1]}, and {n[2]} {cols[2]} marbles. One marble is chosen at random. What is the probability that it is {cols[k]}?",
                      pick4(S(p), [S(Fr(n[k], t - n[k])), S(Fr(1, 3)), S(Fr(t - n[k], t))], [S(Fr(n[k], t + 1))]),
                      [f"Total marbles: {' + '.join(map(str, n))} = {t}.", f"{cols[k].capitalize()} marbles: {n[k]}.", f"Probability = {n[k]}/{t}" + (f" = {S(p)}." if p.denominator != t else ".")],
                      "Probability = favorable outcomes ÷ total outcomes.")
        sides = r.choice([6, 8, 10, 12]); k = r.randint(2, sides - 2); p = Fr(sides - k, sides)
        return SPR(f"A spinner has {sides} equal sections numbered 1 through {sides}. The spinner is spun once. What is the probability that it lands on a number greater than {k}? (Enter a fraction or decimal.)", p,
                   [f"Numbers greater than {k}: {k + 1} through {sides}, which is {sides - k} outcomes.", f"Total outcomes: {sides}.", f"Probability = {sides - k}/{sides}" + (f" = {S(p)}." if p.denominator != sides else "."),
                    f"Note: \"greater than {k}\" does not include {k}."], "Count carefully: \"greater than\" excludes the number itself.")
    a, b, c, e = [r.randint(8, 60) for _ in range(4)]
    rows = [["Grade 11", str(a), str(b), str(a + b)], ["Grade 12", str(c), str(e), str(c + e)], ["Total", str(a + c), str(b + e), str(a + b + c + e)]]
    tab = {"caption": "Preferred lunch option", "head": ["", "Hot meal", "Salad bar", "Total"], "rows": rows}
    if d == 2:
        row = r.random() < 0.5
        if row:
            p = Fr(c, c + e)
            return MC(f"The table shows survey results from {a + b + c + e} students. If a grade 12 student from the survey is selected at random, what is the probability that the student prefers the hot meal?",
                      pick4(S(p), [S(Fr(c, a + b + c + e)), S(Fr(c, a + c)), S(Fr(e, c + e))], [S(Fr(c + 1, c + e))]),
                      [f"The condition is \"a grade 12 student\", so use only the grade 12 row: {c + e} students.", f"Grade 12 students preferring the hot meal: {c}.",
                       f"Probability = {c}/{c + e}" + (f" = {S(p)}." if p.denominator != c + e else "."), "Using the overall total or the column total answers a different question."],
                      "With \"from this group\", the group's total is the denominator.", table=tab)
        p = Fr(a, a + c)
        return SPR(f"The table shows survey results from {a + b + c + e} students. If a student who prefers the hot meal is selected at random, what is the probability that the student is in grade 11? (Enter a fraction or decimal.)", p,
                   [f"The condition is \"prefers the hot meal\", so use the Hot meal column total: {a + c}.", f"Of those, grade 11: {a}.", f"Probability = {a}/{a + c}" + (f" = {S(p)}." if p.denominator != a + c else ".")],
                   "Find the group named in the condition and use its total as the denominator.", table=tab)
    kind = r.choice(["coins2", "coins3", "dice"])
    if kind == "dice":
        return MC("Two fair six-sided dice are rolled. What is the probability that at least one die shows a 6?", ["11/36", "1/6", "1/3", "1/36"],
                  ["There are 6 × 6 = 36 equally likely outcomes.", "Outcomes with no 6: 5 × 5 = 25.", "P(at least one 6) = 1 − 25/36 = 11/36.",
                   "Trap: 1/3 adds 1/6 + 1/6, which counts the outcome (6, 6) twice."], "\"At least one\" = 1 − P(none).")
    n = 2 if kind == "coins2" else 3; face = r.choice(["head", "tail"]); p = 1 - Fr(1, 2 ** n)
    return MC(f"{'Two' if n == 2 else 'Three'} fair coins are flipped. What is the probability of getting at least one {face}?",
              pick4(S(p), [S(Fr(1, 2)), S(Fr(1, 2 ** n)), S(Fr(n, n + 1))], [S(Fr(n, 2 ** n))]),
              [f"There are 2^{n} = {2 ** n} equally likely outcomes.", f"Only one outcome has no {face}s.", f"P(at least one {face}) = 1 − 1/{2 ** n} = {S(p)}."],
              "\"At least one\" = 1 − P(none).")

POPS = [("students at a high school", "a list of all students at the school"), ("residents of a town", "the town's list of all households"),
        ("employees of a large company", "the company's list of all employees"), ("members of a public library", "the library's list of all members")]
SURV = ["how many hours per week they spend reading", "how they usually travel to school or work", "whether they support a new park", "how many hours they sleep on weeknights"]
def ss(r, d):
    if d == 1:
        if r.random() < 0.5:
            n = r.choice([40, 50, 80, 100, 120, 200, 250, 400]); p = r.choice([15, 20, 25, 30, 35, 40, 45, 55, 60, 65, 70, 75, 80]); k = n * p // 100
            if n * p % 100: return None
            return SPR(f"In a random sample of {n} voters in a city, {k} support a proposal. What percent of the sample supports the proposal?", p,
                       [f"Fraction supporting: {k} ÷ {n} = {D(Fr(p, 100), 2)}.", f"Convert to a percent: {p}%."], "Sample percent = part ÷ sample size × 100.")
        pop, lst = r.choice(POPS); q = r.choice(SURV)
        return MC(f"A researcher wants to estimate {q} among {pop}. Which sampling method is most likely to produce a representative sample?",
                  [f"Randomly selecting 100 people from {lst}", "Surveying the first 100 people who respond to an online post", f"Surveying people at a single location on one afternoon", "Asking the researcher's friends who belong to the group"],
                  ["A representative sample gives every member of the population an equal chance of being chosen.", "Random selection from a complete list does this.",
                   "Volunteers, one location, or friends are not random and may differ from the population."], "Random selection from the whole population avoids bias.")
    if d == 2:
        if r.random() < 0.5:
            est = r.randint(35, 75); moe = r.choice([2, 3, 4, 5]); inside = est + r.choice([-1, 1]) * r.randint(0, moe - 1)
            outs = [est - moe - r.randint(2, 6), est + moe + r.randint(1, 4), est + moe + r.randint(6, 12)]
            return MC(f"A survey of a random sample of residents estimates that {est}% of residents support building a new library, with a margin of error of {moe} percentage points. Which of the following is a plausible value for the percentage of all residents who support the library?",
                      [f"{inside}%"] + [f"{o}%" for o in outs],
                      [f"Plausible range: {est}% ± {moe}%, which is {est - moe}% to {est + moe}%.", f"Only {inside}% lies within that range."],
                      "Estimate ± margin of error gives the range of plausible values.")
        n = r.choice([50, 80, 100, 120, 150, 200]); k = r.randint(5, n // 2); N = n * r.randint(5, 40)
        est = Fr(k, n) * N
        if est.denominator != 1: return None
        return SPR(f"A school has {N:,} students. In a random sample of {n} of these students, {k} said they walk to school. Based on the sample, what is the best estimate of the number of students at the school who walk to school?", est,
                   [f"Sample proportion: {k} ÷ {n}.", f"Apply it to the population: ({k} ÷ {n}) × {N:,} = {S(est)}."], "A random sample's proportion estimates the population's proportion.")
    if r.random() < 0.5:
        a = r.choice([100, 200, 300]); b = a * r.choice([4, 9, 16])
        return MC(f"Two random samples are taken from the same population to estimate the mean commute time. Sample A has {a} people and sample B has {b:,} people. Which statement is most likely true?",
                  ["The margin of error for sample B is smaller than for sample A.", "The margin of error for sample A is smaller than for sample B.", "The two samples have the same margin of error.", "Sample B's estimate must equal the true population mean."],
                  ["Larger random samples give more precise estimates, so a smaller margin of error.", f"Sample B is {b // a} times larger, so its margin of error is smaller.", "No sample guarantees the exact population value."],
                  "Bigger random sample → smaller margin of error, but never zero.")
    m = Fr(r.randint(40, 90), 10); moe = Fr(r.choice([3, 4, 5, 6]), 10); n = r.choice([200, 300, 400, 500])
    return MC(f"A random sample of {n} seniors at one high school found a mean study time of {D(m, 1)} hours per week, with a margin of error of {D(moe, 1)} hours. Which conclusion is most appropriate?",
              [f"It is plausible that the mean study time of all seniors at that school is between {D(m - moe, 1)} and {D(m + moe, 1)} hours per week.",
               f"The mean study time of all high school seniors in the country is between {D(m - moe, 1)} and {D(m + moe, 1)} hours per week.",
               f"Every senior at the school studies between {D(m - moe, 1)} and {D(m + moe, 1)} hours per week.", f"The mean study time of all seniors at the school is exactly {D(m, 1)} hours per week."],
              [f"Range: {D(m, 1)} ± {D(moe, 1)} = {D(m - moe, 1)} to {D(m + moe, 1)} hours.", "The sample came from one school, so conclusions apply only to that school's seniors.",
               "The margin of error describes the mean, not every individual.", "The true mean is estimated, not known exactly."],
              "Generalize only to the population sampled, and only about the quantity estimated.")

OSX = [("adults in a city", "a daily 30-minute walking program", "walk for 30 minutes daily", "lower average blood pressure", "the walking program"),
       ("students in a school district", "weekly tutoring sessions", "attend tutoring sessions", "higher average test scores", "tutoring"),
       ("employees at a large company", "a flexible work schedule", "use a flexible schedule", "higher average job satisfaction", "a flexible schedule"),
       ("tomato plants at a farm", "a new fertilizer", None, "greater average fruit weight", "the new fertilizer"),
       ("teenagers in a town", "a sleep-education course", "have taken a sleep-education course", "more average sleep per night", "the sleep-education course"),
       ("patients at a clinic", "a new stretching routine", "do a stretching routine", "less reported back pain", "the stretching routine"),
       ("residents of a county", "a reading-for-pleasure challenge", "read for pleasure every day", "lower average stress scores", "daily reading"),
       ("high school athletes in a state", "a new warm-up routine", "use the new warm-up routine", "fewer injuries on average", "the new warm-up routine")]
def os_(r, d):
    if d == 1:
        ctx = r.choice([c for c in OSX if c[2]])
        others = [f"Researchers record how many hours students sleep and compare their grades.", "Researchers survey shoppers about how often they buy organic food.",
                  "Researchers count the birds at a lake each month for a year.", "Researchers compare the incomes of people who did and did not attend college."]
        return MC("Which of the following describes an experiment rather than an observational study?",
                  [f"Researchers randomly assign {ctx[0]} to {ctx[1]} or no program, then compare the results."] + r.sample(others, 3),
                  ["In an experiment, researchers assign a treatment to the subjects.", "In an observational study, researchers only measure what already happens.",
                   "Only the first choice assigns a treatment, and it does so randomly."], "Experiment = researchers assign the treatment. Observational = researchers just observe.")
    pop, treat, obs, out, short = r.choice(OSX)
    rs = r.random() < 0.5; ra = r.random() < 0.6 or obs is None
    if d == 3 and not (rs and ra) and r.random() < 0.5: rs = ra = True
    n = r.choice([200, 300, 400, 500, 600])
    who = f"Researchers randomly selected {n} {pop}" if rs else f"Researchers recruited {n} volunteers from among {pop}"
    how = f" and randomly assigned half of them to {treat} while the other half did not." if ra else f" and asked whether they {obs}."
    res = f" Those {'assigned to ' + short if ra else 'who said yes'} showed {out}."
    S1 = short[0].upper() + short[1:]
    opts = {(True, True): f"{S1} is likely to cause {out} among {pop}.",
            (False, True): f"{S1} is likely to cause {out} for volunteers like these, but the result may not apply to all {pop}.",
            (True, False): f"{S1} is associated with {out} among {pop}, but a cause cannot be determined.",
            (False, False): f"{S1} is associated with {out} among these volunteers; the result may not apply to all {pop}, and a cause cannot be determined."}
    corr = opts[(rs, ra)]
    return MC(who + how + res + " Which conclusion is best supported by the study?", [corr] + [v for k, v in opts.items() if k != (rs, ra)],
              [f"Random sampling? {'Yes' if rs else 'No (volunteers)'}. " + ("Results can be generalized to " + pop + "." if rs else "Results apply only to people like these volunteers."),
               f"Random assignment? {'Yes' if ra else 'No (people chose for themselves)'}. " + ("A cause-and-effect conclusion is supported." if ra else "Only an association can be claimed; other factors could explain it."),
               f"Combine both: {corr}"], "Random sampling → generalize to the population. Random assignment → cause and effect.")

# ================================================================ GEOMETRY
def av(r, d):
    if d == 1:
        if r.random() < 0.5:
            l, w = r.randint(3, 20), r.randint(2, 15)
            return SPR(f"A rectangle has an area of {l * w} square units and a length of {l} units. What is its width, in units?", w,
                       [f"Area = length × width, so {l * w} = {l} × w.", f"Divide: w = {l * w} ÷ {l} = {w}."], "Rearrange the area formula to find a missing side.")
        s = r.randint(2, 12)
        return MC(f"What is the volume, in cubic units, of a cube with an edge length of {s} units?", pick4(S(s ** 3), [S(s * s), S(6 * s * s), S(3 * s)], numpad(s ** 3)),
                  [f"Volume of a cube = s³.", f"{s}³ = {s} × {s} × {s} = {s ** 3}.", f"Trap: {s * s} is the area of one face."], "Cube volume is edge cubed; face area is edge squared.")
    if d == 2:
        if r.random() < 0.5:
            b, h = r.randint(4, 30), r.randint(3, 20); a = Fr(b * h, 2)
            return MC(f"A triangle has a base of {b} units and a height of {h} units. What is its area, in square units?",
                      pick4(S(a) if a.denominator == 1 else D(a, 1), [S(b * h), S(b + h), D(Fr(b * h, 4), 2)], [S(b * h + 1)]),
                      [f"Area of a triangle = ½ × base × height.", f"½ × {b} × {h} = {S(a) if a.denominator == 1 else D(a, 1)}.", f"Trap: {b * h} forgets the ½."], "Triangle area is half of base × height.")
        rad = r.randint(2, 15)
        return SPR(f"A circle has an area of {rad * rad}π square units. What is the radius of the circle, in units?", rad,
                   [f"Area = πr², so πr² = {rad * rad}π.", f"Divide by π: r² = {rad * rad}.", f"r = {rad}."], "Set πr² equal to the given area and solve for r.")
    if r.random() < 0.5:
        k = r.choice([2, 3]); v = r.choice([60, 90, 120, 150, 200, 240, 360]); nv = v * k ** 3
        return MC(f"A rectangular prism has a volume of {v} cubic centimeters. If its length, width, and height are each multiplied by {k}, what is the volume of the new prism, in cubic centimeters?",
                  pick4(f"{nv:,}", [f"{v * k:,}", f"{v * k * k:,}", f"{v * k ** 4:,}"], []),
                  ["Volume = l × w × h.", f"Multiplying each dimension by {k}: ({k}l)({k}w)({k}h) = {k ** 3}lwh.", f"New volume: {k ** 3} × {v} = {nv:,}.",
                   f"Trap: {v * k} multiplies by {k} only once."], "Scaling lengths by k scales area by k² and volume by k³.")
    r1, h1 = r.randint(2, 6), r.randint(4, 12); r2 = r1 * r.choice([2, 3]); h2 = Fr(h1, r.choice([1, 2, 3, 4]))
    ratio = Fr(r2 * r2 * h2, r1 * r1 * h1)
    if h2.denominator != 1: return None
    return SPR(f"Cylinder A has a radius of {r1} and a height of {h1}. Cylinder B has a radius of {r2} and a height of {S(h2)}. The volume of cylinder B is how many times the volume of cylinder A?", ratio,
               ["V = πr²h.", f"A: π({r1}²)({h1}) = {r1 * r1 * h1}π.", f"B: π({r2}²)({S(h2)}) = {S(r2 * r2 * h2)}π.", f"Ratio: {S(r2 * r2 * h2)}π ÷ {r1 * r1 * h1}π = {S(ratio)}."],
               "Cylinder volume is πr²h; the radius is squared.")

def la(r, d):
    if d == 1:
        t = r.choice([("supplementary", 180), ("complementary", 90)]); a = r.randint(10, t[1] - 10)
        return SPR(f"Two angles are {t[0]}. One angle measures {a}°. What is the measure, in degrees, of the other angle?", t[1] - a,
                   [f"{t[0].capitalize()} angles add to {t[1]}°.", f"{t[1]} − {a} = {t[1] - a}."], "Supplementary = 180°; complementary = 90°.")
    if d == 2:
        if r.random() < 0.5:
            x = r.randint(5, 30); a, c = r.sample(range(2, 7), 2); b = r.randint(-20, 30); dd = a * x + b - c * x
            ang = a * x + b
            if not (10 < ang < 170): return None
            kind = r.choice(["corresponding", "alternate interior"])
            return MC(f"Two parallel lines are cut by a transversal. Two {kind} angles measure ({lin(a, b)})° and ({lin(c, dd)})°. What is the value of x?",
                      pick4(S(x), [S(ang), S(Fr(180 - b - dd, a + c)) if (180 - b - dd) % (a + c) == 0 else S(x + 5), S(x * 2)], numpad(x)),
                      [f"When parallel lines are cut by a transversal, {kind} angles are equal.", f"Set them equal: {lin(a, b)} = {lin(c, dd)}.",
                       f"Solve: {S(a - c)}x = {S(dd - b)}, so x = {S(x)}.", f"Check: both angles measure {ang}° ✓"],
                      "Corresponding and alternate interior angles are equal; same-side interior angles add to 180°.")
        v = r.randint(10, 80) * 2
        return SPR(f"The vertex angle of an isosceles triangle measures {v}°. What is the measure, in degrees, of each base angle?", (180 - v) // 2,
                   ["The angles of a triangle add to 180°.", f"The two base angles are equal: {v} + 2b = 180.", f"2b = {180 - v}, so b = {(180 - v) // 2}."], "In an isosceles triangle, the base angles are equal.")
    if r.random() < 0.5:
        ab = r.randint(3, 12); k = r.choice([Fr(3, 2), 2, Fr(5, 2), 3, Fr(4, 3)]); de = ab * k; bc = r.randint(4, 15); ef = bc * k
        if de.denominator != 1 or ef.denominator != 1: return None
        return MC(f"Triangle ABC is similar to triangle DEF, with A corresponding to D, B to E, and C to F. If AB = {ab}, DE = {S(de)}, and BC = {bc}, what is the length of EF?",
                  pick4(S(ef), [S(bc + de - ab), S(Fr(bc, k)), S(ef + 1)], numpad(ef)),
                  ["Similar triangles have proportional corresponding sides.", f"Scale factor: DE ÷ AB = {S(de)} ÷ {ab} = {S(k)}.", f"EF corresponds to BC: EF = {S(k)} × {bc} = {S(ef)}.",
                   f"Trap: {S(bc + de - ab)} adds the difference instead of multiplying by the scale factor."], "Similar figures scale by multiplying, not adding.")
    a, b, c = r.randint(1, 4), r.randint(1, 4), r.randint(1, 3); p, q = r.randint(-10, 30), r.randint(-10, 30)
    if (180 - p - q) % (a + b + c): return None
    x = (180 - p - q) // (a + b + c); angs = [a * x, b * x + p, c * x + q]
    if min(angs) <= 0: return None
    return SPR(f"In triangle PQR, the measure of angle P is ({coef(a, 'x')})°, the measure of angle Q is ({lin(b, p)})°, and the measure of angle R is ({lin(c, q)})°. What is the measure, in degrees, of the largest angle of the triangle?", max(angs),
               [f"The angles add to 180: {coef(a, 'x')} + ({lin(b, p)}) + ({lin(c, q)}) = 180.", f"Combine: {lin(a + b + c, p + q)} = 180, so x = {x}.",
                f"Angles: P = {angs[0]}°, Q = {angs[1]}°, R = {angs[2]}°.", f"Check: {' + '.join(map(str, angs))} = 180 ✓", f"Largest angle: {max(angs)}° (not x = {x})."],
               "Solve for x, then substitute back. The question asks for an angle, not for x.")

TRIP = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29)]
def rt(r, d):
    a, b, c = r.choice(TRIP); k = r.randint(1, 4) if c < 20 else 1; a, b, c = a * k, b * k, c * k
    if d == 1:
        return SPR(f"A right triangle has legs of length {a} and {b}. What is the length of the hypotenuse?", c,
                   [f"Pythagorean theorem: c² = {a}² + {b}² = {a * a} + {b * b} = {c * c}.", f"c = √{c * c} = {c}."], "a² + b² = c², where c is the hypotenuse.")
    if d == 2:
        if r.random() < 0.5:
            return SPR(f"A right triangle has a hypotenuse of length {c} and one leg of length {a}. What is the length of the other leg?", b,
                       [f"a² + b² = c², so b² = {c}² − {a}² = {c * c} − {a * a} = {b * b}.", f"b = √{b * b} = {b}.", "Trap: adding the squares treats the hypotenuse as a leg."],
                       "To find a leg, subtract: leg² = hypotenuse² − other leg².")
        fn = r.choice(["sin", "cos", "tan"]); val = {"sin": Fr(a, c), "cos": Fr(b, c), "tan": Fr(a, b)}[fn]
        return MC(f"In a right triangle, the side opposite angle θ has length {a} and the hypotenuse has length {c}. What is {fn} θ?",
                  pick4(S(val), [S(Fr(a, c)), S(Fr(b, c)), S(Fr(a, b)), S(Fr(b, a)), S(Fr(c, a))], []),
                  [f"Find the adjacent side: √({c}² − {a}²) = √{b * b} = {b}.", {"sin": f"sin θ = opposite ÷ hypotenuse = {a}/{c}", "cos": f"cos θ = adjacent ÷ hypotenuse = {b}/{c}", "tan": f"tan θ = opposite ÷ adjacent = {a}/{b}"}[fn] + (f" = {S(val)}." if S(val) != {"sin": f"{a}/{c}", "cos": f"{b}/{c}", "tan": f"{a}/{b}"}[fn] else ".")],
                  "SOH-CAH-TOA. Find any missing side first.")
    if r.random() < 0.5:
        v = Fr(a, c)
        return SPR(f"In right triangle ABC, angle C is the right angle and sin A = {S(v)}. What is the value of cos B? (Enter a fraction or decimal.)", v,
                   ["In a right triangle, angles A and B are complementary (they add to 90°).", "For complementary angles, sin A = cos B.",
                    "The side opposite A is the side adjacent to B, and both ratios use the same hypotenuse.", f"So cos B = {S(v)}."], "sin x = cos(90° − x).")
    s = r.randint(2, 12)
    if r.random() < 0.5:
        return MC(f"In a 30°-60°-90° triangle, the shorter leg has length {s}. What are the lengths of the hypotenuse and the longer leg?",
                  [f"Hypotenuse {2 * s}, longer leg {s}√3", f"Hypotenuse {s}√3, longer leg {2 * s}", f"Hypotenuse {2 * s}, longer leg {s}√2", f"Hypotenuse {s}√2, longer leg {s}"],
                  ["Side ratio: shorter leg : longer leg : hypotenuse = 1 : √3 : 2.", f"Hypotenuse = 2 × {s} = {2 * s}.", f"Longer leg = {s}√3.", "√2 belongs to the 45°-45°-90° triangle."],
                  "30-60-90: x, x√3, 2x. 45-45-90: x, x, x√2.")
    return MC(f"A 45°-45°-90° triangle has legs of length {s}. What is the length of its hypotenuse?", [f"{s}√2", f"{2 * s}", f"{s}√3", f"{s * s}"],
              ["Side ratio of a 45°-45°-90° triangle: leg : leg : hypotenuse = 1 : 1 : √2.", f"Hypotenuse = {s}√2.", f"Check: {s}² + {s}² = {2 * s * s} = ({s}√2)² ✓"], "45-45-90: x, x, x√2.")

def ci(r, d):
    if d == 1:
        if r.random() < 0.5:
            dd = r.randint(2, 20) * 2
            return MC(f"What is the circumference of a circle with a diameter of {dd}?", pick4(f"{dd}π", [f"{(dd // 2) ** 2}π", f"{dd // 2}π", f"{dd * dd}π"], [f"{2 * dd}π"]),
                      ["Circumference = πd.", f"π × {dd} = {dd}π.", f"Trap: {(dd // 2) ** 2}π is the area."], "C = πd = 2πr; A = πr².")
        rad = r.randint(2, 20)
        return SPR(f"A circle has a circumference of {2 * rad}π. What is the radius of the circle?", rad,
                   [f"Circumference = 2πr, so 2πr = {2 * rad}π.", f"Divide by 2π: r = {rad}."], "Set 2πr equal to the circumference and solve for r.")
    if d == 2:
        if r.random() < 0.5:
            h, k, rad = nz(r, -8, 8), nz(r, -8, 8), r.randint(2, 9)
            fx = lambda v: f"(x {'−' if v > 0 else '+'} {abs(v)})²"; fy = lambda v: f"(y {'−' if v > 0 else '+'} {abs(v)})²"
            corr = f"{fx(h)} + {fy(k)} = {rad * rad}"
            return MC(f"Which equation represents a circle in the xy-plane with center ({S(h)}, {S(k)}) and radius {rad}?",
                      [corr, f"{fx(-h)} + {fy(-k)} = {rad * rad}", f"{fx(h)} + {fy(k)} = {rad}", f"{fx(-h)} + {fy(k)} = {rad * rad}"],
                      ["Standard form: (x − h)² + (y − k)² = r² with center (h, k).", f"h = {S(h)} gives {fx(h)}; k = {S(k)} gives {fy(k)}.", f"r² = {rad}² = {rad * rad}.",
                       "The signs inside the parentheses are opposite to the center's coordinates, and the right side is r², not r."], "Center (h, k) appears as (x − h) and (y − k); the right side is r².")
        ang = r.choice([30, 45, 60, 90, 120, 135, 150, 240, 270]); rad = r.choice([2, 3, 4, 6, 8, 9, 10, 12, 18]); L = Fr(ang, 360) * 2 * rad
        Ls = (S(L) + "π") if L != 1 else "π"
        return MC(f"A circle has a radius of {rad}. What is the length of an arc of the circle formed by a central angle of {ang}°?",
                  pick4(Ls, [S(Fr(ang, 360) * rad * rad) + "π", S(Fr(ang, 360) * rad) + "π", S(2 * rad) + "π"], [S(L * 2) + "π"]),
                  [f"Circumference = 2π({rad}) = {2 * rad}π.", f"Fraction of the circle: {ang}° ÷ 360° = {S(Fr(ang, 360))}.", f"Arc length = {S(Fr(ang, 360))} × {2 * rad}π = {Ls}."],
                  "Arc length = (central angle ÷ 360°) × circumference.")
    if r.random() < 0.5:
        h, k = nz(r, -7, 7), nz(r, -7, 7); a_, b_, c_ = r.choice(TRIP[:3]); rad = r.choice([c_, r.randint(2, 9)])
        C = h * h + k * k - rad * rad
        return SPR(f"x² + y²{plus(-2 * h).replace(' ', ' ', 1)}x{plus(-2 * k)}y{plus(C) if C else ''} = 0\nThe equation above defines a circle in the xy-plane. What is the radius of the circle?".replace("x² + y² + ", "x² + y² + ").replace(" 0x", "").replace(" 0y", ""), rad,
                   [f"Group terms: (x²{plus(-2 * h)}x) + (y²{plus(-2 * k)}y) = {S(-C)}.",
                    f"Complete the square: add {h * h} for x and {k * k} for y to both sides.",
                    f"(x{plus(-h)})² + (y{plus(-k)})² = {S(-C + h * h + k * k)}.", f"r² = {rad * rad}, so r = {rad}. (Center: ({S(h)}, {S(k)}).)"],
                   "Complete the square in x and y to reach standard form.")
    ang = r.choice([30, 45, 60, 72, 90, 120, 144, 180, 240]); rad = r.choice([2, 3, 4, 5, 6, 10, 12]); A_ = Fr(ang, 360) * rad * rad
    As = (S(A_) + "π") if A_ != 1 else "π"
    return MC(f"A circle has a radius of {rad}. What is the area of a sector of the circle with a central angle of {ang}°?",
              pick4(As, [S(Fr(ang, 360) * 2 * rad) + "π", S(rad * rad) + "π", S(Fr(ang, 360) * rad) + "π"], [S(A_ * 2) + "π"]),
              [f"Area of the circle: π({rad}²) = {rad * rad}π.", f"Fraction of the circle: {ang}° ÷ 360° = {S(Fr(ang, 360))}.", f"Sector area = {S(Fr(ang, 360))} × {rad * rad}π = {As}.",
               "Trap: using 2πr gives the arc length, not the area."], "Sector area = (central angle ÷ 360°) × πr².")

# ---------------------------------------------------------------- driver
AL, AM, PD, GT = "Algebra", "Advanced Math", "Problem-Solving and Data Analysis", "Geometry and Trigonometry"
SKILLS = [(AL, "Linear equations in one variable", "l1", [l1_basic, l1_word]), (AL, "Linear equations in two variables", "l2", [l2]),
          (AL, "Linear functions", "lf", [lf]), (AL, "Systems of linear equations", "sy", [sy]), (AL, "Linear inequalities", "li", [li]),
          (AM, "Equivalent expressions", "ee", [ee]), (AM, "Nonlinear equations and systems", "ne", [ne]), (AM, "Nonlinear functions", "nf", [nf]),
          (PD, "Ratios, rates, and units", "rr", [rr_]), (PD, "Percentages", "pc", [pc]), (PD, "One-variable data", "ov", [ov]), (PD, "Two-variable data", "tv", [tv]),
          (PD, "Probability", "pr", [pr]), (PD, "Sample statistics and margin of error", "ss", [ss]), (PD, "Observational studies and experiments", "os", [os_]),
          (GT, "Area and volume", "av", [av]), (GT, "Lines, angles, and triangles", "la", [la]), (GT, "Right triangles and trigonometry", "rt", [rt]), (GT, "Circles", "ci", [ci])]

def generate(per_level=15, seed=2026):
    r = random.Random(seed); out = []; seen = set()
    for dom, skill, code, fns in SKILLS:
        n = 0
        for d in (1, 2, 3):
            got, tries = 0, 0
            while got < per_level and tries < 4000:
                tries += 1
                fn = r.choice(fns)
                if code == "l1" and d == 3: fn = l1_basic
                try: q = fn(r, d)
                except (ValueError, ZeroDivisionError): q = None
                if not q: continue
                if q["type"] == "mc" and len(set(q["choices"])) != 4: continue
                k = q["stem"] + "|" + "|".join(q.get("choices") or [])
                if k in seen: continue
                seen.add(k); n += 1; got += 1
                q.update(id=f"g-{code}-{n:03d}", section="math", domain=dom, skill=skill, difficulty=d, source=SRC)
                out.append(q)
    return out

if __name__ == "__main__":
    qs = generate(int(sys.argv[1]) if len(sys.argv) > 1 else 15)
    json.dump(qs, open(sys.argv[2] if len(sys.argv) > 2 else "generated_math.json", "w"), ensure_ascii=False, indent=0)
    from collections import Counter
    c = Counter((q["skill"], q["difficulty"]) for q in qs)
    print(len(qs), "generated;", "short:", [(k, v) for k, v in c.items() if v < (int(sys.argv[1]) if len(sys.argv) > 1 else 15)])
