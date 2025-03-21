from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from destinations.models import Location, Like, Review
from destinations.serializers import (
    LocationSerializer, LocationDetailSerializer, 
    LikeSerializer, ReviewSerializer
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render, get_object_or_404
import json
from rest_framework.permissions import AllowAny
from rest_framework import status
import urllib.parse
from django.db import connection
from .nlp_utils import nlp_processor
from .review_utils import find_similar_destinations
from collections import Counter
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.db import models
import time
import random  # 무작위성 추가를 위한 random 모듈 추가
from django.db.models import Count

# ✅ 모든 여행지 목록 조회
class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]  # 🔹 누구나 조회 가능

# ✅ 특정 여행지 상세 조회
class LocationDetailView(generics.RetrieveAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationDetailSerializer
    permission_classes = [AllowAny]  # 🔹 누구나 조회 가능
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@api_view(['GET'])
@permission_classes([AllowAny])
def get_locations(request):
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_location_detail(request, pk):
    try:
        location = Location.objects.get(pk=pk)
        serializer = LocationDetailSerializer(location, context={'request': request})
        return Response(serializer.data)
    except Location.DoesNotExist:
        return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_locations_by_tag(request, tag):
    """
    특정 태그(subcategory0)에 해당하는 여행지 목록을 가져오는 API
    """
    try:
        # URL 디코딩
        decoded_tag = urllib.parse.unquote(tag)
        print(f"태그 검색: {decoded_tag}")
        
        # 정확한 subcategory0 기반으로 여행지 검색
        with connection.cursor() as cursor:
            # 유효한 subcategory0 목록 가져오기
            cursor.execute("""
                SELECT DISTINCT json_extract(subcategories, '$[0]') AS first_subcategory
                FROM destinations_location
                WHERE json_extract(subcategories, '$[0]') IS NOT NULL
                ORDER BY first_subcategory;
            """)
            valid_tags = [row[0] for row in cursor.fetchall() if row[0]]
            
            # 디버깅: 모든 유효한 태그 출력
            print("유효한 태그 목록:")
            for i, vtag in enumerate(valid_tags):
                print(f"{i+1}. {vtag}")
            
            # 태그 이름 정규화 (특수 문자 처리)
            normalized_tag = None
            
            # 정확히 일치하는 태그 찾기
            if decoded_tag in valid_tags:
                normalized_tag = decoded_tag
            else:
                # 대소문자 무시하고 비교
                for valid_tag in valid_tags:
                    if valid_tag.lower() == decoded_tag.lower():
                        normalized_tag = valid_tag
                        break
                
                # 특수 문자 처리하여 비교
                if not normalized_tag:
                    for valid_tag in valid_tags:
                        # '&'와 'and' 변환 비교
                        if valid_tag.replace('&', 'and').lower() == decoded_tag.lower() or \
                           decoded_tag.replace('and', '&').lower() == valid_tag.lower():
                            normalized_tag = valid_tag
                            break
            
            if not normalized_tag:
                print(f"유효하지 않은 태그: {decoded_tag}")
                
                # 가장 유사한 태그 찾기 (부분 일치)
                similar_tags = []
                for valid_tag in valid_tags:
                    if decoded_tag.lower() in valid_tag.lower() or valid_tag.lower() in decoded_tag.lower():
                        similar_tags.append(valid_tag)
                
                if similar_tags:
                    print(f"유사한 태그: {similar_tags}")
                    normalized_tag = similar_tags[0]  # 첫 번째 유사한 태그 사용
                else:
                    return Response({"error": f"유효하지 않은 태그입니다: {decoded_tag}"}, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"정규화된 태그: {normalized_tag}")
            
            # 첫 번째 서브카테고리가 태그와 일치하는 여행지 검색
            cursor.execute("""
                SELECT id, name
                FROM destinations_location
                WHERE json_extract(subcategories, '$[0]') = %s
                LIMIT 20
            """, [normalized_tag])
            
            matching_rows = cursor.fetchall()
            matching_ids = [row[0] for row in matching_rows]
            
            print(f"첫 번째 서브카테고리가 '{normalized_tag}'인 여행지: {len(matching_ids)}개")
            for row in matching_rows[:5]:  # 처음 5개만 출력
                print(f"일치하는 여행지 - ID: {row[0]}, 이름: {row[1]}")
        
        if not matching_ids:
            print(f"태그 '{normalized_tag}'에 해당하는 여행지가 없습니다.")
            return Response({"tag": decoded_tag, "destinations": []}, status=status.HTTP_200_OK)
        
        # 일치하는 여행지 가져오기
        locations = Location.objects.filter(id__in=matching_ids)
        serializer = LocationSerializer(locations, many=True)
        
        return Response({
            "tag": decoded_tag,
            "destinations": serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"태그 검색 중 오류 발생: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_destinations_nlp(request):
    """
    감정 분석과 자연어 처리를 활용한 여행지 검색 API
    
    매개변수:
    - query: 검색어
    - limit: 반환할 결과 개수 (기본값: 20, 최대: 200)
    - retry: 재시도 여부 (True인 경우 캐시를 무시하고 새로 검색)
    """
    try:
        query = request.query_params.get('query', '')
        if not query:
            return Response({"error": "검색어를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 결과 개수 제한 매개변수 처리
        try:
            limit = int(request.query_params.get('limit', 20))
            # 최소 5개, 최대 200개로 제한
            limit = max(5, min(limit, 200))
        except ValueError:
            limit = 20
            
        # 재시도 여부 확인
        retry = request.query_params.get('retry', 'false').lower() == 'true'
        
        print(f"NLP 검색 쿼리: {query}, 결과 제한: {limit}개, 재시도: {retry}")
        
        # 모든 여행지 가져오기
        all_locations = Location.objects.all()
        
        # NLP 검색 수행 (재시도 시 캐시 무시)
        if retry:
            # 캐시 키 생성
            cache_key = f"{query}:{limit}"
            # 캐시에서 해당 키 제거
            from .nlp_utils import search_cache
            if search_cache.get(cache_key):
                search_cache.cache.pop(cache_key, None)
                search_cache.timestamps.pop(cache_key, None)
                print(f"캐시 항목 제거: {cache_key}")
        
        # NLP 검색 수행
        search_results = nlp_processor.search_destinations(query, all_locations, top_n=limit)
        
        # 결과 포맷팅
        formatted_results = []
        for location, similarity in search_results:
            formatted_results.append({
                "id": location.id,
                "name": location.name,
                "description": location.description,
                "category": location.category,
                "subcategories": location.subcategories,
                "subtypes": location.subtypes,
                "image": location.image,
                "city": location.city,
                "country": location.country,
                "similarity_score": float(similarity)  # numpy float를 Python float로 변환
            })
        
        return Response({
            "query": query,
            "limit": limit,
            "results_count": len(formatted_results),
            "results": formatted_results
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"NLP 검색 중 오류 발생: {str(e)}")
        return Response(
            {"error": f"검색 중 오류가 발생했습니다: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# 좋아요 API
class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 이미 좋아요한 경우 409 Conflict 반환
        location = serializer.validated_data['location']
        if Like.objects.filter(user=request.user, location=location).exists():
            return Response(
                {"detail": "이미 좋아요한 여행지입니다."},
                status=status.HTTP_409_CONFLICT
            )
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['delete'])
    def unlike(self, request):
        location_id = request.query_params.get('location_id')
        if not location_id:
            return Response(
                {"detail": "location_id 매개변수가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        like = get_object_or_404(Like, user=request.user, location_id=location_id)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# 리뷰 API
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        print("리뷰 생성 요청 받음:", request.data)
        
        # 요청 데이터 검증
        location_id = request.data.get('location_id')
        rating = request.data.get('rating')
        content = request.data.get('content')
        
        print(f"위치 ID: {location_id}, 평점: {rating}, 내용: {content}")
        
        if not location_id:
            return Response({"error": "location_id는 필수 항목입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not rating or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            return Response({"error": "rating은 1에서 5 사이의 숫자여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not content or not content.strip():
            return Response({"error": "content는 필수 항목입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 이미 리뷰를 작성했는지 확인
        try:
            location = Location.objects.get(id=location_id)
            existing_review = Review.objects.filter(user=request.user, location=location).first()
            
            if existing_review:
                print(f"이미 리뷰가 존재합니다. 리뷰 ID: {existing_review.id}")
                return Response(
                    {"error": "이미 이 여행지에 대한 리뷰를 작성했습니다. 기존 리뷰를 수정해주세요."},
                    status=status.HTTP_409_CONFLICT
                )
        except Location.DoesNotExist:
            return Response({"error": "존재하지 않는 여행지입니다."}, status=status.HTTP_404_NOT_FOUND)
        
        # 리뷰 생성
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            print("리뷰 생성 성공:", serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(f"리뷰 생성 중 오류 발생: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 여행지 추천 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_destinations(request):
    """사용자의 좋아요와 리뷰를 기반으로 여행지를 추천합니다."""
    user = request.user
    limit = int(request.query_params.get('limit', 10))
    
    # 무작위성을 위한 시드 설정 (현재 시간 기반)
    random.seed(time.time())
    
    print(f"사용자 {user.username}의 맞춤 추천 시작 - 타임스탬프: {time.time()}")
    
    # 1. 사용자의 활동 데이터 수집
    likes = Like.objects.filter(user=user)
    reviews = Review.objects.filter(user=user)
    
    likes_count = likes.count()
    reviews_count = reviews.count()
    total_activities = likes_count + reviews_count
    
    print(f"사용자 활동: 좋아요 {likes_count}개, 리뷰 {reviews_count}개")
    
    # 최근 본 여행지 정보 가져오기
    recently_viewed = request.data.get('recently_viewed', [])
    has_recently_viewed = len(recently_viewed) > 0
    
    if has_recently_viewed:
        print(f"최근 본 여행지 수: {len(recently_viewed)}")
    
    # 좋아요한 여행지 ID 출력 (디버깅)
    liked_location_ids = [like.location.id for like in likes]
    print(f"좋아요한 여행지 ID: {liked_location_ids}")
    
    # 2. 활동 데이터 기반 추천 비율 결정 (활동이 많을수록 태그 의존도 감소)
    # 활동이 10개 이상이면 태그 기반 추천은 거의 사용하지 않음
    activity_weight = min(total_activities / 10, 1.0)
    tag_weight = 1.0 - activity_weight
    
    print(f"추천 가중치: 활동 기반 {activity_weight:.2f}, 태그 기반 {tag_weight:.2f}")
    
    results = []
    
    # 3. 태그 기반 추천 (회원가입 시 선택한 태그 기반)
    # 활동이 없는 신규 사용자는 태그 기반 추천을 우선적으로 제공
    if total_activities == 0:
        try:
            selected_tags = user.selected_tags or []
        except:
            selected_tags = []
        
        if selected_tags:
            print(f"신규 사용자의 선택 태그 기반 추천: {selected_tags}")
            
            # 각 태그별로 여행지 검색 및 그룹화
            tag_based_results = []
            tag_groups = {}  # 태그별 여행지 그룹
            
            for tag in selected_tags:
                # 태그에 해당하는 여행지 검색 (정확한 일치 또는 포함 관계)
                # 1. 카테고리가 정확히 일치하는 경우
                exact_matches = Location.objects.filter(category=tag)
                
                # 2. 서브카테고리에 포함된 경우 (JSON 필드 검색)
                # SQLite에서는 JSON 필드 검색이 제한적이므로 Python에서 필터링
                all_locations = Location.objects.all()
                subcategory_matches = []
                
                for loc in all_locations:
                    if loc.subcategories:
                        # 문자열인 경우 리스트로 변환 시도
                        subcats = loc.subcategories
                        if isinstance(subcats, str):
                            try:
                                import json
                                subcats = json.loads(subcats)
                            except:
                                subcats = [subcats]
                        
                        # 리스트가 아닌 경우 리스트로 변환
                        if not isinstance(subcats, list):
                            subcats = [subcats]
                        
                        # 태그가 서브카테고리에 포함되어 있는지 확인
                        if any(tag.lower() in subcat.lower() for subcat in subcats if subcat):
                            subcategory_matches.append(loc)
                
                # 3. 서브타입에 포함된 경우 (JSON 필드 검색)
                subtype_matches = []
                for loc in all_locations:
                    if loc.subtypes:
                        # 문자열인 경우 리스트로 변환 시도
                        subtypes = loc.subtypes
                        if isinstance(subtypes, str):
                            try:
                                import json
                                subtypes = json.loads(subtypes)
                            except:
                                subtypes = [subtypes]
                        
                        # 리스트가 아닌 경우 리스트로 변환
                        if not isinstance(subtypes, list):
                            subtypes = [subtypes]
                        
                        # 태그가 서브타입에 포함되어 있는지 확인
                        if any(tag.lower() in subtype.lower() for subtype in subtypes if subtype):
                            subtype_matches.append(loc)
                
                # 모든 결과 합치기
                tag_locations = list(exact_matches) + subcategory_matches + subtype_matches
                
                # 중복 제거
                tag_locations = list({loc.id: loc for loc in tag_locations}.values())
                
                # 이미 좋아요한 여행지 제외
                liked_ids = [like.location.id for like in likes]
                tag_locations = [loc for loc in tag_locations if loc.id not in liked_ids]
                
                # 결과가 있는 경우에만 태그 그룹 추가
                if tag_locations:
                    # 각 여행지에 유사도 점수 부여 (0.7 고정)
                    tag_group_results = [(loc, 0.7) for loc in tag_locations[:5]]
                    tag_groups[tag] = tag_group_results
                    
                    # 전체 결과 목록에도 추가
                    tag_based_results.extend(tag_group_results)
            
            # 중복 제거
            seen_ids = set()
            unique_tag_results = []
            
            for loc, score in tag_based_results:
                if loc.id not in seen_ids:
                    seen_ids.add(loc.id)
                    unique_tag_results.append((loc, score))
            
            # 태그 기반 추천 결과 추가
            for location, similarity in unique_tag_results[:limit]:
                results.append((location, similarity))
            
            # 태그별 그룹 결과 생성
            tag_group_recommendations = {}
            for tag, group_results in tag_groups.items():
                tag_group_recommendations[tag] = []
                for location, similarity in group_results:
                    tag_group_recommendations[tag].append((location, similarity))
            
            print(f"태그 기반 추천 결과: {len(results)}개, 태그 그룹 수: {len(tag_group_recommendations)}")
    
    # 4. 활동 기반 추천 (좋아요와 리뷰 분석)
    if total_activities > 0:
        # 3.1 좋아요한 여행지 분석
        liked_locations = [like.location for like in likes]
        liked_categories = Counter()
        liked_subcategories = Counter()
        liked_subtypes = Counter()
        liked_countries = Counter()
        liked_cities = Counter()
        
        for loc in liked_locations:
            if loc.category:
                liked_categories[loc.category] += 1
            
            # 서브카테고리 분석
            if loc.subcategories:
                if isinstance(loc.subcategories, list):
                    for subcat in loc.subcategories:
                        liked_subcategories[subcat] += 1
                elif isinstance(loc.subcategories, str):
                    liked_subcategories[loc.subcategories] += 1
            
            # 서브타입 분석
            if loc.subtypes:
                if isinstance(loc.subtypes, list):
                    for subtype in loc.subtypes:
                        liked_subtypes[subtype] += 1
                elif isinstance(loc.subtypes, str):
                    liked_subtypes[loc.subtypes] += 1
            
            if loc.country:
                liked_countries[loc.country] += 1
            if loc.city:
                liked_cities[loc.city] += 1
        
        # 3.2 리뷰 분석
        review_keywords = []
        positive_reviews = []
        negative_reviews = []
        
        # 별점 기반 선호/비선호 여행지 ID 목록
        high_rated_location_ids = []  # 4-5점을 준 여행지 ID
        low_rated_location_ids = []   # 1-2점을 준 여행지 ID
        
        for review in reviews:
            # 키워드 추출
            if review.keywords:
                review_keywords.extend(review.keywords)
            
            # 별점 기반 분류
            if review.rating >= 4:
                high_rated_location_ids.append(review.location.id)
                # 높은 별점의 리뷰는 긍정적인 리뷰로 간주 (감정 분석 결과와 무관하게)
                positive_reviews.append(review)
            elif review.rating <= 2:
                low_rated_location_ids.append(review.location.id)
                negative_reviews.append(review)
            # 별점이 3점인 경우 감정 분석 결과에 따라 분류
            elif review.sentiment == 'POSITIVE':
                positive_reviews.append(review)
        
        print(f"높은 별점(4-5점)을 준 여행지 ID: {high_rated_location_ids}")
        print(f"낮은 별점(1-2점)을 준 여행지 ID: {low_rated_location_ids}")
        
        # 3.3 키워드 빈도 계산
        keyword_counts = Counter(review_keywords)
        top_keywords = [word for word, count in keyword_counts.most_common(10)]
        
        print(f"상위 키워드: {top_keywords}")
        print(f"선호 카테고리: {liked_categories.most_common(3)}")
        print(f"선호 서브카테고리: {liked_subcategories.most_common(5)}")
        print(f"선호 서브타입: {liked_subtypes.most_common(5)}")
        print(f"선호 지역: {liked_countries.most_common(3)}")
        
        # 3.4 활동 기반 추천 여행지 검색
        # 좋아요한 여행지의 특성과 리뷰 키워드를 기반으로 유사한 여행지 검색
        activity_based_results = []
        
        # 3.4.1 키워드 기반 검색
        if top_keywords:
            print(f"Top keywords: {top_keywords}")
            keyword_results = find_similar_destinations(
                top_keywords, 
                user.id, 
                limit=10,
                exclude_location_ids=low_rated_location_ids
            )
            
            # 높은 별점을 받은 여행지와 유사한 여행지의 유사도 점수 증가
            keyword_recommendations = []  # 키워드 기반 추천 결과를 별도로 저장
            for i, (location, similarity) in enumerate(keyword_results):
                for high_rated_loc_id in high_rated_location_ids:
                    try:
                        high_rated_loc = Location.objects.get(id=high_rated_loc_id)
                        
                        # 공통 요소가 있는지 확인하는 함수
                        def has_common_elements(list1, list2):
                            if not list1 or not list2:
                                return False
                            
                            # 문자열이면 리스트로 변환
                            if isinstance(list1, str):
                                try:
                                    import json
                                    list1 = json.loads(list1)
                                except:
                                    list1 = [list1]
                            
                            if isinstance(list2, str):
                                try:
                                    import json
                                    list2 = json.loads(list2)
                                except:
                                    list2 = [list2]
                            
                            # 리스트가 아니면 리스트로 변환
                            if not isinstance(list1, list):
                                list1 = [list1]
                            
                            if not isinstance(list2, list):
                                list2 = [list2]
                            
                            # 공통 요소 확인
                            return any(item in list2 for item in list1)
                        
                        # 서브카테고리 또는 서브타입 중 공통 요소가 있으면 유사도 증가
                        if (has_common_elements(location.subcategories, high_rated_loc.subcategories) or
                            has_common_elements(location.subtypes, high_rated_loc.subtypes)):
                            # 유사도 점수 증가 (최대 0.95까지)
                            new_similarity = min(similarity + 0.2, 0.95)
                            keyword_results[i] = (location, new_similarity)
                            print(f"Increased similarity for {location.name} from {similarity} to {new_similarity}")
                            break
                    except Location.DoesNotExist:
                        continue
            
            # 키워드 기반 추천 결과를 활동 기반 결과 목록에 추가
            for location, similarity in keyword_results:
                # 대신 activity_based_results에 추가
                activity_based_results.append((location, similarity))
                keyword_recommendations.append((location, similarity))  # 키워드 기반 추천 결과 별도 저장
                print(f"키워드 기반 추천: {location.name}, 유사도: {similarity:.2f}")
        
        # 3.4.2 서브카테고리 기반 검색
        if liked_subcategories:
            top_subcategories = [subcat for subcat, _ in liked_subcategories.most_common(5)]
            print(f"상위 서브카테고리: {top_subcategories}")
            
            # JSON 필드 검색을 위한 쿼리 구성
            subcategory_locations = []
            
            # 데이터베이스 호환성 문제로 인해 모든 여행지를 가져와서 Python에서 필터링
            all_locations = Location.objects.all()
            
            for loc in all_locations:
                if loc.subcategories:
                    # 문자열인 경우 리스트로 변환
                    loc_subcats = loc.subcategories
                    if isinstance(loc_subcats, str):
                        try:
                            import json
                            loc_subcats = json.loads(loc_subcats)
                        except:
                            loc_subcats = [loc_subcats]
                    
                    # 리스트가 아닌 경우 리스트로 변환
                    if not isinstance(loc_subcats, list):
                        loc_subcats = [loc_subcats]
                    
                    # 서브카테고리 일치 여부 확인
                    for subcat in top_subcategories:
                        if subcat in loc_subcats:
                            subcategory_locations.append(loc)
                            break
            
            # 중복 제거
            subcategory_locations = list({loc.id: loc for loc in subcategory_locations}.values())
            
            # 이미 좋아요한 여행지 제외
            liked_ids = [loc.id for loc in liked_locations]
            subcategory_locations = [loc for loc in subcategory_locations if loc.id not in liked_ids]
            
            print(f"서브카테고리 기반 추천 여행지 수: {len(subcategory_locations)}")
            
            # 무작위로 섞어서 다양한 추천 결과 제공
            random.shuffle(subcategory_locations)
            
            # 상위 결과만 선택 (유사도 점수 다양화)
            subcategory_results = []
            for i, loc in enumerate(subcategory_locations[:limit]):
                # 유사도 점수 - 무작위성 제거
                base_similarity = 0.75 + (i % 4) * 0.05
                similarity = base_similarity
                
                subcategory_results.append((loc, similarity))
                print(f"서브카테고리 기반 추천: {loc.name}, 유사도: {similarity:.2f}")
            
            activity_based_results.extend(subcategory_results)
        
        # 3.4.3 서브타입 기반 검색
        if liked_subtypes:
            top_subtypes = [subtype for subtype, _ in liked_subtypes.most_common(5)]
            print(f"상위 서브타입: {top_subtypes}")
            
            # JSON 필드 검색을 위한 쿼리 구성
            subtype_locations = []
            
            # 데이터베이스 호환성 문제로 인해 모든 여행지를 가져와서 Python에서 필터링
            all_locations = Location.objects.all()
            
            for loc in all_locations:
                if loc.subtypes:
                    # 문자열인 경우 리스트로 변환
                    loc_subtypes = loc.subtypes
                    if isinstance(loc_subtypes, str):
                        try:
                            import json
                            loc_subtypes = json.loads(loc_subtypes)
                        except:
                            loc_subtypes = [loc_subtypes]
                    
                    # 리스트가 아닌 경우 리스트로 변환
                    if not isinstance(loc_subtypes, list):
                        loc_subtypes = [loc_subtypes]
                    
                    # 서브타입 일치 여부 확인
                    for subtype in top_subtypes:
                        # 정확한 일치 또는 부분 일치(포함) 확인
                        if subtype in loc_subtypes or any(subtype.lower() in st.lower() for st in loc_subtypes):
                            subtype_locations.append(loc)
                            break
            
            # 중복 제거
            subtype_locations = list({loc.id: loc for loc in subtype_locations}.values())
            
            # 이미 좋아요한 여행지와 서브카테고리 결과에 포함된 여행지 제외
            liked_ids = [loc.id for loc in liked_locations]
            subcategory_ids = [loc[0].id for loc in subcategory_results]
            subtype_locations = [loc for loc in subtype_locations if loc.id not in liked_ids and loc.id not in subcategory_ids]
            
            print(f"서브타입 기반 추천 여행지 수: {len(subtype_locations)}")
            
            # 무작위로 섞어서 다양한 추천 결과 제공
            random.shuffle(subtype_locations)
            
            # 상위 결과만 선택 (유사도 점수 다양화)
            subtype_results = []
            for i, loc in enumerate(subtype_locations[:limit]):
                # 유사도 점수 - 무작위성 제거
                base_similarity = 0.7 + (i % 4) * 0.05
                similarity = base_similarity
                
                subtype_results.append((loc, similarity))
                print(f"서브타입 기반 추천: {loc.name}, 유사도: {similarity:.2f}")
            
            activity_based_results.extend(subtype_results)
        
        # 3.4.4 국가 기반 검색
        if liked_countries:
            top_countries = [country for country, _ in liked_countries.most_common(3)]
            print(f"상위 국가: {top_countries}")
            
            country_locations = Location.objects.filter(country__in=top_countries)
            
            # 이미 좋아요한 여행지와 서브카테고리/서브타입 결과에 포함된 여행지 제외
            liked_ids = [loc.id for loc in liked_locations]
            
            # 이전 결과에서 제외할 ID 목록 생성 (변수가 정의되지 않은 경우 빈 리스트 사용)
            previous_results_ids = []
            if 'subcategory_results' in locals() and subcategory_results:
                previous_results_ids.extend([loc[0].id for loc in subcategory_results])
            if 'subtype_results' in locals() and subtype_results:
                previous_results_ids.extend([loc[0].id for loc in subtype_results])
                
            country_locations = country_locations.exclude(id__in=liked_ids + previous_results_ids)
            
            # 리스트로 변환하여 무작위로 섞기
            country_locations_list = list(country_locations)
            random.shuffle(country_locations_list)
            
            print(f"국가 기반 추천 여행지 수: {len(country_locations_list)}")
            
            # 상위 결과만 선택 (유사도 점수 다양화)
            country_results = []
            for i, loc in enumerate(country_locations_list[:limit]):
                # 유사도 점수 - 무작위성 제거
                base_similarity = 0.65 + (i % 4) * 0.05
                similarity = base_similarity
                
                country_results.append((loc, similarity))
                print(f"국가 기반 추천: {loc.name}, 유사도: {similarity:.2f}")
            
            activity_based_results.extend(country_results)
        
        # 중복 제거 및 정렬
        seen_ids = set()
        unique_activity_results = []
        
        for loc, score in activity_based_results:
            if loc.id not in seen_ids:
                seen_ids.add(loc.id)
                unique_activity_results.append((loc, score))
        
        # 점수 기준 정렬
        unique_activity_results.sort(key=lambda x: x[1], reverse=True)
        
        # 활동 기반 추천 결과 저장
        for location, similarity in unique_activity_results[:limit]:
            results.append((location, similarity))
    
    # 5. 태그 기반 추천 (기존 태그 선택 기반) - 활동이 있는 사용자를 위한 보조 추천
    if tag_weight > 0.1 and len(results) < limit and total_activities > 0:
        # 사용자 프로필에서 선택한 태그 가져오기
        try:
            selected_tags = user.selected_tags or []
        except:
            selected_tags = []
        
        if selected_tags:
            print(f"사용자 선택 태그: {selected_tags}")
            
            # 각 태그별로 여행지 검색
            tag_based_results = []
            
            for tag in selected_tags:
                # 태그에 해당하는 여행지 검색
                tag_locations = Location.objects.filter(category=tag)
                
                # 이미 좋아요한 여행지 제외
                liked_ids = [like.location.id for like in likes]
                tag_locations = tag_locations.exclude(id__in=liked_ids)
                
                # 결과 추가 (상위 5개만)
                for loc in tag_locations[:5]:
                    tag_based_results.append((loc, 0.6))  # 태그 기반은 낮은 유사도 점수 부여
            
            # 중복 제거
            seen_ids = set(item["id"] for item in results)
            unique_tag_results = []
            
            for loc, score in tag_based_results:
                if loc.id not in seen_ids:
                    seen_ids.add(loc.id)
                    unique_tag_results.append((loc, score))
            
            # 태그 기반 추천 결과 추가
            remaining_slots = limit - len(results)
            for location, similarity in unique_tag_results[:remaining_slots]:
                results.append((location, similarity))
    
    # 6. 결과가 부족한 경우 인기 여행지로 채우기
    if len(results) < limit:
        print("추천 결과가 부족하여 인기 여행지로 보충합니다")
        
        # 인기 여행지 (좋아요가 많은 순)
        popular_locations = Location.objects.annotate(
            total_likes=models.Count('likes')
        ).order_by('-total_likes')
        
        # 이미 추천된 여행지 제외
        seen_ids = set(item["id"] for item in results)
        popular_locations = popular_locations.exclude(id__in=seen_ids)
        
        # 이미 좋아요한 여행지 제외
        liked_ids = [like.location.id for like in likes]
        popular_locations = popular_locations.exclude(id__in=liked_ids)
        
        # 인기 여행지 추가
        remaining_slots = limit - len(results)
        for location in popular_locations[:remaining_slots]:
            results.append((location, 0.5))  # 인기 여행지는 중간 유사도 점수 부여
    
    # 7. 서브타입 기반 추천 결과 별도 저장
    subtype_recommendations = []
    if 'subtype_results' in locals() and subtype_results:
        for location, similarity in subtype_results[:limit]:
            subtype_recommendations.append((location, similarity))
    
    # 8. 국가 기반 추천 결과 별도 저장
    country_recommendations = []
    if 'country_results' in locals() and country_results:
        for location, similarity in country_results[:limit]:
            country_recommendations.append((location, similarity))
    
    # 9. 서브카테고리 기반 추천 결과 별도 저장
    subcategory_recommendations = []
    if 'subcategory_results' in locals() and subcategory_results:
        for location, similarity in subcategory_results[:limit]:
            subcategory_recommendations.append((location, similarity))
            
    # 10. 최근 본 여행지 기반 추천 결과
    recently_viewed_recommendations = []
    
    if has_recently_viewed:
        # 최근 본 여행지의 국가, 서브카테고리, 서브타입 수집
        rv_countries = []
        rv_subcategories = []
        rv_subtypes = []
        
        for item in recently_viewed:
            if item.get('country'):
                rv_countries.append(item.get('country'))
            
            if item.get('subcategories'):
                subcats = item.get('subcategories')
                if isinstance(subcats, list):
                    rv_subcategories.extend(subcats)
                else:
                    rv_subcategories.append(subcats)
            
            if item.get('subtypes'):
                subtypes = item.get('subtypes')
                if isinstance(subtypes, list):
                    rv_subtypes.extend(subtypes)
                else:
                    rv_subtypes.append(subtypes)
        
        # 중복 제거
        rv_countries = list(set(rv_countries))
        rv_subcategories = list(set(rv_subcategories))
        rv_subtypes = list(set(rv_subtypes))
        
        print(f"최근 본 여행지 국가: {rv_countries}")
        print(f"최근 본 여행지 서브카테고리: {rv_subcategories}")
        print(f"최근 본 여행지 서브타입: {rv_subtypes}")
        
        # 최근 본 여행지와 유사한 여행지 찾기
        recently_viewed_locations = []
        
        # 데이터베이스 호환성 문제로 인해 모든 여행지를 가져와서 Python에서 필터링
        all_locations = Location.objects.all()
        
        for loc in all_locations:
            # 이미 좋아요한 여행지나 최근 본 여행지는 제외
            if loc.id in liked_location_ids or any(rv['id'] == loc.id for rv in recently_viewed):
                continue
                
            match_score = 0  # 유사도 점수
            
            # 1. 국가 일치 여부 확인
            if loc.country and loc.country in rv_countries:
                match_score += 0.3
            
            # 2. 서브카테고리 일치 여부 확인
            if loc.subcategories:
                loc_subcats = loc.subcategories
                if isinstance(loc_subcats, str):
                    try:
                        import json
                        loc_subcats = json.loads(loc_subcats)
                    except:
                        loc_subcats = [loc_subcats]
                
                if not isinstance(loc_subcats, list):
                    loc_subcats = [loc_subcats]
                
                for subcat in rv_subcategories:
                    if any(subcat.lower() in sc.lower() for sc in loc_subcats):
                        match_score += 0.2
                        break
            
            # 3. 서브타입 일치 여부 확인
            if loc.subtypes:
                loc_subtypes = loc.subtypes
                if isinstance(loc_subtypes, str):
                    try:
                        import json
                        loc_subtypes = json.loads(loc_subtypes)
                    except:
                        loc_subtypes = [loc_subtypes]
                
                if not isinstance(loc_subtypes, list):
                    loc_subtypes = [loc_subtypes]
                
                for subtype in rv_subtypes:
                    if any(subtype.lower() in st.lower() for st in loc_subtypes):
                        match_score += 0.2
                        break
            
            # 유사도 점수가 0.2 이상인 경우만 추가 (최소 하나 이상 일치)
            if match_score >= 0.2:
                # 유사도 점수 최대 0.7로 제한 (너무 높지 않게 설정)
                match_score = min(match_score, 0.7)
                recently_viewed_locations.append((loc, match_score))
        
        # 유사도 점수 기준으로 정렬
        recently_viewed_locations.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 결과 선택
        recently_viewed_recommendations = recently_viewed_locations[:limit]
        
        print(f"최근 본 여행지 기반 추천 수: {len(recently_viewed_recommendations)}")
    
    print(f"최종 추천 결과: {len(results)}개")
    
    # Location 객체를 JSON 직렬화 가능한 딕셔너리로 변환하는 함수
    def location_to_dict(location, similarity, recommendation_type="general"):
        return {
            "id": location.id,
            "name": location.name,
            "description": location.description,
            "subcategories": location.subcategories,
            "subtypes": location.subtypes,
            "image": location.image,
            "city": location.city,
            "country": location.country,
            "similarity_score": float(similarity),
            "recommendation_type": recommendation_type
        }
    
    # 결과를 JSON 직렬화 가능한 형태로 변환
    serialized_results = []
    for location, similarity in results:
        # 추천 유형 결정 (간단한 추정)
        recommendation_type = "general"
        serialized_results.append(location_to_dict(location, similarity, recommendation_type))
    
    # 태그 그룹 추천 결과 직렬화
    serialized_tag_groups = {}
    if 'tag_group_recommendations' in locals() and tag_group_recommendations:
        for tag, recommendations in tag_group_recommendations.items():
            serialized_tag_groups[tag] = []
            for location, similarity in recommendations:
                serialized_tag_groups[tag].append(location_to_dict(location, similarity, "tag"))
    
    # 서브카테고리 추천 직렬화
    serialized_subcategory_recommendations = []
    for location, similarity in subcategory_recommendations:
        serialized_subcategory_recommendations.append(location_to_dict(location, similarity, "subcategory"))
    
    # 서브타입 추천 직렬화
    serialized_subtype_recommendations = []
    for location, similarity in subtype_recommendations:
        serialized_subtype_recommendations.append(location_to_dict(location, similarity, "subtype"))
    
    # 국가 추천 직렬화
    serialized_country_recommendations = []
    for location, similarity in country_recommendations:
        serialized_country_recommendations.append(location_to_dict(location, similarity, "country"))
    
    # 키워드 기반 추천 직렬화
    serialized_keyword_recommendations = []
    if 'keyword_recommendations' in locals() and keyword_recommendations:
        for location, similarity in keyword_recommendations:
            serialized_keyword_recommendations.append(location_to_dict(location, similarity, "keyword"))
    
    # 최근 본 여행지 기반 추천 직렬화
    serialized_recently_viewed_recommendations = []
    for location, similarity in recently_viewed_recommendations:
        serialized_recently_viewed_recommendations.append(location_to_dict(location, similarity, "recently_viewed"))
    
    return Response({
        "activity_weight": activity_weight,
        "tag_weight": tag_weight,
        "results": serialized_results,
        "keyword_recommendations": serialized_keyword_recommendations,
        "subcategory_recommendations": serialized_subcategory_recommendations,
        "subtype_recommendations": serialized_subtype_recommendations,
        "country_recommendations": serialized_country_recommendations,
        "recently_viewed_recommendations": serialized_recently_viewed_recommendations,
        "tag_group_recommendations": serialized_tag_groups
    }, status=status.HTTP_200_OK)

# 사용자의 좋아요 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_likes(request):
    """사용자가 좋아요한 여행지 목록을 반환합니다."""
    likes = Like.objects.filter(user=request.user).select_related('location')
    
    # 결과 포맷팅
    results = []
    for like in likes:
        results.append({
            "id": like.id,
            "location": LocationSerializer(like.location).data,
            "created_at": like.created_at
        })
    
    return Response({
        "count": len(results),
        "results": results
    })

# 사용자의 리뷰 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reviews(request):
    """사용자가 작성한 리뷰 목록을 반환합니다."""
    reviews = Review.objects.filter(user=request.user).select_related('location')
    
    # 결과 포맷팅
    results = []
    for review in reviews:
        results.append({
            "id": review.id,
            "location": LocationSerializer(review.location).data,
            "content": review.content,
            "rating": review.rating,
            "sentiment": review.sentiment,
            "keywords": review.keywords,
            "created_at": review.created_at,
            "updated_at": review.updated_at
        })
    
    return Response({
        "count": len(results),
        "results": results
    })

# 여행지의 리뷰 목록 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def location_reviews(request, location_id):
    """특정 여행지의 리뷰 목록을 반환합니다."""
    reviews = Review.objects.filter(location_id=location_id)
    serializer = ReviewSerializer(reviews, many=True)
    
    return Response({
        "count": reviews.count(),
        "results": serializer.data
    })

class UserReviewsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        reviews = Review.objects.filter(user=request.user).order_by('-created_at')
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(reviews, request)
        
        serializer = ReviewSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class UserLikesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        likes = Like.objects.filter(user=request.user).select_related('location').order_by('-created_at')
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(likes, request)
        
        # 결과 포맷팅
        results = []
        for like in result_page:
            results.append({
                "id": like.id,
                "location": LocationSerializer(like.location).data,
                "created_at": like.created_at
            })
        
        return paginator.get_paginated_response(results)

@api_view(['GET'])
@permission_classes([AllowAny])
def most_loved_locations(request):
    """
    가장 좋아요를 많이 받은 여행지 10개를 반환합니다.
    """
    # 좋아요 수를 기준으로 여행지를 정렬하고 상위 10개를 선택
    # Location 모델에 이미 likes_count 필드가 있으므로 직접 사용
    locations = Location.objects.order_by('-likes_count')[:10]
    
    # 각 여행지에 대한 추가 정보 계산
    result = []
    for location in locations:
        # 평균 평점 계산
        reviews = location.reviews.all()
        average_rating = None
        if reviews.exists():
            average_rating = sum(review.rating for review in reviews) / reviews.count()
        
        # 위치 정보 생성
        location_data = LocationSerializer(location).data
        location_data['average_rating'] = average_rating
        
        result.append(location_data)
    
    return Response(result)
