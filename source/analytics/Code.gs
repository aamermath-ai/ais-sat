//
// SAT AIS – usage statistics backend (Google Apps Script + Google Sheet).
// Receives anonymous events from the website and serves daily totals to admin.html.
// Setup steps: see HANDOVER.md, section "Usage statistics".
//
// What is stored per event (no names, emails or IP addresses):
// received  – server time
// date      – the student's local date (YYYY-MM-DD)
// type      – visit | tab | set
// device    – a random ID created by the browser (counts unique visitors; it is not linked to a person)
// mode      – practice set label (e.g. "Math · Algebra")
// questions, correct, hard, minutes, math, rw – numbers for a finished practice set
// tab       – which section was opened (today, practice, formulas, desmos, unis, bank)
//
// Worksheets + teacher login (added later, same script):
// - Students press "Send to my teacher" on a worksheet: their name, class and per-question results go to the
//   "Worksheets" tab (one row per student per worksheet, updated as they go).
// - Teachers log in on teacher.html with their email address (Gmail, Outlook/Microsoft or school email): they type
//   their email, this script emails them a 6-digit code, they type the code. No passwords. Their email is their username.
//   Owners add teachers (or approve requests) on teacher.html. Emails in TEACHER_DOMAINS are approved automatically.
//   Script properties used:
//     OWNER_EMAILS     – comma-separated emails of the people who manage teachers (needed: the first owner logs in with it)
//     GOOGLE_CLIENT_ID – optional, only for the older "Sign in with Google" button
//     TEACHER_DOMAINS  – optional, comma-separated email domains approved automatically (e.g. a school domain)
//     SESSION_SECRET   – created automatically; do not share
//
var SHEET_NAME = 'Events';
var HEAD = ['received', 'date', 'type', 'device', 'mode', 'questions', 'correct', 'hard', 'minutes', 'math', 'rw', 'tab'];
var TYPES = ['visit', 'tab', 'set'];

// ---- security limits
var MAX_BODY = 4000;            // bytes per request; events are ~200, worksheet results ~800, Google sign-in tokens ~1200
var MAX_PER_DEVICE_HOUR = 120;  // a student generates well under 30 events an hour
var MAX_PER_DAY = 20000;        // whole-site cap per day, to stop anyone flooding the sheet
var MIN_KEY_LENGTH = 16;        // admin key must be at least this long
var MAX_BAD_KEYS = 10;          // wrong admin keys allowed per 15 minutes before a 15-minute lockout

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) { sh = ss.insertSheet(SHEET_NAME); sh.appendRow(HEAD); sh.setFrozenRows(1); }
  return sh;
}
function text_(v, max) {
  var t = String(v == null ? '' : v).replace(/[^\w\-\/ .:&()·]/g, '').slice(0, max || 40);
  return /^[=+\-@]/.test(t) ? "'" + t : t;   // never let a value start like a spreadsheet formula
}
function count_(cache, key, ttl) { var n = Number(cache.get(key) || 0) + 1; cache.put(key, String(n), ttl); return n; }
function sameKey_(a, b) {   // constant-time comparison
  a = String(a || ''); b = String(b || ''); var diff = a.length ^ b.length;
  for (var i = 0; i < Math.max(a.length, b.length); i++) diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return diff === 0;
}
function dateOk_(d) {   // the student's date must be within 2 days of today
  var t = Date.parse(d + 'T12:00:00Z'); return isFinite(t) && Math.abs(t - Date.now()) < 3 * 864e5;
}
function num_(v, max) { v = Number(v); return isFinite(v) && v >= 0 ? Math.min(Math.round(v), max) : 0; }
function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

// The website sends events here (POST, plain-text JSON body).
function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    var body = (e && e.postData && e.postData.contents) || '';
    if (body.length > MAX_BODY) return out_({ ok: false });
    var d = JSON.parse(body || '{}');
    if (d.a) return out_(teacherApi_(d));   // teacher sign-in and dashboard (teacher.html)
    if (d.t === 'ws') return out_(worksheetSubmit_(d, lock));   // a student sends a worksheet score
    var t = text_(d.t, 10);
    if (TYPES.indexOf(t) < 0 || !/^\d{4}-\d{2}-\d{2}$/.test(String(d.date)) || !dateOk_(String(d.date))) return out_({ ok: false });
    var dev = String(d.d || '');
    if (!/^[a-z0-9]{6,16}$/.test(dev)) return out_({ ok: false });   // only real browser-made IDs
    var cache = CacheService.getScriptCache();
    if (count_(cache, 'dev:' + dev, 3600) > MAX_PER_DEVICE_HOUR) return out_({ ok: false });
    if (count_(cache, 'day:' + new Date().toISOString().slice(0, 10), 21600) > MAX_PER_DAY) return out_({ ok: false });
    lock.waitLock(10000);
    sheet_().appendRow([new Date(), "'" + d.date, t, dev, text_(d.mode, 80),
      num_(d.n, 200), num_(d.c, 200), num_(d.h, 200), num_(d.m, 600), num_(d.math, 200), num_(d.rw, 200), text_(d.tab, 20)]);
    return out_({ ok: true });
  } catch (err) {
    return out_({ ok: false });
  } finally {
    try { lock.releaseLock(); } catch (x) {}
  }
}

// admin.html reads daily totals here: ?key=ADMIN_KEY&since=YYYY-MM-DD
function doGet(e) {
  var p = (e && e.parameter) || {};
  if (p.a === 'config') return out_({ ok: true, v: 3, owners: list_('OWNER_EMAILS').length > 0, clientId: prop_('GOOGLE_CLIENT_ID') });
  if (p.a === 'join') return out_(joinInfo_(p.c));
  var key = PropertiesService.getScriptProperties().getProperty('ADMIN_KEY');
  if (!key) return out_({ ok: false, error: 'ADMIN_KEY is not set in Project Settings → Script properties.' });
  if (key.length < MIN_KEY_LENGTH) return out_({ ok: false, error: 'For security, ADMIN_KEY must be at least ' + MIN_KEY_LENGTH + ' characters. Make it longer in Script properties.' });
  var cache = CacheService.getScriptCache();
  if (Number(cache.get('badkeys') || 0) >= MAX_BAD_KEYS) return out_({ ok: false, error: 'Too many wrong keys. Statistics are locked for 15 minutes.' });
  if (!sameKey_(p.key, key)) { count_(cache, 'badkeys', 900); return out_({ ok: false, error: 'Wrong admin key.' }); }
  var since = /^\d{4}-\d{2}-\d{2}$/.test(String(p.since)) ? String(p.since) : '0000-00-00';
  var sh = sheet_(), last = sh.getLastRow();
  var rows = last > 1 ? sh.getRange(2, 1, last - 1, HEAD.length).getValues() : [];
  var days = {}, devices = {}, tabs = {}, modes = {}, total = { questions: 0, correct: 0, hard: 0, sets: 0, minutes: 0, math: 0, rw: 0 };
  var allDevices = {}, firstDate = null;
  rows.forEach(function (r) {
    var date = String(r[1]).replace(/^'/, ''), type = r[2], dev = String(r[3]);
    if (!firstDate || date < firstDate) firstDate = date;
    allDevices[dev] = 1;
    if (date < since) return;
    var day = days[date] || (days[date] = { date: date, visitors: {}, questions: 0, correct: 0, sets: 0, minutes: 0 });
    day.visitors[dev] = 1; devices[dev] = 1;
    if (type === 'tab') { var tb = String(r[11]); tabs[tb] = (tabs[tb] || 0) + 1; }
    if (type === 'set') {
      var n = +r[5] || 0, c = +r[6] || 0;
      day.questions += n; day.correct += c; day.sets++; day.minutes += +r[8] || 0;
      total.questions += n; total.correct += c; total.hard += +r[7] || 0; total.sets++; total.minutes += +r[8] || 0;
      total.math += +r[9] || 0; total.rw += +r[10] || 0;
      var md = String(r[4]).split(' · ')[0] || 'Practice'; modes[md] = (modes[md] || 0) + 1;
    }
  });
  var list = Object.keys(days).sort().map(function (k) {
    var d = days[k]; return { date: d.date, visitors: Object.keys(d.visitors).length, questions: d.questions, correct: d.correct, sets: d.sets, minutes: d.minutes };
  });
  return out_({ ok: true, since: since, firstDate: firstDate, days: list, uniqueVisitors: Object.keys(devices).length,
    allTimeVisitors: Object.keys(allDevices).length, totals: total, tabs: tabs, modes: modes, events: rows.length });
}


// ======================================================================================================
// Worksheets: student results
// ======================================================================================================
var WS_SHEET = 'Worksheets';
var WS_HEAD = ['updated', 'date', 'device', 'worksheet', 'title', 'grade', 'name', 'class', 'score', 'total', 'items', 'parts', 'first', 'assignment'];
var MAX_WS_PER_DEVICE_HOUR = 200;

function prop_(k) { return PropertiesService.getScriptProperties().getProperty(k) || ''; }
function list_(k) { return prop_(k).split(',').map(function (x) { return x.trim().toLowerCase().replace(/^@/, ''); }).filter(String); }
function tab_(name, head) {
  var ss = SpreadsheetApp.getActiveSpreadsheet(), sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); sh.appendRow(head); sh.setFrozenRows(1); }
  return sh;
}
// free text typed by students/teachers (names can be in any language): strip markup and control characters
function plain_(v, max) {
  var t = String(v == null ? '' : v).replace(/[\u0000-\u001f\u007f<>"`\\]/g, '').replace(/\s+/g, ' ').trim().slice(0, max || 60);
  return /^[=+\-@\t]/.test(t) ? "'" + t : t;
}
function unplain_(v) { return String(v == null ? '' : v).replace(/^'/, ''); }

function worksheetSubmit_(d, lock) {
  var dev = String(d.d || ''), ws = String(d.ws || '');
  if (!/^[a-z0-9]{6,16}$/.test(dev) || !/^[a-z0-9][a-z0-9\-]{2,60}$/.test(ws)) return { ok: false };
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(d.date)) || !dateOk_(String(d.date))) return { ok: false };
  var name = plain_(d.name, 60), cls = plain_(d.cls, 12).toUpperCase();
  var asg = '';
  if (d.asg) {   // joined with a class code: the class comes from the teacher's assignment
    var A = findAssignment_(d.asg);
    if (A && A.status === 'open' && A.ws === ws) { asg = A.code; cls = A.cls; }
  }
  if (name.length < 2 || !cls) return { ok: false, error: 'name' };
  var items = String(d.items || '');   // e.g. "A10,A11,B02": part letter, done (0/1), wrong tries before (0–9)
  if (!/^([A-Z][01]\d)(,[A-Z][01]\d){0,59}$/.test(items)) return { ok: false };
  var parts = String(d.parts || '').replace(/[^A-Za-z0-9 :|θ⁻¹\-–·()]/g, '').slice(0, 300);
  var list = items.split(','), score = 0, first = 0;
  list.forEach(function (x) { if (x[1] === '1') { score++; if (x[2] === '0') first++; } });
  var cache = CacheService.getScriptCache();
  if (count_(cache, 'wsdev:' + dev, 3600) > MAX_WS_PER_DEVICE_HOUR) return { ok: false };
  if (count_(cache, 'day:' + new Date().toISOString().slice(0, 10), 21600) > MAX_PER_DAY) return { ok: false };
  lock.waitLock(10000);
  var sh = tab_(WS_SHEET, WS_HEAD), last = sh.getLastRow();
  if (sh.getLastColumn && sh.getLastColumn() < WS_HEAD.length) sh.getRange(1, 1, 1, WS_HEAD.length).setValues([WS_HEAD]);   // older sheets: add new columns
  var row = [new Date(), "'" + d.date, dev, ws, plain_(d.title, 90), plain_(d.grade, 4), name, cls, score, list.length, items, parts, first, asg];
  // one row per student per worksheet (per class code) on this device: update it if it is already there
  var key = dev + '|' + ws + '|' + name.toLowerCase() + '|' + asg, at = -1;
  if (last > 1) {
    var v = sh.getRange(2, 3, last - 1, 5).getValues();   // device, worksheet, title, grade, name
    var g = sh.getRange(2, 14, last - 1, 1).getValues();  // assignment
    for (var i = v.length - 1; i >= 0; i--) {
      if (v[i][0] + '|' + v[i][1] + '|' + unplain_(v[i][4]).toLowerCase() + '|' + String(g[i][0] || '') === key) { at = i + 2; break; }
    }
  }
  if (at > 0) sh.getRange(at, 1, 1, row.length).setValues([row]); else sh.appendRow(row);
  return { ok: true, score: score, total: list.length, cls: cls, asg: asg };
}

// ======================================================================================================
// Teachers: Sign in with Google, approval, dashboard data
// ======================================================================================================
var T_SHEET = 'Teachers';
var T_HEAD = ['email', 'name', 'status', 'requested', 'lastLogin'];
var SESSION_DAYS = 7;
var MAX_LOGINS_PER_HOUR = 300;

function secret_() {
  var props = PropertiesService.getScriptProperties(), s = props.getProperty('SESSION_SECRET');
  if (!s) { s = Utilities.getUuid() + Utilities.getUuid(); props.setProperty('SESSION_SECRET', s); }
  return s;
}
function sign_(text) { return Utilities.base64EncodeWebSafe(Utilities.computeHmacSha256Signature(text, secret_())).replace(/=+$/, ''); }
function makeSession_(email) {
  var body = Utilities.base64EncodeWebSafe(email + '|' + (Date.now() + SESSION_DAYS * 864e5)).replace(/=+$/, '');
  return body + '.' + sign_(body);
}
function readSession_(tok) {
  var m = /^([A-Za-z0-9_\-]{4,400})\.([A-Za-z0-9_\-]{20,80})$/.exec(String(tok || ''));
  if (!m || !sameKey_(sign_(m[1]), m[2])) return null;
  var pad = m[1] + '==='.slice((m[1].length + 3) % 4);
  var parts = Utilities.newBlob(Utilities.base64DecodeWebSafe(pad)).getDataAsString().split('|');
  if (parts.length !== 2 || !(Number(parts[1]) > Date.now())) return null;
  return parts[0];
}
// Checks a Google access token (from the site's own Sign up / Log in buttons) and returns {email, name} or null
function verifyAccess_(at) {
  var clientId = prop_('GOOGLE_CLIENT_ID');
  if (!clientId || !/^[A-Za-z0-9._\-~+\/]{20,4000}$/.test(String(at || ''))) return null;
  var r = UrlFetchApp.fetch('https://oauth2.googleapis.com/tokeninfo?access_token=' + encodeURIComponent(at), { muteHttpExceptions: true });
  if (r.getResponseCode() !== 200) return null;
  var p = JSON.parse(r.getContentText());
  if (p.aud !== clientId && p.azp !== clientId) return null;   // the token must have been issued to this site
  if (String(p.email_verified) !== 'true' || !p.email || !(Number(p.exp) * 1000 > Date.now())) return null;
  var name = '';
  try {
    var u = UrlFetchApp.fetch('https://openidconnect.googleapis.com/v1/userinfo', { headers: { Authorization: 'Bearer ' + at }, muteHttpExceptions: true });
    if (u.getResponseCode() === 200) name = JSON.parse(u.getContentText()).name || '';
  } catch (e) {}
  return { email: String(p.email).toLowerCase(), name: plain_(name || p.email, 60) };
}
// Checks a Google ID token with Google and returns {email, name} or null
function verifyGoogle_(cred) {
  var clientId = prop_('GOOGLE_CLIENT_ID');
  if (!clientId || !/^[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+$/.test(String(cred || ''))) return null;
  var r = UrlFetchApp.fetch('https://oauth2.googleapis.com/tokeninfo?id_token=' + encodeURIComponent(cred), { muteHttpExceptions: true });
  if (r.getResponseCode() !== 200) return null;
  var p = JSON.parse(r.getContentText());
  if (p.aud !== clientId) return null;
  if (p.iss !== 'accounts.google.com' && p.iss !== 'https://accounts.google.com') return null;
  if (String(p.email_verified) !== 'true' || !(Number(p.exp) * 1000 > Date.now())) return null;
  return { email: String(p.email).toLowerCase(), name: plain_(p.name || p.email, 60) };
}
function teachers_() {
  var sh = tab_(T_SHEET, T_HEAD), last = sh.getLastRow();
  var rows = last > 1 ? sh.getRange(2, 1, last - 1, T_HEAD.length).getValues() : [];
  return { sh: sh, rows: rows };
}
function findTeacher_(t, email) {
  for (var i = 0; i < t.rows.length; i++) if (String(t.rows[i][0]).toLowerCase() === email) return i;
  return -1;
}
function isOwner_(email) { return list_('OWNER_EMAILS').indexOf(email) >= 0; }
function autoApproved_(email) { return isOwner_(email) || list_('TEACHER_DOMAINS').indexOf(email.split('@')[1]) >= 0; }
function statusOf_(email) {
  if (isOwner_(email)) return 'approved';
  var t = teachers_(), i = findTeacher_(t, email);
  return i < 0 ? 'none' : String(t.rows[i][2]);
}

function teacherApi_(d) {
  var cache = CacheService.getScriptCache();
  if (d.a === 'login') {
    if (count_(cache, 'logins:' + new Date().toISOString().slice(0, 13), 3600) > MAX_LOGINS_PER_HOUR) return { ok: false, error: 'Too many sign-ins right now. Try again in a few minutes.' };
    if (!prop_('GOOGLE_CLIENT_ID')) return { ok: false, error: 'Teacher sign-in is not set up yet (GOOGLE_CLIENT_ID is missing).' };
    var g = d.at ? verifyAccess_(d.at) : verifyGoogle_(d.cred);
    if (!g) return { ok: false, error: 'Google sign-in could not be verified. Please try again.' };
    var lock = LockService.getScriptLock(); lock.waitLock(10000);
    try {
      var t = teachers_(), i = findTeacher_(t, g.email), status;
      if (i < 0) {
        status = autoApproved_(g.email) ? 'approved' : 'pending';
        t.sh.appendRow([g.email, g.name, status, new Date(), new Date()]);
        if (status === 'pending') notifyOwners_(g);
      } else {
        status = String(t.rows[i][2]);
        if (status !== 'approved' && autoApproved_(g.email)) status = 'approved';
        t.sh.getRange(i + 2, 2, 1, 4).setValues([[g.name, status, t.rows[i][3], new Date()]]);
      }
      if (status !== 'approved') return { ok: true, status: status, email: g.email, name: g.name };
      return { ok: true, status: 'approved', email: g.email, name: g.name, owner: isOwner_(g.email), session: makeSession_(g.email) };
    } finally { try { lock.releaseLock(); } catch (x) {} }
  }
  if (d.a === 'code') return sendCode_(d.email);
  if (d.a === 'verify') return verifyCode_(d.email, d.code);
  if (d.a === 'request') return requestAccess_(d.email, d.name);
  // everything below needs a valid session of an approved teacher
  var email = readSession_(d.s);
  if (!email) return { ok: false, error: 'session' };
  if (statusOf_(email) !== 'approved') return { ok: false, error: 'session' };
  if (count_(cache, 'tapi:' + email, 3600) > 600) return { ok: false, error: 'Too many requests. Try again later.' };
  if (d.a === 'data') return worksheetData_(email);
  if (d.a === 'assign') {   // create a class code for a worksheet
    var ws = String(d.ws || ''), file = String(d.file || ''), cls = plain_(d.cls, 12).toUpperCase();
    if (!/^[a-z0-9][a-z0-9\-]{2,60}$/.test(ws) || !/^worksheets\/[a-z0-9\-]+\.html$/.test(file) || !cls) return { ok: false, error: 'Choose a worksheet and type the class.' };
    var due = /^\d{4}-\d{2}-\d{2}$/.test(String(d.due)) ? String(d.due) : '';
    var me2 = teachers_(), mi = findTeacher_(me2, email), tname = mi >= 0 ? unplain_(me2.rows[mi][1]) : email;
    var lock3 = LockService.getScriptLock(); lock3.waitLock(10000);
    try {
      var sh = tab_(A_SHEET, A_HEAD), code;
      do { code = newCode_(); } while (findAssignment_(code));
      sh.appendRow([code, ws, file, plain_(d.title, 90), plain_(d.grade, 4), cls, email, tname, new Date(), due, 'open']);
    } finally { try { lock3.releaseLock(); } catch (x) {} }
    var res = worksheetData_(email); res.created = code; return res;
  }
  if (d.a === 'close' || d.a === 'reopen') {   // stop or restart a class code (only its teacher or an owner)
    var A = findAssignment_(d.code);
    if (!A || (A.email !== email && !isOwner_(email))) return { ok: false, error: 'Class code not found.' };
    tab_(A_SHEET, A_HEAD).getRange(A.row, 11).setValue(d.a === 'close' ? 'closed' : 'open');
    return worksheetData_(email);
  }
  if (d.a === 'add' && isOwner_(email)) {   // the owner gives a teacher their login
    var ne = cleanEmail_(d.email), nn = plain_(d.name, 60);
    if (!ne) return { ok: false, error: 'Type a valid email address.' };
    var lk = LockService.getScriptLock(); lk.waitLock(10000);
    try {
      var t2 = teachers_(), k2 = findTeacher_(t2, ne);
      if (k2 < 0) t2.sh.appendRow([ne, nn || ne, 'approved', new Date(), '']);
      else t2.sh.getRange(k2 + 2, 2, 1, 2).setValues([[nn || unplain_(t2.rows[k2][1]) || ne, 'approved']]);
    } finally { try { lk.releaseLock(); } catch (x) {} }
    notifyApproved_(ne, nn);
    return worksheetData_(email);
  }
  if (d.a === 'approve' && isOwner_(email)) {
    var who = String(d.email || '').toLowerCase(), to = String(d.status || '');
    if (['approved', 'removed', 'pending'].indexOf(to) < 0) return { ok: false };
    var lock2 = LockService.getScriptLock(); lock2.waitLock(10000);
    try {
      var tt = teachers_(), k = findTeacher_(tt, who);
      if (k < 0) return { ok: false, error: 'Teacher not found.' };
      tt.sh.getRange(k + 2, 3).setValue(to);
      if (to === 'approved' && String(tt.rows[k][2]) !== 'approved') notifyApproved_(who, String(tt.rows[k][1]));
    } finally { try { lock2.releaseLock(); } catch (x) {} }
    return worksheetData_(email);
  }
  return { ok: false };
}

function worksheetData_(email) {
  var sh = tab_(WS_SHEET, WS_HEAD), last = sh.getLastRow();
  var rows = last > 1 ? sh.getRange(2, 1, last - 1, WS_HEAD.length).getValues() : [];
  var out = rows.map(function (r) {
    return { at: r[0] instanceof Date ? r[0].toISOString() : String(r[0]), date: unplain_(r[1]), ws: String(r[3]), title: unplain_(r[4]),
      grade: unplain_(r[5]), name: unplain_(r[6]), cls: unplain_(r[7]), score: +r[8] || 0, total: +r[9] || 0,
      items: String(r[10]), parts: unplain_(r[11]), first: +r[12] || 0, asg: String(r[13] || '') };
  });
  var own = isOwner_(email);
  var asg = assignments_().filter(function (a) { return own || a.email === email; });
  var res = { ok: true, email: email, owner: own, rows: out, assignments: asg };
  if (res.owner) {
    res.teachers = teachers_().rows.map(function (r) {
      return { email: String(r[0]), name: unplain_(r[1]), status: String(r[2]),
        requested: r[3] instanceof Date ? r[3].toISOString() : '', lastLogin: r[4] instanceof Date ? r[4].toISOString() : '' };
    });
  }
  return res;
}

function siteUrl_() { return 'https://aamermath-ai.github.io/ais-sat/teacher.html'; }
function notifyOwners_(g) {
  try {
    var to = list_('OWNER_EMAILS').join(',');
    if (to) MailApp.sendEmail(to, 'Worksheets AIS: teacher access request from ' + g.name,
      g.name + ' (' + g.email + ') asked for teacher access on Worksheets AIS.\n\nTo approve, log in at ' + siteUrl_() + ' and open "Teachers".');
  } catch (e) {}
}
function notifyApproved_(email, name) {
  try {
    MailApp.sendEmail(email, 'Worksheets AIS: your teacher login is ready',
      'Hello ' + (name || '') + ',\n\nYou now have a teacher login on Worksheets AIS.\n\n1. Open ' + siteUrl_() + '\n2. Press "Log in" and type this email address: ' + email +
      '\n3. We email you a 6-digit code. Type it in, and you are in.\n\nThere is no password. Share worksheets with your class by QR code or Microsoft Teams, and see your students\' results.\n\nMathematics Department, American International School');
  } catch (e) {}
}

// ---------------- email login codes (works with any email: Gmail, Outlook/Microsoft, school) ----------------
var CODE_MINUTES = 10, CODE_TRIES = 5, CODES_PER_EMAIL_15MIN = 4, CODES_PER_HOUR = 200;
function cleanEmail_(v) {
  var e = String(v || '').trim().toLowerCase();
  return /^[^\s@<>"'(),;:\\]{1,64}@[a-z0-9.\-]{1,190}\.[a-z]{2,}$/.test(e) ? e : '';
}
function sendCode_(raw) {
  var email = cleanEmail_(raw);
  if (!email) return { ok: false, error: 'Type your full email address, for example name@school.ae.' };
  if (!list_('OWNER_EMAILS').length) return { ok: false, error: 'Teacher login is not set up yet: OWNER_EMAILS is missing in the Apps Script.' };
  var cache = CacheService.getScriptCache();
  if (count_(cache, 'codes:' + new Date().toISOString().slice(0, 13), 3600) > CODES_PER_HOUR) return { ok: false, error: 'Too many login emails right now. Try again in a few minutes.' };
  var st = statusOf_(email);
  if (st === 'none') return { ok: true, status: 'none' };
  if (st !== 'approved') return { ok: true, status: st };
  if (count_(cache, 'codemail:' + email, 900) > CODES_PER_EMAIL_15MIN) return { ok: false, error: 'We already sent you several codes. Check your inbox (and junk folder), or try again in 15 minutes.' };
  var code = String(100000 + parseInt(Utilities.getUuid().replace(/-/g, '').slice(0, 12), 16) % 900000);   // getUuid uses a secure random source
  cache.put('otp:' + email, JSON.stringify({ h: sign_('otp|' + email + '|' + code), n: 0 }), CODE_MINUTES * 60);
  try {
    MailApp.sendEmail(email, 'Your Worksheets AIS login code: ' + code,
      'Your login code is ' + code + '\n\nType it on the Worksheets AIS teacher page. It works for ' + CODE_MINUTES + ' minutes.\n\nIf you did not ask for this, you can ignore this email.\n\nMathematics Department, American International School');
  } catch (e) { return { ok: false, error: 'The login email could not be sent. Please try again later.' }; }
  return { ok: true, status: 'sent', email: email };
}
function verifyCode_(raw, code) {
  var email = cleanEmail_(raw); code = String(code || '').replace(/\D/g, '');
  if (!email || code.length !== 6) return { ok: false, error: 'Type the 6-digit code from the email.' };
  var cache = CacheService.getScriptCache(), key = 'otp:' + email, o = null;
  try { o = JSON.parse(cache.get(key) || 'null'); } catch (e) { o = null; }
  if (!o) return { ok: false, error: 'This code has expired. Press "Send a new code".' };
  if (!sameKey_(o.h, sign_('otp|' + email + '|' + code))) {
    o.n++;
    if (o.n >= CODE_TRIES) { cache.remove(key); return { ok: false, error: 'Too many wrong codes. Press "Send a new code".' }; }
    cache.put(key, JSON.stringify(o), CODE_MINUTES * 60);
    return { ok: false, error: 'That code is not right. Check the email and try again.' };
  }
  cache.remove(key);
  if (statusOf_(email) !== 'approved') return { ok: false, error: 'This email does not have teacher access.' };
  var t = teachers_(), i = findTeacher_(t, email), name = email;
  if (i >= 0) { name = unplain_(t.rows[i][1]) || email; t.sh.getRange(i + 2, 5).setValue(new Date()); }
  else if (isOwner_(email)) { t.sh.appendRow([email, email.split('@')[0], 'approved', new Date(), new Date()]); name = email.split('@')[0]; }
  return { ok: true, status: 'approved', email: email, name: name, owner: isOwner_(email), session: makeSession_(email) };
}
function requestAccess_(raw, nm) {
  var email = cleanEmail_(raw), name = plain_(nm, 60);
  if (!email) return { ok: false, error: 'Type your full email address.' };
  if (name.length < 2) return { ok: false, error: 'Type your name.' };
  var cache = CacheService.getScriptCache();
  if (count_(cache, 'req:' + new Date().toISOString().slice(0, 13), 3600) > 60) return { ok: false, error: 'Too many requests right now. Try again later.' };
  var lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    var t = teachers_(), i = findTeacher_(t, email);
    if (i >= 0) return { ok: true, status: String(t.rows[i][2]), email: email };
    var status = autoApproved_(email) ? 'approved' : 'pending';
    t.sh.appendRow([email, name, status, new Date(), '']);
    if (status === 'pending') notifyOwners_({ email: email, name: name });
    return { ok: true, status: status, email: email };
  } finally { try { lock.releaseLock(); } catch (x) {} }
}


// ======================================================================================================
// Class codes (assignments): a teacher shares a worksheet with a class by QR code, link or Microsoft Teams
// ======================================================================================================
var A_SHEET = 'Assignments';
var A_HEAD = ['code', 'worksheet', 'file', 'title', 'grade', 'class', 'teacher', 'teacherName', 'created', 'due', 'status'];
var CODE_ABC = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';   // no 0/O or 1/I/L, so codes are easy to read aloud
function newCode_() { var c = ''; for (var i = 0; i < 6; i++) c += CODE_ABC.charAt(Math.floor(Math.random() * CODE_ABC.length)); return c; }
function assignments_() {
  var sh = tab_(A_SHEET, A_HEAD), last = sh.getLastRow();
  var rows = last > 1 ? sh.getRange(2, 1, last - 1, A_HEAD.length).getValues() : [];
  return rows.map(function (r, i) {
    return { row: i + 2, code: String(r[0]), ws: String(r[1]), file: String(r[2]), title: unplain_(r[3]), grade: unplain_(r[4]), cls: unplain_(r[5]),
      email: String(r[6]), teacher: unplain_(r[7]), created: r[8] instanceof Date ? r[8].toISOString() : String(r[8]), due: String(r[9]).replace(/^'/, ''), status: String(r[10]) };
  });
}
function findAssignment_(code) {
  code = String(code || '').toUpperCase();
  if (!/^[A-Z0-9]{6}$/.test(code)) return null;
  var all = assignments_();
  for (var i = 0; i < all.length; i++) if (all[i].code === code) return all[i];
  return null;
}
// public: what a student sees after typing or scanning a class code (no emails)
function joinInfo_(code) {
  var cache = CacheService.getScriptCache();
  if (count_(cache, 'join:' + new Date().toISOString().slice(0, 13), 3600) > 5000) return { ok: false, error: 'busy' };
  var A = findAssignment_(code);
  if (!A) return { ok: false, error: 'notfound' };
  if (A.status !== 'open') return { ok: false, error: 'closed' };
  return { ok: true, code: A.code, ws: A.ws, file: A.file, title: A.title, grade: A.grade, cls: A.cls, teacher: A.teacher, due: A.due };
}
