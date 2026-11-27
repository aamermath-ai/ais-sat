//
// Omega – usage statistics backend (Google Apps Script + Google Sheet).
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
//     OWNER_EMAILS     – optional: emails that can also manage teachers from teacher.html (admin.html can always do it with ADMIN_KEY)
//     PRO_DOMAINS      – optional: email domains whose teachers all get Omega Pro (a school licence), e.g. aisschool.net
//     GOOGLE_CLIENT_ID – optional, only for the older "Sign in with Google" button
//     TEACHER_DOMAINS  – optional, comma-separated email domains approved automatically (e.g. a school domain)
//     SESSION_SECRET   – created automatically; do not share
//
var SHEET_NAME = 'Events';
var HEAD = ['received', 'date', 'type', 'device', 'mode', 'questions', 'correct', 'hard', 'minutes', 'math', 'rw', 'tab'];
var TYPES = ['visit', 'tab', 'set'];

// ---- security limits
var MAX_UPLOAD_BODY = 21000000;   // a 15 MB file becomes about 20 MB as base64
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
    var big = /^\{"a":"build-(new|save)"/.test(body.slice(0, 20));   // contributor upload (file) or saved worksheet draft
    if (body.length > (big ? MAX_UPLOAD_BODY : MAX_BODY)) return out_({ ok: false, error: big ? 'The file is too big (max 15 MB).' : '' });
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

// Checks the admin key. Returns '' when it is right, or an error message.
function adminError_(given) {
  var key = PropertiesService.getScriptProperties().getProperty('ADMIN_KEY');
  if (!key) return 'ADMIN_KEY is not set in Project Settings → Script properties.';
  if (key.length < MIN_KEY_LENGTH) return 'For security, ADMIN_KEY must be at least ' + MIN_KEY_LENGTH + ' characters. Make it longer in Script properties.';
  var cache = CacheService.getScriptCache();
  if (Number(cache.get('badkeys') || 0) >= MAX_BAD_KEYS) return 'Too many wrong keys. Locked for 15 minutes.';
  if (!sameKey_(given, key)) { count_(cache, 'badkeys', 900); return 'Wrong admin key.'; }
  return '';
}

// admin.html reads daily totals here: ?key=ADMIN_KEY&since=YYYY-MM-DD
function doGet(e) {
  var p = (e && e.parameter) || {};
  if (p.a === 'config') return out_({ ok: true, v: 3, owners: list_('OWNER_EMAILS').length > 0, clientId: prop_('GOOGLE_CLIENT_ID') });
  if (p.a === 'join') return out_(joinInfo_(p.c));
  if (p.a === 'wslist') return out_(liveList_());
  if (p.a === 'wsget') return out_(liveGet_(p.id));
  var key = PropertiesService.getScriptProperties().getProperty('ADMIN_KEY');
  if (!key) return out_({ ok: false, error: 'ADMIN_KEY is not set in Project Settings → Script properties.' });
  if (key.length < MIN_KEY_LENGTH) return out_({ ok: false, error: 'For security, ADMIN_KEY must be at least ' + MIN_KEY_LENGTH + ' characters. Make it longer in Script properties.' });
  var cache = CacheService.getScriptCache();
  if (Number(cache.get('badkeys') || 0) >= MAX_BAD_KEYS) return out_({ ok: false, error: 'Too many wrong keys. Statistics are locked for 15 minutes.' });
  if (!sameKey_(p.key, key)) { count_(cache, 'badkeys', 900); return out_({ ok: false, error: 'Wrong admin key.' }); }
  return out_(stats_(p.since));
}

// Daily totals for admin.html. Called by POST {a:'admin', op:'stats'} (the key stays out of web addresses and logs);
// the old GET ?key= address above still works until every copy of admin.html is updated.
function stats_(sinceRaw) {
  var since = /^\d{4}-\d{2}-\d{2}$/.test(String(sinceRaw)) ? String(sinceRaw) : '0000-00-00';
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
  return { ok: true, since: since, firstDate: firstDate, days: list, uniqueVisitors: Object.keys(devices).length,
    allTimeVisitors: Object.keys(allDevices).length, totals: total, tabs: tabs, modes: modes, events: rows.length };
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
var T_HEAD = ['email', 'name', 'status', 'requested', 'lastLogin', 'grades', 'plan'];   // grades: worksheet contributor, e.g. "6,7"; plan: "pro" or empty (free)
// ---- Free and Pro plans. Students are always free. Pro: set per teacher on admin.html, or for whole email domains in PRO_DOMAINS.
var FREE_OPEN_CODES = 2;   // Free plan: open class codes at a time
function planOf_(email) {
  email = String(email || '').toLowerCase();
  if (isOwner_(email) || list_('PRO_DOMAINS').indexOf(email.split('@')[1]) >= 0) return 'pro';
  var t = teachers_(), i = findTeacher_(t, email);
  return i >= 0 && String(t.rows[i][6]).toLowerCase() === 'pro' ? 'pro' : 'free';
}
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
  if (d.a === 'admin') return adminTeachers_(d);   // admin.html: manage teacher logins with the admin key
  if (d.a === 'code') return sendCode_(d.email);
  if (d.a === 'verify') return verifyCode_(d.email, d.code);
  if (d.a === 'request') return requestAccess_(d.email, d.name);
  if (d.a === 'pro-request') return proRequest_(d);
  // everything below needs a valid session of an approved teacher
  var email = readSession_(d.s);
  if (!email) return { ok: false, error: 'session' };
  if (statusOf_(email) !== 'approved') return { ok: false, error: 'session' };
  if (count_(cache, 'tapi:' + email, 3600) > 600) return { ok: false, error: 'Too many requests. Try again later.' };
  if (d.a === 'data') return worksheetData_(email);
  if (/^build-/.test(String(d.a))) {
    if (planOf_(email) !== 'pro') return { ok: false, error: 'The Worksheet builder is part of Omega Pro.', pro: true };
    return buildApi_(email, d);
  }
  if (d.a === 'assign') {   // create a class code for a worksheet
    var ws = String(d.ws || ''), file = String(d.file || ''), cls = plain_(d.cls, 12).toUpperCase();
    if (!/^[a-z0-9][a-z0-9\-]{2,60}$/.test(ws) || !/^worksheets\/([a-z0-9\-]+\.html|w\.html\?id=w[a-z0-9]{8})$/.test(file) || !cls) return { ok: false, error: 'Choose a worksheet and type the class.' };
    var due = /^\d{4}-\d{2}-\d{2}$/.test(String(d.due)) ? String(d.due) : '';
    if (planOf_(email) !== 'pro' && assignments_().filter(function (a) { return a.email === email && a.status === 'open'; }).length >= FREE_OPEN_CODES)
      return { ok: false, error: 'The Free plan has ' + FREE_OPEN_CODES + ' open class codes at a time. Close one, or upgrade to Omega Pro for unlimited class codes.', pro: true };
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
  if (!own) {   // a teacher sees only their own students: results from their class codes, plus results typed in for a class they made a code for
    var codes = {}, classes = {};
    asg.forEach(function (a) { codes[a.code] = 1; classes[a.cls] = 1; });
    out = out.filter(function (r) { return r.asg ? codes[r.asg] === 1 : classes[r.cls] === 1; });
  }
  var plan = planOf_(email);
  if (plan !== 'pro') out = out.map(function (r) { r.items = ''; r.first = 0; r.parts = ''; return r; });   // question-by-question analysis is Pro
  var res = { ok: true, email: email, owner: own, plan: plan, rows: out, assignments: asg, grades: plan === 'pro' ? gradesOf_(email) : '' };
  if (res.owner) {
    res.teachers = teachers_().rows.map(function (r) {
      return { email: String(r[0]), name: unplain_(r[1]), status: String(r[2]),
        requested: r[3] instanceof Date ? r[3].toISOString() : '', lastLogin: r[4] instanceof Date ? r[4].toISOString() : '' };
    });
  }
  return res;
}

function siteUrl_() { return (prop_('SITE_URL') || 'https://aamermath-ai.github.io/ais-sat/').replace(/\/?$/, '/') + 'teacher.html'; }   // SITE_URL script property: the site's address after a move
// Turns a MailApp error into a plain message for the website (and writes it to Apps Script → Executions)
function mailError_(e) {
  var m = String(e && e.message || e);
  console.error('Email failed: ' + m);
  if (/permission|authori[sz]/i.test(m)) return 'The school server is not allowed to send email yet. The site owner needs to open Apps Script, choose "testEmail" next to Run, press Run and click Allow.';
  if (/quota|too many|limit|exceeded/i.test(m)) return 'The school server has sent its maximum number of emails for today. Please try again tomorrow.';
  if (/invalid email|recipient/i.test(m)) return 'This email address could not receive mail. Check it for typos.';
  return 'The email could not be sent (' + m.slice(0, 140) + ').';
}
// Run this once from the Apps Script editor: choose "testEmail" in the list next to Run, then press Run.
// Google asks for permission to send email (click Allow), and you get a test message.
function testEmail() {
  var me = Session.getEffectiveUser().getEmail();
  MailApp.sendEmail(me, 'Omega: test email', 'Email works. Teachers can now get their login codes.\n\nOmega · The last word in math');
  Logger.log('Sent a test email to ' + me + '. Emails left today: ' + MailApp.getRemainingDailyQuota());
}
function notifyOwners_(g) {
  try {
    var to = list_('OWNER_EMAILS').join(',');
    if (to) MailApp.sendEmail(to, 'Omega: teacher access request from ' + g.name,
      g.name + ' (' + g.email + ') asked for teacher access on Omega.\n\nTo approve, log in at ' + siteUrl_() + ' and open "Teachers".');
  } catch (e) { mailError_(e); }
}
function notifyApproved_(email, name) {
  try {
    MailApp.sendEmail(email, 'Omega: your teacher login is ready',
      'Hello ' + (name || '') + ',\n\nYou now have a teacher login on Omega.\n\n1. Open ' + siteUrl_() + '\n2. Press "Log in" and type this email address: ' + email +
      '\n3. We email you a 6-digit code. Type it in, and you are in.\n\nThere is no password. Share worksheets with your class by QR code or Microsoft Teams, and see your students\' results.\n\nOmega · The last word in math');
    return '';
  } catch (e) { return mailError_(e); }
}

// ---------------- email login codes (works with any email: Gmail, Outlook/Microsoft, school) ----------------
var CODE_MINUTES = 10, CODE_TRIES = 5, CODES_PER_EMAIL_15MIN = 4, CODES_PER_HOUR = 200;
// Account lockout: 5 wrong codes (across all codes sent) lock that email for 15 minutes; 15 wrong in 6 hours lock it for 6 hours.
var BAD_CODES_15MIN = 5, BAD_CODES_6H = 15;
function codeLocked_(email) {
  var c = CacheService.getScriptCache();
  if (Number(c.get('otpbad6:' + email) || 0) >= BAD_CODES_6H) return 'Too many wrong codes for this email. Login is locked for 6 hours. Ask the site owner if you need help.';
  if (Number(c.get('otpbad:' + email) || 0) >= BAD_CODES_15MIN) return 'Too many wrong codes. Login for this email is locked for 15 minutes.';
  return '';
}
function cleanEmail_(v) {
  var e = String(v || '').trim().toLowerCase();
  return /^[^\s@<>"'(),;:\\]{1,64}@[a-z0-9.\-]{1,190}\.[a-z]{2,}$/.test(e) ? e : '';
}
function sendCode_(raw) {
  var email = cleanEmail_(raw);
  if (!email) return { ok: false, error: 'Type your full email address, for example name@school.ae.' };
  var cache = CacheService.getScriptCache();
  if (count_(cache, 'codes:' + new Date().toISOString().slice(0, 13), 3600) > CODES_PER_HOUR) return { ok: false, error: 'Too many login emails right now. Try again in a few minutes.' };
  var st = statusOf_(email);
  if (st === 'none') return { ok: true, status: 'none' };
  if (st !== 'approved') return { ok: true, status: st };
  var locked = codeLocked_(email);
  if (locked) return { ok: false, error: locked };
  if (count_(cache, 'codemail:' + email, 900) > CODES_PER_EMAIL_15MIN) return { ok: false, error: 'We already sent you several codes. Check your inbox (and junk folder), or try again in 15 minutes.' };
  var code = String(100000 + parseInt(Utilities.getUuid().replace(/-/g, '').slice(0, 12), 16) % 900000);   // getUuid uses a secure random source
  cache.put('otp:' + email, JSON.stringify({ h: sign_('otp|' + email + '|' + code), n: 0 }), CODE_MINUTES * 60);
  try {
    MailApp.sendEmail(email, 'Your Omega login code: ' + code,
      'Your login code is ' + code + '\n\nType it on the Omega teacher page. It works for ' + CODE_MINUTES + ' minutes.\n\nIf you did not ask for this, you can ignore this email.\n\nOmega · The last word in math');
  } catch (e) { cache.remove('otp:' + email); return { ok: false, error: mailError_(e) }; }
  return { ok: true, status: 'sent', email: email };
}
function verifyCode_(raw, code) {
  var email = cleanEmail_(raw); code = String(code || '').replace(/\D/g, '');
  if (!email || code.length !== 6) return { ok: false, error: 'Type the 6-digit code from the email.' };
  var cache = CacheService.getScriptCache(), key = 'otp:' + email, o = null;
  var locked = codeLocked_(email);
  if (locked) { cache.remove(key); return { ok: false, error: locked }; }
  try { o = JSON.parse(cache.get(key) || 'null'); } catch (e) { o = null; }
  if (!o) return { ok: false, error: 'This code has expired. Press "Send a new code".' };
  if (!sameKey_(o.h, sign_('otp|' + email + '|' + code))) {
    o.n++;
    count_(cache, 'otpbad:' + email, 900); count_(cache, 'otpbad6:' + email, 21600);
    if (codeLocked_(email)) { cache.remove(key); return { ok: false, error: codeLocked_(email) }; }
    if (o.n >= CODE_TRIES) { cache.remove(key); return { ok: false, error: 'Too many wrong codes. Press "Send a new code".' }; }
    cache.put(key, JSON.stringify(o), CODE_MINUTES * 60);
    return { ok: false, error: 'That code is not right. Check the email and try again.' };
  }
  cache.remove(key);
  if (statusOf_(email) !== 'approved') return { ok: false, error: 'This email does not have teacher access.' };
  var t = teachers_(), i = findTeacher_(t, email), name = email;
  if (i >= 0) { name = unplain_(t.rows[i][1]) || email; t.sh.getRange(i + 2, 5).setValue(new Date()); }
  else if (isOwner_(email)) { t.sh.appendRow([email, email.split('@')[0], 'approved', new Date(), new Date()]); name = email.split('@')[0]; }
  return { ok: true, status: 'approved', email: email, name: name, owner: isOwner_(email), plan: planOf_(email), grades: gradesOf_(email), session: makeSession_(email) };
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
function newCode_() {   // secure random (getUuid), not Math.random, so class codes and worksheet IDs cannot be predicted
  var c = '', hex = Utilities.getUuid().replace(/-/g, '');
  for (var i = 0; i < 6; i++) c += CODE_ABC.charAt(parseInt(hex.slice(i * 4, i * 4 + 4), 16) % CODE_ABC.length);
  return c;
}
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


// ---------------- admin.html: teacher logins (needs ADMIN_KEY) ----------------
function adminTeachers_(d) {
  var err = adminError_(d.key);
  if (err) return { ok: false, error: err };
  var op = String(d.op || 'list'), mailNote = '';
  if (op === 'stats') return stats_(d.since);
  if (/^build/.test(op)) return adminBuilds_(op, d);
  if (op === 'plan') {
    var pe = cleanEmail_(d.email), tp = teachers_(), pi = findTeacher_(tp, pe);
    if (pi < 0) return { ok: false, error: 'Teacher not found.' };
    tp.sh.getRange(pi + 2, 7).setValue(d.plan === 'pro' ? 'pro' : '');
    op = 'list';
  }
  if (op === 'prorequests') return { ok: true, requests: proRequests_() };
  if (op === 'grades') {
    var ge = cleanEmail_(d.email), gl = cleanGrades_(d.grades);
    var tg = teachers_(), gi = findTeacher_(tg, ge);
    if (gi < 0) return { ok: false, error: 'Teacher not found.' };
    tg.sh.getRange(gi + 2, 6).setValue("'" + gl);
    op = 'list';
  }
  if (op === 'add' || op === 'set') {
    var email = cleanEmail_(d.email);
    if (!email) return { ok: false, error: 'Type a valid email address.' };
    var status = op === 'add' ? 'approved' : String(d.status || '');
    if (['approved', 'removed', 'pending'].indexOf(status) < 0) return { ok: false, error: 'Unknown status.' };
    var name = plain_(d.name, 60), notify = false;
    var lock = LockService.getScriptLock(); lock.waitLock(10000);
    try {
      var t = teachers_(), i = findTeacher_(t, email);
      if (i < 0) {
        if (op !== 'add') return { ok: false, error: 'Teacher not found.' };
        t.sh.appendRow([email, name || email, 'approved', new Date(), '']); notify = true;
      } else {
        if (status === 'approved' && String(t.rows[i][2]) !== 'approved') notify = true;
        t.sh.getRange(i + 2, 2, 1, 2).setValues([[name || unplain_(t.rows[i][1]) || email, status]]);
      }
    } finally { try { lock.releaseLock(); } catch (x) {} }
    if (notify) mailNote = notifyApproved_(email, name) || 'sent';
  }
  var list = teachers_().rows.map(function (r) {
    return { email: String(r[0]), name: unplain_(r[1]), status: String(r[2]),
      requested: r[3] instanceof Date ? r[3].toISOString() : '', lastLogin: r[4] instanceof Date ? r[4].toISOString() : '', grades: unplain_(r[5]), plan: planOf_(String(r[0])) };
  });
  return { ok: true, teachers: list, owners: list_('OWNER_EMAILS'), mail: mailNote };
}


// ======================================================================================================
// Worksheet builder: contributors upload a lesson file → a Claude session builds a draft → contributor edits →
// owner approves on admin.html → the worksheet is live at worksheets/w.html?id=…
// Files: Drive folder "Omega uploads" (uploads) and "Omega drafts" (drafts written by Claude, named <id>.json).
// ======================================================================================================
var B_SHEET = 'Builds';
var B_HEAD = ['id', 'created', 'email', 'name', 'grade', 'term', 'module', 'topic', 'code', 'title', 'notes', 'fileId', 'fileName', 'status', 'json', 'feedback', 'updated'];
var GRADES_OK = ['6', '7', '8', '9', '10', '11', '12'];
var UPLOAD_TYPES = { 'application/pdf': 1, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 1, 'application/msword': 1,
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 1, 'application/vnd.ms-powerpoint': 1, 'image/png': 1, 'image/jpeg': 1 };
var MAX_WS_JSON = 250000;
// The browser says what type a file is; check the file's first bytes so a renamed file of another type is refused.
function magicOk_(bytes, mime) {
  var h = []; for (var i = 0; i < 8 && i < bytes.length; i++) h.push((bytes[i] + 256) % 256);
  var starts = function (sig) { for (var k = 0; k < sig.length; k++) if (h[k] !== sig[k]) return false; return true; };
  if (mime === 'application/pdf') return starts([0x25, 0x50, 0x44, 0x46]);                         // %PDF
  if (mime === 'image/png') return starts([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]);
  if (mime === 'image/jpeg') return starts([0xFF, 0xD8, 0xFF]);
  if (/openxmlformats/.test(mime)) return starts([0x50, 0x4B, 0x03, 0x04]);                          // .docx / .pptx (zip)
  if (mime === 'application/msword' || mime === 'application/vnd.ms-powerpoint') return starts([0xD0, 0xCF, 0x11, 0xE0]);   // old .doc / .ppt
  return false;
}

function cleanGrades_(v) { return String(v || '').split(',').map(function (x) { return x.trim(); }).filter(function (x) { return GRADES_OK.indexOf(x) >= 0; }).join(','); }
function gradesOf_(email) {
  if (isOwner_(email)) return GRADES_OK.join(',');
  var t = teachers_(), i = findTeacher_(t, email);
  return i < 0 ? '' : cleanGrades_(unplain_(t.rows[i][5]));
}
function canGrade_(email, grade) { return gradesOf_(email).split(',').indexOf(String(grade)) >= 0; }
function folder_(name) {
  var it = DriveApp.getFoldersByName(name);
  return it.hasNext() ? it.next() : DriveApp.createFolder(name);
}
function builds_() {
  var sh = tab_(B_SHEET, B_HEAD), last = sh.getLastRow();
  var rows = last > 1 ? sh.getRange(2, 1, last - 1, B_HEAD.length).getValues() : [];
  return { sh: sh, rows: rows };
}
function bRow_(r, withJson) {
  var o = { id: String(r[0]), created: r[1] instanceof Date ? r[1].toISOString() : '', email: String(r[2]), name: unplain_(r[3]), grade: unplain_(r[4]),
    term: unplain_(r[5]), module: unplain_(r[6]), topic: unplain_(r[7]), code: unplain_(r[8]), title: unplain_(r[9]), notes: unplain_(r[10]),
    fileName: unplain_(r[12]), status: String(r[13]), feedback: unplain_(r[15]), updated: r[16] instanceof Date ? r[16].toISOString() : '' };
  if (withJson) o.json = String(r[14] || '');
  return o;
}
function findBuild_(b, id) { for (var i = 0; i < b.rows.length; i++) if (String(b.rows[i][0]) === id) return i; return -1; }

// Checks the shape of a worksheet (the page also cleans all text before showing it)
function validWs_(text) {
  if (!text || text.length > MAX_WS_JSON) return null;
  var w; try { w = JSON.parse(text); } catch (e) { return null; }
  if (!w || typeof w !== 'object' || !Array.isArray(w.questions) || !Array.isArray(w.parts)) return null;
  if (w.questions.length < 1 || w.questions.length > 40 || w.parts.length < 1 || w.parts.length > 8) return null;
  for (var i = 0; i < w.questions.length; i++) {
    var q = w.questions[i];
    if (!q || typeof q.text !== 'string' || ['pick', 'num'].indexOf(q.kind) < 0 || typeof q.part !== 'string') return null;
    if (q.kind === 'pick' && (!Array.isArray(q.options) || q.options.length < 2 || q.options.indexOf(q.answer) < 0)) return null;
    if (q.kind === 'num' && !isFinite(Number(q.answer))) return null;
  }
  return w;
}
// Drafts written by a Claude session into "Omega drafts" become ready for the contributor
function importDrafts_() {
  var it = DriveApp.getFoldersByName('Omega drafts'); if (!it.hasNext()) return;
  var lock = LockService.getScriptLock(); if (!lock.tryLock(5000)) return;
  try {
    var b = null;
    while (it.hasNext()) {
      var files = it.next().getFiles();
      while (files.hasNext()) {
        var f = files.next(), m = /^(w[a-z0-9]{8})\.json$/.exec(f.getName());
        if (!m) continue;
        b = b || builds_();
        var i = findBuild_(b, m[1]); if (i < 0) continue;
        var text = f.getBlob().getDataAsString('UTF-8');
        if (!validWs_(text)) { f.setName('invalid-' + f.getName()); continue; }
        b.sh.getRange(i + 2, 14, 1, 4).setValues([['draft', text, b.rows[i][15], new Date()]]);
        f.setName('imported-' + f.getName());
        try { MailApp.sendEmail(String(b.rows[i][2]), 'Omega: your worksheet draft is ready – ' + unplain_(b.rows[i][9]),
          'Your worksheet "' + unplain_(b.rows[i][8]) + ' ' + unplain_(b.rows[i][9]) + '" is ready to check.\n\nOpen ' + siteUrl_().replace('teacher.html', 'build.html') +
          ', preview it, fix anything you need, and press "Send for approval".\n\nOmega · The last word in math'); } catch (e) { mailError_(e); }
      }
    }
  } finally { try { lock.releaseLock(); } catch (x) {} }
}
function buildApi_(email, d) {
  var cache = CacheService.getScriptCache();
  if (d.a === 'build-new') {
    if (count_(cache, 'up:' + email + ':' + new Date().toISOString().slice(0, 10), 86400) > 30) return { ok: false, error: 'Upload limit reached for today.' };
    var grade = String(d.grade || '');
    if (!canGrade_(email, grade)) return { ok: false, error: 'You do not have access to Grade ' + grade + '.' };
    var mime = String(d.mime || ''), title = plain_(d.title, 90), code = plain_(d.code, 12);
    if (!UPLOAD_TYPES[mime]) return { ok: false, error: 'Upload a PDF, Word or PowerPoint file.' };
    if (!title || !code) return { ok: false, error: 'Type the lesson number and title.' };
    var bytes; try { bytes = Utilities.base64Decode(String(d.data || '')); } catch (e) { return { ok: false, error: 'The file could not be read.' }; }
    if (!bytes.length || bytes.length > 15 * 1048576) return { ok: false, error: 'The file is empty or bigger than 15 MB.' };
    if (!magicOk_(bytes, mime)) return { ok: false, error: 'This file is not a real PDF, Word, PowerPoint or image file.' };
    var id = 'w' + newCode_().toLowerCase() + newCode_().toLowerCase().slice(0, 2);
    var name = plain_(d.fileName, 80).replace(/^'/, '') || 'lesson';
    var file = folder_('Omega uploads').createFile(Utilities.newBlob(bytes, mime, id + ' · Grade ' + grade + ' · ' + code + ' ' + title + ' · ' + name));
    var t = teachers_(), ti = findTeacher_(t, email);
    tab_(B_SHEET, B_HEAD).appendRow([id, new Date(), email, ti >= 0 ? unplain_(t.rows[ti][1]) : email, "'" + grade, plain_(d.term, 30), plain_(d.module, 40), plain_(d.topic, 60),
      "'" + code.replace(/^'/, ''), title, plain_(d.notes, 600), file.getId(), name, 'queued', '', '', new Date()]);
    try { var to = list_('OWNER_EMAILS').join(','); if (to) MailApp.sendEmail(to, 'Omega: new worksheet upload – Grade ' + grade + ' ' + code + ' ' + title,
      (ti >= 0 ? unplain_(t.rows[ti][1]) : email) + ' uploaded "' + name + '" for Grade ' + grade + ', ' + code + ' ' + title + '.\n\nIt is in the queue (Drive folder "Omega uploads", request ' + id + '). Ask Claude to build the queued worksheets.'); } catch (e) { mailError_(e); }
    return buildList_(email, id);
  }
  if (d.a === 'build-list') { importDrafts_(); return buildList_(email); }
  var b = builds_(), i = findBuild_(b, String(d.id || ''));
  if (i < 0) return { ok: false, error: 'Worksheet request not found.' };
  var r = b.rows[i];
  if (!canGrade_(email, unplain_(r[4]))) return { ok: false, error: 'You do not have access to this grade.' };
  var st = String(r[13]);
  if (d.a === 'build-get') return { ok: true, build: bRow_(r, true) };
  // changing a request: only the teacher who uploaded it (or an owner), not every contributor for that grade
  if (String(r[2]).toLowerCase() !== email && !isOwner_(email)) return { ok: false, error: 'Only the teacher who uploaded this worksheet can change it.' };
  if (d.a === 'build-save') {
    if (['draft', 'changes'].indexOf(st) < 0) return { ok: false, error: 'This worksheet cannot be edited now (' + st + ').' };
    var text = String(d.json || '');
    if (!validWs_(text)) return { ok: false, error: 'Something in the worksheet is not complete: every question needs text, and the correct answer must be one of the options.' };
    b.sh.getRange(i + 2, 15).setValue(text); b.sh.getRange(i + 2, 17).setValue(new Date());
    return { ok: true, saved: true };
  }
  if (d.a === 'build-submit') {
    if (['draft', 'changes'].indexOf(st) < 0) return { ok: false, error: 'This worksheet cannot be sent now (' + st + ').' };
    b.sh.getRange(i + 2, 14).setValue('submitted'); b.sh.getRange(i + 2, 17).setValue(new Date());
    try { var to2 = list_('OWNER_EMAILS').join(','); if (to2) MailApp.sendEmail(to2, 'Omega: worksheet waiting for approval – Grade ' + unplain_(r[4]) + ' ' + unplain_(r[8]) + ' ' + unplain_(r[9]),
      unplain_(r[3]) + ' sent a worksheet for approval. Open admin.html → Worksheet requests to preview and approve it.'); } catch (e) { mailError_(e); }
    return buildList_(email);
  }
  if (d.a === 'build-cancel') {
    if (['queued', 'draft', 'changes'].indexOf(st) < 0) return { ok: false, error: 'This worksheet cannot be cancelled now.' };
    b.sh.getRange(i + 2, 14).setValue('cancelled'); b.sh.getRange(i + 2, 17).setValue(new Date());
    return buildList_(email);
  }
  return { ok: false };
}
function buildList_(email, created) {
  var g = gradesOf_(email).split(','), b = builds_();
  var list = b.rows.filter(function (r) { return g.indexOf(unplain_(r[4])) >= 0 && String(r[13]) !== 'cancelled'; }).map(function (r) { return bRow_(r, false); });
  return { ok: true, grades: g.join(','), builds: list, created: created || '' };
}
function adminBuilds_(op, d) {
  if (op === 'builds') { importDrafts_(); return { ok: true, builds: builds_().rows.map(function (r) { return bRow_(r, false); }) }; }
  var b = builds_(), i = findBuild_(b, String(d.id || ''));
  if (i < 0) return { ok: false, error: 'Worksheet request not found.' };
  var r = b.rows[i];
  if (op === 'build-get') return { ok: true, build: bRow_(r, true) };
  if (op === 'build-approve' || op === 'build-changes' || op === 'build-unpublish') {
    var to = op === 'build-approve' ? 'live' : op === 'build-changes' ? 'changes' : 'draft';
    if (to === 'live' && !validWs_(String(r[14] || ''))) return { ok: false, error: 'This request has no complete worksheet yet.' };
    b.sh.getRange(i + 2, 14, 1, 4).setValues([[to, r[14], op === 'build-changes' ? plain_(d.feedback, 600) : r[15], new Date()]]);
    CacheService.getScriptCache().remove('wslist');
    try {
      if (op === 'build-approve') MailApp.sendEmail(String(r[2]), 'Omega: your worksheet is live – ' + unplain_(r[8]) + ' ' + unplain_(r[9]),
        'Great work! "' + unplain_(r[8]) + ' ' + unplain_(r[9]) + '" is now live on the Worksheets page for Grade ' + unplain_(r[4]) + '.\n\nOmega · The last word in math');
      if (op === 'build-changes') MailApp.sendEmail(String(r[2]), 'Omega: changes requested – ' + unplain_(r[8]) + ' ' + unplain_(r[9]),
        'Please update your worksheet "' + unplain_(r[8]) + ' ' + unplain_(r[9]) + '":\n\n' + plain_(d.feedback, 600) + '\n\nOpen ' + siteUrl_().replace('teacher.html', 'build.html') + ' to edit it.\n\nOmega · The last word in math');
    } catch (e) { mailError_(e); }
    return { ok: true, builds: builds_().rows.map(function (x) { return bRow_(x, false); }) };
  }
  return { ok: false };
}
// public: live worksheets for the Worksheets page and the teachers' Assign list
function liveList_() {
  var cache = CacheService.getScriptCache(), c = cache.get('wslist');
  if (c) return JSON.parse(c);
  var list = builds_().rows.filter(function (r) { return String(r[13]) === 'live'; }).map(function (r) {
    var w = validWs_(String(r[14] || '')) || {};
    return { id: String(r[0]), grade: unplain_(r[4]), term: unplain_(r[5]), module: unplain_(r[6]), topic: unplain_(r[7]), code: unplain_(r[8]), title: unplain_(r[9]),
      n: (w.questions || []).length };
  });
  var res = { ok: true, worksheets: list };
  try { cache.put('wslist', JSON.stringify(res), 300); } catch (e) {}
  return res;
}
function liveGet_(id) {
  id = String(id || ''); if (!/^w[a-z0-9]{8}$/.test(id)) return { ok: false };
  var b = builds_(), i = findBuild_(b, id);
  if (i < 0 || String(b.rows[i][13]) !== 'live') return { ok: false, error: 'notfound' };
  return { ok: true, build: bRow_(b.rows[i], true) };
}


// ---------------- Omega Pro requests (plans section on teacher.html) ----------------
var P_SHEET = 'ProRequests';
var P_HEAD = ['received', 'name', 'email', 'school', 'teachers', 'message'];
function proRequest_(d) {
  var email = cleanEmail_(d.email), name = plain_(d.name, 60), school = plain_(d.school, 90);
  if (!email || name.length < 2 || school.length < 2) return { ok: false, error: 'Type your name, school and email.' };
  var cache = CacheService.getScriptCache();
  if (count_(cache, 'proreq:' + new Date().toISOString().slice(0, 13), 3600) > 30) return { ok: false, error: 'Too many requests right now. Try again later.' };
  if (count_(cache, 'proreq:' + email, 86400) > 3) return { ok: true };
  tab_(P_SHEET, P_HEAD).appendRow([new Date(), name, email, school, num_(d.teachers, 5000), plain_(d.message, 600)]);
  try {
    var to = list_('OWNER_EMAILS').join(',');
    if (to) MailApp.sendEmail(to, 'Omega Pro request – ' + school, name + ' (' + email + ') from ' + school + ' asked about Omega Pro' +
      (num_(d.teachers, 5000) ? ' for about ' + num_(d.teachers, 5000) + ' teachers' : '') + '.\n\n' + plain_(d.message, 600) + '\n\nSee admin.html → Pro requests.');
  } catch (e) { mailError_(e); }
  return { ok: true };
}
function proRequests_() {
  var sh = tab_(P_SHEET, P_HEAD), last = sh.getLastRow();
  return (last > 1 ? sh.getRange(2, 1, last - 1, P_HEAD.length).getValues() : []).reverse().slice(0, 100).map(function (r) {
    return { received: r[0] instanceof Date ? r[0].toISOString() : '', name: unplain_(r[1]), email: String(r[2]), school: unplain_(r[3]), teachers: +r[4] || 0, message: unplain_(r[5]) };
  });
}
