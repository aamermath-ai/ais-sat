# SAT AIS: handover guide

**Created and developed by [Aamer Bashir](https://www.linkedin.com/in/aamer-b-9b3575126/)**, Mathematics Department, American International School.

A free Digital SAT practice website for students of the American International School (AIS), built by the Mathematics Department.

- **Live site:** https://aamermath-ai.github.io/ais-sat/
- **Code:** https://github.com/aamermath-ai/ais-sat
- **Download everything as a ZIP:** https://github.com/aamermath-ai/ais-sat/archive/refs/heads/main.zip

---

## Brand: Omega

- **Name:** Omega. The sections are **Omega SAT**, **Omega ACT** and **Omega Worksheets**.
- **Tagline:** *The last word in math.* (Ω is the last letter of the Greek alphabet.) Second line: *From algebra to calculus*.
- **Logo:** source files are in `source/brand/`.
  - `omega-tile.svg`: the full logo, a glowing Ω on a navy graph-paper tile, with a gold point and a tangent line as a calculus nod. Use it for large sizes and app icons.
  - `omega-favicon.svg`: a simplified, bolder version for small sizes (browser tab, sidebar).
  - `omega-logo-1024.png`: a high-resolution PNG for documents and slides.
- **Where they are used:**
  - `source/logo-512.png` becomes the site's `logo.png`.
  - `source/logo-180.png` becomes `apple-touch-icon.png`.
  - The marks inside the pages are embedded in `source/emir.html`, and the build copies them to every page.
- **What still names the school:** the creator page keeps your job title and the thank-you note to Ms. Shahnaz Nawaz as written. The ACT "AIST Math 1" mode keeps its name.

## 1. What the website does

| Section | What students get |
|---|---|
| **Summary** | Animated daily rings (questions, correct answers, minutes), an estimated SAT score, a progress graph, streaks, awards, a test-day countdown and a "Dream big" card with a motivating quote |
| **Practice** | Timed adaptive sets (whole syllabus, Math or Reading & Writing; by domain or skill). Each set opens in its own **test window** (full screen on computers) that warns students if they leave it and records each time in the results. All served questions are SAT Hard level, with the hardest first. Built-in Desmos calculator and reference sheet, as on test day. Step-by-step solutions after every wrong answer |
| **Formulas** | The SAT Math formula sheet with geometry diagrams, plus a mind map of every Math subtopic |
| **Desmos Practice** | The *Full SAT Desmos Guide* video, plus three tools that each open in their own window: 27 Desmos techniques with worked solutions (each with a "Try it in Desmos" calculator window beside it), the Desmos Speed Trainer and the Desmos calculator |
| **SAT guide** | Test format, timing, adaptive modules, scoring, content domains with percentages, strategies, SAT vs ACT, and official College Board resources |
| **Universities** | SAT ranges and scholarships at 50 universities (20 US, 20 UK, 10 UAE), with a score slider, a nationality filter for 10 countries and links to every official website |
| **Question Bank** | Browse every question by skill |

Themes: Night (animated beach video), Auto, Light, Dark. Sounds can be switched off.

## 2. How it works (technical summary)

- **A static website**: plain HTML, CSS and JavaScript in one file (`index.html`), with no server, database or build framework. It can be hosted anywhere that serves files (GitHub Pages, the school's web server, Netlify, Cloudflare Pages, Azure Static Web Apps…).
- **No accounts, no personal data collected.** Optional anonymous usage counts can be switched on (section 7). Each student's progress, profile name and goals are stored only in their own browser (`localStorage`). Progress does not follow a student to another device or browser, and clearing browser data deletes it.
- **Cost:** free. GitHub Pages hosting is free for a public repository.

## 3. What is in this repository

```
index.html               the website (generated from source/emir.html; do not edit by hand)
worksheets.html          the Worksheets page (generated from source/worksheets.html)
worksheets/              the interactive worksheets (generated from source/worksheets/)
admin.html               private usage dashboard (needs your admin key; see section 7)
questions.json           questions served to students (Hard level only: 2,956; 2,845 Math, 111 R&W)
data/questions-all.json  the full bank: 3,782 questions (3,562 Math, 220 R&W; easy, medium, hard)
assets/                  background video (720p and 1080p) and its poster image
logo.png, apple-touch-icon.png
tools/                   copies of the Math question generator and the figure builder
source/                  EVERYTHING NEEDED TO EDIT AND REBUILD THE SITE
  emir.html              the master source of the app (edit this one)
  build.py               rebuilds the website from source/
  bank/                  334 hand-written questions, one JSON file each
  rw_batch3a.py, rw_batch3b.py   the latest 60 SAT-Hard Reading & Writing questions (they write into bank/)
  generated_math.json    955 generated Math questions (easy, medium, hard)
  generated_math_hard2.json  2,493 more SAT-Hard Math questions (made by gen_more_math.py)
  gen_math.py            the Math question generator (exact answers, worked steps)
  gen_more_math.py       makes extra Hard Math questions without repeating existing ones
  figures.py             attaches geometry diagrams to questions
  admin.html             source of the usage dashboard
  analytics/Code.gs      the statistics backend (Google Apps Script)
  logo-512.png, logo-180.png
  media/night_walk_original.mp4   the original background clip
```

## 4. How to make changes

You need Python 3 (free) on any computer.

1. Edit `source/emir.html` (design, text, features, university data) or the questions in `source/bank/`.
2. From the repository folder, run:
   ```
   python3 source/build.py
   ```
3. Open `index.html` in a browser to check it. To test fully, serve the folder locally, for example with `python3 -m http.server`, and open http://localhost:8000.
4. Upload or commit the changed files. GitHub Pages republishes in a few minutes.

**Adding a question:** add a JSON file to `source/bank/` (format in `README.md`), then rebuild. Only questions with `"difficulty": 3` are served to students, because of the student feedback asking for Hard-only practice. To serve all levels, remove the line marked `the website serves Hard-level questions only` in `source/build.py`.

**More Math questions:** `python3 source/gen_more_math.py` makes another set of Hard questions with no repeats (change `TARGET` and `seed` inside it), or use `source/gen_math.py` for all levels.

**About the test window:** a website cannot physically stop students switching apps, so the test window works by *detecting and warning*. Leaving the window, switching tabs or apps, or exiting full screen shows a warning and is counted in the results. For real exams, a locked-down browser on school-managed devices (for example Safe Exam Browser, or Bluebook for official SAT practice) is the only true lockdown.

**University and scholarship data:** it is the `const UNIS=[...]` list in `source/emir.html`. It was checked in November 2026 and **should be reviewed every year** (for example each September), because score ranges, testing policies, scholarships and deadlines change.

**Background video:** to replace it, re-encode the new clip into `night-720.mp4`, `night-1080.mp4` and `night-poster.jpg` (for example with ffmpeg), put them in `source/nightwalk/`, then rebuild.

## 5. Moving it to the school (options)

1. **Keep GitHub, give the school ownership (easiest).** The repository owner can use *Settings → General → Transfer ownership* to move it to a school GitHub account or organisation. The site keeps working at the new account's GitHub Pages address.
2. **Use a school web address** (for example `sat.ais.sch.ae`): the school's IT team adds a DNS `CNAME` record pointing to `<account>.github.io` and enters the domain under *Settings → Pages → Custom domain*.
3. **Host it on the school's own server:** copy the files in the repository root (everything except `source/` and `tools/`, which are only needed for editing) to any web folder. No server software is needed.

**Security:** see [SECURITY.md](SECURITY.md) for what has been checked, the protections built in, and the account steps the owner must take.

## 6. Things the school should review before making it official

- **Third-party content shown inside the site:**
  - The *Full SAT Desmos Guide* is a YouTube video by another creator, embedded with YouTube's privacy-enhanced player.
  - The Desmos Speed Trainer (sceptrell.github.io) is embedded with an iframe. Consider asking its author for permission and crediting them.
  - The Desmos calculator is embedded from desmos.com. For an official, high-traffic school site, Desmos offers an API with a free key for educational use, which is the recommended way to embed it.
  - Fonts load from Google Fonts.
- **Background video:** confirm the school has the right to use the *Night Walk* clip publicly.
- **Questions:** all questions are original practice items written to College Board's published Digital SAT specifications. They are not official SAT questions. "SAT" is a registered trademark of College Board, which is not affiliated with this website. The README explains that the questions are original. Before launch, add a one-line notice to the site saying the SAT is a College Board trademark and that College Board is not affiliated with the site.
- **University and scholarship information** is a guide for students. Every card links to the official website, and the page tells students to confirm details there.
- **Student data:** nothing personal is collected. The optional usage statistics (section 7) are anonymous; students should be told about them. If the school later wants teachers to see student progress, that needs logins and a database (a larger project).
- **Accessibility:** the site works on phones, tablets and computers. It supports keyboard use, light/dark modes and reduced motion.

## ACT preparation (act.html)

Opening the site shows a welcome screen once per visit, where students choose **SAT** or **ACT**; each side links to the other.

- **What it is:** a separate ACT page with the same design, theme and statistics. Practice runs in the same kind of test window as the SAT, with the same leave-the-window warnings.
- **Real test conditions:**
  - fixed sections in ACT order: English 50 Q / 35 min, Math 45 Q / 50 min, the 10-minute break, Reading 36 Q / 40 min, and optional Science 40 Q / 40 min;
  - a countdown with a five-minute warning, and automatic submission when time runs out;
  - passages beside the questions, with numbered underlined portions in English;
  - A–D / F–J answer letters, an answer eliminator, flag for review and a question navigator;
  - Desmos in Math, and no formula sheet (as on the ACT);
  - answers and explanations only after the test.
- **Scores:** estimated 1–36 per section from typical ACT conversion curves. Composite = average of English, Math and Reading; STEM = average of Math and Science.
- **Content** (all original, written to the enhanced ACT specifications):
  - Practice Form 1: English 5 passages / 50 Q, Reading 4 passages / 36 Q, Science 6 passages / 40 Q;
  - Math: a pool of 1,105 questions (SAT-bank multiple-choice items plus 330 ACT-only items: matrices, logarithms, complex numbers, sequences, exact trig values, counting and probability, circle equations, composition). A fresh 45-question set is drawn for each test, ordered easier to harder.
- **Source files:** `source/act.html` (the page), and in `source/act/`: `english_form1.py`, `reading_form1.py`, `science_form1.py`, `gen_act_math.py` and `build_act.py`. `python3 source/build.py` builds `act.html` and `act-questions.json` together with the SAT site.
- **AIST Math 1 practice (ACT International Subject Test):** 50 questions in 60 minutes, algebra and geometry heavy, with a calculator. Results are shown as a percentage, because ACT publishes no 1–36 conversion for subject tests. The questions come from `source/act/gen_aist.py`: 534 original items modelled on the topics and difficulty of the department's AIST notes and question banks, which are not copied. Each has worked steps, and many geometry questions have drawn figures.
- **ACT Math sets** follow the approximate official reporting-category mix (number and quantity, algebra, functions, geometry, statistics and probability, essential skills) and are ordered easier to harder.
- **Step-by-step solutions:**
  - every ACT question (English, Reading, Science and Math) has numbered solution steps, shown in the review after a test;
  - in **learning mode** (a drill option), the solution appears right after each answer.
- **Adding another full ACT form:** write `english_form2.py`, `reading_form2.py` and `science_form2.py` in the same format, and add them to `forms` in `build_act.py`.

## Worksheets (worksheets.html)

The welcome screen offers three choices, with **Worksheets** first, then SAT and ACT. Each page links to the other two.

- **What it is:** interactive class worksheets for Grades 6–10, organised grade → term → module. Students answer on screen, check each answer, get a hint after a wrong answer and the worked steps after a second one, and see a score they can copy or screenshot for Microsoft Teams.
- **Now on the site:** Grade 9 Algebra 1 → Term 1 → Module 3 → 3.1 Linear Equations in Standard Form (quiz, Eid Al Etihad edition), and Grade 10 Geometry → Term 1 → Module 13 → 13.1 Tangent Ratio (Eid Al Etihad edition). Grades 6–8 show "coming soon".
- **Adding a worksheet:**
  1. Put the worksheet's HTML file in `source/worksheets/` (one self-contained file; give it a "← All worksheets" link to `../worksheets.html`).
  2. Add an item to `source/worksheets-catalog.js` (grade → term → module → `{code, ws, title, sub, file}`). This one list feeds both the Worksheets page and the teacher's "Assign" picker. `ws` must equal the id in the worksheet's `window.AISWS`.
  - To let students send results to teachers, the worksheet needs three small additions (copy them from an existing worksheet): `<div id="ais-report"></div>` in its result box, `window.AISWS={id,title,grade,parts,get}`, and `document.dispatchEvent(new Event('ais-ws-change'))` at the end of its `score()` function. The build adds the "Send to my teacher" button (`source/ws-report.html`) automatically.
  3. Run `python3 source/build.py`. It builds `worksheets.html` and copies every worksheet into `worksheets/` with the same security policy as the rest of the site.
- **Scientific calculator (on every page):** the SAT, ACT and Worksheets pages and every worksheet have a "Calculator" button at the bottom right (above the tab bar on phones). It opens an iPhone-style scientific calculator beside the work (a bottom sheet on phones): degrees by default, 2nd for inverse trig and hyperbolics, powers and roots, logs, x!, nCr, nPr, |x|, π, e, EE, %, memory, Ans, S⇔D (fraction or decimal), history and keyboard input. It uses its own parser (no `eval`) and is hidden inside test windows, so SAT and ACT practice keep test-day rules (Desmos only). The build adds it from `source/calculator.html`, so new pages and worksheets get it automatically.
- **QR codes:** every worksheet gets its own QR code (`worksheets/qr/<worksheet>.svg`), made by the build with the `segno` library (`pip install segno`). Teachers show it from the QR button beside each worksheet in the list, or from the QR button inside the worksheet, and students scan it to open the worksheet straight away. The address comes from `SITE_URL` in `source/build.py`: change it if the site moves.
- **City Missions game (`source/worksheet-kit.html`, added to every worksheet by the build):** a start screen, then each part of the worksheet is a "mission" in a Dubai district on a city map. Students earn XP (+100 per correct answer, +50 on the first try, combo bonus for answers in a row), stars per mission and ranks (Rookie → Explorer → Navigator → Pro → City Legend), with sounds that can be muted. It reads the worksheet's own right/wrong feedback, so new worksheets need no extra code. The rank and XP appear in the result box and in "Copy my result". Name and class are required: the START button stays locked until both are filled in, students who clear them later get a reminder when 2 questions are left and again when they finish, and "Copy my result" asks for them first.
  - *Content rules (UAE school setting):* original artwork only, no commercial game brands or characters, no violence, weapons, crime, gambling or chance-based rewards, respectful use of the UAE flag and landmarks, and no personal data sent anywhere (progress stays in the student's browser). Keep to these rules when changing the game.
- **How-to video:** `assets/calculator-howto.mp4` (68 s, with captions; poster `assets/calculator-howto.jpg`) plays from the calculator's "How to use" button and on the Worksheets page. `source/media/calculator_howto_film.py` films it again from the live calculator if the design changes (then encode with ffmpeg as in the script's notes).

## Teacher sign-in and worksheet results (teacher.html)

- **Students** press **Send to my teacher** at the end of a worksheet. Their name, class and per-question results go to the **Worksheets** tab of the statistics Google Sheet. After the first send, new answers are sent automatically.
- **Teachers** open `teacher.html` (link on the Worksheets page) and press **Sign up** or **Log in**, which open Google's account window. Their Gmail address is their username. No passwords are stored by the site.
- **Approval:** new teachers wait until an owner approves them on `teacher.html` (Teachers panel). Owners get an email for each new request, and teachers get an email when approved. Emails in a domain listed in `TEACHER_DOMAINS` are approved automatically.
- **Dashboard:** students, average score, finished, right first time, score distribution, by part, by class, per-question analysis with "Re-teach" flags, a student table (sortable, searchable) and CSV download.

**Class codes, QR codes and Microsoft Teams:**
- On `teacher.html` a teacher picks a worksheet and a class (e.g. 9B4), with an optional due date, and presses **Create class code**. This makes a 6-character code (no 0/O or 1/I/L, so it is easy to read aloud) and a QR code.
- **Share** gives four ways to send it:
  - **Share to Teams:** Microsoft's own "Share to Teams" window opens. The teacher picks the class team and posts the link in a channel, or turns it into a Teams **Assignment** (Teams for Education).
  - **Show on the board:** a full-screen QR code and code for the projector. Students' names appear as they join.
  - **Copy link**.
  - **Download QR code** (a PNG to print or paste anywhere).
- Students scan the QR code, or open `join.html` and type the code. They see the teacher's name and the class, press Start, and the worksheet opens with the class filled in and locked. Their answers are sent automatically and appear under that class code in the dashboard.
- **Close** stops a code; **Reopen** starts it again. Class codes are stored in the **Assignments** tab of the Google Sheet.
- The look of the signed-out teacher page and `join.html` is in `source/landing.css` and `source/landing-ill.html` (original illustrations).
- The QR codes on the teacher page are drawn in the browser by `source/vendor/qrcode.js`, Kazuhiko Arase's QR Code Generator (MIT licence; its notice is kept at the top of the file).

**How teachers log in (no passwords):** a teacher presses **Log in**, types their email (school, Outlook/Microsoft or Gmail), and gets a 6-digit code by email. They type the code and they are in for 7 days. Codes last 10 minutes; 5 wrong tries cancel a code; a code is only emailed to approved teachers. The emails are sent from the Google account that owns the Apps Script (Gmail allows about 100 a day, which is plenty).

**Giving a teacher a login:** open `admin.html` (your admin key), go to **Teacher logins**, type the teacher's name and email, and press **Add teacher**. They get an email telling them how to log in. Teachers can also press **Sign up** on the teacher page; their request appears on `admin.html` with **Approve** / **Decline**. **Remove** logs a teacher out at once. (Emails listed in the optional `OWNER_EMAILS` property can also do this from `teacher.html`.)

**One-time setup (owner, about 3 minutes):**
1. Open the Apps Script project (the Google Sheet → **Extensions → Apps Script**). Open https://raw.githubusercontent.com/aamermath-ai/ais-sat/main/source/analytics/Code.gs in another tab, select all (Ctrl+A / Cmd+A) and copy. In Apps Script, click inside `Code.gs`, select all, paste, and save (Ctrl+S / Cmd+S).
2. **Deploy → Manage deployments → Edit (pencil) → Version: New version → Deploy.** Keep the same deployment so the web-app URL does not change. Google asks you to authorize again (the script now sends login emails): choose your account → **Advanced → Go to (project name) (unsafe) → Allow**. "Unsafe" only means Google has not reviewed your own script.
3. Still in Apps Script, choose **testEmail** in the list next to **▷ Run**, press **Run**, then **Review permissions → your account → Advanced → Go to (project) (unsafe) → Allow**. You get a test email. (Deploying does not ask for this permission; without it, login codes cannot be sent.)
4. Open `admin.html`, enter the admin key (16+ characters), and add yourself and your colleagues under **Teacher logins**.
5. Open `teacher.html`, press **Log in**, type your email, and use the code from your inbox.

If the login page says "the school server needs the latest Code.gs", step 1 or 3 has not been done yet. No Google Cloud or Microsoft (Azure) setup is needed.

Change the link in the approval emails with `siteUrl_()` in `Code.gs` if the site moves.

## 7. Usage statistics (your private backend)

The site can count anonymous usage: **daily visitors, questions practised, accuracy, practice sets, minutes, and which sections are used**. The data goes into a Google Sheet that you own, and you read it on a private dashboard at **`admin.html`** (for example https://aamermath-ai.github.io/ais-sat/admin.html), which needs your admin key.

**What is sent:** a random device ID (to count unique visitors), the date, which sections were opened (once per day), and for each practice set the number of questions, correct answers and minutes. **No names, emails, profile details or IP addresses are stored.** Tell students and parents this before switching it on, in line with the school's privacy policy.

### One-time setup (about 10 minutes, free)
1. Signed in to Google, open **sheets.new** and name the sheet *SAT AIS statistics*.
2. In the sheet: **Extensions → Apps Script**. Delete the sample code, paste the whole of `source/analytics/Code.gs`, and click **Save**.
3. Click the gear icon (**Project Settings**) → **Script properties** → **Add script property**: name `ADMIN_KEY`, value a long password only you know. Save.
4. Click **Deploy → New deployment** → gear icon → **Web app**. Set *Execute as:* **Me**, *Who has access:* **Anyone**. Click **Deploy**, allow the permissions, and copy the **Web app URL** (it ends in `/exec`).
5. Put that URL in `source/emir.html` at `const STATS_URL="";` (between the quotes), run `python3 source/build.py`, and publish. Statistics start from that moment.
6. Open `admin.html`, paste the same URL and your admin key, and click **Show statistics**. Use **Download CSV** for reports, or open the Google Sheet for every raw event.

### Notes
- "Anyone" access is needed so students' browsers can send counts without signing in. Anyone can send data, but only someone with the admin key can read the totals.
- A *visitor* is one browser on one device, so a student who uses a phone and a laptop counts twice.
- After editing `Code.gs`, choose **Deploy → Manage deployments → Edit → New version** so the same URL keeps working.
- To pause collection, set `STATS_URL` back to `""` and rebuild.
- Free Google limits are far above what a school needs (each student sends only a few events a day).

## 8. Contact

Mathematics Department, American International School.
