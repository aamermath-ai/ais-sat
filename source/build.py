"""Builds the public website from source/.
Usage (from the repository root):  python3 source/build.py
Writes index.html, questions.json, data/questions-all.json, logo.png, apple-touch-icon.png into the repository root."""
import json,os,sys,shutil
S=os.path.dirname(os.path.abspath(__file__)); OUT=sys.argv[1] if len(sys.argv)>1 else os.path.dirname(S)
qs=[]
for f in sorted(os.listdir(S+'/bank')):
    q=json.load(open(S+'/bank/'+f)); q={'id':f[:-5],**q}
    q['source']=q.get('source','').replace('Emir original item','SAT AIS original item'); qs.append(q)
gen=os.path.join(S,'generated_math.json')
if os.path.exists(gen): qs+=json.load(open(gen))
gen2=os.path.join(S,'generated_math_hard2.json')   # extra SAT-Hard Math (source/gen_more_math.py)
if os.path.exists(gen2): qs+=json.load(open(gen2))
sys.path.insert(0,S); from figures import figure_for
for q in qs:
    f=figure_for(q)
    if f: q['figure']=f
print('figures:',sum(1 for q in qs if q.get('figure')),'of',sum(1 for q in qs if q.get('domain')=='Geometry and Trigonometry'),'geometry questions')
os.makedirs(OUT+'/data',exist_ok=True)
json.dump(qs,open(OUT+'/data/questions-all.json','w'),ensure_ascii=False,separators=(',',':'))   # full bank (easy, medium, hard) kept for teachers
qs=[q for q in qs if q.get('difficulty')==3]   # the website serves Hard-level questions only
print('served (hard only):',len(qs))
json.dump(qs,open(OUT+'/questions.json','w'),ensure_ascii=False,separators=(',',':'))
shutil.copy(S+'/logo-512.png',OUT+'/logo.png'); shutil.copy(S+'/logo-180.png',OUT+'/apple-touch-icon.png')
os.makedirs(OUT+'/assets',exist_ok=True)
# background video files: copied only if a re-encoded set exists in source/nightwalk (see HANDOVER.md);
# otherwise the ones already in assets/ are kept
for f in ('night-720.mp4','night-1080.mp4','night-poster.jpg'):
    p=os.path.join(S,'nightwalk',f)
    if os.path.exists(p): shutil.copy(p,OUT+'/assets/'+f)
src=open(S+'/emir.html').read()
a=src.index('/* ---------- boot ---------- */'); b=src.index('})();\n</script>')
src=src[:a]+'''/* ---------- boot (standalone: questions.json + progress in this browser) ---------- */
route(); booted=true;
(async function boot(){
  const l=loadLocal(); if(l)progress=l; saveMode="local"; render();
  try{
    const r=await fetch("questions.json",{cache:"no-cache"});
    if(!r.ok)throw new Error(r.status);
    const data=await r.json();
    bank=onlyHard((Array.isArray(data)?data:[]).filter(q=>q&&q.id&&!validQ(q)));
    bankState=bank.length?"ready":"empty";
    setConn(bank.length?"ok":"warn",bank.length?bank.length+" questions loaded":"Question bank is empty");
  }catch(e){bankState="error";setConn("err","Question bank could not be loaded");}
  if(!S)render();
})();
'''+src[b:]
def R(x,y):
    global src; assert src.count(x)==1,x[:60]; src=src.replace(x,y)
R('saveMode==="local"?"Progress is saved in this browser only."','saveMode==="local"?"Your progress is saved on this device and browser. Use the same device to keep your history."')
R('Department staff with edit access can add items from papers the school is licensed to use.','Department staff can add questions by editing <code>questions.json</code> in the GitHub repository.')
a=src.index('<div class="card" id="editor" hidden>'); b=src.index('</section>',a); src=src[:a]+src[b:]
R('unavailable:"Sign in to claude.ai to load the question bank.",','unavailable:"The question bank could not be loaded.",')
a=src.index('$("imp-go").addEventListener'); b=src.index('/* ---------- formulas events'); src=src[:a]+src[b:]
R('<meta name="claude:viewport-fit-sides" content="cover">\n','')
head='''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="SAT AIS: free adaptive Digital SAT practice for AIS students, from the Mathematics Department, American International School.">
<meta name="theme-color" content="#F5F5F7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="SAT AIS">
<meta name="author" content="Aamer Bashir">
<link rel="icon" type="image/png" href="logo.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<script>try{var t=localStorage.getItem("ais-theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t);}catch(e){}</script>
'''
src=head+src.replace('</style>\n','</style>\n</head>\n<body>\n',1)+'</body>\n</html>\n'
# ---- security: strict Content Security Policy (only our own scripts run; only listed services are contacted)
import re, hashlib, base64
def csp(html, connect, frames, referrer, scripts="", styles=""):
    hashes=" ".join("'sha256-"+base64.b64encode(hashlib.sha256(m.encode()).digest()).decode()+"'"
                    for m in re.findall(r"<script>(.*?)</script>", html, re.S))
    pol=("default-src 'self'; script-src "+hashes+(" "+scripts if scripts else "")+"; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com"+(" "+styles if styles else "")+"; "
         "font-src https://fonts.gstatic.com; img-src 'self' data:; media-src 'self'; connect-src 'self' "+connect+"; "
         "frame-src "+(frames or "'none'")+"; worker-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; upgrade-insecure-requests")
    meta='<meta http-equiv="Content-Security-Policy" content="'+pol+'">\n<meta name="referrer" content="'+referrer+'">\n'
    return html.replace('<meta charset="utf-8">\n','<meta charset="utf-8">\n'+meta,1)
GS="https://script.google.com https://script.googleusercontent.com"
calc_widget=open(S+'/calculator.html').read()   # the shared scientific calculator (button + panel + how-to video)
def add_calc(html, root):
    i=html.rfind('</body>'); assert i>0
    return html[:i]+calc_widget.replace('@@ROOT@@',root)+html[i:]
src=csp(add_calc(src,''), GS, "https://www.youtube-nocookie.com https://www.desmos.com https://sceptrell.github.io", "strict-origin-when-cross-origin")
open(OUT+'/index.html','w').write(src)
# ---- ACT practice site (act.html + act-questions.json), sharing the SAT page's design
sys.path.insert(0,os.path.join(S,'act')); import build_act
print('ACT:',build_act.build(OUT))
act=open(S+'/act.html').read()
css=src[src.index('<style>')+7:src.index('</style>')]
sprite=re.search(r'<svg width="0" height="0" style="position:absolute" aria-hidden="true">.*?</svg>',src,re.S).group(0)
logo=re.search(r'<img class="mark" src="(data:image/[^"]+)"',src).group(1)
act=act.replace('/*@@SHARED_CSS@@*/',css,1).replace('<!--@@SPRITE@@-->',sprite,1).replace('@@LOGO@@',logo)
act=head.replace('content="SAT AIS: free adaptive Digital SAT practice','content="ACT AIS: free timed ACT practice').replace('<meta name="apple-mobile-web-app-title" content="SAT AIS">','<meta name="apple-mobile-web-app-title" content="ACT AIS">')+act.replace('</style>\n','</style>\n</head>\n<body>\n',1)+'</body>\n</html>\n'
open(OUT+'/act.html','w').write(csp(add_calc(act,''), GS, "https://www.desmos.com", "strict-origin-when-cross-origin"))
# ---- Worksheets page (worksheets.html, Grades 6-10) + the interactive worksheets in source/worksheets/
ws=open(S+'/worksheets.html').read()
ws=ws.replace('/*@@SHARED_CSS@@*/',css,1).replace('<!--@@SPRITE@@-->',sprite,1).replace('@@LOGO@@',logo)
ws=head.replace('content="SAT AIS: free adaptive Digital SAT practice for AIS students','content="Worksheets AIS: interactive maths class worksheets for Grades 6-10').replace('<meta name="apple-mobile-web-app-title" content="SAT AIS">','<meta name="apple-mobile-web-app-title" content="Worksheets AIS">')+ws.replace('</style>\n','</style>\n</head>\n<body>\n',1)+'</body>\n</html>\n'
open(OUT+'/worksheets.html','w').write(csp(add_calc(ws,''), "", None, "strict-origin-when-cross-origin"))
STATS_URL=re.search(r'const STATS_URL="([^"]*)"',src).group(1)   # the school's Apps Script (source/analytics/Code.gs)
report=open(S+'/ws-report.html').read().replace('@@STATS_URL@@',STATS_URL)   # "Send to my teacher" on every worksheet
os.makedirs(OUT+'/worksheets',exist_ok=True)
SITE_URL='https://aamermath-ai.github.io/ais-sat/'   # public address of the site, used in the worksheet QR codes
kit=open(S+'/worksheet-kit.html').read()             # City Missions game + QR code, added to every worksheet
os.makedirs(OUT+'/worksheets/qr',exist_ok=True)
try: import segno                                    # pip install segno  (only needed to make new QR codes)
except ImportError: segno=None
for f in sorted(os.listdir(S+'/worksheets')):
    if f.endswith('.html'):
        url=SITE_URL+'worksheets/'+f; qr=OUT+'/worksheets/qr/'+f[:-5]+'.svg'
        if segno: segno.make(url,error='h').save(qr,kind='svg',dark='#062b1c',light='#ffffff',border=2,scale=10,xmldecl=False)
        elif not os.path.exists(qr): print('WARNING: no QR code for',f,'- run: pip install segno')
        w=open(S+'/worksheets/'+f).read()
        i=w.rfind('</body>'); assert i>0
        w=w[:i]+kit.replace('@@QR@@','qr/'+f[:-5]+'.svg').replace('@@URL@@',url)+report+w[i:]
        w=add_calc(w,'../')
        open(OUT+'/worksheets/'+f,'w').write(csp(w, GS, None, "strict-origin-when-cross-origin"))
# ---- Teacher sign-in (Sign in with Google) + worksheet results dashboard
tp=open(S+'/teacher.html').read().replace('@@STATS_URL@@',STATS_URL)
tp=tp.replace('/*@@SHARED_CSS@@*/',css,1).replace('<!--@@SPRITE@@-->',sprite,1).replace('@@LOGO@@',logo)
tp=head.replace('content="SAT AIS: free adaptive Digital SAT practice for AIS students','content="Worksheets AIS teachers: sign in to see worksheet results').replace('<meta name="apple-mobile-web-app-title" content="SAT AIS">','<meta name="apple-mobile-web-app-title" content="AIS Teachers">')+tp.replace('</style>\n','</style>\n</head>\n<body>\n',1)+'</body>\n</html>\n'
GSI="https://accounts.google.com/gsi/"
open(OUT+'/teacher.html','w').write(csp(add_calc(tp,''), GS+" "+GSI, GSI, "strict-origin-when-cross-origin", scripts=GSI+"client", styles=GSI+"style"))
print('worksheets:',len([f for f in os.listdir(S+'/worksheets') if f.endswith('.html')]))
adm=open(S+'/admin.html').read()
open(OUT+'/admin.html','w').write(csp(adm, GS, None, "no-referrer"))   # private usage dashboard (needs the admin key)
r=open(OUT+'/README.md').read().replace('# Emir\n','# SAT AIS\n')
open(OUT+'/README.md','w').write(r)
print('built',len(qs))
