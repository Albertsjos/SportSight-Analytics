from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("login/", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path("analytics/", views.analytics_page, name="analytics"),
    path("compare/", views.compare_page, name="compare"),
    path("compare-xi/", views.compare_xi, name="compare_xi"),
    path("attendance/", views.player_attendance, name="player_attendance"),
    path("my-attendance/", views.player_attendance, name="player_attendance"),
    path("admin-attendance/", views.admin_attendance_view, name="admin_attendance"),

    path("season-analytics/", views.season_analytics, name="season_analytics"),
    path("logout/", views.logout_view, name="logout"),
]
