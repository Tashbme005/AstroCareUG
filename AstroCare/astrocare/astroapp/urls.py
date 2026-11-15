from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("env/", views.set_env, name="set_env"),
    path("demo/", views.demo, name="demo"),
    path("export.csv", views.export_csv, name="export_csv"),
    path("about/", views.about, name="about"),
]
