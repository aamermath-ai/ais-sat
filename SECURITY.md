# SAT AIS: security

Last reviewed: 27 November 2026.

## How the site is built (why the attack surface is small)
- A **static website** (GitHub Pages) plus one Google Apps Script backend (`source/analytics/Code.gs`) and a Google Sheet. The Sheet is reached only through the script, never directly from the browser.
- **Logins:** teachers log in with a 6-digit code emailed to them (or Google sign-in); the owner uses the admin key on `admin.html`. There are no passwords to leak.
- SAT practice progress stays in each student's own browser. Worksheet results sent with "Send to my teacher" (name, class, score) are stored in the Sheet.
- The only data sent anywhere is the optional, anonymous usage statistics (random device ID, date, sections opened, practice-set totals). It goes to a Google Sheet owned by the department.

## What was checked
| Area | Finding |
|---|---|
| Cross-site scripting (injected code) | All question text, choices, passages, tables, diagram labels, university data and statistics are escaped before display. No problems found. |
| Secrets in the code or its history | None. No passwords, API keys, admin key or personal email addresses are in the repository. The statistics URL is public by design: it accepts counts but reveals nothing without the admin key. |
| HTTPS | Enforced by GitHub Pages (HSTS header present). |
| Third-party code | No third-party JavaScript runs in the site. External services are shown only inside isolated frames (YouTube, Desmos, Speed Trainer) or as links. |

## Login security audit (27 Nov 2026)
Checked against the 6-point pre-launch checklist (database, secrets, access control, login limits, uploads, input).

| # | Check | Result | What was done |
|---|---|---|---|
| 1 | Database locked down | PASS | Sheet is only reachable through `Code.gs`; every teacher action checks a signed session and that the teacher is still approved. |
| 2 | No secrets in the browser or git | PASS | No keys or passwords in code or history. `SESSION_SECRET` and `ADMIN_KEY` live only in Apps Script properties. |
| 3 | Login checked AND owner checked | **Fixed** | (a) Any approved teacher could see every student's worksheet results in the school. Now a teacher sees only results from their own class codes (and results typed in for a class they made a code for); owners still see all. (b) Any contributor for a grade could edit, submit or cancel another teacher's worksheet upload. Now only the uploader or an owner can. |
| 4 | Login / code attempt limits | **Fixed** | Before: 5 wrong tries per code, but a new code could be requested 4 times per 15 min (20 guesses). Now: 5 wrong codes lock that email for 15 minutes, 15 wrong in 6 hours lock it for 6 hours, and no new code is sent while locked. |
| 5 | File uploads | **Fixed** | Type was trusted from the browser. Now the file's first bytes must match (PDF, Word, PowerPoint, PNG, JPEG). Size limit 15 MB; files are stored in Drive and never run. |
| 6 | Injection / XSS | PASS (hardened) | Text is escaped before display; Sheet formula injection blocked. The escape helper in `admin.html` and `worksheets/w.html` now also escapes quotes. |

Also: the admin dashboard now sends the admin key in a POST body instead of the web address (`?key=`), so it no longer appears in server logs; class codes and worksheet IDs now use a secure random source instead of `Math.random`.

## Protections added
**Website (`index.html`)**
- **Content Security Policy:** the browser runs only the site's own scripts, identified by their SHA-256 fingerprints, and contacts only the listed services: Google Fonts, the statistics script, YouTube (privacy mode), Desmos and the Speed Trainer. Any injected or tampered script is blocked. The fingerprints are recalculated automatically by `source/build.py`.
- **Anti-clickjacking:** the site refuses to run inside another website's frame and shows a safe link instead.
- **Referrer policy:** other sites receive only the site's address, never page details.
- **Test-window links checked:** a crafted `?exam=` link cannot start a malformed test; every setting is checked against an allowed list.
- **External windows** (Desmos, Speed Trainer) cannot control the SAT AIS page that opened them.
- **The Speed Trainer frame is sandboxed:** it cannot redirect or take over the page.
- `object-src`, `base-uri` and `form-action` are disabled.

**ACT page (`act.html`)**: the same Content Security Policy (script fingerprints; only Google Fonts, the statistics script and Desmos allowed), anti-clickjacking, validated test links and the same test-window rules.

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
- **Logging out does not cancel a stolen session token** before its 7 days end; removing the teacher on admin.html does. On a shared computer, always press Log out.
- **The admin-key lockout is site-wide:** someone sending 10 wrong keys can lock you out of the dashboard for 15 minutes (they still can't get in).
- **Anyone could send fake usage counts** to the statistics script, within the rate limits. Treat the dashboard as a guide, not an audited figure.
- **GitHub Pages can't send custom security headers.** The protections above are delivered inside the pages, which modern browsers enforce. Hosting on a school server would allow adding the same rules as real HTTP headers (`Content-Security-Policy` with `frame-ancestors 'none'`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`).

## Reporting a problem
Contact the Mathematics Department, American International School.
