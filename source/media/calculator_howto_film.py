"""Films the calculator how-to video as a sequence of stills (one per step) with captions and key highlights."""
import json, sys
from playwright.sync_api import sync_playwright

U = 'file:///home/claude/ais-sat/worksheets/g10-geometry-13-1-tangent-ratio.html'
OUT = '/home/claude/vid/frames'
W, H = 1600, 900

CSS = """
#vo-cap{position:fixed;left:40px;bottom:40px;max-width:1080px;z-index:200;display:flex;flex-direction:column;gap:10px;font-family:Inter,system-ui,sans-serif}
#vo-cap .tag{align-self:flex-start;background:#ff9f0a;color:#000;font-weight:800;font-size:22px;padding:8px 16px;border-radius:999px}
#vo-cap .txt{background:rgba(12,14,18,.92);color:#fff;font-weight:700;font-size:38px;line-height:1.25;padding:18px 26px;border-radius:22px;box-shadow:0 18px 50px rgba(0,0,0,.35)}
#vo-cap .txt b{color:#ffb340}
#vo-ring{position:fixed;z-index:210;border:5px solid #ff9f0a;border-radius:999px;box-shadow:0 0 0 6px rgba(255,159,10,.35),0 0 30px rgba(255,159,10,.8);pointer-events:none}
#vo-title{position:fixed;inset:0;z-index:300;display:grid;place-items:center;text-align:center;font-family:Inter,system-ui,sans-serif;color:#fff;
  background:radial-gradient(70% 70% at 50% 30%,rgba(255,159,10,.35),transparent 60%),linear-gradient(135deg,#0b1020,#000 70%)}
#vo-title .k{font-size:26px;font-weight:700;color:#ffb340;letter-spacing:.08em;text-transform:uppercase}
#vo-title h1{font-size:92px;line-height:1.02;margin:14px 0 18px;letter-spacing:-.03em}
#vo-title p{font-size:32px;color:#c9d3e6;margin:0}
#vo-title .fl{display:flex;justify-content:center;gap:0;margin-top:34px}
#vo-title .fl i{display:block;width:60px;height:14px}
"""

def main():
    steps = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': W, 'height': H})
        pg.goto(U); pg.wait_for_timeout(1200)
        pg.evaluate("localStorage.removeItem('ais-calc-hist')")
        pg.reload(); pg.wait_for_timeout(1200)
        pg.add_style_tag(content=CSS)
        pg.evaluate("""()=>{const c=document.createElement('div');c.id='vo-cap';c.innerHTML='<span class="tag"></span><div class="txt"></div>';document.body.appendChild(c);
            const r=document.createElement('div');r.id='vo-ring';document.body.appendChild(r);}""")
        n = [0]

        def cap(text, tag=None):
            pg.evaluate("""([t,g])=>{const c=document.getElementById('vo-cap');c.querySelector('.txt').innerHTML=t;const s=c.querySelector('.tag');s.textContent=g||'';s.style.display=g?'':'none';c.style.display=t?'':'none';}""", [text, tag])

        def ring(sel=None, pad=6):
            pg.evaluate("""([s,p])=>{const r=document.getElementById('vo-ring');const e=s&&document.querySelector(s);if(!e){r.style.display='none';return;}
                const b=e.getBoundingClientRect();r.style.display='';r.style.left=(b.left-p)+'px';r.style.top=(b.top-p)+'px';r.style.width=(b.width+2*p)+'px';r.style.height=(b.height+2*p)+'px';
                r.style.borderRadius=getComputedStyle(e).borderRadius;}""", [sel, pad])

        def shot(dur):
            n[0] += 1
            f = f'{OUT}/s{n[0]:03d}.jpg'
            pg.screenshot(path=f, type='jpeg', quality=92)
            steps.append((f, dur))

        def key(k, text, dur, tag=None):
            sel = f'#sc-panel [data-k="{k}"]'
            pg.click(sel)
            ring(sel); cap(text, tag)
            pg.evaluate("s=>{const e=document.querySelector(s);e.classList.add('hit');}", sel)
            pg.wait_for_timeout(60); shot(dur)
            pg.evaluate("s=>document.querySelector(s).classList.remove('hit')", sel)

        def scroll_to(sel):
            pg.evaluate("s=>{const e=document.querySelector(s);window.scrollTo(0,e.getBoundingClientRect().top+scrollY-120);}", sel)
            pg.wait_for_timeout(150)

        # 0. title card
        pg.evaluate("""()=>{const t=document.createElement('div');t.id='vo-title';t.innerHTML='<div><div class="k">AIS Worksheets</div><h1>How to use the<br>scientific calculator</h1><p>Open it · type · press = · read your answer</p><div class="fl"><i style="background:#C8102E"></i><i style="background:#00843D"></i><i style="background:#fff"></i><i style="background:#111"></i></div></div>';document.body.appendChild(t);}""")
        cap(''); ring(None); shot(3.4)
        pg.evaluate("document.getElementById('vo-title').remove()")

        # 1. the button
        scroll_to('#q-c1')
        cap('Tap <b>Calculator</b> at the bottom right of any page.', 'Step 1'); ring('#sc-fab', 8); shot(3.4)
        # 2. open
        pg.click('#sc-fab'); pg.wait_for_timeout(300); scroll_to('#q-c1')
        cap('It opens beside your work. <b>DEG</b> mode is on, ready for trigonometry.', 'Step 2'); ring('#sc-mode', 6); shot(3.6)

        # 3. Example 1: h = 12 × tan 50°
        T = 'Example 1 · Question 7'
        cap('Find the height: <b>h = 12 × tan 50°</b>', T); ring(None); shot(3.0)
        key('1', 'Type <b>12</b>', 0.7, T); key('2', 'Type <b>12</b>', 0.9, T)
        key('mul', 'Press <b>×</b>', 1.1, T)
        key('tan', 'Press <b>tan</b>. It opens a bracket for you.', 1.9, T)
        key('5', 'Type <b>50</b>', 0.7, T); key('0', 'Type <b>50</b>', 0.9, T)
        key(')', 'Close the bracket <b>)</b>', 1.2, T)
        key('eq', 'Press <b>=</b>', 1.4, T)
        cap('h = 14.301… so <b>h ≈ 14.3 m</b> to the nearest tenth.', T); ring('#sc-res', 4); shot(3.4)

        # 4. Example 2: θ = tan⁻¹(45 ÷ 30)
        scroll_to('#q-d1')
        T = 'Example 2 · Question 11'
        key('ac', 'Press <b>AC</b> to start a new calculation.', 1.8, T)
        cap('Find the angle: <b>θ = tan⁻¹(45 ÷ 30)</b>', T); ring(None); shot(2.8)
        key('2nd', 'Press <b>2nd</b>. The trig keys change to sin⁻¹, cos⁻¹, tan⁻¹.', 2.6, T)
        key('tan', 'Now press <b>tan⁻¹</b>', 1.6, T)
        for k in ['4', '5']: key(k, 'Type <b>45 ÷ 30</b>', 0.6, T)
        key('div', 'Type <b>45 ÷ 30</b>', 0.6, T)
        for k in ['3', '0']: key(k, 'Type <b>45 ÷ 30</b>', 0.6, T)
        key(')', 'Close the bracket, then press <b>=</b>', 1.0, T)
        key('eq', 'Close the bracket, then press <b>=</b>', 1.3, T)
        cap('θ = 56.30…° so <b>θ ≈ 56°</b> to the nearest degree.', T); ring('#sc-res', 4); shot(3.4)

        # 5. fractions
        T = 'Tip · fractions'
        key('ac', 'Want a fraction? Try <b>8 ÷ 15 =</b>', 1.2, T)
        for k in ['8', 'div', '1', '5']: key(k, 'Want a fraction? Try <b>8 ÷ 15 =</b>', 0.55, T)
        key('eq', 'Want a fraction? Try <b>8 ÷ 15 =</b>', 1.6, T)
        key('sd', '<b>S⇔D</b> switches between decimal and fraction: <b>8/15</b>', 3.2, T)

        # 6. more tips
        T = 'Tips'
        cap('<b>⌫</b> deletes one key. <b>AC</b> clears everything.', T); ring('#sc-panel [data-k="back"]'); shot(3.0)
        cap('<b>Ans</b> puts your last answer into a new calculation.', T); ring('#sc-panel [data-k="ans"]'); shot(3.0)
        pg.click('#sc-histbtn'); pg.wait_for_timeout(250)
        cap('The <b>clock</b> shows your history. Tap a line to use that answer again.', T); ring('#sc-histbtn'); shot(3.6)
        pg.click('#sc-histbtn'); pg.wait_for_timeout(150)
        cap('On a computer you can also type with the <b>keyboard</b>: 0–9 + − * / ( ) and Enter.', T); ring(None); shot(3.6)
        cap('Tap <b>✕</b> to close the calculator. Good luck!', 'Done'); ring('#sc-close'); shot(3.2)
        b.close()
    json.dump(steps, open('/home/claude/vid/steps.json', 'w'))
    print(len(steps), 'stills,', round(sum(d for _, d in steps), 1), 's')

main()
