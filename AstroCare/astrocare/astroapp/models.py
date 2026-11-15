from django.conf import settings
from django.db import models

class CheckIn(models.Model):
    astronaut = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    day = models.PositiveIntegerField(help_text="Mission day")
    created = models.DateTimeField(auto_now_add=True)
    hr = models.PositiveIntegerField("Heart rate (bpm)")
    sys = models.PositiveIntegerField("Blood pressure, top number")
    dia = models.PositiveIntegerField("Blood pressure, bottom number")
    temp = models.FloatField("Temperature (°C)")
    glu = models.PositiveIntegerField("Blood sugar (mg/dL)")
    spo2 = models.PositiveIntegerField("Blood oxygen (%)")
    sleep = models.FloatField("Sleep last night (hours)")
    mood = models.PositiveSmallIntegerField(
        "Mood", choices=[(1, "1 · Very low"), (2, "2 · Low"), (3, "3 · Okay"), (4, "4 · Good"), (5, "5 · Great")])
    ex = models.PositiveIntegerField("Exercise today (min)")

    class Meta:
        ordering = ["day", "created"]