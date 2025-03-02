<template>
  <div>
    <h1>{{ post.title }}</h1>
    <p>{{ post.content }}</p>
    <p><strong>작성자:</strong> {{ post.author }}</p>
    <p><small>작성 날짜: {{ post.created_at }}</small></p>

    <!-- 수정 및 삭제 버튼 -->
    <div v-if="isAuthor">
      <router-link :to="`/community/${post.id}/edit`">게시글 수정</router-link>
      <button @click="deletePost">게시글 삭제</button>
    </div>

    <!-- 댓글 목록 -->
    <h2>댓글</h2>
    <ul>
      <li v-for="comment in post.comments" :key="comment.id">
        <p><strong>{{ comment.author }}:</strong> {{ comment.content }}</p>
        <button v-if="isCommentAuthor(comment)" @click="deleteComment(comment.id)">댓글 삭제</button>
      </li>
    </ul>

    <!-- 댓글 작성 -->
    <textarea v-model="newComment" placeholder="댓글 작성..."></textarea>
    <button @click="addComment">댓글 추가</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      post: {
        comments: [] // ✅ 기본값을 빈 배열로 설정 (초기 로딩 시 오류 방지)
      },
      newComment: '',
    };
  },
  computed: {
    isAuthor() {
      const userId = localStorage.getItem('user_id'); // ✅ 로그인한 유저 ID 가져오기
      return this.post.author_id === parseInt(userId); // ✅ 게시글 작성자와 비교
    },
    isCommentAuthor() {
      return (comment) => {
        const userId = localStorage.getItem('user_id'); // ✅ 로그인한 유저 ID 가져오기
        return comment.author_id === parseInt(userId); // ✅ 댓글 작성자와 비교
      };
    }
  },
  async created() {
  try {
    const postId = this.$route.params.id;
    const response = await axios.get(`http://localhost:8000/api/community/posts/${postId}/`);
    this.post = response.data;

    if (!this.post.comments) {
      this.post.comments = [];
    } else {
      // ✅ GET 요청 경로를 posts/{post_id}/comments/all/ 로 변경
      const commentsResponse = await axios.get(`http://localhost:8000/api/community/posts/${postId}/comments/all/`);
      this.post.comments = commentsResponse.data;
    }
  } catch (error) {
    console.error("🚨 게시글 조회 실패:", error);
  }
}
,
  methods: {
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

    // ✅ 댓글 추가 후, 서버에서 다시 댓글을 가져오기
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
