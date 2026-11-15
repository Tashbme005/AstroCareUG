"""Rule-based, non-diagnostic wellness guidance for the AstroCare dashboard.

These screening ranges and suggestions are informational, not a diagnosis or a
substitute for the mission medical protocol or a qualified clinician. Symptoms
that feel severe or rapidly worsen should be handled using the emergency
procedure, regardless of the readings below.

The ranges are prototype values chosen for demonstration. They have NOT been
validated against NASA flight medical standards. See the About page.
"""

OK, WATCH, ACT = 0, 1, 2
LABELS = ["Normal", "Watch", "Act now"]
RED_FLAG = "Contact the flight surgeon now."
PERSISTENT_FLAG = "This has lasted several days. Tell the flight surgeon today."
ESCALATE = (
    "For chest pain, trouble breathing, faintness, or confusion, follow the "
    "onboard Emergency guide now."
)

# Sleep and exercise are lifestyle signals. One bad day is a "Watch", not an
# emergency. It only becomes "Act now" after PERSIST_DAYS bad days in a row.
LIFESTYLE = {"sleep", "ex"}
PERSIST_DAYS = 3


def band(value, warn=(None, None), red=(None, None)):
    """Return (severity, direction), with direction 'lo', 'hi', or 'ok'."""
    below = lambda limits: limits[0] is not None and value < limits[0]
    above = lambda limits: limits[1] is not None and value > limits[1]
    if below(red) or above(red):
        return ACT, "lo" if below(red) else "hi"
    if below(warn) or above(warn):
        return WATCH, "lo" if below(warn) else "hi"
    return OK, "ok"


def bp_check(check_in):
    """Screen a blood-pressure reading and return its severity and direction."""
    s, d = check_in.sys, check_in.dia
    if s >= 160 or d >= 100:
        return ACT, "hi"
    if s < 85 or d < 50:
        return ACT, "lo"
    if s >= 130 or d >= 85:
        return WATCH, "hi"
    if s < 95 or d < 60:
        return WATCH, "lo"
    return OK, "ok"


# Each direction maps to a plain-language explanation and practical next steps.
# "warn" and "red" are (low, high) limits; None means no limit on that side.
METRICS = [
    dict(
        key="hr", name="Heart rate", unit="bpm", region="heart",
        raw=lambda c: c.hr, warn=(50, 90), red=(40, 110),
        value=lambda c: c.hr,
        say={
            "ok": ("Your resting heart rate is within the screening range.",
                   ["Keep up regular activity and follow your usual monitoring routine."]),
            "hi": ("Your resting heart rate is higher than this guide's range. "
                   "Activity, stress, dehydration, fever, caffeine, or poor sleep may affect it.",
                   ["Rest quietly for 5 minutes, then recheck.",
                    "Drink water if you are able and avoid caffeine for now.",
                    "If it remains high or you feel unwell, contact the flight surgeon."]),
            "lo": ("Your heart rate is lower than this guide's range. Some fit people "
                   "have a low resting rate, but symptoms matter.",
                   ["Rest for 5 minutes and recheck.",
                    "If dizzy, faint, weak, or unwell, stop activity and contact the medical team."]),
        },
    ),
    dict(
        key="bp", name="Blood pressure", unit="mmHg", region="heart",
        check=bp_check, value=lambda c: f"{c.sys}/{c.dia}",
        limits_text="Watch: top ≥130 or bottom ≥85, or top <95 or bottom <60. "
                    "Act: top ≥160 or bottom ≥100, or top <85 or bottom <50.",
        say={
            "ok": ("Your blood pressure is within this guide's screening range.",
                   ["Continue your usual hydration and activity routine."]),
            "hi": ("Your blood pressure is above this guide's range. Fluid shifts, "
                   "stress, and salty food can influence a reading.",
                   ["Sit quietly for 5 minutes and repeat the measurement using the approved technique.",
                    "Avoid extra salty food and follow your fluid plan.",
                    "If repeated readings remain high, contact the flight surgeon."]),
            "lo": ("Your blood pressure is below this guide's range. Low readings "
                   "can contribute to light-headedness, especially when standing.",
                   ["Sit or lie down if light-headed; rise slowly and hold a stable support.",
                    "Drink water if permitted by your care plan.",
                    "Fainting, confusion, or persistent symptoms need prompt medical help."]),
        },
    ),
    dict(
        key="spo2", name="Blood oxygen", unit="%", region="heart",
        raw=lambda c: c.spo2, warn=(95, None), red=(91, None),
        value=lambda c: c.spo2,
        say={
            "ok": ("Your blood-oxygen reading is within this guide's screening range.",
                   ["No specific action is suggested by this reading alone."]),
            "lo": ("Your blood-oxygen reading is lower than this guide's range. "
                   "A measurement can be affected by movement, cold hands, or the sensor.",
                   ["Sit still, warm your hands, check sensor placement, and recheck.",
                    "Check cabin-air readings using the approved procedure.",
                    "If still low or you have breathing symptoms, contact the flight surgeon; "
                    "use oxygen only as directed by your medical protocol."]),
        },
    ),
    dict(
        key="temp", name="Body temperature", unit="°C", region="immune",
        raw=lambda c: c.temp, warn=(36.1, 37.5), red=(35.5, 38.0),
        value=lambda c: c.temp,
        say={
            "ok": ("Your temperature is within this guide's screening range.",
                   ["Continue routine monitoring."]),
            "hi": ("Your temperature is elevated compared with this guide's range. "
                   "A reading alone cannot identify the cause.",
                   ["Rest, drink fluids if permitted, and recheck with the approved device.",
                    "Use good hand hygiene and reduce close contact if you feel ill.",
                    "Report a persistent fever or worsening symptoms to the flight surgeon."]),
            "lo": ("Your temperature is below this guide's screening range.",
                   ["Use comfortable layers and a warm drink if appropriate.",
                    "Recheck in 15 minutes and verify the measurement technique.",
                    "If it stays low or you feel unwell, contact the medical team."]),
        },
    ),
    dict(
        key="glu", name="Blood sugar", unit="mg/dL", region="metab",
        raw=lambda c: c.glu, warn=(70, 125), red=(55, 200),
        value=lambda c: c.glu,
        say={
            "ok": ("Your blood-sugar reading is within this guide's screening range.",
                   ["Continue regular, balanced meals and follow your care plan."]),
            "hi": ("Your blood-sugar reading is above this guide's range. Meals, "
                   "stress, illness, and activity can affect it.",
                   ["Drink water if permitted and repeat the measurement as directed.",
                    "Choose a balanced meal and follow any prescribed diabetes plan.",
                    "A persistently high reading or feeling unwell warrants contacting the flight surgeon."]),
            "lo": ("Your blood-sugar reading is low. Shakiness, sweating, or confusion "
                   "can occur, but symptoms vary.",
                   ["If awake and able to swallow, take fast-acting sugar according to your medical plan.",
                    "Recheck in 15 minutes and follow your care plan.",
                    "If confused, unable to swallow, or not improving, get medical help now; "
                    "do not give food or drink by mouth to someone unable to swallow."]),
        },
    ),
    dict(
        key="sleep", name="Sleep last night", unit="hours", region="brain",
        raw=lambda c: c.sleep, warn=(6.5, None), red=(5, None),
        value=lambda c: c.sleep,
        say={
            "ok": ("Your reported sleep is within this guide's target range.",
                   ["Keep a regular sleep schedule and use the planned wind-down routine."]),
            "lo": ("You slept less than this guide's target. Light, noise, schedule "
                   "changes, or stress may interfere with rest.",
                   ["Dim lights and reduce screens before the scheduled sleep period.",
                    "Request a protected rest period if available.",
                    "If poor sleep persists or affects safety, tell the flight surgeon."]),
        },
    ),
    dict(
        key="mood", name="Mood", unit="/ 5", region="brain",
        raw=lambda c: c.mood, warn=(4, None), red=(2, None),
        value=lambda c: c.mood,
        say={
            "ok": ("Your mood rating is in the positive range.",
                   ["Stay connected with crewmates and supportive contacts."]),
            "lo": ("You reported a low mood. Isolation, confinement, and disrupted "
                   "routines can be difficult, and support is available.",
                   ["Talk with a trusted crewmate or behavioral-health professional.",
                    "Arrange a supportive call or check-in if available.",
                    "If you feel unsafe or at risk of harming yourself, tell the flight surgeon "
                    "immediately and follow the emergency procedure."]),
        },
    ),
    dict(
        key="ex", name="Exercise today", unit="min", region="bones",
        raw=lambda c: c.ex, warn=(100, None), red=(60, None),
        value=lambda c: c.ex,
        say={
            "ok": ("Your reported exercise is within this guide's target range.",
                   ["Continue the approved mix of strength and cardiovascular activity."]),
            "lo": ("Your reported exercise is below this guide's target. Regular "
                   "approved exercise helps maintain strength and conditioning.",
                   ["If medically cleared, schedule an approved strength or cardio session.",
                    "Build back gradually and follow the mission exercise plan.",
                    "If illness, injury, or equipment issues prevent exercise, tell the medical team."]),
        },
    ),
]

REGIONS = {
    "heart": (
        "Heart and blood vessels",
        "Fluid shifts and other mission conditions can affect circulation. A screening result is not a diagnosis.",
    ),
    "brain": (
        "Brain and mood",
        "Isolation, confinement, distance from Earth, and disrupted sleep can affect mood, focus, and decisions.",
    ),
    "immune": (
        "Immune system",
        "Stress and a closed environment can affect health. Temperature is only one part of assessing illness.",
    ),
    "metab": (
        "Metabolism and food",
        "Meals, activity, health conditions, and some treatments can affect blood sugar and nutrition.",
    ),
    "bones": (
        "Bones and muscles",
        "Weightlessness can affect bones and muscles; follow the mission's approved exercise and medical plans.",
    ),
}

# Trend ("drift") rules: compare the average of the last 3 check-ins with the
# average of the first 3 in the window. sign=+1 means a rise is the concern,
# sign=-1 means a fall is the concern. Prototype heuristics, to be tuned.
DRIFT_MIN_DAYS = 6
DRIFTS = {
    "hr":    dict(name="Heart rate",       sign=+1, delta=10,  unit="bpm"),
    "sys":   dict(name="Blood pressure",   sign=+1, delta=10,  unit="mmHg (top number)"),
    "spo2":  dict(name="Blood oxygen",     sign=-1, delta=2,   unit="%"),
    "temp":  dict(name="Body temperature", sign=+1, delta=0.5, unit="°C"),
    "glu":   dict(name="Blood sugar",      sign=+1, delta=20,  unit="mg/dL"),
    "sleep": dict(name="Sleep",            sign=-1, delta=1.0, unit="hours"),
    "mood":  dict(name="Mood",             sign=-1, delta=1.0, unit="points"),
    "ex":    dict(name="Exercise",         sign=-1, delta=30,  unit="min"),
}


def evaluate(metric, check_in):
    """Return (severity, direction) for one metric and one check-in."""
    if "check" in metric:
        return metric["check"](check_in)
    return band(metric["raw"](check_in), metric["warn"], metric["red"])


def describe_limits(metric):
    """Human-readable limits for the About page (single source of truth)."""
    if "limits_text" in metric:
        return metric["limits_text"]
    parts = []
    for level, limits in (("Watch", metric["warn"]), ("Act", metric["red"])):
        lo, hi = limits
        bits = []
        if lo is not None:
            bits.append(f"below {lo}")
        if hi is not None:
            bits.append(f"above {hi}")
        if bits:
            parts.append(f"{level}: " + " or ".join(bits))
    return ". ".join(parts) + "."


def _persistent(metric, history):
    """True if the last PERSIST_DAYS check-ins were all in the Act band."""
    if not history or len(history) < PERSIST_DAYS:
        return False
    return all(evaluate(metric, h)[0] == ACT for h in history[-PERSIST_DAYS:])


def find_drifts(history):
    """Return plain-language notes for readings that are trending the wrong way."""
    if not history or len(history) < DRIFT_MIN_DAYS:
        return []
    notes = []
    for field, rule in DRIFTS.items():
        values = [getattr(h, field) for h in history]
        baseline = sum(values[:3]) / 3
        recent = sum(values[-3:]) / 3
        change = (recent - baseline) * rule["sign"]
        if change >= rule["delta"]:
            verb = "risen" if rule["sign"] > 0 else "fallen"
            notes.append(dict(
                name=rule["name"],
                text=(f"{rule['name']} has {verb} by about {change:.1f} {rule['unit']} "
                      f"since your first check-ins, even if each reading looks acceptable on its own."),
            ))
    return notes


def assess(check_in, history=None):
    """Turn one check-in (and optional history, oldest first, ending with this
    check-in) into dashboard cards and summary guidance."""
    cards = []
    region_severity = {region: OK for region in REGIONS}
    severities = {}

    for metric in METRICS:
        severity, direction = evaluate(metric, check_in)
        persistent_flag = False
        if metric["key"] in LIFESTYLE and severity == ACT:
            if _persistent(metric, history):
                persistent_flag = True
            else:
                severity = WATCH
        text, suggested_actions = metric["say"].get(direction, metric["say"]["ok"])
        actions = list(suggested_actions)
        if severity == ACT:
            actions.append(RED_FLAG)
            if metric["key"] not in LIFESTYLE:
                actions.append(ESCALATE)
        elif persistent_flag:
            actions.append(PERSISTENT_FLAG)

        severities[(metric["key"], direction)] = severity
        region = metric["region"]
        region_severity[region] = max(region_severity[region], severity)
        cards.append(dict(
            key=metric["key"], name=metric["name"], unit=metric["unit"],
            value=metric["value"](check_in), severity=severity,
            label=LABELS[severity], text=text, actions=actions, region=region,
        ))

    combinations = []
    if severities.get(("temp", "hi"), OK) and severities.get(("hr", "hi"), OK):
        combinations.append(
            "An elevated temperature with a fast heart rate can occur with infection and has several possible causes. "
            "Report the combination to the flight surgeon and follow the illness protocol."
        )
    if severities.get(("sleep", "lo"), OK) and severities.get(("mood", "lo"), OK):
        combinations.append(
            "Poor sleep and low mood together may affect well-being and attention. "
            "Request rest and talk with a trusted support person or clinician."
        )
    if severities.get(("spo2", "lo"), OK) and (
        severities.get(("hr", "hi"), OK) or severities.get(("hr", "lo"), OK)
    ):
        combinations.append(
            "A low oxygen reading with an unusual heart rate needs prompt review. "
            "Recheck the sensor and follow the cabin-air and medical procedures."
        )

    drifts = find_drifts(history)
    overall = max(card["severity"] for card in cards)
    headlines = [
        ("All clear", "These readings are within the guide's screening ranges."),
        ("Keep an eye on things", "Some readings merit a recheck or routine follow-up."),
        ("Act now", "One or more readings are outside this guide's limits. " + RED_FLAG),
    ]
    headline = headlines[overall]
    if overall == ACT and all(
        c["key"] in LIFESTYLE for c in cards if c["severity"] == ACT
    ):
        headline = ("Act today",
                    "A pattern has lasted several days. Tell the flight surgeon today.")
    if overall == OK and drifts:
        overall = WATCH
        headline = ("Keep an eye on things",
                    "No single reading is out of range, but some are trending the wrong way.")

    regions = [
        dict(key=key, name=REGIONS[key][0], text=REGIONS[key][1],
             severity=severity, label=LABELS[severity])
        for key, severity in region_severity.items()
    ]
    return dict(
        cards=cards, combos=combinations, drifts=drifts, overall=overall,
        headline=headline, regions=regions,
    )
