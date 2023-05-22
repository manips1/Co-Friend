from django.contrib.auth.models import User
from django.db import models

class UserSolvedProblems(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    problems = models.CharField(max_length=255)
    solved = models.IntegerField()

    def __str__(self):
        return f"User: {self.user.username}, Problems: {self.problems}, Solved: {self.solved}"
