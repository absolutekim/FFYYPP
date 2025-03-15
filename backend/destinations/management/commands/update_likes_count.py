from django.core.management.base import BaseCommand
from django.db.models import Count
from destinations.models import Location

class Command(BaseCommand):
    help = '기존 좋아요 데이터를 기반으로 Location 모델의 likes_count 필드를 업데이트합니다.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('좋아요 수 업데이트를 시작합니다...'))
        
        # 모든 여행지의 likes_count를 0으로 초기화
        Location.objects.all().update(likes_count=0)
        self.stdout.write('모든 여행지의 likes_count를 0으로 초기화했습니다.')
        
        # 각 여행지의 좋아요 수를 계산
        locations_with_counts = Location.objects.annotate(count=Count('likes'))
        
        # 업데이트 카운터
        updated = 0
        
        # 각 여행지의 likes_count 필드 업데이트
        for location in locations_with_counts:
            # 이상치 확인 및 로깅
            if location.count > 100:  # 100개 이상의 좋아요는 의심스러움
                self.stdout.write(self.style.WARNING(
                    f'주의: {location.name}(ID: {location.id})의 좋아요 수가 비정상적으로 많습니다: {location.count}'
                ))
            
            location.likes_count = location.count
            location.save(update_fields=['likes_count'])
            updated += 1
            
            # 진행 상황 출력 (100개마다)
            if updated % 100 == 0:
                self.stdout.write(f"{updated}개의 여행지 업데이트 완료...")
        
        self.stdout.write(self.style.SUCCESS(f"총 {updated}개의 여행지의 좋아요 수가 업데이트되었습니다.")) 