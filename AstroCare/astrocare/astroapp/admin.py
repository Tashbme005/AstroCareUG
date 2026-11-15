from django.apps import apps
from django.contrib import admin

# Register your models here.
for model in apps.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
