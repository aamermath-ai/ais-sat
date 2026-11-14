"""Adds a large set of extra SAT-Hard Math questions (ids g3-...) without repeating any existing stem.
Usage (from the repository root):  python3 source/gen_more_math.py
Writes source/generated_math_hard2.json; build.py includes it automatically."""
import sys, os, json, random
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
import gen_math as G
TARGET = {"Linear equations in one variable": 150, "Linear equations in two variables": 150, "Linear functions": 150,
          "Systems of linear equations": 150, "Linear inequalities": 150,
          "Equivalent expressions": 300, "Nonlinear equations and systems": 300, "Nonlinear functions": 300,
          "Ratios, rates, and units": 100, "Percentages": 60, "One-variable data": 80, "Two-variable data": 80,
          "Sample statistics and margin of error": 60, "Observational studies and experiments": 60,
          "Area and volume": 150, "Lines, angles, and triangles": 120, "Right triangles and trigonometry": 13, "Circles": 120}
def main(seed=2027, conv=0.3):
    old = json.load(open(os.path.join(S, "generated_math.json")))
    seen = {q["stem"] + "|" + "|".join(q.get("choices") or []) for q in old}
    stems = {q["stem"] for q in old}
    r = random.Random(seed); out = []
    for dom, skill, code, fns in G.SKILLS:
        want = TARGET.get(skill, 0); got = tries = 0
        while got < want and tries < 40000:
            tries += 1
            fn = G.l1_basic if code == "l1" else r.choice(fns)
            try: q = fn(r, 3)
            except (ValueError, ZeroDivisionError, TypeError): q = None
            if not q or (q["type"] == "mc" and len(set(q["choices"])) != 4): continue
            k = q["stem"] + "|" + "|".join(q.get("choices") or [])
            if k in seen or q["stem"] in stems: continue
            alts, disp = q.pop("_alts", None), q.pop("_disp", None)
            if alts and r.random() < conv:   # keep student-produced responses near the SAT's ~25%
                try:
                    ch = G.pick4(disp, [a for a in alts if a != disp], G.numpad(G.Fr(q["answer"])))
                    q.update(type="mc", choices=ch, answer=0); q["stem"] = q["stem"].replace(" (Enter a fraction or decimal.)", "")
                except (ValueError, ZeroDivisionError): pass
            seen.add(k); stems.add(q["stem"]); got += 1
            q.update(id=f"g3-{code}-{got:04d}", section="math", domain=dom, skill=skill, difficulty=3, source=G.SRC)
            out.append(q)
        print(f"{skill}: {got}")
    json.dump(out, open(os.path.join(S, "generated_math_hard2.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    print(len(out), "new hard questions")
if __name__ == "__main__": main()
