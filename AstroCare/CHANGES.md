# What changed

## Bugs fixed

- **`requirements.txt` could not be installed.** It contained setup instructions as
  text, so `pip install -r requirements.txt` failed on line 6. It now lists only the
  four packages.
- **Blood pressure direction was wrong.** A low bottom number (for example 120/45)
  was reported as "high". `bp_check` now reports high and low correctly.
- **No input validation.** A heart rate of 900 or an oxygen level of 500% was saved.
  The form now rejects impossible values and requires top number > bottom number.
- **Demo endpoint crashed** with a server error on an unknown scenario. It now
  returns a clean 400.
- **Hard-coded secret key, `DEBUG=True`, empty `ALLOWED_HOSTS`.** Settings now read
  environment variables and refuse to start in production without a secret key.
  The invalid `MAILERS` setting was removed.
- **Body map** drew the immune-system dot outside the body. It is now on the torso.
- **Packaging.** The zip contained a 70 MB Windows virtual environment and a
  database file. Both are excluded, with a `.gitignore`.
- The two test files (`test.py`, `tests.py`) are merged into `tests.py`.

## New

- Trend alerts ("Trends to watch") and a banner that rises to Watch on trends alone.
- Sleep and exercise need 3 bad days in a row to reach "Act now" (one bad day is Watch).
- Softer "Act today" headline when only lifestyle signals escalated.
- CSV export, logout button, styled login page, public **How it works** page whose
  ranges table is generated from `rules.py`.
- `seed_demo` command: creates a demo user and loads sample data in one step.
- Confirmation before demo data replaces saved check-ins.
- README, SUBMISSION.md (draft page text, 30-second demo script, checklist).
- Tests grew from 4 to 29.

## Behaviour changes you may want to review

1. The sleep/exercise persistence rule changes what the demo scenarios show.
   To revert, set `LIFESTYLE = set()` in `rules.py`.
2. Trend thresholds (`DRIFTS` in `rules.py`) are my starting values, not clinical
   ones. Tune or cite them.
3. Low mood (1 out of 5) still triggers "Act now" immediately, by design.

## Not done

- No NASA HRP or OSDR data is used yet (see SUBMISSION.md). I could not reach NASA
  data hosts from my sandbox, so I did not add an integration I could not test.
- Clinical ranges are unvalidated, and not reviewed by a clinician.
- Not deployed. Local run only.
