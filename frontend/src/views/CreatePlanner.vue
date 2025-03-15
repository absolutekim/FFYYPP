<template>
  <div class="planner-container">
    <h1 class="page-title">여행 플래너</h1>
    
    <div v-if="loadingPlanners" class="loading-container">
      <div class="spinner"></div>
      <p>플래너 정보를 불러오는 중...</p>
    </div>
    
    <!-- 플래너 선택 및 생성 -->
    <div v-else class="planner-selection">
      <div v-if="userPlanners.length > 0" class="planner-list">
        <h2>내 플래너 목록</h2>
        <div class="planner-tabs">
          <button 
            v-for="planner in userPlanners" 
            :key="planner.id"
            @click="currentPlanner = planner; fetchPlannerItems();"
            :class="['planner-tab', { active: currentPlanner && currentPlanner.id === planner.id }]"
          >
            {{ planner.title }}
            <span class="item-count">({{ planner.items_count || 0 }})</span>
          </button>
          <button @click="currentPlanner = null" class="planner-tab new-planner">
            <i class="fas fa-plus"></i> 새 플래너
          </button>
        </div>
      </div>
      
      <!-- 플래너 생성 폼 -->
      <div v-if="!currentPlanner" class="create-planner-form">
        <h2>새 플래너 만들기</h2>
        <div class="form-group">
          <label for="planner-title">플래너 제목</label>
          <input 
            type="text" 
            id="planner-title" 
            v-model="newPlanner.title" 
            placeholder="예: 유럽 여행 계획"
            class="form-control"
          >
        </div>
        <div class="form-group">
          <label for="planner-description">설명 (선택사항)</label>
          <textarea 
            id="planner-description" 
            v-model="newPlanner.description" 
            placeholder="플래너에 대한 설명을 입력하세요"
            class="form-control"
          ></textarea>
        </div>
        <button @click="createPlanner" class="btn-primary">플래너 만들기</button>
      </div>
      
      <!-- 플래너 관리 화면 -->
      <div v-else class="planner-management">
        <div class="planner-header">
          <div>
            <h2>{{ currentPlanner.title }}</h2>
            <p v-if="currentPlanner.description" class="planner-description">{{ currentPlanner.description }}</p>
          </div>
          <div class="planner-actions">
            <button @click="savePlannerOrder" class="btn-primary">변경사항 저장</button>
            <button @click="currentPlanner = null" class="btn-secondary">다른 플래너 만들기</button>
            <button @click="deletePlanner" class="btn-danger">
              <i class="fas fa-trash"></i> 플래너 삭제
            </button>
          </div>
        </div>
        
        <div class="planner-content">
          <!-- 좌측: 플래너 영역 -->
          <div class="planner-area">
            <h3>내 여행 계획 <span class="item-count">({{ plannerItems.length }}/10)</span></h3>
            <div 
              class="planner-drop-area"
              @dragover.prevent
              @drop="onDrop"
            >
              <div v-if="plannerItems.length === 0" class="empty-planner">
                <p>여행지를 이곳으로 드래그하여 플래너에 추가하세요</p>
                <p class="small">최대 10개까지 추가할 수 있습니다</p>
              </div>
              <draggable 
                v-model="plannerItems" 
                group="destinations"
                item-key="id"
                class="planner-items-list"
                @change="onDraggableChange"
              >
                <template #item="{ element }">
                  <div class="planner-item">
                    <div class="item-image">
                      <img :src="element.location_details.image || 'https://via.placeholder.com/100x60?text=No+Image'" :alt="element.location_details.name">
                    </div>
                    <div class="item-info">
                      <h4>{{ element.location_details.name }}</h4>
                      <p class="location">
                        {{ getLocationString(element.location_details) }}
                      </p>
                    </div>
                    <button @click="removeFromPlanner(element)" class="btn-remove" title="여행지 제거">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </template>
              </draggable>
            </div>
          </div>
          
          <!-- 우측: 여행지 검색 및 목록 -->
          <div class="destinations-area">
            <h3>여행지 검색</h3>
            <div class="filter-controls">
              <div class="search-box">
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  placeholder="여행지 검색... (2글자 이상 입력)" 
                  class="search-input"
                >
              </div>
              <div class="country-filter" v-if="countries.length > 0">
                <select v-model="selectedCountry" class="country-select">
                  <option value="">모든 국가</option>
                  <option v-for="country in countries" :key="country" :value="country">
                    {{ country }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="destinations-list">
              <div v-if="searchQuery.trim().length < 2" class="search-prompt">
                <p>여행지를 검색하려면 2글자 이상 입력하세요</p>
              </div>
              
              <div 
                v-else-if="filteredDestinations.length > 0"
                v-for="destination in filteredDestinations" 
                :key="destination.id"
                class="destination-card"
                draggable="true"
                @dragstart="onDragStart($event, destination)"
              >
                <div class="destination-image">
                  <img :src="destination.image || 'https://via.placeholder.com/150x100?text=No+Image'" :alt="destination.name">
                </div>
                <div class="destination-info">
                  <h4>{{ destination.name }}</h4>
                  <p class="location">{{ getLocationString(destination) }}</p>
                </div>
                <button 
                  @click="addToPlanner(destination)" 
                  class="btn-add"
                  :disabled="isDestinationInPlanner(destination) || plannerItems.length >= 10"
                >
                  <i class="fas fa-plus"></i>
                </button>
              </div>
              
              <div v-else-if="searchQuery.trim().length >= 2 && filteredDestinations.length === 0 && !isLoading" class="no-results">
                <p>검색 결과가 없습니다</p>
              </div>
              
              <div v-if="isLoading" class="loading">
                <div class="spinner"></div>
                <p>여행지를 불러오는 중...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { ref, computed, onMounted, watch } from 'vue';
import draggable from 'vuedraggable';

export default {
  name: 'CreatePlanner',
  components: {
    draggable
  },
  setup() {
    // 상태 변수
    const destinations = ref([]);
    const countries = ref([]);
    const searchQuery = ref('');
    const selectedCountry = ref('');
    const isLoading = ref(true);
    const currentPlanner = ref(null);
    const plannerItems = ref([]);
    const originalOrder = ref([]);
    const newPlanner = ref({
      title: '',
      description: ''
    });
    const draggedDestination = ref(null);
    const userPlanners = ref([]);  // 사용자의 플래너 목록
    const loadingPlanners = ref(false);  // 플래너 로딩 상태
    const searchTimeout = ref(null); // 검색 디바운싱을 위한 타임아웃
    
    // 필터링된 여행지 목록
    const filteredDestinations = computed(() => {
      let filtered = destinations.value;
      
      // 검색어로 필터링 (백엔드에서 이미 수행되므로 제거)
      // 백엔드에서 이미 검색어로 필터링된 결과를 받아오므로 여기서는 필터링하지 않음
      
      // 국가로 필터링
      if (selectedCountry.value) {
        filtered = filtered.filter(dest => 
          dest.country === selectedCountry.value
        );
      }
      
      return filtered;
    });
    
    // 순서 변경 여부 확인
    const hasOrderChanged = computed(() => {
      if (plannerItems.value.length !== originalOrder.value.length) return true;
      
      for (let i = 0; i < plannerItems.value.length; i++) {
        if (plannerItems.value[i].id !== originalOrder.value[i]) return true;
      }
      
      return false;
    });
    
    // 사용자의 플래너 목록 가져오기
    const fetchUserPlanners = async () => {
      try {
        loadingPlanners.value = true;
        const response = await axios.get('/api/planner/planners/');
        userPlanners.value = response.data;
        
        // 플래너가 있으면 첫 번째 플래너 선택
        if (userPlanners.value.length > 0) {
          currentPlanner.value = userPlanners.value[0];
        }
        
        loadingPlanners.value = false;
      } catch (error) {
        console.error('플래너 목록을 불러오는데 실패했습니다:', error);
        loadingPlanners.value = false;
      }
    };
    
    // URL 쿼리 파라미터에서 여행지 ID 가져오기
    const handleDestinationFromQuery = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const destinationId = urlParams.get('destination');
      
      if (destinationId && currentPlanner.value) {
        try {
          // 여행지 정보 가져오기
          const response = await axios.get(`/api/destinations/${destinationId}/`);
          const destination = response.data;
          
          // 플래너에 여행지 추가
          addToPlanner(destination);
          
          // URL에서 쿼리 파라미터 제거
          const url = new URL(window.location);
          url.searchParams.delete('destination');
          window.history.replaceState({}, '', url);
        } catch (error) {
          console.error('여행지 정보를 불러오는데 실패했습니다:', error);
        }
      }
    };
    
    // 여행지 목록 가져오기 (검색용)
    const fetchDestinations = async () => {
      if (searchQuery.value.trim() === '') {
        destinations.value = [];
        isLoading.value = false;
        return;
      }
      
      try {
        isLoading.value = true;
        console.log(`검색 쿼리: "${searchQuery.value}", 결과 제한: 20개`);
        const response = await axios.get(`/api/destinations/search/nlp/?query=${encodeURIComponent(searchQuery.value)}&limit=20`);
        
        if (response.data && response.data.results) {
          destinations.value = response.data.results;
          console.log(`검색 결과: ${destinations.value.length}개 항목 받음`);
          
          // 결과가 예상보다 적을 경우 (10개 미만) 자동으로 다시 검색 시도
          if (destinations.value.length < 10 && response.data.results_count > 10) {
            console.log('검색 결과가 예상보다 적습니다. 다시 시도합니다...');
            setTimeout(async () => {
              try {
                const retryResponse = await axios.get(`/api/destinations/search/nlp/?query=${encodeURIComponent(searchQuery.value)}&limit=20&retry=true`);
                if (retryResponse.data && retryResponse.data.results && retryResponse.data.results.length > destinations.value.length) {
                  destinations.value = retryResponse.data.results;
                  console.log(`재시도 검색 결과: ${destinations.value.length}개 항목 받음`);
                }
              } catch (retryError) {
                console.error('재시도 검색 중 오류 발생:', retryError);
              }
            }, 500);
          }
        } else {
          destinations.value = [];
          console.log('검색 결과 없음');
        }
        
        // 국가 목록 추출
        const countrySet = new Set();
        destinations.value.forEach(dest => {
          if (dest.country) countrySet.add(dest.country);
        });
        countries.value = Array.from(countrySet).sort();
        
        isLoading.value = false;
      } catch (error) {
        console.error('여행지를 불러오는데 실패했습니다:', error);
        isLoading.value = false;
      }
    };
    
    // 검색어 변경 시 여행지 목록 가져오기 (디바운싱 적용)
    watch(searchQuery, () => {
      // 이전 타임아웃 취소
      if (searchTimeout.value) {
        clearTimeout(searchTimeout.value);
      }
      
      if (searchQuery.value.trim().length >= 2) {
        // 500ms 디바운싱 적용
        searchTimeout.value = setTimeout(() => {
          fetchDestinations();
        }, 500);
      } else if (searchQuery.value.trim() === '') {
        destinations.value = [];
      }
    });
    
    // 플래너 생성
    const createPlanner = async () => {
      if (!newPlanner.value.title) {
        alert('플래너 제목을 입력해주세요.');
        return;
      }
      
      try {
        const response = await axios.post('/api/planner/planners/', {
          title: newPlanner.value.title,
          description: newPlanner.value.description
        });
        
        currentPlanner.value = response.data;
        newPlanner.value = { title: '', description: '' };
      } catch (error) {
        console.error('플래너 생성에 실패했습니다:', error);
        alert('플래너 생성에 실패했습니다. 다시 시도해주세요.');
      }
    };
    
    // 플래너 초기화
    const resetPlanner = () => {
      currentPlanner.value = null;
      plannerItems.value = [];
      originalOrder.value = [];
    };
    
    // 플래너에 여행지 추가
    const addToPlanner = async (destination) => {
      if (plannerItems.value.length >= 10) {
        alert('플래너에는 최대 10개의 여행지만 추가할 수 있습니다.');
        return;
      }
      
      if (isDestinationInPlanner(destination)) {
        alert('이미 플래너에 추가된 여행지입니다.');
        return;
      }
      
      try {
        const response = await axios.post('/api/planner/planner-items/', {
          planner: currentPlanner.value.id,
          location: destination.id,
          order: plannerItems.value.length
        });
        
        // 응답에서 location_details가 없을 경우 추가
        if (!response.data.location_details) {
          response.data.location_details = destination;
        }
        
        plannerItems.value.push(response.data);
        updateOriginalOrder();
      } catch (error) {
        console.error('여행지 추가에 실패했습니다:', error);
        alert('여행지 추가에 실패했습니다. 다시 시도해주세요.');
      }
    };
    
    // 플래너에서 여행지 제거
    const removeFromPlanner = async (item) => {
      try {
        await axios.delete(`/api/planner/planner-items/${item.id}/`);
        plannerItems.value = plannerItems.value.filter(i => i.id !== item.id);
        
        // 순서 업데이트
        plannerItems.value.forEach((item, index) => {
          item.order = index;
        });
        
        updateOriginalOrder();
      } catch (error) {
        console.error('여행지 제거에 실패했습니다:', error);
        alert('여행지 제거에 실패했습니다. 다시 시도해주세요.');
      }
    };
    
    // 플래너 항목 순서 저장
    const savePlannerOrder = async () => {
      try {
        // 플래너 항목이 없으면 저장할 필요 없음
        if (plannerItems.value.length === 0) {
          alert('저장할 여행지가 없습니다.');
          return;
        }
        
        // 저장 전에 서버에서 최신 데이터를 가져와 동기화
        console.log('서버에서 최신 데이터를 가져와 동기화합니다...');
        await fetchPlannerItems();
        
        // 서버에 저장할 항목 데이터 생성
        const items = plannerItems.value.map((item, index) => ({
          id: item.id,
          order: index
        }));
        
        console.log('저장할 데이터:', { items });
        
        await axios.post('/api/planner/planner-items/reorder/', {
          items: items
        });
        
        updateOriginalOrder();
        
        // 플래너 목록 다시 불러오기
        await fetchUserPlanners();
        
        alert('플래너 순서가 저장되었습니다.');
      } catch (error) {
        console.error('플래너 순서 저장에 실패했습니다:', error);
        if (error.response) {
          console.error('응답 데이터:', error.response.data);
          console.error('상태 코드:', error.response.status);
          
          // 항목을 찾을 수 없는 경우 플래너 항목을 다시 불러옴
          if (error.response.status === 400 && error.response.data.detail === '일부 항목을 찾을 수 없습니다.') {
            alert('일부 항목을 찾을 수 없습니다. 플래너 항목을 다시 불러옵니다.');
            await fetchPlannerItems();
            return;
          }
        }
        alert('플래너 순서 저장에 실패했습니다. 다시 시도해주세요.');
      }
    };
    
    // 플래너 항목 가져오기
    const fetchPlannerItems = async () => {
      if (!currentPlanner.value) return;
      
      try {
        console.log(`플래너 ID ${currentPlanner.value.id}의 항목을 불러오는 중...`);
        const response = await axios.get(`/api/planner/planners/${currentPlanner.value.id}/items/`);
        
        // 응답 데이터 로깅
        console.log('서버에서 받은 플래너 항목:', response.data);
        
        // 항목 ID 목록 비교
        const oldIds = plannerItems.value.map(item => item.id);
        const newIds = response.data.map(item => item.id);
        
        console.log('기존 항목 ID:', oldIds);
        console.log('새 항목 ID:', newIds);
        
        // 데이터 업데이트
        plannerItems.value = response.data;
        updateOriginalOrder();
      } catch (error) {
        console.error('플래너 항목을 불러오는데 실패했습니다:', error);
        if (error.response) {
          console.error('응답 데이터:', error.response.data);
          console.error('상태 코드:', error.response.status);
        }
        alert('플래너 항목을 불러오는데 실패했습니다. 페이지를 새로고침하세요.');
      }
    };
    
    // 원본 순서 업데이트
    const updateOriginalOrder = () => {
      originalOrder.value = plannerItems.value.map(item => item.id);
    };
    
    // 여행지가 이미 플래너에 있는지 확인
    const isDestinationInPlanner = (destination) => {
      return plannerItems.value.some(item => 
        item.location === destination.id || 
        (item.location_details && item.location_details.id === destination.id)
      );
    };
    
    // 위치 문자열 생성
    const getLocationString = (destination) => {
      const parts = [];
      if (destination.city) parts.push(destination.city);
      if (destination.country) parts.push(destination.country);
      
      return parts.join(', ') || '위치 정보 없음';
    };
    
    // 드래그 시작 이벤트 핸들러
    // eslint-disable-next-line no-unused-vars
    const onDragStart = (event, destination) => {
      draggedDestination.value = destination;
      event.dataTransfer.effectAllowed = 'move';
    };
    
    // 드롭 이벤트 핸들러
    // eslint-disable-next-line no-unused-vars
    const onDrop = (event) => {
      if (draggedDestination.value) {
        addToPlanner(draggedDestination.value);
        draggedDestination.value = null;
      }
    };
    
    // 드래그 앤 드롭 변경 이벤트 핸들러
    const onDraggableChange = () => {
      // 순서 업데이트
      plannerItems.value.forEach((item, index) => {
        item.order = index;
      });
      
      console.log('드래그 앤 드롭으로 항목 순서가 변경되었습니다.');
      console.log('변경된 순서:', plannerItems.value.map(item => item.id));
      
      // 원본 순서와 비교하기 위해 originalOrder는 업데이트하지 않음
      // 이렇게 하면 hasOrderChanged가 true를 반환하여 저장 버튼이 활성화됨
      
      // 자동 저장 기능 (선택적으로 활성화)
      // savePlannerOrder();
    };
    
    // 컴포넌트 마운트 시 사용자의 플래너 목록 가져오기
    onMounted(() => {
      fetchUserPlanners().then(() => {
        // 플래너 목록을 가져온 후 URL 쿼리 파라미터 처리
        handleDestinationFromQuery();
      });
    });
    
    // 현재 플래너 변경 시 플래너 항목 가져오기
    watch(currentPlanner, () => {
      fetchPlannerItems();
    });
    
    // 플래너 삭제
    const deletePlanner = async () => {
      if (confirm('정말로 이 플래너를 삭제하시겠습니까? 삭제된 플래너는 복구할 수 없습니다.')) {
        try {
          await axios.delete(`/api/planner/planners/${currentPlanner.value.id}/`);
          currentPlanner.value = null;
          // 플래너 목록 다시 불러오기
          await fetchUserPlanners();
          alert('플래너가 성공적으로 삭제되었습니다.');
        } catch (error) {
          console.error('플래너 삭제에 실패했습니다:', error);
          alert('플래너 삭제에 실패했습니다. 다시 시도해주세요.');
        }
      }
    };
    
    return {
      destinations,
      countries,
      searchQuery,
      selectedCountry,
      isLoading,
      currentPlanner,
      plannerItems,
      newPlanner,
      filteredDestinations,
      hasOrderChanged,
      userPlanners,
      loadingPlanners,
      createPlanner,
      resetPlanner,
      addToPlanner,
      removeFromPlanner,
      savePlannerOrder,
      isDestinationInPlanner,
      getLocationString,
      onDragStart,
      onDrop,
      onDraggableChange,
      fetchDestinations,
      fetchPlannerItems,
      deletePlanner
    };
  }
};
</script>

<style scoped>
.planner-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #2c3e50;
}

/* 플래너 생성 폼 */
.create-planner-form {
  max-width: 600px;
  margin: 0 auto;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.create-planner-form h2 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

/* 플래너 관리 화면 */
.planner-management {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.planner-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.planner-header h2 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.planner-actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
}

.planner-content {
  display: flex;
  min-height: 600px;
}

/* 좌측: 플래너 영역 */
.planner-area {
  flex: 1;
  padding: 1.5rem;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

.planner-area h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.item-count {
  font-size: 0.9rem;
  color: #666;
  font-weight: normal;
}

.planner-drop-area {
  flex: 1;
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 1rem;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.empty-planner {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
  text-align: center;
}

.empty-planner .small {
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.planner-items-list {
  flex: 1;
  overflow-y: auto;
}

.planner-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 0.75rem;
  cursor: move;
}

.item-image {
  width: 60px;
  height: 60px;
  margin-right: 1rem;
  border-radius: 4px;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
}

.item-info h4 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
}

.location {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

.btn-remove {
  background: transparent;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.5rem;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.btn-remove:hover {
  background-color: rgba(231, 76, 60, 0.1);
}

/* 우측: 여행지 목록 */
.destinations-area {
  flex: 1;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.destinations-area h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-box {
  flex: 1;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.country-select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  min-width: 150px;
}

.destinations-list {
  flex: 1;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  max-height: 500px;
  padding-right: 0.5rem;
  grid-auto-rows: min-content;
}

.destination-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: grab;
  position: relative;
  height: auto;
  min-height: 220px;
  display: flex;
  flex-direction: column;
}

.destination-image {
  height: 120px;
  overflow: hidden;
}

.destination-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.destination-info {
  padding: 1rem;
}

.destination-info h4 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
}

.btn-add {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.btn-add:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.no-results, .loading {
  grid-column: 1 / -1;
  padding: 2rem;
  text-align: center;
  color: #666;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 버튼 스타일 */
.btn-primary {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #ecf0f1;
  color: #2c3e50;
  border: 1px solid #ddd;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: #dde4e6;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-danger:hover {
  background-color: #c0392b;
}

/* 플래너 선택 및 목록 */
.planner-selection {
  margin-bottom: 2rem;
}

.planner-list {
  margin-bottom: 2rem;
}

.planner-list h2 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.planner-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.planner-tab {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.planner-tab.active {
  background-color: #3498db;
  color: white;
  border-color: #3498db;
}

.planner-tab:hover:not(.active) {
  background-color: #e9ecef;
}

.planner-tab .item-count {
  font-size: 0.8rem;
  color: inherit;
  opacity: 0.8;
  margin-left: 0.25rem;
}

.planner-tab.new-planner {
  background-color: #27ae60;
  color: white;
  border-color: #27ae60;
}

.planner-tab.new-planner:hover {
  background-color: #219653;
}

.planner-description {
  color: #666;
  margin-top: 0.5rem;
}

.search-prompt {
  grid-column: 1 / -1;
  padding: 2rem;
  text-align: center;
  color: #666;
  background-color: #f8f9fa;
  border-radius: 8px;
}

/* 반응형 스타일 */
@media (max-width: 768px) {
  .planner-tabs {
    flex-direction: column;
  }
  
  .planner-tab {
    width: 100%;
  }
  
  .planner-content {
    flex-direction: column;
  }
  
  .planner-area, .destinations-area {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #eee;
  }
  
  .filter-controls {
    flex-direction: column;
  }
}
</style>