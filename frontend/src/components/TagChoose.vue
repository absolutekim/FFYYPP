<template>
  <div class="tag-choose-container">
    <h3>관심 있는 여행 카테고리를 선택해주세요 (3-7개)</h3>
    <p class="tag-instruction">선택한 태그: {{ selectedTags.length }}개 (최소 3개, 최대 7개)</p>
    
    <div class="tags-grid">
      <div 
        v-for="tag in tags" 
        :key="tag" 
        :class="['tag-item', { selected: isSelected(tag) }]"
        @click="toggleTag(tag)"
      >
        {{ tag }}
      </div>
    </div>
    
    <div class="error-message" v-if="error">{{ error }}</div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'TagChoose',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      tags: [],
      selectedTags: [],
      error: '',
      isLoading: false
    };
  },
  created() {
    // 초기값 설정
    this.selectedTags = Array.isArray(this.modelValue) ? [...this.modelValue] : [];
    this.fetchTags();
  },
  methods: {
    isSelected(tag) {
      return this.selectedTags.includes(tag);
    },
    toggleTag(tag) {
      let newSelectedTags;
      
      if (this.isSelected(tag)) {
        // 이미 선택된 태그라면 제거
        newSelectedTags = this.selectedTags.filter(t => t !== tag);
      } else {
        // 7개 이상 선택하려고 할 때
        if (this.selectedTags.length >= 7) {
          this.error = '최대 7개의 태그만 선택할 수 있습니다.';
          return;
        }
        // 선택되지 않은 태그라면 추가
        newSelectedTags = [...this.selectedTags, tag];
      }
      
      // 로컬 상태 업데이트
      this.selectedTags = newSelectedTags;
      
      // 부모 컴포넌트에 변경 알림 (Vue 3 방식)
      this.$emit('update:modelValue', newSelectedTags);
      
      // 에러 메시지 업데이트
      if (newSelectedTags.length < 3) {
        this.error = '최소 3개의 태그를 선택해주세요.';
      } else if (newSelectedTags.length > 7) {
        this.error = '최대 7개의 태그만 선택할 수 있습니다.';
      } else {
        this.error = '';
      }
      
      console.log('태그 선택 변경:', newSelectedTags);
    },
    async fetchTags() {
      try {
        this.isLoading = true;
        const response = await axios.get('http://localhost:8000/api/accounts/tags/');
        this.tags = response.data.tags;
      } catch (error) {
        console.error('태그 목록을 가져오는데 실패했습니다:', error);
        this.error = '태그 목록을 가져오는데 실패했습니다.';
      } finally {
        this.isLoading = false;
      }
    }
  },
  watch: {
    modelValue: {
      handler(newVal) {
        // props가 변경되면 로컬 상태 업데이트
        this.selectedTags = Array.isArray(newVal) ? [...newVal] : [];
      },
      deep: true
    }
  }
};
</script>

<style scoped>
.tag-choose-container {
  margin: 20px 0;
}

h3 {
  margin-bottom: 10px;
  color: #4a5568;
}

.tag-instruction {
  margin-bottom: 15px;
  font-size: 14px;
  color: #718096;
}

.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.tag-item {
  padding: 10px 15px;
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.tag-item:hover {
  background-color: #edf2f7;
}

.tag-item.selected {
  background-color: #667eea;
  color: white;
  border-color: #5a67d8;
}

.error-message {
  color: #e53e3e;
  font-size: 14px;
  margin-top: 10px;
}
</style> 