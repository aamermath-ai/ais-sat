"""ACT-only Math topics (original, generated): matrices, logarithms, complex numbers, sequences, exact trig values,
counting/probability, circle equations, composition of functions, absolute-value equations.
Every answer is computed exactly; each item has 4 distinct choices (correct listed first; the build shuffles).
Usage: python3 source/act/gen_act_math.py  -> source/act/act_math_extra.json"""
import json, os, random
from fractions import Fraction as F
from math import comb, perm

M = "−"  # minus sign
def n(v):  # format a number / fraction
    v = F(v)
    s = str(abs(v.numerator)) if v.denominator == 1 else f"{abs(v.numerator)}/{v.denominator}"
    return (M if v < 0 else "") + s
def sg(v): return f" + {n(v)}" if v >= 0 else f" {M} {n(-v)}"
def four(correct, wrongs, r):
    out = [correct]
    for w in wrongs:
        if w not in out: out.append(w)
        if len(out) == 4: break
    k = 1
    while len(out) < 4:  # fallback distractors
        cand = correct + " " * k
        out.append(cand); k += 1
    return out

def det(r, d):
    a, b, c, e = [r.randint(-6, 9) for _ in range(4)]
    v = a * e - b * c
    return dict(stem=f"What is the determinant of the matrix [[{n(a)}, {n(b)}], [{n(c)}, {n(e)}]]?",
                choices=four(n(v), [n(a * e + b * c), n(a * b - c * e), n(a + e)], r), cat="Number and Quantity",
                steps=[f"For [[a, b], [c, d]], the determinant is ad {M} bc.", f"({n(a)})({n(e)}) {M} ({n(b)})({n(c)}) = {n(a*e)} {M} ({n(b*c)}) = {n(v)}."],
                key="Determinant of a 2×2 matrix: ad − bc.")
def matmul(r, d):
    A = [[r.randint(-3, 5) for _ in range(2)] for _ in range(2)]; B = [[r.randint(-3, 5) for _ in range(2)] for _ in range(2)]
    i, j = r.randint(0, 1), r.randint(0, 1)
    v = A[i][0] * B[0][j] + A[i][1] * B[1][j]
    wrong = [A[i][0] * B[j][0] + A[i][1] * B[j][1], A[i][j] * B[i][j], A[0][j] * B[i][0] + A[1][j] * B[i][1]]
    nm = ["first", "second"]
    return dict(stem=f"Let A = [[{n(A[0][0])}, {n(A[0][1])}], [{n(A[1][0])}, {n(A[1][1])}]] and B = [[{n(B[0][0])}, {n(B[0][1])}], [{n(B[1][0])}, {n(B[1][1])}]]. What is the entry in the {nm[i]} row and {nm[j]} column of the product AB?",
                choices=four(n(v), [n(x) for x in wrong] + [n(v + 1), n(v - 2)], r), cat="Number and Quantity",
                steps=[f"Multiply row {i+1} of A by column {j+1} of B.", f"({n(A[i][0])})({n(B[0][j])}) + ({n(A[i][1])})({n(B[1][j])}) = {n(v)}."],
                key="Entry (i, j) of AB = row i of A times column j of B.")
def logsolve(r, d):
    b = r.choice([2, 3, 4, 5, 10]); k = r.randint(2, 4 if b < 5 else 3); x = b ** k
    if d == 1:
        return dict(stem=f"What is the value of log base {b} of {x}?", choices=four(n(k), [n(x // b), n(k + 1), n(b * k)], r), cat="Algebra",
                    steps=[f"log_{b}({x}) asks: {b} to what power equals {x}?", f"{b}^{k} = {x}, so the value is {k}."], key="log_b(x) = y means b^y = x.")
    c = r.randint(1, 4)
    return dict(stem=f"If log base {b} of (x {M} {c}) = {k}, what is the value of x?", choices=four(n(x + c), [n(x - c), n(b * k + c), n(x)], r), cat="Algebra",
                steps=[f"Rewrite in exponential form: x {M} {c} = {b}^{k} = {x}.", f"x = {x} + {c} = {x + c}."], key="Convert a log equation to exponential form.")
def logrules(r, d):
    b = r.choice([2, 3, 10]); m, p = r.randint(1, 3), r.randint(1, 3)
    return dict(stem=f"Which of the following is equal to log base {b} of {b**m} + log base {b} of {b**p}?",
                choices=four(n(m + p), [n(m * p), n(b ** m + b ** p), n(abs(m - p) or m + p + 1)], r), cat="Algebra",
                steps=[f"log_{b}({b**m}) = {m} and log_{b}({b**p}) = {p}.", f"Sum: {m} + {p} = {m + p}. (Equivalently log_{b}({b**m}·{b**p}) = log_{b}({b**(m+p)}).)"],
                key="log(a) + log(b) = log(ab).")
def ipow(r, d):
    k = r.randint(5, 60); res = ["1", "i", M + "1", M + "i"][k % 4]
    return dict(stem=f"For the imaginary unit i, where i² = {M}1, what is the value of i^{k}?",
                choices=four(res, [x for x in ["1", "i", M + "1", M + "i"] if x != res], r), cat="Number and Quantity",
                steps=["Powers of i repeat every 4: i, −1, −i, 1.", f"{k} ÷ 4 leaves remainder {k % 4}, so i^{k} = {res}."], key="Reduce the exponent mod 4.")
def cmul(r, d):
    a, b, c, e = [r.choice([x for x in range(-5, 6) if x]) for _ in range(4)]
    re, im = a * c - b * e, a * e + b * c
    def z(x, y): return f"{n(x)}{' + ' if y >= 0 else ' ' + M + ' '}{n(abs(y))}i"
    return dict(stem=f"Which of the following is equal to ({z(a, b)})({z(c, e)}), where i² = {M}1?",
                choices=four(z(re, im), [z(a * c + b * e, im), z(a * c, b * e), z(re, a * e - b * c)], r), cat="Number and Quantity",
                steps=["Use FOIL and replace i² with −1.", f"Real part: ({n(a)})({n(c)}) − ({n(b)})({n(e)}) = {n(re)}.", f"Imaginary part: ({n(a)})({n(e)}) + ({n(b)})({n(c)}) = {n(im)}."],
                key="(a + bi)(c + di) = (ac − bd) + (ad + bc)i.")
def arith2(r, d):
    a1, dd, k = r.randint(-10, 15), r.choice([x for x in range(-6, 9) if x]), r.randint(12, 40)
    v = a1 + (k - 1) * dd
    return dict(stem=f"The first term of an arithmetic sequence is {n(a1)}, and the common difference is {n(dd)}. What is the {k}th term of the sequence?",
                choices=four(n(v), [n(a1 + k * dd), n(a1 * k), n(k * dd)], r), cat="Functions",
                steps=["aₙ = a₁ + (n − 1)d.", f"a_{k} = {n(a1)} + ({k} − 1)({n(dd)}) = {n(v)}."], key="nth term: a₁ + (n − 1)d.")
def geo(r, d):
    a1, ratio, k = r.randint(1, 5), r.choice([2, 3, -2]), r.randint(4, 7)
    v = a1 * ratio ** (k - 1)
    return dict(stem=f"In a geometric sequence, the first term is {a1} and the common ratio is {n(ratio)}. What is the {k}th term?",
                choices=four(n(v), [n(a1 * ratio ** k), n(a1 + (k - 1) * ratio), n(a1 * abs(ratio) ** (k - 1) * (-1 if v > 0 else 1))], r), cat="Functions",
                steps=["aₙ = a₁ · r^(n − 1).", f"a_{k} = {a1} · ({n(ratio)})^{k-1} = {n(v)}."], key="Geometric nth term: a₁·r^(n−1).")
TRIG = {(30, "sin"): "1/2", (30, "cos"): "√3/2", (30, "tan"): "√3/3", (45, "sin"): "√2/2", (45, "cos"): "√2/2", (45, "tan"): "1",
        (60, "sin"): "√3/2", (60, "cos"): "1/2", (60, "tan"): "√3", (120, "sin"): "√3/2", (120, "cos"): M + "1/2", (135, "cos"): M + "√2/2",
        (150, "sin"): "1/2", (210, "sin"): M + "1/2", (225, "tan"): "1", (240, "cos"): M + "1/2", (300, "sin"): M + "√3/2", (330, "cos"): "√3/2"}
def trig(r, d):
    (ang, f), v = r.choice(list(TRIG.items()))
    pool = ["1/2", "√3/2", "√2/2", "√3", "1", M + "1/2", M + "√3/2", M + "√2/2", "√3/3"]
    return dict(stem=f"What is the exact value of {f}({ang}°)?", choices=four(v, [x for x in r.sample(pool, len(pool)) if x != v], r), cat="Geometry",
                steps=[f"Use the reference angle for {ang}° and the sign of {f} in that quadrant.", f"{f}({ang}°) = {v}."], key="Special angles: 30°, 45°, 60° and their reference angles.")
def counting(r, d):
    nn, k = r.randint(6, 10), r.randint(2, 4)
    if r.random() < 0.5:
        v = comb(nn, k)
        return dict(stem=f"A club with {nn} members will choose a committee of {k} members. How many different committees are possible?",
                    choices=four(str(v), [str(perm(nn, k)), str(nn * k), str(comb(nn, k - 1))], r), cat="Statistics and Probability",
                    steps=["Order does not matter, so use combinations.", f"C({nn}, {k}) = {v}."], key="Committees → combinations; ranked positions → permutations.")
    v = perm(nn, k)
    roles = {2: "a president and a secretary", 3: "a president, a secretary, and a treasurer", 4: "a president, a secretary, a treasurer, and a historian"}[k]
    return dict(stem=f"A club with {nn} members will choose {roles}. No member can hold more than one position. In how many different ways can the positions be filled?",
                choices=four(str(v), [str(comb(nn, k)), str(nn ** k), str(nn * k)], r), cat="Statistics and Probability",
                steps=["Order matters (different positions), so use permutations.", f"P({nn}, {k}) = {v}."], key="Distinct roles → permutations.")
def prob(r, d):
    red, blue = r.randint(2, 7), r.randint(2, 7); t = red + blue
    v = F(red, t) * F(red - 1, t - 1)
    return dict(stem=f"A bag contains {red} red marbles and {blue} blue marbles. Two marbles are drawn at random without replacement. What is the probability that both are red?",
                choices=four(n(v), [n(F(red, t) ** 2), n(F(red, t)), n(F(red, t) * F(red - 1, t))], r), cat="Statistics and Probability",
                steps=[f"First draw: {red}/{t}. Second draw (one red removed): {red-1}/{t-1}.", f"Multiply: {n(v)}."], key="Without replacement, the second probability changes.")
def circle(r, d):
    h, k, rad = r.randint(-6, 6), r.randint(-6, 6), r.randint(2, 7)
    D, E, Fc = -2 * h, -2 * k, h * h + k * k - rad * rad
    eq = f"x² + y²{sg(D)}x{sg(E)}y{sg(Fc)} = 0".replace(" + 0x", "").replace(" + 0y", "").replace(" + 0 = 0", " = 0")
    return dict(stem=f"What is the radius of the circle with equation {eq} in the standard (x, y) coordinate plane?",
                choices=four(str(rad), [str(rad * rad), str(abs(Fc)) if abs(Fc) != rad else str(rad + 1), str(abs(h) + abs(k) or rad + 2)], r), cat="Geometry",
                steps=["Complete the square in x and in y.", f"(x{sg(-h)})² + (y{sg(-k)})² = {rad*rad}.", f"r² = {rad*rad}, so r = {rad}."], key="Complete the square to get (x − h)² + (y − k)² = r².")
def compose(r, d):
    a, b, c, e = r.randint(2, 5), r.randint(-6, 6), r.randint(2, 4), r.randint(-5, 5); x = r.randint(-3, 4)
    g = c * x + e; v = a * g + b
    return dict(stem=f"If f(x) = {a}x{sg(b)} and g(x) = {c}x{sg(e)}, what is the value of f(g({n(x)}))?",
                choices=four(n(v), [n(c * (a * x + b) + e), n((a * x + b) * g), n(a * x + b + g)], r), cat="Functions",
                steps=[f"g({n(x)}) = {c}({n(x)}){sg(e)} = {n(g)}.", f"f({n(g)}) = {a}({n(g)}){sg(b)} = {n(v)}."], key="Work from the inside out.")
def absval(r, d):
    a, b = r.randint(-8, 8), r.randint(2, 9)
    lo, hi = a - b, a + b
    return dict(stem=f"What is the sum of the solutions of |x{sg(-a)}| = {b}?",
                choices=four(n(lo + hi), [n(hi), n(b), n(lo)], r), cat="Algebra",
                steps=[f"x{sg(-a)} = {b} or x{sg(-a)} = {M}{b}.", f"x = {n(hi)} or x = {n(lo)}; sum = {n(lo + hi)}."], key="|u| = c splits into u = c or u = −c.")
GENS = [(det, 1, 2), (matmul, 2, 3), (logsolve, 1, 3), (logrules, 2, 2), (ipow, 2, 2), (cmul, 2, 3), (arith2, 1, 2), (geo, 2, 3),
        (trig, 2, 3), (counting, 2, 3), (prob, 2, 3), (circle, 3, 3), (compose, 1, 2), (absval, 1, 2)]

def main(per=24, seed=1959):
    r = random.Random(seed); out = []; seen = set()
    for fn, dlo, dhi in GENS:
        got = tries = 0
        while got < per and tries < 3000:
            tries += 1; d = r.randint(dlo, dhi)
            q = fn(r, d)
            if not q or q["stem"] in seen or len(set(q["choices"])) != 4 or any("\u2009" in c for c in q["choices"]): continue   # no padded duplicates
            seen.add(q["stem"]); got += 1
            q.update(id=f"am-{fn.__name__}-{got:03d}", difficulty=d, answer=0, source="Omega original ACT-style item")
            out.append(q)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "act_math_extra.json"), "w"), ensure_ascii=False)
    print(len(out), "ACT-only math items")
if __name__ == "__main__": main()
