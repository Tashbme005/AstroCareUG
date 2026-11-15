# Space Apps submission pack

## Deadline

Submission opens Saturday 14 Nov 2026 at 9:00 and closes Sunday 15 Nov at 11:59 PM,
local time of your team owner's event. Submit from the **Project tab** on your team
page. Only submitted projects get a participant certificate and reach judging.

I could only read the 2025 submission guide and third-party summaries. The 2026
Project Submission Guide was released on 13 Nov. Read it once and check its field
list against this pack.

## The one gap to close before you submit

The challenge asks teams to make use of NASA's Human Research Program (HRP) and the
Open Science Data Repository (OSDR). The app currently uses **no NASA data**: the
ranges in `rules.py` are general screening values. Judges look for how NASA
resources were integrated, so close this gap honestly:

1. Open 2 or 3 HRP risk pages and 1 or 2 OSDR datasets that relate to your eight
   readings (cardiovascular, sleep, immune, bone and muscle, behavioural health).
2. Write down what you actually learned from each and which rule or text it
   supports. Even "this dataset measures X, so we plan to calibrate Y with it" is
   a fair statement of future work.
3. Add each source with its exact title and URL to **References** (README and the
   project page).
4. Only write "uses NASA data" if the app really reads it. If not, say
   "designed around HRP risk areas; OSDR calibration is next". The submission form
   has a box confirming that all outside resources are listed, so accuracy matters.

## Demo (30-second video, English subtitles)

The 2025 guide required a video pitch of at most 30 seconds, or slides, hosted on a
public link (YouTube, Drive, GitHub). Subtitles must be in English. Suggested script:

| Time | Show | Say |
|---|---|---|
| 0:00-0:04 | Title, team name | "We are <team>. This is AstroCare." |
| 0:04-0:09 | Mars setting, delay note | "On Mars, a message home takes up to 22 minutes. Astronauts must make the first call." |
| 0:09-0:19 | Click Infection demo: banner, body map, one card | "AstroCare turns daily readings into plain-language guidance: what it means and what to do." |
| 0:19-0:25 | Trends to watch card | "It also catches slow trends before any single reading is out of range." |
| 0:25-0:30 | Emergency guide, About page | "Open source, tested, and honest about its limits. Next: calibrating with NASA HRP and OSDR data." |

Record at 1080p, keep text readable, and avoid copyrighted music or images.

## Project page text (edit to match what you really built)

**Summary (short):**
AstroCare is a Django web app that gives astronauts plain-language health guidance
when ground support is delayed. A daily check-in becomes a clear status, practical
next steps, a body map, and early warnings for slow trends and risky combinations.

**What it does:**
Eight daily readings (heart rate, blood pressure, oxygen, temperature, blood sugar,
sleep, mood, exercise) are screened against fixed ranges. Each gets Normal, Watch or
Act now, an explanation a non-doctor can follow, and steps to take. Combination rules
and a 3-day versus first-3-day trend rule catch problems that single readings miss.
Sleep and exercise only escalate after repeated bad days, to avoid alarm fatigue. The
setting (ISS, deep space, Moon, Mars) changes the guidance note. Data can be exported
as CSV for the flight surgeon.

**How we built it:**
Python and Django 6.1, SQLite, plain HTML/CSS/JavaScript with inline SVG for the body
map and sparklines. All guidance logic lives in one file (`rules.py`) with automated
tests, so clinicians can review and change it without touching the web code.

**Challenges:**
Keeping alerts useful: too many "Act now" alerts would be ignored, so lifestyle
signals need persistence. Keeping the language plain without sounding like a
diagnosis.

**What is next:**
Calibrate ranges and trend rules with HRP evidence and OSDR datasets, add personal
baselines, connect wearables, work offline, and have clinicians review the rules.

## Checklist

- [ ] Every team member is registered and on the Members tab (max 6).
- [ ] Demo link is public (open it in a private window to check) and has English subtitles.
- [ ] Code repository link is public and contains no secrets or `db.sqlite3`.
- [ ] README References and the form's References field list every library, dataset, image, and text used.
- [ ] If the form asks about AI tools, list them (for example, Claude for code review and docs).
- [ ] No photos or voices of people under 18 in the demo.
- [ ] Both confirmation boxes are ticked, then press **Submit** (saving a draft is not enough).
- [ ] Submit well before 11:59 PM, in case of slow uploads.
