from django.contrib import admin
from .models import Team, Player, Match, PlayerPerformance, Attendance


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("team_name",)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("player_name", "team", "position", "jersey_no")
    list_filter = ("team", "position")
    search_fields = ("player_name",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("match_date", "opponent", "venue")


@admin.register(PlayerPerformance)
class PlayerPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "player",
        "match",
        "goals",
        "assists",
        "tackles",
        "shots_on_target",
    )
    list_filter = ("match", "player")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("player", "date", "present")
    list_filter = ("date", "present")
    search_fields = ("player__player_name",)
