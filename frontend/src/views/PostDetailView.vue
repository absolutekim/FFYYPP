<template>
  <v-container class="post-detail-container">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card class="post-detail-card" elevation="4">
          <!-- 게시글 제목 및 정보 -->
          <v-card-title class="text-h4 font-weight-bold primary--text">
            {{ post.title }}
          </v-card-title>

          <v-card-subtitle class="d-flex align-center">
            <v-icon small class="mr-1">mdi-account</v-icon>
            {{ post.author }}
            <v-spacer></v-spacer>
            <v-icon small class="mr-1">mdi-clock-outline</v-icon>
            {{ formatDate(post.created_at) }}
          </v-card-subtitle>

          <v-divider></v-divider>

          <!-- 게시글 내용 -->
          <v-card-text class="text-body-1">
            {{ post.content }}
          </v-card-text>

          <!-- 수정 및 삭제 버튼 -->
          <v-card-actions v-if="isAuthor" class="px-4">
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              text
              @click="$router.push(`/community/${post.id}/edit`)"
            >
              <v-icon left>mdi-pencil</v-icon>
              Modify
            </v-btn>
            <v-btn
              color="error"
              text
              @click="deletePost"
            >
              <v-icon left>mdi-delete</v-icon>
              Delete
            </v-btn>
          </v-card-actions>

          <v-divider></v-divider>

          <!-- 댓글 섹션 -->
          <v-card-text>
            <div class="text-h6 font-weight-bold mb-4">
              <v-icon left>mdi-comment</v-icon>
              Comment
            </div>

            <!-- 댓글 목록 -->
            <v-list>
              <v-list-item
                v-for="comment in post.comments"
                :key="comment.id"
                class="comment-item"
              >
                <v-list-item-content>
                  <v-list-item-title class="d-flex align-center">
                    <v-icon small class="mr-1">mdi-account</v-icon>
                    {{ comment.author }}
                    <v-spacer></v-spacer>
                    <v-btn
                      v-if="isCommentAuthor(comment)"
                      icon
                      small
                      color="error"
                      @click="deleteComment(comment.id)"
                    >
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </v-list-item-title>
                  <v-list-item-subtitle class="mt-2">
                    {{ comment.content }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>

            <!-- 댓글 작성 -->
            <v-form @submit.prevent="addComment" class="mt-4">
              <v-textarea
                v-model="newComment"
                label="Write Comment"
                rows="3"
                outlined
                dense
                hide-details
                class="mb-2"
                placeholder="Remain your Comment..."
              ></v-textarea>
              <v-btn
                color="primary"
                type="submit"
                :disabled="!newComment.trim()"
              >
                Write Comment
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      post: {
        comments: []
      },
      newComment: '',
    };
  },
  computed: {
    isAuthor() {
      const username = localStorage.getItem('username');
      return this.post.author === username;
    }
  },
  async created() {
    try {
      const postId = this.$route.params.id;
      const response = await axios.get(`http://localhost:8000/api/community/posts/${postId}/`);
      this.post = response.data;

      const commentsResponse = await axios.get(`http://localhost:8000/api/community/posts/${postId}/comments/all/`);
      this.post.comments = commentsResponse.data;
      
      console.log('현재 로그인한 사용자:', localStorage.getItem('username'));
      console.log('댓글 목록:', this.post.comments);
    } catch (error) {
      console.error("게시글 조회 실패:", error);
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    isCommentAuthor(comment) {
      const username = localStorage.getItem('username');
      return comment.author === username;
    },
    async deletePost() {
      if (confirm("정말 삭제하시겠습니까?")) {
        try {
          await axios.delete(`http://localhost:8000/api/community/posts/${this.post.id}/`);
          alert("게시글이 삭제되었습니다.");
          this.$router.push('/community');
        } catch (error) {
          console.error("🚨 게시글 삭제 실패:", error);
        }
      }
    },
    async addComment() {
      if (!this.newComment.trim()) return;
      try {
        await axios.post(`http://localhost:8000/api/community/posts/${this.post.id}/comments/`, {
          content: this.newComment,
        });

        this.newComment = '';

        const commentsResponse = await axios.get(`http://localhost:8000/api/community/posts/${this.post.id}/comments/all/`);
        this.post.comments = commentsResponse.data;
      } catch (error) {
        console.error("🚨 댓글 작성 실패:", error);
      }
    },
    async deleteComment(commentId) {
      if (confirm("댓글을 삭제하시겠습니까?")) {
        try {
          await axios.delete(`http://localhost:8000/api/community/comments/${commentId}/`);
          this.post.comments = this.post.comments.filter(c => c.id !== commentId);
        } catch (error) {
          console.error("🚨 댓글 삭제 실패:", error);
        }
      }
    }
  }
};
</script>

<style scoped>
.post-detail-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f6f9fc 0%, #eef2f7 100%);
  padding: 40px 0;
}

.post-detail-card {
  border-radius: 12px;
  overflow: hidden;
}

.v-card-title {
  padding: 24px 16px;
}

.v-card-subtitle {
  padding: 0 16px 16px;
  color: #666;
}

.v-card-text {
  padding: 24px 16px;
  line-height: 1.8;
}

.comment-item {
  border-bottom: 1px solid #eee;
  padding: 16px 0;
}

.comment-item:last-child {
  border-bottom: none;
}

.v-list-item-title {
  font-weight: 500;
  color: #333;
}

.v-list-item-subtitle {
  color: #666;
  white-space: pre-wrap;
}

.v-btn {
  text-transform: none;
  letter-spacing: 0.5px;
}

.v-textarea {
  background-color: #f8f9fa;
  border-radius: 4px;
}
</style>
