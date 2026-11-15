import math
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from astroapp.models import CheckIn

# field: (day 1 value, day 14 value)
SCENARIOS = {
 "healthy":   dict(hr=(63,64), sys=(118,120), dia=(76,78), temp=(36.6,36.7), glu=(92,95), spo2=(98,98), sleep=(7,7.2), mood=(4,4), ex=(130,125)),
 "immune":    dict(hr=(64,104), sys=(119,126), dia=(77,82), temp=(36.7,38.3), glu=(94,110), spo2=(98,95), sleep=(7,5.6), mood=(4,3), ex=(125,70)),
 "bones":     dict(hr=(62,72), sys=(120,138), dia=(78,88), temp=(36.6,36.7), glu=(95,105), spo2=(98,97), sleep=(7,6.8), mood=(4,4), ex=(120,35)),
 "isolation": dict(hr=(66,88), sys=(120,128), dia=(78,82), temp=(36.6,36.8), glu=(95,140), spo2=(98,97), sleep=(7,4.5), mood=(4,1), ex=(120,60)),
 "emergency": dict(hr=(70,128), sys=(120,178), dia=(78,112), temp=(36.7,37.4), glu=(96,150), spo2=(98,89), sleep=(6.8,5), mood=(4,2), ex=(110,40)),
}
FLOAT = {"temp", "sleep"}

class Command(BaseCommand):
    help = "Load 14 days of demo check-ins: python manage.py demo <scenario> --user <username>"

    def add_arguments(self, parser):
        parser.add_argument("scenario", choices=list(SCENARIOS))
        parser.add_argument("--user", required=True)

    def handle(self, *args, **o):
        user = get_user_model().objects.get(username=o["user"])
        CheckIn.objects.filter(astronaut=user).delete()
        for i in range(14):
            t, row = i / 13, {}
            for f, (a, b) in SCENARIOS[o["scenario"]].items():
                v = a + (b - a) * t + math.sin(i * 2.1 + len(f)) * (0.08 if f == "temp" else 0 if f == "mood" else 0.2 if f == "sleep" else 6 if f == "ex" else 1.2)
                row[f] = max(1, round(v)) if f == "mood" else round(v, 1) if f in FLOAT else round(v)
            CheckIn.objects.create(astronaut=user, day=i + 1, **row)
        self.stdout.write(f"Loaded {o['scenario']} for {user.username}")