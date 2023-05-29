from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserSolvedProblems

class UserSolvedProblemsSerializer(serializers.ModelSerializer):
    user = serializers.CharField(required=False)
    problems = serializers.CharField(required=False)
    solved = serializers.CharField(required=False)

    class Meta:
        model = UserSolvedProblems
        fields = ['user','problems', 'solved']



