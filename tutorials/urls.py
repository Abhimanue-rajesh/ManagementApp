from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from tutorials import views

app_name = "tutorials"

urlpatterns = [
    path("login/", views.TutorialLoginView.as_view(), name="login"),
    path(
        "logout/",
        LogoutView.as_view(next_page=reverse_lazy("tutorials:login")),
        name="logout",
    ),
    path("", views.tutorial_list, name="list"),
    path("<int:pk>/", views.tutorial_detail, name="detail"),
]
