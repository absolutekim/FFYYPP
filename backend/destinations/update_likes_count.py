"""
이 스크립트는 기존 좋아요 데이터를 기반으로 Location 모델의 likes_count 필드를 업데이트합니다.
Django 쉘에서 실행하세요:
python manage.py shell < destinations/update_likes_count.py
"""

from django.db.models import Count
from destinations.models import Location

def update_likes_count():
    print("좋아요 수 업데이트를 시작합니다...")
    
    # 각 여행지의 좋아요 수를 계산
    locations_with_counts = Location.objects.annotate(count=Count('likes'))
    
    # 업데이트 카운터
    updated = 0
    
    # 각 여행지의 likes_count 필드 업데이트
    for location in locations_with_counts:
        location.likes_count = location.count
        location.save(update_fields=['likes_count'])
        updated += 1
        
        # 진행 상황 출력 (100개마다)
        if updated % 100 == 0:
            print(f"{updated}개의 여행지 업데이트 완료...")
    
    print(f"총 {updated}개의 여행지의 좋아요 수가 업데이트되었습니다.")

if __name__ == "__main__":
    update_likes_count() 