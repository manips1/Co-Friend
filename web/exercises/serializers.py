from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserSolvedProblems

class UserSolvedProblemsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserSolvedProblems
        fields = ['user','username','problems', 'solved']



