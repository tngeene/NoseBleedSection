from django.db import models


# This class will store team logos in the database
class TeamLogo(models.Model):
    team_id = models.CharField(unique=True, max_length=50)
    team_name = models.CharField(max_length=50)
    logo_url = models.URLField()

    def __str__(self):
        return f'{self.team_name}'
