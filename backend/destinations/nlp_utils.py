import os
import re
from collections import Counter
import time
import functools

# 라이브러리 가용성 확인
NLP_ADVANCED = False
try:
    from transformers import pipeline
    import torch
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    from sentence_transformers import SentenceTransformer, util
    NLP_ADVANCED = True
    print("고급 NLP 기능이 활성화되었습니다.")
except ImportError:
    print("고급 NLP 라이브러리가 설치되지 않았습니다. 기본 검색 기능만 사용 가능합니다.")

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    
    # NLTK 데이터 다운로드 (처음 실행 시 필요)
    nltk_resources = ['punkt', 'stopwords']
    for resource in nltk_resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            print(f"NLTK {resource} 다운로드 중...")
            nltk.download(resource)
    
    # 추가 리소스 다운로드
    try:
        nltk.download('punkt')
    except:
        pass
    
    NLTK_AVAILABLE = True
    print("NLTK 기능이 활성화되었습니다.")
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK 라이브러리가 설치되지 않았습니다. 기본 토큰화 기능을 사용합니다.")

# 모델 캐싱 디렉토리 설정
os.environ['TRANSFORMERS_CACHE'] = './models/transformers_cache'
os.environ['TORCH_HOME'] = './models/torch_cache'

# 간단한 LRU 캐시 구현
class LRUCache:
    def __init__(self, capacity=100):
        self.cache = {}
        self.capacity = capacity
        self.timestamps = {}
    
    def get(self, key):
        if key in self.cache:
            self.timestamps[key] = time.time()
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if len(self.cache) >= self.capacity:
            # 가장 오래된 항목 제거
            oldest_key = min(self.timestamps, key=self.timestamps.get)
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = time.time()

# 검색 결과 캐시
search_cache = LRUCache(capacity=500)

class NLPProcessor:
    def __init__(self):
        # 감정 분석 모델 초기화
        self.sentiment_analyzer = None
        
        # 문장 임베딩 모델 초기화
        self.sentence_model = None
        
        # 불용어 설정
        self.stop_words = set(['a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what', 
                              'when', 'where', 'how', 'all', 'with', 'for', 'in', 'to', 'at', 'by', 
                              'from', 'on', 'off']) if not NLTK_AVAILABLE else set(stopwords.words('english'))
        
        # 모델 로드 플래그
        self.models_loaded = False
        
        # 임베딩 캐시
        self.embedding_cache = {}
        
        # 감정 분석 캐시
        self.sentiment_cache = {}
        
        # 성능 최적화를 위한 설정
        self.use_lightweight_model = True
    
    def load_models(self):
        """모델을 로드합니다. 처음 사용할 때만 호출됩니다."""
        if self.models_loaded or not NLP_ADVANCED:
            return
        
        print("NLP 모델 로딩 중...")
        start_time = time.time()
        
        # 감정 분석 모델 로드 - 모델 명시적 지정
        self.sentiment_analyzer = pipeline(
            'sentiment-analysis',
            model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
            revision="714eb0f"
        )
        
        # 문장 임베딩 모델 로드 (경량 다국어 지원 모델)
        if self.use_lightweight_model:
            # 더 가벼운 모델 사용
            model_name = "sentence-transformers/paraphrase-MiniLM-L3-v2"
        else:
            model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            
        self.sentence_model = SentenceTransformer(model_name)
        
        self.models_loaded = True
        print(f"NLP 모델 로딩 완료! (소요 시간: {time.time() - start_time:.2f}초)")
    
    def analyze_sentiment(self, text):
        """텍스트의 감정을 분석합니다."""
        # 캐시 확인
        if text in self.sentiment_cache:
            return self.sentiment_cache[text]
            
        if not NLP_ADVANCED:
            # 간단한 감정 분석 (키워드 기반)
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'happy', 'love', 'enjoy', 'fun', 'beautiful']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'hate', 'dislike', 'boring', 'ugly', 'disappointed']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                result = ("POSITIVE", 0.8)
            elif negative_count > positive_count:
                result = ("NEGATIVE", 0.8)
            else:
                result = ("NEUTRAL", 0.5)
                
            # 결과 캐싱
            self.sentiment_cache[text] = result
            return result
        
        if not self.models_loaded:
            self.load_models()
        
        try:
            # 짧은 텍스트는 간단한 방법으로 처리
            if len(text.split()) < 5:
                text_lower = text.lower()
                positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'happy', 'love', 'enjoy', 'fun', 'beautiful', 'clean']
                negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'hate', 'dislike', 'boring', 'ugly', 'disappointed', 'dirty']
                
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                if positive_count > negative_count:
                    result = ("POSITIVE", 0.8)
                elif negative_count > positive_count:
                    result = ("NEGATIVE", 0.8)
                else:
                    # 모델 사용
                    model_result = self.sentiment_analyzer(text)
                    result = (model_result[0]['label'], model_result[0]['score'])
            else:
                # 긴 텍스트는 모델 사용
                model_result = self.sentiment_analyzer(text)
                result = (model_result[0]['label'], model_result[0]['score'])
                
            # 결과 캐싱
            self.sentiment_cache[text] = result
            return result
        except Exception as e:
            print(f"감정 분석 중 오류 발생: {str(e)}")
            result = ("NEUTRAL", 0.5)
            self.sentiment_cache[text] = result
            return result
    
    def get_embedding(self, text):
        """텍스트의 임베딩 벡터를 반환합니다."""
        # 캐시 확인
        if text in self.embedding_cache:
            return self.embedding_cache[text]
            
        if not NLP_ADVANCED:
            # 간단한 임베딩 대체 (단어 빈도 기반)
            words = self.preprocess_text(text)
            word_counts = Counter(words)
            # 단어 빈도를 벡터로 변환 (간단한 대체 방법)
            result = word_counts
            self.embedding_cache[text] = result
            return result
        
        if not self.models_loaded:
            self.load_models()
        
        try:
            # 짧은 텍스트도 항상 Sentence-Transformers 모델 사용
            result = self.sentence_model.encode(text, convert_to_numpy=True)
                
            # 결과 캐싱
            self.embedding_cache[text] = result
            return result
        except Exception as e:
            print(f"임베딩 생성 중 오류 발생: {str(e)}")
            result = np.zeros(384)  # 기본 임베딩 차원 (MiniLM 모델)
            self.embedding_cache[text] = result
            return result
    
    def calculate_similarity(self, text1, text2):
        """두 텍스트 간의 유사도를 계산합니다."""
        if not NLP_ADVANCED:
            return self.calculate_similarity_fallback(text1, text2)
        
        if not self.models_loaded:
            self.load_models()
            
        try:
            # Sentence-Transformers를 사용한 유사도 계산
            embedding1 = self.get_embedding(text1)
            embedding2 = self.get_embedding(text2)
            
            # 코사인 유사도 계산
            similarity = util.cos_sim(embedding1, embedding2)
            
            # 짧은 쿼리에 대한 유사도 점수 향상
            if len(text1.split()) < 3:
                # 짧은 쿼리의 경우 유사도 점수를 증폭
                similarity_value = float(similarity[0][0])
                
                # 로그 출력 제거 (성능 개선)
                # print(f"원래 유사도: {similarity_value:.4f}, 쿼리: '{text1}', 대상: '{text2[:50]}...'")
                
                # 유사도가 0.2 이상인 경우 점수 증폭 (기준 낮춤)
                if similarity_value >= 0.2:
                    # 최대 0.85까지 증폭, 증폭 비율 감소 (2.0 -> 1.5)
                    amplified = min(similarity_value * 1.5, 0.85)
                    # print(f"증폭된 유사도: {amplified:.4f}")
                    return amplified
                # 유사도가 0.1 이상인 경우에도 약간 증폭
                elif similarity_value >= 0.1:
                    amplified = similarity_value * 1.3
                    # print(f"증폭된 유사도: {amplified:.4f}")
                    return amplified
            
            return float(similarity[0][0])  # 텐서에서 스칼라 값으로 변환
        except Exception as e:
            print(f"유사도 계산 중 오류 발생: {str(e)}")
            # 기본 유사도 계산으로 폴백
            return self.calculate_similarity_fallback(text1, text2)
    
    def calculate_similarity_fallback(self, text1, text2):
        """유사도 계산 폴백 메서드"""
        words1 = set(self.preprocess_text(text1))
        words2 = set(self.preprocess_text(text2))
        
        if not words1 or not words2:
            return 0.0
        
        # 자카드 유사도 계산
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0.0
        
        # 짧은 쿼리에 대한 유사도 점수 향상
        if len(text1.split()) < 3:
            # 짧은 쿼리의 경우 유사도 점수를 증폭
            if similarity >= 0.2:
                # 최대 0.8까지 증폭
                return min(similarity * 1.5, 0.8)
        
        return similarity
    
    def preprocess_text(self, text):
        """텍스트 전처리: 토큰화, 불용어 제거 등"""
        try:
            if NLTK_AVAILABLE:
                # NLTK 사용 시 오류 처리 강화
                try:
                    tokens = word_tokenize(text.lower())
                    tokens = [t for t in tokens if t not in self.stop_words and t.isalpha()]
                except Exception as e:
                    print(f"NLTK 토큰화 중 오류 발생: {str(e)}, 기본 토큰화로 대체합니다.")
                    # 기본 토큰화로 폴백
                    text = re.sub(r'[^\w\s]', '', text.lower())
                    tokens = [t for t in text.split() if t not in self.stop_words]
            else:
                # 간단한 토큰화 (공백 기준)
                text = re.sub(r'[^\w\s]', '', text.lower())  # 특수문자 제거
                tokens = [t for t in text.split() if t not in self.stop_words]
            
            return tokens
        except Exception as e:
            print(f"텍스트 전처리 중 오류 발생: {str(e)}")
            # 가장 기본적인 방법으로 폴백
            return text.lower().split()
    
    def search_destinations(self, query, destinations, top_n=10):
        """
        쿼리와 가장 유사한 여행지를 찾습니다.
        
        Args:
            query: 검색 쿼리
            destinations: 여행지 목록 (Location 객체)
            top_n: 반환할 결과 수
            
        Returns:
            유사도 점수와 함께 정렬된 여행지 목록
        """
        try:
            start_time = time.time()
            print(f"NLP 검색 쿼리: {query}")
            
            # 캐시 키 생성 (쿼리 + 결과 수)
            cache_key = f"{query}:{top_n}"
            cached_results = search_cache.get(cache_key)
            if cached_results:
                print(f"캐시에서 결과 반환 (쿼리: {query})")
                return cached_results
            
            # 쿼리 길이에 따른 처리 방식 로깅 (간소화)
            query_words_count = len(query.split())
            if query_words_count < 3:
                print(f"짧은 쿼리 감지 ({query_words_count}개 단어)")
            
            # 쿼리 감정 분석
            sentiment, confidence = self.analyze_sentiment(query)
            print(f"쿼리 감정 분석 결과: {sentiment}")
            
            # 쿼리 전처리
            query_words = set(self.preprocess_text(query))
            
            # 전체 여행지 처리 (제한 없음)
            total_destinations = len(destinations)
            print(f"전체 {total_destinations}개 여행지 처리 시작")
            
            # 초기 키워드 필터링으로 관련성 높은 여행지 먼저 선별
            # 짧은 쿼리의 경우 항상 키워드 필터링 활성화
            filtered_destinations = []
            
            # 데이터베이스 수준에서 초기 필터링 시도
            if len(query_words) > 0:
                print("키워드 기반 사전 필터링 적용")
                for dest in destinations:
                    dest_text = f"{dest.name} {dest.description or ''}".lower()
                    
                    # 도시와 국가 정보도 검색 텍스트에 포함
                    if dest.city:
                        dest_text += f" {dest.city}".lower()
                    if dest.country:
                        dest_text += f" {dest.country}".lower()
                    
                    # 최소 하나의 키워드가 포함된 여행지만 선택
                    if any(word in dest_text for word in query_words):
                        filtered_destinations.append(dest)
                
                # 충분한 결과가 없으면 원래 목록 사용
                if len(filtered_destinations) < max(50, top_n * 2):  # 최소 50개 또는 요청 결과의 2배
                    print(f"필터링 결과가 부족함 ({len(filtered_destinations)}개), 원래 목록 사용")
                    # 전체 목록 사용
                    filtered_destinations = destinations
                    print(f"전체 {len(filtered_destinations)}개 여행지 처리")
                else:
                    print(f"필터링으로 {len(filtered_destinations)}개 여행지 선별")
            else:
                # 전체 목록 사용
                filtered_destinations = destinations
                print(f"전체 {len(filtered_destinations)}개 여행지 처리")
            
            # 처리 시간 측정 시작
            process_start_time = time.time()
            
            results = []
            for i, dest in enumerate(filtered_destinations):
                # 진행 상황 로깅 (5000개마다) - 로그 빈도 감소
                if i > 0 and i % 5000 == 0:
                    elapsed = time.time() - process_start_time
                    print(f"진행 상황: {i}/{len(filtered_destinations)} 처리 완료 ({elapsed:.2f}초 소요)")
                
                # 여행지 정보 결합
                dest_text = f"{dest.name} {dest.description or ''}"
                
                # 도시와 국가 정보 추가 (가중치 증가를 위해 반복 추가)
                if dest.city:
                    # 도시 정보를 3번 반복하여 가중치 증가
                    dest_text += f" {dest.city} {dest.city} {dest.city}"
                if dest.country:
                    # 국가 정보를 3번 반복하여 가중치 증가
                    dest_text += f" {dest.country} {dest.country} {dest.country}"
                
                # subcategory와 subtype 추가 (간소화)
                if dest.subcategories:
                    if isinstance(dest.subcategories, list):
                        dest_text += " " + " ".join(dest.subcategories[:5])  # 처음 5개만 사용
                    elif isinstance(dest.subcategories, str):
                        dest_text += " " + dest.subcategories
                
                if dest.subtypes:
                    if isinstance(dest.subtypes, list):
                        dest_text += " " + " ".join(dest.subtypes[:5])  # 처음 5개만 사용
                    elif isinstance(dest.subtypes, str):
                        dest_text += " " + dest.subtypes
                
                # 유사도 계산
                similarity = self.calculate_similarity(query, dest_text)
                
                # 짧은 쿼리(3단어 미만)의 경우 추가 가중치 부여
                if len(query.split()) < 3:
                    # 쿼리 단어가 여행지 이름에 직접 포함된 경우 가중치 증가
                    if any(word in dest.name.lower() for word in query_words):
                        similarity *= 1.5  # 50% 가중치 증가
                    
                    # 쿼리 단어가 도시 이름에 직접 포함된 경우 가중치 크게 증가
                    if dest.city and any(word in dest.city.lower() for word in query_words):
                        similarity *= 2.0  # 100% 가중치 증가
                    
                    # 쿼리 단어가 국가 이름에 직접 포함된 경우 가중치 크게 증가
                    if dest.country and any(word in dest.country.lower() for word in query_words):
                        similarity *= 2.0  # 100% 가중치 증가
                    
                    # 쿼리 단어가 여행지 설명에 포함된 경우 가중치 약간 증가
                    elif any(word in dest_text.lower() for word in query_words):
                        similarity *= 1.3  # 30% 가중치 증가
                
                # 감정 기반 가중치 적용
                if sentiment == "POSITIVE":
                    # 긍정적인 쿼리는 "Fun & Games", "Entertainment" 등의 카테고리에 가중치 부여
                    positive_categories = ["Fun & Games", "Entertainment", "Spas & Wellness", "Food & Drink"]
                    for cat in positive_categories:
                        if cat in dest_text:
                            similarity *= 1.2  # 20% 가중치 증가
                elif sentiment == "NEGATIVE":
                    # 부정적인 쿼리는 "Nature & Parks", "Museums" 등 조용한 카테고리에 가중치 부여
                    negative_categories = ["Nature & Parks", "Museums", "Sights & Landmarks"]
                    for cat in negative_categories:
                        if cat in dest_text:
                            similarity *= 1.2  # 20% 가중치 증가
                
                # 쿼리 키워드가 제목에 직접 포함된 경우 가중치 부여
                if any(word in dest.name.lower() for word in query_words):
                    similarity *= 1.5  # 50% 가중치 증가
                
                results.append((dest, similarity))
            
            # 유사도 기준으로 정렬
            results.sort(key=lambda x: x[1], reverse=True)
            
            # 처리 시간 측정 종료
            process_end_time = time.time()
            process_duration = process_end_time - process_start_time
            
            print(f"검색 완료: 전체 {len(results)}개 결과 중 상위 {top_n}개 반환")
            print(f"처리 시간: 총 {time.time() - start_time:.2f}초 (데이터 처리: {process_duration:.2f}초)")
            
            # 상위 5개 결과 로깅 (간소화)
            top_results = [dest.name for dest, _ in results[:5]]
            print(f"상위 검색 결과: {', '.join(top_results)}")
            
            # 짧은 쿼리의 경우 유사도 점수가 0.03 이상인 결과만 반환 (기준 낮춤: 0.05 -> 0.03)
            if len(query.split()) < 3:
                filtered_results = [(dest, sim) for dest, sim in results if sim >= 0.03]
                # 결과가 너무 적으면 원래 결과 사용
                if len(filtered_results) < top_n:
                    print(f"유사도 필터링 결과가 부족함 ({len(filtered_results)}개), 원래 결과 사용")
                    final_results = results[:top_n]
                else:
                    print(f"유사도 필터링으로 {len(filtered_results)}개 결과 선별")
                    final_results = filtered_results[:top_n]
            else:
                final_results = results[:top_n]
            
            # 결과 캐싱
            search_cache.put(cache_key, final_results)
            
            return final_results
        except Exception as e:
            print(f"여행지 검색 중 오류 발생: {str(e)}")
            # 오류 발생 시 키워드 검색으로 폴백
            return self.keyword_search(query, destinations, top_n)
    
    def keyword_search(self, query, destinations, top_n=10):
        """키워드 기반 간단한 검색 (폴백 메서드)"""
        try:
            start_time = time.time()
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            # 전체 여행지 처리 (제한 없음)
            total_destinations = len(destinations)
            print(f"키워드 검색: 전체 {total_destinations}개 여행지 처리")
            
            # 유사 단어 사전 (검색 확장용)
            similar_words = {
                'clean': ['neat', 'tidy', 'spotless', 'immaculate', 'pristine'],
                'cozy': ['comfortable', 'warm', 'snug', 'homely', 'intimate', 'pleasant'],
                'excited': ['thrilling', 'exciting', 'fun', 'entertainment', 'thrill', 'adventure', 'joy', 'happy'],
                'beautiful': ['pretty', 'scenic', 'gorgeous', 'lovely', 'stunning', 'attractive'],
                'quiet': ['peaceful', 'calm', 'serene', 'tranquil', 'silent', 'relaxing'],
                'historic': ['ancient', 'old', 'traditional', 'heritage', 'historical', 'classic'],
                'modern': ['contemporary', 'new', 'trendy', 'stylish', 'innovative'],
                'nature': ['natural', 'outdoor', 'green', 'park', 'garden', 'forest', 'mountain', 'lake', 'river'],
                'food': ['restaurant', 'cuisine', 'dining', 'eat', 'culinary', 'gastronomy', 'delicious'],
                'shopping': ['shop', 'store', 'mall', 'market', 'boutique', 'retail'],
                'family': ['kid', 'child', 'children', 'friendly', 'fun'],
                'luxury': ['luxurious', 'upscale', 'premium', 'elegant', 'fancy', 'high-end'],
                'budget': ['cheap', 'affordable', 'inexpensive', 'economical', 'reasonable'],
                'view': ['vista', 'panorama', 'overlook', 'scenery', 'landscape', 'scenic']
            }
            
            # 검색어 확장 (유사 단어 포함)
            expanded_query_words = set(query_words)
            for word in query_words:
                if word in similar_words:
                    expanded_query_words.update(similar_words[word])
            
            print(f"검색어 확장: {query_words} → {expanded_query_words}")
            
            # 처리 시간 측정 시작
            process_start_time = time.time()
            
            results = []
            raw_scores = []  # 정규화를 위한 원시 점수 저장
            
            for i, dest in enumerate(destinations):
                # 진행 상황 로깅 (1000개마다)
                if i > 0 and i % 1000 == 0:
                    elapsed = time.time() - process_start_time
                    print(f"진행 상황: {i}/{len(destinations)} 처리 완료 ({elapsed:.2f}초 소요)")
                
                # 여행지 정보 결합
                dest_text = f"{dest.name} {dest.description or ''}".lower()
                
                # 카테고리 정보 추가
                if dest.category:
                    dest_text += f" {dest.category}".lower()
                
                # 도시와 국가 정보 추가 (가중치 증가를 위해 반복 추가)
                city_match = False
                country_match = False
                
                if dest.city:
                    city_lower = dest.city.lower()
                    # 도시 정보를 3번 반복하여 가중치 증가
                    dest_text += f" {city_lower} {city_lower} {city_lower}"
                    # 도시 일치 여부 확인
                    city_match = any(word in city_lower for word in query_words)
                
                if dest.country:
                    country_lower = dest.country.lower()
                    # 국가 정보를 3번 반복하여 가중치 증가
                    dest_text += f" {country_lower} {country_lower} {country_lower}"
                    # 국가 일치 여부 확인
                    country_match = any(word in country_lower for word in query_words)
                
                # 서브카테고리 정보 추가
                if dest.subcategories:
                    if isinstance(dest.subcategories, list):
                        dest_text += " " + " ".join([s.lower() for s in dest.subcategories])
                    elif isinstance(dest.subcategories, str):
                        dest_text += " " + dest.subcategories.lower()
                
                # 1. 정확한 단어 매칭 (높은 점수)
                exact_match_count = sum(1 for word in query_words if f" {word} " in f" {dest_text} ")
                
                # 2. 부분 문자열 매칭 (중간 점수)
                partial_match_count = sum(1 for word in query_words if word in dest_text)
                
                # 3. 확장 단어 매칭 (낮은 점수)
                expanded_match_count = sum(1 for word in expanded_query_words if word in dest_text)
                
                # 종합 점수 계산 (가중치 적용)
                score = 0
                if exact_match_count > 0:
                    score += exact_match_count * 0.6  # 정확한 매칭에 가장 높은 가중치
                if partial_match_count > 0:
                    score += partial_match_count * 0.3  # 부분 매칭에 중간 가중치
                if expanded_match_count > 0:
                    score += expanded_match_count * 0.1  # 확장 단어 매칭에 낮은 가중치
                
                # 제목에 키워드가 있으면 가중치 부여
                if any(word in dest.name.lower() for word in query_words):
                    score *= 1.5  # 50% 가중치 증가
                
                # 도시 이름에 키워드가 있으면 가중치 크게 부여
                if city_match:
                    score *= 2.0  # 100% 가중치 증가
                
                # 국가 이름에 키워드가 있으면 가중치 크게 부여
                if country_match:
                    score *= 2.0  # 100% 가중치 증가
                
                # 점수가 있는 결과만 추가
                if score > 0:
                    raw_scores.append((dest, score))
            
            # 점수 정규화 및 분포 개선
            if raw_scores:
                # 최대 점수 찾기
                max_score = max(score for _, score in raw_scores)
                
                # 점수 정규화 및 분포 개선 (로그 스케일 적용)
                for dest, score in raw_scores:
                    # 로그 스케일 적용 (점수 분포 개선)
                    normalized_score = 0.2 + (0.8 * (score / max_score))
                    
                    # 시그모이드 함수로 점수 분포 부드럽게 조정
                    # 0.5를 중심으로 분포 (0.2 ~ 1.0 범위)
                    adjusted_score = 0.2 + (0.8 / (1 + 2.5 * (1 - normalized_score)))
                    
                    results.append((dest, adjusted_score))
            
            # 점수 기준으로 정렬
            results.sort(key=lambda x: x[1], reverse=True)
            
            # 처리 시간 측정 종료
            process_end_time = time.time()
            process_duration = process_end_time - process_start_time
            
            print(f"키워드 검색 완료: {len(results)} 결과 찾음")
            print(f"처리 시간: 총 {time.time() - start_time:.2f}초 (데이터 처리: {process_duration:.2f}초)")
            
            return results[:top_n]
        except Exception as e:
            print(f"키워드 검색 중 오류 발생: {str(e)}")
            # 최후의 폴백: 무작위 결과 반환
            import random
            random_results = [(dest, 0.1) for dest in random.sample(list(destinations), min(top_n, len(destinations)))]
            return random_results

# 싱글톤 인스턴스 생성
nlp_processor = NLPProcessor() 