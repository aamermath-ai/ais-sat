# SAT AIS: security

Last reviewed: November 2026.

## How the site is built (why the attack surface is small)
- A **static website**: no server code, no database and no logins on the site. Nothing personal is collected.
- Student progress stays in each student's own browser.
- The only data sent anywhere is the optional, anonymous usage statistics (random device ID, date, sections opened, practice-set totals). It goes to a Google Sheet owned by the department.

## What was checked
| Area | Finding |
|---|---|
| Cross-site scripting (injected code) | All question text, choices, passages, tables, diagram labels, university data and statistics are escaped before display. No problems found. |
| Secrets in the code or its history | None. No passwords, API keys, admin key or personal email addresses are in the repository. The statistics URL is public by design: it accepts counts but reveals nothing without the admin key. |
| HTTPS | Enforced by GitHub Pages (HSTS header present). |
| Third-party code | No third-party JavaScript runs in the site. External services are shown only inside isolated frames (YouTube, Desmos, Speed Trainer) or as links. |

## Protections added
**Website (`index.html`)**
- **Content Security Policy:** the browser runs only the site's own scripts, identified by their SHA-256 fingerprints, and contacts only the listed services: Google Fonts, the statistics script, YouTube (privacy mode), Desmos and the Speed Trainer. Any injected or tampered script is blocked. The fingerprints are recalculated automatically by `source/build.py`.
- **Anti-clickjacking:** the site refuses to run inside another website's frame and shows a safe link instead.
- **Referrer policy:** other sites receive only the site's address, never page details.
- **Test-window links checked:** a crafted `?exam=` link cannot start a malformed test; every setting is checked against an allowed list.
- **External windows** (Desmos, Speed Trainer) cannot control the SAT AIS page that opened them.
- **The Speed Trainer frame is sandboxed:** it cannot redirect or take over the page.
- `object-src`, `base-uri` and `form-action` are disabled.

**Admin dashboard (`admin.html`)**
- The same Content Security Policy and anti-clickjacking protection; `no-referrer`; not indexed by search engines.
- The admin key is kept **only for the browser session** unless "Remember" is ticked, and it signs out after **30 minutes** without activity.

**Statistics backend (`source/analytics/Code.gs`)**
- **Size and format checks:** each event is limited to 1.5 KB. Only known event types, real browser-made device IDs, and dates within two days of today are accepted.
- **Rate limits:** 120 events per device per hour, and 20,000 events per day site-wide, so nobody can flood the sheet.
- **Spreadsheet formula protection:** no stored value can start with `=`, `+`, `-` or `@`.
- **Admin key protection:**
  - it must be at least **16 characters**;
  - it is compared in constant time;
  - after **10 wrong keys**, reading statistics locks for 15 minutes.

## What the owner must do (cannot be done from the code)
1. **Update the statistics script:** paste the new `source/analytics/Code.gs` into Apps Script, Save, then **Deploy → Manage deployments → ✏️ Edit → Version: New version → Deploy**. The web address stays the same.
2. **Admin key:** make it at least 16 characters, for example four random words with numbers. Change it in Apps Script → Project Settings → Script properties if it may have been shared.
3. **GitHub account** (it controls the live site):
   - turn on **two-factor authentication** (Settings → Password and authentication);
   - keep collaborators to the people who need them;
   - in the repository's Settings → Pages, keep **Enforce HTTPS** ticked.
4. **Google account** (it owns the statistics): turn on **2-Step Verification**. Don't share the sheet with anyone who shouldn't see the statistics.
5. **Review once a term:** who has access to the GitHub repository and the Google Sheet.

## Known limits (be honest with users)
- **The test window can't physically lock a device.** It detects leaving and warns, and each time is counted. A student with technical skill can bypass browser-based checks. For high-stakes exams, use a managed lockdown browser on school devices.
- **Progress is self-reported.** It lives in the student's browser, so a student could edit their own stats. It is a practice tool, not a grade record.
- **Anyone could send fake usage counts** to the statistics script, within the rate limits. Treat the dashboard as a guide, not an audited figure.
- **GitHub Pages can't send custom security headers.** The protections above are delivered inside the pages, which modern browsers enforce. Hosting on a school server would allow adding the same rules as real HTTP headers (`Content-Security-Policy` with `frame-ancestors 'none'`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`).

## Reporting a problem
Contact the Mathematics Department, American International School.
