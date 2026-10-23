---
name: school-calendar
description: Update the Fox Society (狐狸学社) passcode-locked school calendar at foxsociety.com.cn/school-calendar (static/school-calendar.html) — student schools' 2026–27 校历 merged with SAT/ACT/AP/A-Level/IGCSE/IBDP dates. Use whenever the user drops a school calendar, exam schedule, holiday notice, 考试通知, 校历 PDF/screenshot, or a date correction and asks to add or update it "in the calendar" / "school calendar", or adds a new school (e.g. "add 位育's calendar", "here's SHSID's midterm schedule").
---

# School calendar updates

The page `static/school-calendar.html` is a self-contained page whose whole app
(HTML + JS, including every date) is AES-GCM encrypted under the consultant
passcode. There is **no plaintext source in the repo**: every change is
decrypt → edit → re-encrypt.

## 0. Branch and passcode

- Work on the session's designated branch. If its previous PR is already merged
  into `main`, restart the branch from `origin/main` first
  (`git merge-base --is-ancestor <old head> origin/main` tells you).
- Passcode: use `$FS_CAL_PASS` if set; otherwise ask the user with
  AskUserQuestion. Never write the passcode into the repo, a commit message, or
  any file outside the scratchpad.

## 1. Read the source material

- PDF: `pdftotext -layout` **and** render with `pdftoppm -r 110 -png` and look
  at the image — tables of 周序 / 活动内容 lose their row grouping in text.
- Screenshot: read it directly. Check weekday labels against real dates.
- Note the document's exact title; it goes in the footer and in notes.

## 2. Decrypt

```bash
SK=.claude/skills/school-calendar/scripts
W=<scratchpad>/cal            # fresh dir each time
python3 -I $SK/calendar_crypt.py decrypt static/school-calendar.html $W
```

## 3. Edit `$W/app.js` (and `$W/app.html`)

Data structures in `app.js` (grep for them; keep their style):

| Structure | What it is |
|---|---|
| `SCHOOLS` | `key:{short,name,c:"var(--key)"}`; exams have `g:"test"` |
| `TYPES` | `off` 不上课 · `exam` 考试 · `result` 出分 · `reg` 报名截止 · `term` 学期节点 · `event` 活动/家长会 · `adj` 调课/调休 |
| `RAW` | `["school","YYYY-MM-DD", end-or-null, type, 中文, English, note?]`, grouped by school in date order |
| `CMP` | 主要假期对照 rows; each row is `{schoolKey:[main, small?]}`. `null` = "第二学期详细校历未提供", missing = "—" |
| `TT` | 标化/国际课程考试 table rows (exam keys only) |
| `ORDER` | sort order per school key |

Current schools: `uwc` UWC 常熟, `sas` SAS, `ykps` 包玉刚, `ph` 平和, `shs`
上海中学国际部, `wy` 位育中学国际部; exams `sat act ap alevel igcse ib`.

Conventions (follow them — consultants rely on them):
- Chinese title first, short English second. Keep the school's own wording
  (Y9/G11, 牛剑, ED/EA) rather than translating it away.
- Items the source gives only by **week** (周次): span that week's school days
  (Mon–Fri, skipping holidays) and put `校历仅写周次（第 N 周）` in the note.
- Anything uncertain, inferred, or conflicting with another source: keep both,
  and say so in the note (e.g. `与…不一致，需向学校确认`). Never silently pick one.
- Holidays given in two pieces across a week boundary (10/1–4 + 10/5–7) become
  one `off` range with a note.
- School-internal application deadlines (“…工作截止”) are `event`, noted
  `学校升学指导内部截止，非大学官方截止日`.
- A narrower notice (e.g. one grade's exam timetable) **adds** entries; keep
  the whole-school calendar entry unless the notice clearly replaces it. Put
  times, who has class vs. exams, and bus changes in the note, and cite the
  notice title (`来源：《…》`).
- Update the `CMP` cell for that school when holidays, exams or term dates change.
- Add one `<li>` to the footer `数据说明` in `app.html` naming the source
  document and any assumptions. If a school is added, update the intro
  `<p class="sub">` list and its count (五校 → 六校 …).
- Students only: skip staff-only dates (教师培训, 入职).

### Adding a new school

1. `SCHOOLS`: new key after the last school (before `sat`), plus `ORDER` entry.
2. `CMP`: add the key to **every** row (value or `null`).
3. CSS colour — outside the encrypted blob, in `static/school-calendar.html`
   itself: add `--key:<light>` to `:root` and `--key:<dark>` to **both** dark
   blocks (`@media (prefers-color-scheme:dark)` and `:root[data-theme="dark"]`).
   Pick a hue distinct from the existing school/exam colours.

Check syntax:
```bash
node -e "new Function(require('fs').readFileSync('$W/app.js','utf8'))"
```

## 4. Re-encrypt and verify

```bash
python3 -I $SK/calendar_crypt.py encrypt static/school-calendar.html $W
(cd static && python3 -m http.server 8765 >/dev/null 2>&1 &); sleep 1
NODE_PATH=$(npm root -g) node $SK/smoke_test.js \
  http://localhost:8765/school-calendar.html 2026-11 <scratchpad>/shot.png <schoolKey>
```

Read the screenshot: the new entries should appear on the right days with the
school's colour, and `errors=[]`. Check the list view or detail notes too if
you changed notes. Stop the server afterwards by PID (don't `pkill -f`
a pattern that matches your own shell). `git diff --stat` should show only
`static/school-calendar.html` (plus nothing else unintended).

## 5. Commit, push, report

- Commit message like `Add SHSID G11-12 midterm exam schedule to school calendar`.
- Push to the designated branch. Open a PR only if the user asks.
- Report to the user: what was added per date, every judgment call (week-only
  items, conflicts kept, internal vs. official deadlines), and that it goes
  live only after merge to `main` + deploy.
