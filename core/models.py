from django.db import models
from django.contrib.auth.models import User

# ---------------- TEAM ----------------
class Team(models.Model):
    team_name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.team_name


# ---------------- PLAYER ----------------
class Player(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    player_name = models.CharField(max_length=150)
    position = models.CharField(max_length=50)
    jersey_no = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.player_name} ({self.team.team_name})"


# ---------------- MATCH ----------------
class Match(models.Model):
    match_date = models.DateField()
    opponent = models.CharField(max_length=150)
    venue = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.match_date} vs {self.opponent}"


# ---------------- PLAYER PERFORMANCE ----------------
class PlayerPerformance(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    shots_on_target = models.PositiveIntegerField(default=0)
    tackles = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.player.player_name} - {self.match}"


# ================= TRAINING =================
class TrainingSession(models.Model):
    date = models.DateField()
    training_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.date} - {self.training_type}"


class TrainingAttendance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    training = models.ForeignKey(TrainingSession, on_delete=models.CASCADE)
    present = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.player} - {self.training}"


# ================= MATCH ATTENDANCE =================
class MatchAttendance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[("Played", "Played"), ("Benched", "Benched"), ("Absent", "Absent")]
    )

    def __str__(self):
        return f"{self.player} - {self.match} - {self.status}"
