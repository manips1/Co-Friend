from allauth.socialaccount.models import SocialAccount

# 모든 SocialAccount 레코드 가져오기
social_accounts = SocialAccount.objects.all()

# SocialAccount 레코드를 순회하며 원하는 정보에 접근
for account in social_accounts:
    provider = account.provider  # 소셜 계정 공급자 (예: 'google')
    uid = account.uid  # 소셜 계정의 고유 식별자
    user = account.user  # 소셜 계정에 연결된 사용자
    # 추가적인 필드들도 여기서 접근할 수 있습니다.
    
    # 원하는 작업 수행
    print(f"Provider: {provider}, UID: {uid}, User: {user}")
