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
var SHEET_NAME = 'Events';
var HEAD = ['received', 'date', 'type', 'device', 'mode', 'questions', 'correct', 'hard', 'minutes', 'math', 'rw', 'tab'];
var TYPES = ['visit', 'tab', 'set'];

// ---- security limits
var MAX_BODY = 1500;            // bytes per event; real events are ~200
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
