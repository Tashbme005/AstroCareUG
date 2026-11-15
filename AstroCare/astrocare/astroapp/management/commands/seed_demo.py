from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

from astroapp.management.commands.demo import SCENARIOS


class Command(BaseCommand):
    help = "Create a demo crew account and load 14 days of sample check-ins."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="crew")
        parser.add_argument("--password", default="astro-demo-2026")
        parser.add_argument("--scenario", choices=list(SCENARIOS), default="immune")

    def handle(self, *args, **o):
        User = get_user_model()
        user, created = User.objects.get_or_create(username=o["username"])
        user.set_password(o["password"])
        user.save()
        call_command("demo", o["scenario"], user=user.username)
        state = "Created" if created else "Updated"
        self.stdout.write(
            f"{state} user '{user.username}'. Log in with password '{o['password']}'. "
            "This is for demos only; do not deploy it with a public password."
        )
