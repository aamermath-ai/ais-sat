"""Builds act-questions.json for the ACT practice site.
Called by source/build.py (after data/questions-all.json is written). Can also be run alone:
    python3 source/act/build_act.py <site-root>"""
import json, os, re, sys, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import english_form1, reading_form1, science_form1

CATN = {"POW": "Production of Writing", "KLA": "Knowledge of Language", "CSE": "Conventions of Standard English",
        "KID": "Key Ideas and Details", "CS": "Craft and Structure", "IKI": "Integration of Knowledge and Ideas",
        "IOD": "Interpretation of Data", "SIN": "Scientific Investigation", "EMI": "Evaluation of Models, Inferences, and Experimental Results"}
FIRST = {"CSE": "Read the whole sentence and identify the grammar or punctuation rule being tested.",
         "KLA": "Check each choice for precise, concise, consistent wording.",
         "POW": "Ask what the sentence or passage is trying to do (its purpose and focus).",
         "KID": "Find the part of the passage the question points to and reread it.",
         "CS": "Think about why the author wrote this part and how it works in the passage.",
         "IKI": "Connect ideas across the passage (or across both passages) before choosing.",
         "IOD": "Go to the table or figure named in the question and read its axes, labels and units.",
         "SIN": "Identify what was changed, what was measured, and what was kept the same.",
         "EMI": "Compare the claim or model with the data or viewpoint, one statement at a time."}
def steps_for(q, correct):
    """Turn an explanation into numbered steps: approach, reasoning, answer."""
    parts = [p.strip() for p in re.split(r'(?<=[.!?]["\u201d])\s+(?=[A-Z0-9"\u201c(])|(?<=[.!?])\s+(?=[A-Z0-9"\u201c(])', q["x"]) if p.strip()]
    return [FIRST.get(q["cat"], "Read the question carefully.")] + parts + ["Answer: " + correct]

LETTER_REF = re.compile(r"(^|[\s,;(])[B-D](?=[\s,]|'s|$)")
def scrub(x):
    """Drop explanation sentences that mention choice letters (letters change once choices are shuffled)."""
    parts = re.split(r'(?<=[.!?]["\u201d])\s+(?=[A-Z0-9"\u201c(])|(?<=[.!?])\s+(?=[A-Z0-9"\u201c(])', x)
    keep = [p for p in parts if not LETTER_REF.search(p)]
    return " ".join(keep) if keep else x

def english(passages, rng, nc_target=0.24):
    out = []
    # 1) choose which NO CHANGE-correct items get an error placed in the passage
    nc_items = [(pi, qi) for pi, P in enumerate(passages) for qi, q in enumerate(P["qs"]) if q["c"][0] == "NO CHANGE" and q["a"] == 0]
    total = sum(len(P["qs"]) for P in passages)
    keep_nc = max(0, round(total * nc_target))
    rng.shuffle(nc_items); to_flip = set(nc_items[keep_nc:])
    for pi, P in enumerate(passages):
        paras = list(P["paras"]); qs = []
        for qi, q in enumerate(P["qs"]):
            num = pi * 10 + qi + 1
            c, a = list(q["c"]), q["a"]
            if (pi, qi) in to_flip:
                # find the underlined text for this question and swap in a wrong version
                pat = re.compile(r"\{" + str(num) + r"\|([^}]*)\}")
                for k, para in enumerate(paras):
                    m = pat.search(para)
                    if m and m.group(1):
                        w = rng.randint(1, 3); orig = m.group(1)
                        paras[k] = para[:m.start(1)] + c[w] + para[m.end(1):]
                        c[w] = orig; a = w
                        break
            elif c[0] != "NO CHANGE":
                if c[0].startswith("Yes") and all(s.startswith(("Yes", "No")) for s in c):
                    yes = [i for i in range(4) if c[i].startswith("Yes")]; no = [i for i in range(4) if c[i].startswith("No")]
                    rng.shuffle(yes); rng.shuffle(no); order = yes + no
                else:
                    order = list(range(4)); rng.shuffle(order)
                c = [c[i] for i in order]; a = order.index(a)
            x = scrub(q["x"]); qq = {"n": num, "q": q.get("q", ""), "c": c, "a": a, "cat": q["cat"], "x": x}
            qq["steps"] = steps_for({"x": x, "cat": q["cat"]}, "“" + c[a] + "”"); qs.append(qq)
        out.append({"title": P["title"], "paras": paras, "qs": qs})
    return out

def shuffled(passages, rng, start=1):
    out = []; num = start
    for P in passages:
        qs = []
        for q in P["qs"]:
            order = list(range(4)); rng.shuffle(order)
            x = scrub(q["x"]); c = [q["c"][i] for i in order]
            qs.append({"n": num, "q": q["q"], "c": c, "a": order.index(0), "cat": q["cat"], "x": x, "steps": steps_for({"x": x, "cat": q["cat"]}, c[order.index(0)])}); num += 1
        d = {k: v for k, v in P.items() if k != "qs"}; d["qs"] = qs; out.append(d)
    return out

CAT = {"Algebra": "Algebra", "Advanced Math": "Functions", "Geometry and Trigonometry": "Geometry"}
def math_pool(root, rng):
    allq = json.load(open(os.path.join(root, "data", "questions-all.json")))
    mc = [q for q in allq if q.get("section") == "math" and q.get("type") == "mc" and len(q.get("choices") or []) == 4 and not q.get("figure")]
    pool = []
    for d in (1, 2, 3):
        lvl = [q for q in mc if q.get("difficulty") == d]; rng.shuffle(lvl)
        for q in lvl[:320]:
            sk = q.get("skill", "")
            cat = CAT.get(q.get("domain"), "Statistics and Probability" if sk in ("Probability", "One-variable data", "Two-variable data", "Sample statistics and margin of error", "Observational studies and experiments") else "Integrating Essential Skills")
            st = q.get("steps") or [p for p in re.split(r"(?<=[.!?])\s+", q.get("explanation", "")) if p]
            if not st: continue   # every ACT item must have a worked solution
            item = {"id": "s-" + q["id"], "stem": q["stem"], "choices": q["choices"], "answer": q["answer"], "difficulty": d, "cat": cat,
                    "steps": st, "key": q.get("key", "")}
            if q.get("table"): item["table"] = q["table"]
            pool.append(item)
    extra = json.load(open(os.path.join(HERE, "act_math_extra.json")))
    for q in extra:
        order = list(range(4)); rng.shuffle(order)
        pool.append({"id": q["id"], "stem": q["stem"], "choices": [q["choices"][i] for i in order], "answer": order.index(0),
                     "difficulty": q["difficulty"], "cat": q["cat"], "steps": q["steps"], "key": q["key"], "act": True})
    for q in json.load(open(os.path.join(HERE, "aist_math.json"))):
        order = list(range(4)); rng.shuffle(order)
        item = {"id": q["id"], "stem": q["stem"], "choices": [q["choices"][i] for i in order], "answer": order.index(0),
                "difficulty": q["difficulty"], "cat": q["cat"], "steps": q["steps"], "key": q["key"], "aist": True}
        if q.get("svg"): item["svg"] = q["svg"]
        pool.append(item)
    assert all(it["steps"] for it in pool)
    return pool

def build(root):
    rng = random.Random(20261117)
    data = {"version": 1, "forms": [{"id": 1, "name": "Practice Form 1",
            "english": english(english_form1.PASSAGES, rng),
            "reading": shuffled(reading_form1.PASSAGES, rng),
            "science": shuffled(science_form1.PASSAGES, rng)}],
            "math": math_pool(root, rng)}
    json.dump(data, open(os.path.join(root, "act-questions.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    f = data["forms"][0]
    return {"english": sum(len(p["qs"]) for p in f["english"]), "reading": sum(len(p["qs"]) for p in f["reading"]),
            "science": sum(len(p["qs"]) for p in f["science"]), "math": len(data["math"])}

if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(HERE))))
