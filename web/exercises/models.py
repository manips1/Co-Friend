from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserSolvedProblems(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    problems = models.CharField(max_length=255)
    solved = models.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.problems:
            self.problems = '0'
        if not self.solved:
            self.solved = 0

    def __str__(self):
        return f"User: {self.user.username}, Problems: {self.problems}, Solved: {self.solved}"


@receiver(post_save, sender=User)
def create_user_solved_problems(sender, instance, created, **kwargs):
    if created:
        UserSolvedProblems.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_solved_problems(sender, instance, **kwargs):
    instance.usersolvedproblems.save()