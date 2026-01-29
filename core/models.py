from django.db import models

class Team(models.Model):
    team_name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.team_name


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    player_name = models.CharField(max_length=150)
    position = models.CharField(max_length=50)  # Striker/Midfielder/Defender/GK
    jersey_no = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.player_name} ({self.team.team_name})"


class Match(models.Model):
    match_date = models.DateField()
    opponent = models.CharField(max_length=150)
    venue = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.match_date} vs {self.opponent}"


class PlayerPerformance(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="performances")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="performances")

    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    shots_on_target = models.PositiveIntegerField(default=0)
    pass_accuracy = models.FloatField(default=0.0)  # %
    tackles = models.PositiveIntegerField(default=0)
    saves = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.player.player_name} - {self.match}"
