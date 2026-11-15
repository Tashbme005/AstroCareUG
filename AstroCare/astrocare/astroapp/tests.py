from types import SimpleNamespace as C

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from .forms import CheckInForm
from .models import CheckIn
from .rules import ACT, OK, WATCH, assess, bp_check, find_drifts

BASE = dict(hr=64, sys=118, dia=76, temp=36.6, glu=92, spo2=98, sleep=7.2, mood=4, ex=125)


def reading(**kw):
    return C(**{**BASE, **kw})


def card(result, key):
    return next(c for c in result["cards"] if c["key"] == key)


class RuleTests(TestCase):
    def sev(self, key, **kw):
        return card(assess(reading(**kw)), key)["severity"]

    def test_healthy(self):
        self.assertEqual(assess(reading())["overall"], OK)

    def test_heart_rate_bands(self):
        self.assertEqual(self.sev("hr", hr=95), WATCH)
        self.assertEqual(self.sev("hr", hr=130), ACT)
        self.assertEqual(self.sev("hr", hr=45), WATCH)
        self.assertEqual(self.sev("hr", hr=35), ACT)

    def test_fever_and_fast_pulse_combo(self):
        out = assess(reading(temp=38.4, hr=115))
        self.assertTrue(any("infection" in c for c in out["combos"]))
        self.assertEqual(out["overall"], ACT)

    def test_red_adds_flight_surgeon(self):
        c = card(assess(reading(spo2=88)), "spo2")
        self.assertIn("Contact the flight surgeon now.", c["actions"])

    def test_blood_pressure_direction(self):
        # A low bottom number alone must not be reported as "high".
        self.assertEqual(bp_check(C(sys=120, dia=45)), (ACT, "lo"))
        self.assertEqual(bp_check(C(sys=120, dia=55)), (WATCH, "lo"))
        self.assertEqual(bp_check(C(sys=150, dia=70)), (WATCH, "hi"))
        self.assertEqual(bp_check(C(sys=125, dia=90)), (WATCH, "hi"))
        self.assertEqual(bp_check(C(sys=170, dia=95)), (ACT, "hi"))
        self.assertEqual(bp_check(C(sys=80, dia=55)), (ACT, "lo"))
        self.assertEqual(bp_check(C(sys=118, dia=76)), (OK, "ok"))

    def test_one_bad_night_is_only_a_watch(self):
        out = assess(reading(sleep=4, ex=30))
        self.assertEqual(card(out, "sleep")["severity"], WATCH)
        self.assertEqual(card(out, "ex")["severity"], WATCH)
        self.assertEqual(out["overall"], WATCH)

    def test_three_bad_nights_escalate(self):
        history = [reading(sleep=4.5) for _ in range(3)]
        out = assess(history[-1], history)
        self.assertEqual(card(out, "sleep")["severity"], ACT)
        self.assertNotIn("chest pain", " ".join(card(out, "sleep")["actions"]))

    def test_lifestyle_only_escalation_has_softer_headline(self):
        history = [reading(ex=30) for _ in range(3)]
        out = assess(history[-1], history)
        self.assertEqual(out["overall"], ACT)
        self.assertEqual(out["headline"][0], "Act today")
        self.assertNotIn("Contact the flight surgeon now", out["headline"][1])

    def test_vital_sign_escalation_keeps_urgent_headline(self):
        out = assess(reading(spo2=88))
        self.assertEqual(out["headline"][0], "Act now")

    def test_low_mood_is_never_downgraded(self):
        self.assertEqual(self.sev("mood", mood=1), ACT)


class DriftTests(TestCase):
    def test_needs_enough_history(self):
        self.assertEqual(find_drifts([reading()] * 5), [])

    def test_stable_history_has_no_drift(self):
        self.assertEqual(find_drifts([reading()] * 10), [])

    def test_detects_declining_exercise_and_sleep(self):
        history = [reading(ex=130 - i * 10, sleep=7.5 - i * 0.3) for i in range(8)]
        names = {d["name"] for d in find_drifts(history)}
        self.assertIn("Exercise", names)
        self.assertIn("Sleep", names)

    def test_drift_alone_raises_banner_to_watch(self):
        history = [reading(hr=62 + i * 2) for i in range(8)]  # 62 -> 76, still normal
        out = assess(history[-1], history)
        self.assertTrue(all(c["severity"] == OK for c in out["cards"]))
        self.assertEqual(out["overall"], WATCH)
        self.assertTrue(out["drifts"])


class FormTests(TestCase):
    def form(self, **kw):
        return CheckInForm({**BASE, **kw})

    def test_valid(self):
        self.assertTrue(self.form().is_valid())

    def test_rejects_impossible_values(self):
        for bad in (dict(hr=900), dict(spo2=140), dict(temp=5), dict(sleep=40), dict(mood=9)):
            self.assertFalse(self.form(**bad).is_valid(), bad)

    def test_bottom_number_must_be_lower(self):
        f = self.form(sys=110, dia=120)
        self.assertFalse(f.is_valid())
        self.assertIn("dia", f.errors)


class ViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("tester", password="pw-12345-xyz")
        self.client.login(username="tester", password="pw-12345-xyz")

    def test_login_required(self):
        self.client.logout()
        self.assertEqual(self.client.get("/").status_code, 302)
        self.assertEqual(self.client.get("/export.csv").status_code, 302)

    def test_empty_dashboard(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_save_check_in_increments_day(self):
        self.client.post("/", BASE)
        self.client.post("/", BASE)
        self.assertEqual(list(CheckIn.objects.values_list("day", flat=True)), [1, 2])

    def test_invalid_check_in_is_not_saved(self):
        resp = self.client.post("/", {**BASE, "hr": 900})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(CheckIn.objects.count(), 0)

    def test_every_demo_scenario_renders(self):
        for name in ("healthy", "immune", "bones", "isolation", "emergency"):
            self.assertEqual(self.client.post("/demo/", {"scenario": name}).status_code, 302)
            self.assertEqual(CheckIn.objects.filter(astronaut=self.user).count(), 14)
            self.assertEqual(self.client.get("/").status_code, 200)

    def test_healthy_demo_is_all_clear(self):
        self.client.post("/demo/", {"scenario": "healthy"})
        self.assertEqual(self.client.get("/").context["a"]["overall"], OK)

    def test_emergency_demo_is_act_now(self):
        self.client.post("/demo/", {"scenario": "emergency"})
        self.assertEqual(self.client.get("/").context["a"]["overall"], ACT)

    def test_unknown_demo_scenario_is_a_400(self):
        self.assertEqual(self.client.post("/demo/", {"scenario": "nope"}).status_code, 400)

    def test_csv_export_only_contains_own_data(self):
        other = get_user_model().objects.create_user("other", password="pw-12345-xyz")
        CheckIn.objects.create(astronaut=other, day=1, **BASE)
        self.client.post("/", BASE)
        body = self.client.get("/export.csv").content.decode()
        self.assertEqual(len(body.strip().splitlines()), 2)  # header + 1 row

    def test_about_page_is_public(self):
        self.client.logout()
        self.assertEqual(self.client.get("/about/").status_code, 200)

    def test_logout(self):
        self.assertEqual(self.client.post("/accounts/logout/").status_code, 302)
        self.assertEqual(self.client.get("/").status_code, 302)


class SeedTests(TestCase):
    def test_seed_demo_creates_user_with_data(self):
        call_command("seed_demo", "--username", "crew", "--password", "pw-12345-xyz", verbosity=0)
        user = get_user_model().objects.get(username="crew")
        self.assertEqual(CheckIn.objects.filter(astronaut=user).count(), 14)
