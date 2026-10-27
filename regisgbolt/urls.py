from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("munkatarsaink/", views.MunkatarsainkView.as_view(), name="munkatarsaink"),
    path("elerhetoseg/", views.ElerhetosegView.as_view(), name="elerhetoseg"),
    
    path("termekek/", views.TermekekListView.as_view(), name="termekek"),
    path("termekek/<int:pk>/", views.TermekDetailView.as_view(), name="termek_reszlet"),
    path("termekek/<int:pk>/licit/", views.licit_tetel, name="licit_tetel"),
    path("termekek/<int:pk>/start/", views.arveres_inditasa, name="arveres_inditasa"),
    path("termekek/<int:pk>/stop/", views.arveres_lezarasa, name="arveres_lezarasa"),

    path("accounts/signup/", views.SignUpView.as_view(), name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
]