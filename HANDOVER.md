# SAT AIS: handover guide

A free Digital SAT practice website for students of the American International School (AIS), built by the Mathematics Department.

- **Live site:** https://aamermath-ai.github.io/ais-sat/
- **Code:** https://github.com/aamermath-ai/ais-sat
- **Download everything as a ZIP:** https://github.com/aamermath-ai/ais-sat/archive/refs/heads/main.zip

---

## 1. What the website does

| Section | What students get |
|---|---|
| **Summary** | Animated daily rings (questions, correct answers, minutes), an estimated SAT score, a progress graph, streaks, awards, a test-day countdown and a "Dream big" card with a motivating quote |
| **Practice** | Timed adaptive sets (whole syllabus, Math or Reading & Writing; by domain or skill). All served questions are SAT Hard level, with the hardest first. Built-in Desmos calculator and reference sheet, as on test day. Step-by-step solutions after every wrong answer |
| **Formulas** | The SAT Math formula sheet with geometry diagrams, plus a mind map of every Math subtopic |
| **Desmos Practice** | The *Full SAT Desmos Guide* video, 27 Desmos techniques with worked solutions, the Desmos Speed Trainer and a full Desmos calculator |
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
admin.html               private usage dashboard (needs your admin key; see section 7)
questions.json           questions served to students (Hard level only, 403)
data/questions-all.json  the full bank: 1,229 questions (1,069 Math, 160 R&W; easy, medium, hard)
assets/                  background video (720p and 1080p) and its poster image
logo.png, apple-touch-icon.png
tools/                   copies of the Math question generator and the figure builder
source/                  EVERYTHING NEEDED TO EDIT AND REBUILD THE SITE
  emir.html              the master source of the app (edit this one)
  build.py               rebuilds the website from source/
  bank/                  274 hand-written questions, one JSON file each
  generated_math.json    955 generated Math questions
  gen_math.py            the Math question generator (exact answers, worked steps)
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

**More Math questions:** `python3 source/gen_math.py` (see the comments at the top of the file).

**University and scholarship data:** it is the `const UNIS=[...]` list in `source/emir.html`. It was checked in November 2026 and **should be reviewed every year** (for example each September), because score ranges, testing policies, scholarships and deadlines change.

**Background video:** to replace it, re-encode the new clip into `night-720.mp4`, `night-1080.mp4` and `night-poster.jpg` (for example with ffmpeg), put them in `source/nightwalk/`, then rebuild.

## 5. Moving it to the school (options)

1. **Keep GitHub, give the school ownership (easiest).** The repository owner can use *Settings → General → Transfer ownership* to move it to a school GitHub account or organisation. The site keeps working at the new account's GitHub Pages address.
2. **Use a school web address** (for example `sat.ais.sch.ae`): the school's IT team adds a DNS `CNAME` record pointing to `<account>.github.io` and enters the domain under *Settings → Pages → Custom domain*.
3. **Host it on the school's own server:** copy the files in the repository root (everything except `source/` and `tools/`, which are only needed for editing) to any web folder. No server software is needed.

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
