from django.contrib import messages
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from .models import (
    Player,
    PlayerPerformance,
    TrainingAttendance,
    MatchAttendance,
    Match
)

import json
import csv
from io import TextIOWrapper


# ---------------- HOME ----------------
def home_page(request):
    return render(request, "core/home.html")


# ---------------- LOGIN ----------------
def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "core/login.html")


# ---------------- REGISTER ----------------
def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(username=username, password=password)

        if role == "admin":
            user.is_staff = True
            user.save()

        messages.success(request, "Account created.")
        return redirect("login")

    return render(request, "core/register.html")


# ---------------- DASHBOARD ----------------
@login_required
def dashboard(request):
    if request.user.is_staff:

        top_players_qs = (
            PlayerPerformance.objects
            .values("player__player_name")
            .annotate(total_goals=Sum("goals"))
            .order_by("-total_goals")[:5]
        )

        top_players = list(top_players_qs)

        chart_labels = [p["player__player_name"] for p in top_players]
        chart_goals = [p["total_goals"] or 0 for p in top_players]

        return render(request, "core/admin_dashboard.html", {
            "top_players": top_players,
            "chart_labels_json": json.dumps(chart_labels),
            "chart_goals_json": json.dumps(chart_goals),
        })

    return render(request, "core/user_dashboard.html")


# ---------------- ANALYTICS ----------------
@login_required
def analytics_page(request):
    performances = PlayerPerformance.objects.select_related("player")

    labels = [p.player.player_name for p in performances]
    goals = [p.goals for p in performances]

    return render(request, "core/analytics.html", {
        "labels": labels,
        "goals": goals,
        "total_entries": len(performances),
    })


# ---------------- SEASON ANALYTICS ----------------
@login_required
def season_analytics(request):
    players = Player.objects.all()
    data = []

    for player in players:
        performances = PlayerPerformance.objects.filter(player=player)

        matches = performances.count()
        total_goals = sum(p.goals for p in performances)

        data.append({
            "player": player.player_name,
            "matches": matches,
            "goals": total_goals
        })

    return render(request, "core/season_analytics.html", {
        "analytics_data": data
    })


# ---------------- COMPARE 2 ----------------
@login_required
def compare_page(request):
    players = Player.objects.all().order_by("player_name")
    return render(request, "core/compare.html", {
        "players": players
    })


# ---------------- COMPARE XI ----------------
@login_required
def compare_xi(request):
    players = Player.objects.all()
    return render(request, "core/compare_xi.html", {
        "players": players
    })

# ---------------- PLAYER ATTENDANCE ----------------
@login_required
def player_attendance(request):
    user = request.user

    try:
        player = Player.objects.get(player_name=user.username)
    except Player.DoesNotExist:
        return render(request, "core/player_attendance.html", {
            "attendance": [],
            "total": 0,
            "present": 0,
            "percentage": 0
        })

    attendance = TrainingAttendance.objects.filter(player=player).select_related("training")

    total = attendance.count()
    present = attendance.filter(present=True).count()

    percentage = round((present / total) * 100, 2) if total > 0 else 0

    return render(request, "core/player_attendance.html", {
        "attendance": attendance,
        "total": total,
        "present": present,
        "percentage": percentage
    })


# ---------------- ADMIN ATTENDANCE ----------------
@staff_member_required
def admin_attendance_view(request):
    players = Player.objects.all()
    data = []

    for player in players:
        training_total = TrainingAttendance.objects.filter(player=player).count()
        training_present = TrainingAttendance.objects.filter(
            player=player, present=True
        ).count()

        match_played = MatchAttendance.objects.filter(
            player=player, status="Played"
        ).count()

        percentage = round((training_present / training_total) * 100, 2) if training_total > 0 else 0

        data.append({
            "player": player,
            "training_total": training_total,
            "training_present": training_present,
            "training_absent": training_total - training_present,
            "match_played": match_played,
            "percentage": percentage
        })

    return render(request, "core/admin_attendance.html", {"data": data})

# ---------------- CSV UPLOAD ----------------
@staff_member_required
def upload_performance_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):

        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Please upload a valid CSV file.")
            return redirect("dashboard")

        file_data = TextIOWrapper(csv_file.file, encoding="utf-8")
        reader = csv.DictReader(file_data)

        inserted = 0
        skipped = 0

        for row in reader:
            try:
                # 🔥 Create match using your model structure
                match, _ = Match.objects.get_or_create(
                    opponent=row["match"].strip(),
                    defaults={
                        "match_date": date.today(),
                        "venue": "Unknown"
                    }
                )

                player = Player.objects.get(
                    player_name=row["player_name"].strip()
                )

                PlayerPerformance.objects.create(
                    match=match,
                    player=player,
                    goals=int(row["goals"]),
                    assists=int(row["assists"]),
                    shots_on_target=int(row["shots_on_target"]),
                    tackles=int(row["tackles"]),
                )

                inserted += 1

            except Exception:
                skipped += 1

        messages.success(request, f"Inserted: {inserted} | Skipped: {skipped}")
        return redirect("dashboard")

    return redirect("dashboard")


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect("login")