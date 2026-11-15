from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from .models import CheckIn

# Plausibility limits. These reject typos and impossible entries (for example
# a heart rate of 900). They are not clinical limits; see rules.py for those.
RANGES = {
    "hr": (20, 250),
    "sys": (50, 260),
    "dia": (30, 160),
    "temp": (30.0, 43.0),
    "glu": (20, 600),
    "spo2": (50, 100),
    "sleep": (0, 24),
    "mood": (1, 5),
    "ex": (0, 600),
}
STEPS = {"temp": "0.1", "sleep": "0.1"}


class CheckInForm(forms.ModelForm):
    class Meta:
        model = CheckIn
        fields = ("hr", "sys", "dia", "temp", "glu", "spo2", "sleep", "mood", "ex")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, (low, high) in RANGES.items():
            field = self.fields[name]
            if isinstance(field, forms.TypedChoiceField):
                continue  # mood: the dropdown already limits it to 1 to 5
            field.validators.append(MinValueValidator(low))
            field.validators.append(MaxValueValidator(high))
            field.widget.attrs.update(min=low, max=high)
            if name in STEPS:
                field.widget.attrs["step"] = STEPS[name]

    def clean(self):
        data = super().clean()
        sys_, dia = data.get("sys"), data.get("dia")
        if sys_ is not None and dia is not None and sys_ <= dia:
            self.add_error("dia", "The bottom number must be lower than the top number.")
        return data
