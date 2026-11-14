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
shutil.copy(S+'/admin.html',OUT+'/admin.html')   # private usage dashboard (needs the admin key)
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
<link rel="icon" type="image/png" href="logo.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<script>try{var t=localStorage.getItem("ais-theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t);}catch(e){}</script>
'''
src=head+src.replace('</style>\n','</style>\n</head>\n<body>\n',1)+'</body>\n</html>\n'
open(OUT+'/index.html','w').write(src)
r=open(OUT+'/README.md').read().replace('# Emir\n','# SAT AIS\n')
open(OUT+'/README.md','w').write(r)
print('built',len(qs))
