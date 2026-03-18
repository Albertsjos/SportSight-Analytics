from django.contrib import messages
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from .models import (
    Team,
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

        # --- REAL KPI DATA ---
        total_players = Player.objects.count()
        total_goals_season = PlayerPerformance.objects.aggregate(
            t=Sum("goals")
        )["t"] or 0

        from .models import TrainingAttendance as TA
        total_att = TA.objects.count()
        present_att = TA.objects.filter(present=True).count()
        avg_attendance = round((present_att / total_att) * 100, 1) if total_att > 0 else 0

        return render(request, "core/admin_dashboard.html", {
            "top_players": top_players,
            "chart_labels_json": json.dumps(chart_labels),
            "chart_goals_json": json.dumps(chart_goals),
            "display_name": request.user.username.title(),
            "total_players": total_players,
            "total_goals_season": total_goals_season,
            "avg_attendance": avg_attendance,
        })

    # --- USER DASHBOARD LOGIC ---
    display_name = request.user.username.title()
    player_stats = None
    trend_data = None
    rankings = None
    attendance_summary = None
    next_match = None
    user_rank = 0

    try:
        # Try finding linked player first, then fallback to name match
        player = Player.objects.filter(user=request.user).first()
        if not player:
            # Exact match
            player = Player.objects.filter(player_name__iexact=request.user.username).first()
            
            # Fallback 1: Match by the last part of the username (i.e. last name)
            if not player and " " in request.user.username:
                last_name = request.user.username.split()[-1]
                player = Player.objects.filter(player_name__icontains=last_name).first()
                
            # Fallback 2: Basic 'contains' check
            if not player:
                player = Player.objects.filter(player_name__icontains=request.user.username).first()

            if player and not player.user:
                player.user = request.user
                player.save()

        if player:
            # 1. Quick Stats
            perfs = PlayerPerformance.objects.filter(player=player).select_related('match').order_by('match__match_date', 'match__id')
            player_stats = {
                "goals": perfs.aggregate(Sum('goals'))['goals__sum'] or 0,
                "assists": perfs.aggregate(Sum('assists'))['assists__sum'] or 0,
                "tackles": perfs.aggregate(Sum('tackles'))['tackles__sum'] or 0,
                "matches": perfs.count(),
            }

            # 2. Performance Trend (Line Chart Data)
            trend_labels = [p.match.opponent[:20] for p in perfs if p.match]
            trend_goals = [p.goals for p in perfs]
            trend_data = {
                "labels": json.dumps(trend_labels),
                "goals": json.dumps(trend_goals),
            }

            # 3. Squad Ranking (Top 5 Scorers)
            squad_stats = (
                PlayerPerformance.objects.values("player__player_name")
                .annotate(total_goals=Sum("goals"))
                .order_by("-total_goals")
            )
            
            rankings = []
            user_rank = 0
            for i, p_stat in enumerate(squad_stats):
                name = p_stat["player__player_name"]
                goals = p_stat["total_goals"] or 0
                if i < 5:
                    rankings.append({"name": name, "goals": goals, "rank": i + 1})
                if name == player.player_name:
                    user_rank = i + 1
            
            # 4. Attendance Summary
            att_qs = TrainingAttendance.objects.filter(player=player)
            total_att = att_qs.count()
            present_att = att_qs.filter(present=True).count()
            attendance_summary = {
                "present": present_att,
                "missed": total_att - present_att,
                "rate": round((present_att / total_att * 100), 1) if total_att > 0 else 0
            }

            # 5. Next Match
            import datetime
            next_match = Match.objects.filter(match_date__gte=datetime.date.today()).order_by('match_date').first()

    except Player.DoesNotExist:
        pass

    return render(request, "core/user_dashboard.html", {
        "display_name": display_name,
        "stats": player_stats,
        "trend": trend_data,
        "rankings": rankings,
        "user_rank": user_rank,
        "attendance": attendance_summary,
        "next_match": next_match,
    })


# ---------------- ANALYTICS ----------------
@login_required
def analytics_page(request):
    # Aggregate goals AND assists AND tackles per match
    matches_qs = (
        PlayerPerformance.objects
        .values("match__id", "match__opponent", "match__match_date")
        .annotate(
            team_goals=Sum("goals"),
            team_assists=Sum("assists"),
            team_tackles=Sum("tackles"),
        )
        .order_by("match__match_date", "match__id")
    )

    labels   = [m["match__opponent"] for m in matches_qs if m["match__opponent"]]
    goals    = [m["team_goals"]   or 0 for m in matches_qs if m["match__opponent"]]
    assists  = [m["team_assists"] or 0 for m in matches_qs if m["match__opponent"]]
    tackles  = [m["team_tackles"] or 0 for m in matches_qs if m["match__opponent"]]

    # Fallback if not enough matches
    if len(labels) < 2:
        performances = PlayerPerformance.objects.all().order_by('id')
        labels  = [f"Match {p.id}" for p in performances]
        goals   = [p.goals for p in performances]
        assists = [p.assists for p in performances]
        tackles = [p.tackles for p in performances]

    total_goals   = sum(goals)
    avg_goals     = round(total_goals / len(goals), 1) if goals else 0
    max_goals     = max(goals) if goals else 0
    best_match    = labels[goals.index(max_goals)] if goals else "N/A"
    total_matches = len(labels)

    return render(request, "core/analytics.html", {
        "labels":        labels,
        "goals":         goals,
        "assists":       assists,
        "tackles":       tackles,
        "total_entries": PlayerPerformance.objects.count(),
        "total_goals":   total_goals,
        "avg_goals":     avg_goals,
        "max_goals":     max_goals,
        "best_match":    best_match,
        "total_matches": total_matches,
    })


# ---------------- SEASON ANALYTICS ----------------
@login_required
def season_analytics(request):
    players = Player.objects.all().prefetch_related('playerperformance_set')
    data = []

    for player in players:
        performances = player.playerperformance_set.all()

        matches = performances.count()
        total_goals = sum(p.goals for p in performances)
        total_assists = sum(p.assists for p in performances)
        total_tackles = sum(p.tackles for p in performances)
        total_shots = sum(p.shots_on_target for p in performances)

        avg_goals = round(total_goals / matches, 2) if matches > 0 else 0
        conversion_rate = round((total_goals / total_shots) * 100, 1) if total_shots > 0 else 0
        goal_involvement = total_goals + total_assists
        
        # Max scale for the radar chart scaling (e.g., max stats across all players or arbitrary max)
        max_stats = 100

        # Heuristic to determine role (1=Attacker, 2=Midfielder, 3=Defender, 4=GK) for sorting purposes
        role_rank = 3
        if total_goals >= 5 or total_shots >= 20:
            role_rank = 1
        elif total_assists >= 5 or (total_goals >= 2 and total_tackles < 120):
            role_rank = 2
            
        if total_goals == 0 and total_assists == 0 and total_tackles <= 30:
            role_rank = 4

        suggestions = []
        if total_goals >= 5:
            suggestions.append("🚀 Excellent scoring form. Keep positioning high in the box.")
        elif total_shots > 10 and total_goals < 3:
            suggestions.append("🎯 Needs finishing practice. High shots but low goal conversion.")
        elif total_tackles >= 10:
            suggestions.append("🛡️ Strong defensive presence. Very reliable at winning the ball back.")
        elif total_assists >= 5:
            suggestions.append("👁️ Great vision and playmaking ability. Key creative outlet.")
        
        if not suggestions:
            suggestions.append("✅ Maintain current training regime and consistent performance.")

        data.append({
            "player": player.player_name,
            "matches": matches,
            "goals": total_goals,
            "assists": total_assists,
            "tackles": total_tackles,
            "shots": total_shots,
            "avg_goals": avg_goals,
            "conversion_rate": conversion_rate,
            "goal_involvement": goal_involvement,
            "role_rank": role_rank,
            "suggestions": suggestions,
            "id": player.id
        })

    display_name = request.user.username.lower()
    for entry in data:
        entry["is_current"] = (entry["player"].lower() == display_name) or (display_name in entry["player"].lower())

    # Sort data to bring current user's player to the top, then by role, then by output
    data.sort(key=lambda x: (
        0 if x["is_current"] else 1, 
        x["role_rank"], 
        -x["goals"], 
        -x["assists"], 
        -x["tackles"]
    ))

    return render(request, "core/season_analytics.html", {
        "analytics_data": data
    })


# ---------------- COMPARE 2 ----------------
@login_required
def compare_page(request):
    players = Player.objects.all().order_by("player_name")
    p1_id = request.GET.get("p1")
    p2_id = request.GET.get("p2")

    p1_data = None
    p2_data = None
    insight = ""

    if p1_id and p2_id:
        try:
            player1 = Player.objects.get(id=p1_id)
            player2 = Player.objects.get(id=p2_id)

            def get_stats(p_obj):
                perfs = PlayerPerformance.objects.filter(player=p_obj)
                return {
                    "goals": sum(p.goals for p in perfs),
                    "assists": sum(p.assists for p in perfs),
                    "tackles": sum(p.tackles for p in perfs),
                    "shots_on_target": sum(p.shots_on_target for p in perfs),
                }

            p1_data = get_stats(player1)
            p2_data = get_stats(player2)

            # Generate Insight
            if p1_data["goals"] > p2_data["goals"]:
                insight = f"{player1.player_name} is more clinical with {p1_data['goals']} goals."
            elif p2_data["goals"] > p1_data["goals"]:
                insight = f"{player2.player_name} is the sharper finisher this season."
            elif p1_data["assists"] > p2_data["assists"]:
                insight = f"{player1.player_name} provides more creative support."
            else:
                insight = "Both players show very similar performance levels."

        except Player.DoesNotExist:
            pass

    return render(request, "core/compare.html", {
        "players": players,
        "p1": p1_data,
        "p2": p2_data,
        "p1_id": p1_id,
        "p2_id": p2_id,
        "insight": insight
    })


# ---------------- COMPARE XI ----------------
@login_required
def compare_xi(request):
    players = Player.objects.all()
    
    selected_player_ids = request.GET.getlist('players')
    
    chart_data = None
    insights = None
    selected_count = 0
    
    if selected_player_ids:
        selected_players = Player.objects.filter(id__in=selected_player_ids)
        selected_count = selected_players.count()
        chart_data = []
        
        top_scorer = None
        max_goals = -1
        
        best_defender = None
        max_tackles = -1
        
        needs_improvement = None
        min_impact = 999999
        
        for player in selected_players:
            performances = PlayerPerformance.objects.filter(player=player)
            goals = sum(p.goals for p in performances)
            assists = sum(p.assists for p in performances)
            tackles = sum(p.tackles for p in performances)
            shots = sum(p.shots_on_target for p in performances)
            
            # Heuristic for sorting positions
            role_rank = 3
            if goals >= 5 or shots >= 20:
                role_rank = 1
            elif assists >= 5 or (goals >= 2 and tackles < 120):
                role_rank = 2
            if goals == 0 and assists == 0 and tackles <= 30:
                role_rank = 4
            
            chart_data.append({
                "name": player.player_name,
                "goals": goals,
                "assists": assists,
                "tackles": tackles,
                "shots": shots,
                "role_rank": role_rank
            })
            
            if goals > max_goals:
                max_goals = goals
                top_scorer = player.player_name
                
            if tackles > max_tackles:
                max_tackles = tackles
                best_defender = player.player_name
                
            impact = goals + assists + tackles
            if impact < min_impact:
                min_impact = impact
                needs_improvement = player.player_name
                
        insights = {
            "top_scorer": f"{top_scorer} ({max_goals} goals)" if top_scorer else "N/A",
            "best_defender": f"{best_defender} ({max_tackles} tackles)" if best_defender else "N/A",
            "needs_improvement": needs_improvement if needs_improvement else "N/A"
        }

        # Sort correctly: Attackers -> Midfielders -> Defenders -> GK
        chart_data.sort(key=lambda x: (
            x["role_rank"], 
            -x["goals"], 
            -x["assists"], 
            -x["tackles"]
        ))

    return render(request, "core/compare_xi.html", {
        "players": players,
        "chart_data": chart_data,
        "insights": insights,
        "selected_count": selected_count
    })

# ---------------- PLAYER ATTENDANCE ----------------
@login_required
def player_attendance(request):
    user = request.user

    player = Player.objects.filter(user=request.user).first()
    if not player:
        # Exact match
        player = Player.objects.filter(player_name__iexact=request.user.username).first()
        
        # Fallback 1: Match by the last part of the username (i.e. last name)
        if not player and " " in request.user.username:
            last_name = request.user.username.split()[-1]
            player = Player.objects.filter(player_name__icontains=last_name).first()
            
        # Fallback 2: Basic 'contains' check
        if not player:
            player = Player.objects.filter(player_name__icontains=request.user.username).first()

        if player and not player.user:
            player.user = user
            player.save()

    if not player:
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

        team_name_input = request.POST.get("team_name", "FC Barcelona").strip()
        if not team_name_input:
            team_name_input = "FC Barcelona"

        default_team, _ = Team.objects.get_or_create(team_name=team_name_input)

        for row in reader:
            try:
                # 🔥 Create match using your model structure
                match, _ = Match.objects.get_or_create(
                    opponent=row.get("match", "Unknown").strip(),
                    defaults={
                        "match_date": date.today(),
                        "venue": "Unknown"
                    }
                )

                player_name_val = row.get("player_name", row.get("player", "")).strip()

                player, _ = Player.objects.get_or_create(
                    player_name=player_name_val,
                    defaults={
                        "team": default_team,
                        "position": "Unknown",
                        "jersey_no": 0
                    }
                )

                PlayerPerformance.objects.create(
                    match=match,
                    player=player,
                    goals=int(row.get("goals", 0)),
                    assists=int(row.get("assists", 0)),
                    shots_on_target=int(row.get("shots_on_target", 0)),
                    tackles=int(row.get("tackles", 0)),
                )

                inserted += 1

            except Exception as e:
                print(f"Skipping row due to error: {e}")
                skipped += 1

        messages.success(request, f"Inserted: {inserted} | Skipped: {skipped}")
        return redirect("dashboard")

    return redirect("dashboard")


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect("login")