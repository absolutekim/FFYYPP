import re
from collections import Counter
from .nlp_utils import nlp_processor

def analyze_review(review_text):
    """
    리뷰 텍스트를 분석하여 감정과 키워드를 추출합니다.
    
    Args:
        review_text: 분석할 리뷰 텍스트
        
    Returns:
        dict: 감정 분석 결과와 키워드를 포함한 딕셔너리
    """
    # 감정 분석
    sentiment, confidence = nlp_processor.analyze_sentiment(review_text)
    
    # 키워드 추출
    keywords = extract_keywords(review_text)
    
    return {
        'sentiment': sentiment,
        'sentiment_score': float(confidence),
        'keywords': keywords
    }

def extract_keywords(text, top_n=5):
    """
    텍스트에서 중요한 키워드를 추출합니다.
    
    Args:
        text: 키워드를 추출할 텍스트
        top_n: 반환할 키워드 수
        
    Returns:
        list: 중요도 순으로 정렬된 키워드 목록
    """
    # 텍스트 전처리
    tokens = nlp_processor.preprocess_text(text)
    
    # 불용어 제거 및 단어 빈도 계산
    word_counts = Counter(tokens)
    
    # 중요 키워드 선택 (빈도 기준)
    keywords = [word for word, count in word_counts.most_common(top_n)]
    
    return keywords

def find_similar_destinations(keywords, user_id, limit=10, exclude_location_ids=None):
    """
    키워드를 기반으로 유사한 여행지를 찾습니다.
    
    Args:
        keywords: 검색할 키워드 목록
        user_id: 사용자 ID (이미 방문한 여행지 제외용)
        limit: 반환할 여행지 수
        exclude_location_ids: 제외할 여행지 ID 목록 (낮은 별점을 준 여행지와 유사한 여행지 제외용)
        
    Returns:
        list: 유사한 여행지 목록
    """
    from .models import Location, Like, Review
    
    # 키워드가 없으면 빈 목록 반환
    if not keywords:
        return []
    
    # 키워드를 공백으로 구분된 문자열로 변환
    query = ' '.join(keywords)
    
    # 모든 여행지 가져오기
    all_locations = Location.objects.all()
    
    # 사용자가 이미 좋아요한 여행지 ID 목록
    liked_location_ids = Like.objects.filter(user_id=user_id).values_list('location_id', flat=True)
    
    # 제외할 여행지 ID 목록이 None이면 빈 리스트로 초기화
    if exclude_location_ids is None:
        exclude_location_ids = []
    
    # NLP 검색 수행
    search_results = nlp_processor.search_destinations(query, all_locations, top_n=limit+len(liked_location_ids)+len(exclude_location_ids))
    
    # 이미 좋아요한 여행지와 제외할 여행지 제외
    filtered_results = []
    for loc, similarity in search_results:
        if loc.id not in liked_location_ids and loc.id not in exclude_location_ids:
            filtered_results.append((loc, similarity))
            
    return filtered_results[:limit] 