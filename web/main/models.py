from django.db import models
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User

# 모든 SocialAccount 레코드 가져오기
social_accounts = SocialAccount.objects.all()

