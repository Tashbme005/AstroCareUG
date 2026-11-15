import csv

from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import CheckInForm
from .management.commands.demo import SCENARIOS
from .models import CheckIn
from .rules import DRIFT_MIN_DAYS, METRICS, assess, describe_limits

ENVIRONMENTS = {
    "iss": (
        "Space station (low Earth orbit)",
        "Help from the ground is quick. Radiation is lower, but bone loss and fluid shifts still build up.",
    ),
    "transit": (
        "Deep-space transit",
        "More radiation and slower ground contact. You may need to act first and update the flight surgeon.",
    ),
    "moon": (
        "Moon base",
        "Lunar gravity is about one sixth of Earth's, so keep exercising. Dust can irritate lungs and eyes.",
    ),
    "mars": (
        "Mars mission",
        "One-way messages take about 3 to 22 minutes. Plan to make the first decision yourself.",
    ),
}

TREND_FIELDS = {
    "hr": "hr",
    "bp": "sys",
    "spo2": "spo2",
    "temp": "temp",
    "glu": "glu",
    "sleep": "sleep",
    "mood": "mood",
    "ex": "ex",
}


@login_required
def dashboard(request):
    check_ins = CheckIn.objects.filter(astronaut=request.user)
    last = check_ins.last()

    if request.method == "POST":
        form = CheckInForm(request.POST)
        if form.is_valid():
            check_in = form.save(commit=False)
            check_in.astronaut = request.user
            check_in.day = last.day + 1 if last else 1
            check_in.save()
            return redirect("dashboard")
    else:
        form = CheckInForm(instance=last) if last else CheckInForm()

    env = request.session.get("env", "iss")
    if env not in ENVIRONMENTS:
        env = "iss"
    context = {
        "form": form,
        "env": env,
        "envs": ENVIRONMENTS,
        "env_note": ENVIRONMENTS[env][1],
        "last": last,
        "drift_min_days": DRIFT_MIN_DAYS,
    }
    if last:
        history = list(check_ins.order_by("-day", "-created")[:14])[::-1]
        trends = {
            key: [getattr(item, field) for item in history]
            for key, field in TREND_FIELDS.items()
        }
        context.update(
            a=assess(last, history),
            trends=trends,
            days=len(history),
        )

    return render(request, "dashboard.html", context)


@login_required
@require_POST
def set_env(request):
    environment = request.POST.get("env")
    if environment in ENVIRONMENTS:
        request.session["env"] = environment
    return redirect("dashboard")


@login_required
@require_POST
def demo(request):
    scenario = request.POST.get("scenario", "healthy")
    if scenario not in SCENARIOS:
        return HttpResponseBadRequest("Unknown demo scenario.")
    call_command("demo", scenario, user=request.user.username)
    return redirect("dashboard")


@login_required
def export_csv(request):
    """Download every check-in as CSV, so it can be sent to the flight surgeon."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="astrocare-checkins.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "mission_day", "recorded_utc", "heart_rate_bpm", "bp_systolic", "bp_diastolic",
        "temperature_c", "glucose_mg_dl", "spo2_percent", "sleep_hours", "mood_1_to_5",
        "exercise_min",
    ])
    for c in CheckIn.objects.filter(astronaut=request.user):
        writer.writerow([
            c.day, c.created.strftime("%Y-%m-%d %H:%M"), c.hr, c.sys, c.dia,
            c.temp, c.glu, c.spo2, c.sleep, c.mood, c.ex,
        ])
    return response


def about(request):
    """Public page explaining the method, limits and sources."""
    rows = [
        dict(name=m["name"], unit=m["unit"], limits=describe_limits(m))
        for m in METRICS
    ]
    return render(request, "about.html", {"rows": rows})
