"""Checks a Worksheet builder draft before it is put in the Drive folder "Omega drafts".
Usage:  python3 source/tools/check_worksheet.py draft.json
Same rules as validWs_() in source/analytics/Code.gs, plus friendlier checks (hints, steps, parts, pictures)."""
import json, re, sys

ALLOWED_TAGS = {'b', 'strong', 'i', 'em', 'sub', 'sup', 'br', 'span', 'u'}

def check(w):
    errs, warns = [], []
    if not isinstance(w, dict): return ['top level must be an object'], warns
    parts, qs = w.get('parts'), w.get('questions')
    if not isinstance(parts, list) or not 1 <= len(parts) <= 8: errs.append('parts: 1–8 parts needed')
    if not isinstance(qs, list) or not 1 <= len(qs) <= 40: errs.append('questions: 1–40 questions needed')
    if errs: return errs, warns
    pids = [p.get('id') for p in parts]
    if len(set(pids)) != len(pids): errs.append('part ids must be different')
    if not (12 <= len(qs) <= 16): warns.append(f'{len(qs)} questions (12–16 is the usual size)')
    if len(json.dumps(w, ensure_ascii=False)) > 250000: errs.append('worksheet is bigger than 250 KB')
    ids = set()
    for i, q in enumerate(qs, 1):
        tag = f'Q{i}'
        if q.get('id') in ids: errs.append(f'{tag}: duplicate id {q.get("id")}')
        ids.add(q.get('id'))
        if q.get('part') not in pids: errs.append(f'{tag}: part "{q.get("part")}" is not in parts')
        if not isinstance(q.get('text'), str) or not q['text'].strip(): errs.append(f'{tag}: text is empty')
        for t in re.findall(r'</?\s*([a-zA-Z0-9]+)', ' '.join(str(q.get(k, '')) for k in ('text', 'hint')) + ' '.join(q.get('steps') or [])):
            if t.lower() not in ALLOWED_TAGS: warns.append(f'{tag}: <{t}> will be removed (only b, i, sub, sup, br)')
        kind = q.get('kind')
        if kind == 'pick':
            opts = q.get('options')
            if not isinstance(opts, list) or len(opts) < 2: errs.append(f'{tag}: pick needs 2+ options')
            elif q.get('answer') not in opts: errs.append(f'{tag}: answer "{q.get("answer")}" is not one of the options')
            elif len(set(opts)) != len(opts): errs.append(f'{tag}: options repeat')
        elif kind == 'num':
            try: float(q.get('answer'))
            except (TypeError, ValueError): errs.append(f'{tag}: num answer must be a number')
        else: errs.append(f'{tag}: kind must be "pick" or "num"')
        if not q.get('hint'): warns.append(f'{tag}: no hint')
        if not q.get('steps'): warns.append(f'{tag}: no worked steps')
        d = q.get('draw')
        if d is not None and d.get('type') not in ('plot', 'card', 'svg'): errs.append(f'{tag}: draw.type must be plot, card or svg')
        if d and d.get('type') == 'svg' and re.search(r'<script|on\w+\s*=|javascript:|<image|<foreignObject', d.get('svg', ''), re.I):
            errs.append(f'{tag}: svg contains scripts, images or events (they would be removed)')
    hero = (w.get('hero') or {}).get('svg', '')
    if hero and re.search(r'<script|on\w+\s*=|javascript:|<image|<foreignObject', hero, re.I): errs.append('hero: svg contains scripts, images or events')
    return errs, warns

if __name__ == '__main__':
    w = json.load(open(sys.argv[1]))
    errs, warns = check(w)
    for q in w.get('questions', []):
        if q.get('kind') == 'num': print(f"  {q.get('id')}: answer {q.get('answer')} {q.get('unit', '')}")
    for x in warns: print('note:', x)
    for x in errs: print('ERROR:', x)
    print('OK' if not errs else f'{len(errs)} error(s)')
    sys.exit(1 if errs else 0)
