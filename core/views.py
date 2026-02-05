from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db.models import Sum, Count, Avg
from .models import Player, PlayerPerformance


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

        if user is not None:
            login(request, user)
            return redirect("dashboard")   # 👈 THIS IS THE IMPORTANT LINE
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "core/login.html")


# ---------------- REGISTER ----------------
def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")  # admin / user

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(username=username, password=password)

        if role == "admin":
            user.is_staff = True
            user.save()

        messages.success(request, "Account created. Please login.")
        return redirect("login")

    return render(request, "core/register.html")


# ---------------- DASHBOARD ROUTER ----------------
@login_required
def dashboard(request):
    """
    ONE dashboard entry point.
    """
    if request.user.is_staff:
        return render(request, "core/admin_dashboard.html")
    else:
        return render(request, "core/user_dashboard.html")


# ---------------- ANALYTICS ----------------
@login_required
def analytics_page(request):
    performances = PlayerPerformance.objects.select_related("player")

    labels = [p.player.player_name for p in performances]
    goals = [p.goals for p in performances]

    context = {
        "labels": labels,
        "goals": goals,
        "total_entries": len(performances),
    }

    return render(request, "core/analytics.html", context)

@login_required
def season_analytics(request):
    # Aggregate season data per player
    season_data = (
        PlayerPerformance.objects
        .values("player__player_name")
        .annotate(
            matches_played=Count("id"),
            total_goals=Sum("goals"),
            total_assists=Sum("assists"),
            total_tackles=Sum("tackles"),
            avg_goals=Avg("goals"),
        )
        .order_by("-total_goals")
    )

    # Insights
    top_scorer = season_data[0]["player__player_name"] if season_data else "N/A"
    team_avg_goals = round(
        sum(d["total_goals"] or 0 for d in season_data) / len(season_data), 2
    ) if season_data else 0

    # Data for chart
    labels = [d["player__player_name"] for d in season_data]
    goals = [d["total_goals"] or 0 for d in season_data]

    context = {
        "season_data": season_data,
        "top_scorer": top_scorer,
        "team_avg_goals": team_avg_goals,
        "labels": labels,
        "goals": goals,
    }

    return render(request, "core/season_analytics.html", context)


# ---------------- COMPARE ----------------
@login_required
def compare_page(request):
    players = Player.objects.all().order_by("player_name")

    p1_id = request.GET.get("p1")
    p2_id = request.GET.get("p2")

    def totals(pid):
        if not pid:
            return {"goals": 0, "assists": 0, "tackles": 0, "shots_on_target": 0}

        qs = PlayerPerformance.objects.filter(player_id=pid)
        return {
            "goals": sum(x.goals for x in qs),
            "assists": sum(x.assists for x in qs),
            "tackles": sum(x.tackles for x in qs),
            "shots_on_target": sum(x.shots_on_target for x in qs),
        }

    p1 = totals(p1_id)
    p2 = totals(p2_id)

    context = {
        "players": players,
        "p1_id": p1_id,
        "p2_id": p2_id,
        "p1": p1,
        "p2": p2,
    }

    return render(request, "core/compare.html", context)

@login_required
def season_analytics(request):
    players = Player.objects.all()

    analytics_data = []

    for player in players:
        performances = PlayerPerformance.objects.filter(player=player)

        matches = performances.count()
        total_goals = sum(p.goals for p in performances)
        total_assists = sum(p.assists for p in performances)
        total_tackles = sum(p.tackles for p in performances)
        total_shots = sum(p.shots_on_target for p in performances)

        avg_goals = round(total_goals / matches, 2) if matches > 0 else 0

        # ---------- ANALYTICS LOGIC ----------
        suggestions = []

        if avg_goals < 0.5:
            suggestions.append("Needs improvement in finishing and shooting accuracy.")
        else:
            suggestions.append("Good goal scoring consistency.")

        if total_assists < matches:
            suggestions.append("Should improve passing and chance creation.")
        else:
            suggestions.append("Strong playmaking ability.")

        if total_tackles > matches * 2:
            suggestions.append("Excellent defensive contribution.")
        else:
            suggestions.append("Needs to improve defensive work rate.")

        analytics_data.append({
            "player": player.player_name,
            "matches": matches,
            "goals": total_goals,
            "assists": total_assists,
            "tackles": total_tackles,
            "shots": total_shots,
            "avg_goals": avg_goals,
            "suggestions": suggestions
        })

    return render(
        request,
        "core/season_analytics.html",
        {"analytics_data": analytics_data}
    )

@login_required
def compare_xi(request):
    players = Player.objects.all()

    selected_ids = request.GET.getlist("players")

    chart_data = []

    if len(selected_ids) >= 2:
        for pid in selected_ids:
            player = Player.objects.get(id=pid)

            stats = PlayerPerformance.objects.filter(player=player)

            chart_data.append({
                "name": player.player_name,
                "goals": sum(p.goals for p in stats),
                "assists": sum(p.assists for p in stats),
                "tackles": sum(p.tackles for p in stats),
                "shots": sum(p.shots_on_target for p in stats),
            })

    context = {
        "players": players,
        "chart_data": chart_data,
        "selected_count": len(selected_ids)
    }

    return render(request, "core/compare_xi.html", context)

# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect("login")
