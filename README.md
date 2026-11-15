# AstroCare

Plain-language health check-ins for astronauts on long missions, where the doctor
may be minutes away by radio. Built for the NASA Space Apps Challenge 2026,
"Create Health Monitoring Software for Astronauts on Space Missions".

An astronaut enters a daily check-in. AstroCare explains each reading in plain
words, marks it Normal, Watch or Act now, says what to do next, and warns about
slow trends and risky combinations of readings.

> Prototype. Not a medical device. See the About page in the app for its limits.

## Run it (about 2 minutes)

Requires Python 3.12 or newer (Django 6.1 needs it).

```bash
cd astrocare

# create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # macOS / Linux
venv\Scripts\activate             # Windows (cmd or PowerShell)

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo        # creates user "crew" with 14 days of sample data
python manage.py runserver
```

Open http://127.0.0.1:8000 and log in as `crew` with password `astro-demo-2026`.
That account exists for demos only. Change the password, or skip `seed_demo`, for
anything public (`python manage.py createsuperuser` makes a real account).

## Try it

- Use the five **demo crew data** buttons: Healthy, Infection, Bone and heart,
  Isolation, Emergency.
- Switch the setting (space station, deep-space transit, Moon, Mars). The
  guidance note changes.
- Tap a body area to read about it. It works with the keyboard too.
- Open **Emergency guide** for the onboard first-response steps.
- **Download CSV** exports every check-in for the flight surgeon.
- **How it works** shows the exact screening ranges and the limits of the project.

## Features

- Plain-language explanations and next steps for 8 readings: heart rate, blood
  pressure, blood oxygen, temperature, blood sugar, sleep, mood, exercise.
- Combination alerts (fever with fast heart rate, low oxygen with unusual heart
  rate, poor sleep with low mood).
- Trend alerts: compares the latest 3 check-ins with the first 3, after 6 check-ins.
- Sleep and exercise only reach "Act now" after 3 bad days in a row, which avoids
  false alarms.
- Mission-setting notes for ISS, deep space, Moon and Mars.
- Input validation, login, logout, CSV export, automated tests.

## Tests

```bash
python manage.py test
```

## Configuration

Nothing is needed for local use. For deployment set:

| Variable | Meaning |
|---|---|
| `DJANGO_DEBUG` | `0` to turn debug off (then `DJANGO_SECRET_KEY` is required) |
| `DJANGO_SECRET_KEY` | long random string |
| `DJANGO_ALLOWED_HOSTS` | comma-separated hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | comma-separated origins, e.g. `https://your-app.example.com` |

## Project layout

```
astrocare/
  astroconfig/        Django settings and root URLs
  astroapp/
    rules.py          screening ranges, plain-language text, trends (the "brain")
    models.py         CheckIn
    forms.py          check-in form with plausibility limits
    views.py          dashboard, export, demo loader, About page
    templates/        dashboard.html, index.html (login), about.html
    management/commands/
      demo.py         load a sample scenario for a user
      seed_demo.py    create the demo user and load data
    tests.py
```

## Limits

- The ranges are general screening values chosen for demonstration. They are not
  validated against NASA flight medical standards.
- The rules are fixed. They do not learn and do not know a person's baseline.
- Sample crew data is synthetic.

## References

Add every external resource used (libraries, datasets, images, text) here and in the
Space Apps project page. See `SUBMISSION.md`.

- Django 6.1 (BSD licence), https://www.djangoproject.com
- Python standard library
