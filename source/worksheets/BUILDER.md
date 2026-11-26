# Worksheet builder: how queued uploads become worksheets

These are instructions for the **Claude session** that builds the queued worksheets. People only need the first section.

## For people

1. On `admin.html`, tick the grades a teacher may build worksheets for (Teacher logins → "Can build worksheets for").
2. That teacher logs in on `teacher.html` and opens **Worksheet builder** (`build.html`). They upload a PDF, Word or PowerPoint lesson.
3. Start a Claude session and say: **"Build the queued Omega worksheets."** You can also schedule this to run daily.
4. The contributor gets an email when the draft is ready. They check it, edit it and press **Send for approval**.
5. On `admin.html` → **Worksheet requests**, press **Preview** and then **Approve**. The worksheet goes live straight away at `worksheets/w.html?id=…`. It also appears on the Worksheets page, in the teachers' Assign list and in class codes.

## For the Claude session

### 1. Find the queue (Google Drive connector)
- **Requests:** open the Google Sheet **"SAT AIS statistics"** and read its **Builds** tab.
  - Each row is one request: id, created, email, name, grade, term, module, topic, code, title, notes, fileId, fileName, status, …
  - Work on rows whose status is **queued**.
- **Uploads:** the files are in the Drive folder **"Omega uploads"**. Each file name starts with the request id, e.g. `wk7q2mxab · Grade 7 · 3.2 Unit Rates · lesson.pptx`. Read the file (`read_file_content`, or download it if pictures matter).

### 2. Build the worksheet as JSON
- Follow the same style as the hand-made worksheets, e.g. `g9-algebra-3-2-slopes-rates-of-change.html`:
  - clear, friendly language for the grade, and short sentences;
  - UAE contexts where they fit;
  - **12–16 questions** in **4–5 parts**, going from warm-up to real life to critical thinking;
  - every question has a **hint** and **worked steps**.
- Use the lesson's own LO, standard, vocabulary and worked examples. Respect the contributor's **notes**.
- Write original questions modelled on the lesson. Do not copy copyrighted textbook questions word for word.
- **Format:** see `builder-example.json` for a complete example.

```json
{
  "v": 1,
  "kicker": "Grade 7 Mathematics · Module 2",          // small green line above the title
  "lo": "I can …", "standard": "7.RP.A.1",
  "formula": "unit rate = total ÷ number of units",    // optional, big green line
  "tip": "short reminder",                              // optional
  "keywords": ["rate", "unit rate"],                    // up to 8
  "hero": {"svg": "<svg viewBox='0 0 640 400' …>…</svg>"},  // optional picture beside the title
  "parts": [{"id": "A", "name": "Warm-up", "intro": "Tap the correct answer."}],
  "questions": [
    {"id": "a1", "part": "A", "kind": "pick", "text": "…", "options": ["…", "…"], "answer": "…",
     "hint": "…", "steps": ["…", "…"], "draw": {…}},
    {"id": "b1", "part": "B", "kind": "num", "text": "…", "answer": 6, "tol": 0.01, "unit": "AED per kg",
     "hint": "…", "steps": ["…"]}
  ],
  "footer": "optional small print"
}
```

**Fields**
- **Question kinds:**
  - `pick` means tap an answer. `answer` must equal one of the `options` exactly.
  - `num` means type a number. `answer` is a number, and students may type fractions such as `3/4`.
  - `tol` is the tolerance; use a bigger one for rounded answers.
- **Text:** may use `<b> <i> <sub> <sup> <br>` and nothing else (the page removes everything else).
- **Pictures** (`draw`, optional per question):
  - `{"type":"plot", x0,x1,y0,y1, gx,gy (grid step), lx,ly (label step), "lines":[[[x,y],[x,y],"#colour","label"]], "pts":[[x,y,"label"]], "rr":{"a":[x,y],"b":[x,y],"rise":"text","run":"text"}, "xl":"x-axis title", "yl":"y-axis title"}`
  - `{"type":"card","rows":[["big text","big"],["normal text","l"],["small text","sm"]]}`
  - `{"type":"svg","svg":"<svg …>"}` for any other diagram. Simple shapes and text only: no scripts, no images, no links.
- **Hero:** an SVG `viewBox="0 0 640 400"` scene related to the lesson. Use UAE flag colours: green `#00843D`, red `#C8102E` and black, on a light sky `#e8f3f9`.

### 3. Check it
Run `python3 source/tools/check_worksheet.py draft.json`. It must say **OK**. It also prints each numeric answer, so you can double-check the maths.

### 4. Hand it back
- With the Drive connector, create a file named exactly **`<id>.json`** (for example `wk7q2mxab.json`) in the Drive folder **"Omega drafts"**.
- Use `contentMimeType` `application/json` and `disableConversionToGoogleType: true`. Create the folder if it does not exist.
- The website imports it the next time anyone opens the builder or the admin page:
  - the request becomes **Draft ready**;
  - the contributor gets an email;
  - the file is renamed `imported-<id>.json`.
- **Rejected drafts:** an `invalid-<id>.json` name means the draft did not pass the check. Fix it and upload it again under the original name.
