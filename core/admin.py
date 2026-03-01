from django.contrib import admin
from .models import (
    Team,
    Player,
    Match,
    PlayerPerformance,
    TrainingSession,
    TrainingAttendance,
    MatchAttendance,
)

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(PlayerPerformance)
admin.site.register(TrainingSession)
admin.site.register(TrainingAttendance)
admin.site.register(MatchAttendance)
