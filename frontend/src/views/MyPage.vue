<template>
  <v-container class="mypage">
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card class="mx-auto" elevation="3">
          <v-card-title class="text-h4 font-weight-bold text-center py-6 primary white--text">
            마이페이지
          </v-card-title>

          <v-card-text v-if="profile" class="pa-6">
            <v-row>
              <!-- 프로필 이미지 섹션 -->
              <v-col cols="12" sm="4" class="text-center">
                <v-avatar size="200" class="profile-avatar">
                  <v-img
                    :src="profile.profile_image || `https://ui-avatars.com/api/?name=${profile.user.username}&background=random&size=200`"
                    alt="프로필 이미지"
                  />
                </v-avatar>
              </v-col>

              <!-- 프로필 정보 섹션 -->
              <v-col cols="12" sm="8">
                <div v-if="!isEditing">
                  <h2 class="text-h5 font-weight-bold mb-4">
                    {{ profile.nickname || profile.user.username }}
                  </h2>
                  <v-card outlined class="pa-4 mb-4 bio-card">
                    <p class="text-body-1">{{ profile.bio || '소개글이 없습니다.' }}</p>
                  </v-card>
                  <v-btn
                    color="primary"
                    @click="startEditing"
                    prepend-icon="mdi-account-edit"
                    class="mr-2"
                  >
                    프로필 수정
                  </v-btn>
                  <v-btn
                    color="error"
                    @click="showDeleteAccountDialog"
                    prepend-icon="mdi-account-remove"
                  >
                    계정 삭제
                  </v-btn>
                </div>

                <!-- 수정 폼 -->
                <v-form v-else @submit.prevent="updateProfile">
                  <v-text-field
                    v-model="editForm.nickname"
                    label="닉네임"
                    outlined
                    dense
                    class="mb-4"
                  />
                  
                  <v-textarea
                    v-model="editForm.bio"
                    label="소개글"
                    outlined
                    auto-grow
                    rows="4"
                    class="mb-4"
                  />

                  <v-file-input
                    v-model="editForm.profile_image"
                    label="프로필 이미지"
                    prepend-icon="mdi-camera"
                    outlined
                    dense
                    accept="image/*"
                    class="mb-4"
                  />

                  <v-btn
                    color="primary"
                    type="submit"
                    class="mr-4"
                    prepend-icon="mdi-content-save"
                  >
                    저장
                  </v-btn>
                  <v-btn
                    color="grey"
                    @click="cancelEditing"
                    prepend-icon="mdi-close"
                  >
                    취소
                  </v-btn>
                </v-form>
              </v-col>
            </v-row>
          </v-card-text>

          <!-- 로딩 상태 표시 -->
          <v-card-text v-else class="text-center pa-6">
            <v-progress-circular
              indeterminate
              color="primary"
              size="64"
            />
          </v-card-text>
        </v-card>

        <!-- 좋아요 및 리뷰 탭 -->
        <v-card class="mx-auto mt-6" elevation="3">
          <v-tabs v-model="activeTab" background-color="primary" dark>
            <v-tab value="likes">
              <v-icon left>mdi-heart</v-icon>
              좋아요한 여행지
            </v-tab>
            <v-tab value="reviews">
              <v-icon left>mdi-comment</v-icon>
              내 리뷰
            </v-tab>
          </v-tabs>

          <v-card-text class="pa-0">
            <v-window v-model="activeTab">
              <!-- 좋아요 탭 -->
              <v-window-item value="likes">
                <div class="pa-4">
                  <user-likes />
                </div>
              </v-window-item>

              <!-- 리뷰 탭 -->
              <v-window-item value="reviews">
                <div class="pa-4">
                  <user-reviews />
                </div>
              </v-window-item>
            </v-window>
          </v-card-text>
        </v-card>

        <!-- 계정 삭제 다이얼로그 -->
        <v-dialog v-model="deleteAccountDialog" max-width="500">
          <v-card>
            <v-card-title class="text-h5 error white--text">
              계정 삭제
            </v-card-title>
            <v-card-text class="pt-4">
              <p class="mb-4">계정을 삭제하면 모든 데이터가 영구적으로 삭제되며 복구할 수 없습니다. 정말로 삭제하시겠습니까?</p>
              <v-form @submit.prevent="deleteAccount">
                <v-text-field
                  v-model="deleteAccountPassword"
                  label="비밀번호 확인"
                  type="password"
                  outlined
                  dense
                  :error-messages="deleteAccountError"
                  required
                ></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="grey" text @click="deleteAccountDialog = false">
                취소
              </v-btn>
              <v-btn color="error" @click="deleteAccount" :loading="isDeleting">
                계정 삭제
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'
import UserLikes from '@/components/UserLikes.vue'
import UserReviews from '@/components/UserReviews.vue'

export default {
  name: 'MyPage',
  components: {
    UserLikes,
    UserReviews
  },
  data() {
    return {
      profile: null,
      isEditing: false,
      activeTab: 'likes',
      editForm: {
        nickname: '',
        bio: '',
        profile_image: null
      },
      deleteAccountDialog: false,
      deleteAccountPassword: '',
      deleteAccountError: '',
      isDeleting: false
    }
  },
  methods: {
    async fetchProfile() {
      try {
        const response = await axios.get('/api/mypage/profile/')
        this.profile = response.data
      } catch (error) {
        console.error('프로필 로딩 실패:', error)
      }
    },
    startEditing() {
      this.editForm = {
        nickname: this.profile.nickname,
        bio: this.profile.bio
      }
      this.isEditing = true
    },
    cancelEditing() {
      this.isEditing = false
    },
    handleImageChange(event) {
      this.editForm.profile_image = event.target.files[0]
    },
    async updateProfile() {
      try {
        const formData = new FormData()
        formData.append('nickname', this.editForm.nickname)
        formData.append('bio', this.editForm.bio)
        if (this.editForm.profile_image) {
          formData.append('profile_image', this.editForm.profile_image)
        }

        await axios.put('/api/mypage/profile/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        await this.fetchProfile()
        this.isEditing = false
      } catch (error) {
        console.error('프로필 업데이트 실패:', error)
      }
    },
    showDeleteAccountDialog() {
      this.deleteAccountDialog = true
      this.deleteAccountPassword = ''
      this.deleteAccountError = ''
    },
    
    async deleteAccount() {
      if (!this.deleteAccountPassword) {
        this.deleteAccountError = '비밀번호를 입력해주세요.'
        return
      }
      
      this.isDeleting = true
      
      try {
        await axios.delete('/api/accounts/delete-account/', {
          data: {
            password: this.deleteAccountPassword
          }
        })
        
        // 로그아웃 처리
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        
        // 인증 헤더 제거
        delete axios.defaults.headers.common['Authorization']
        
        // 인증 상태 변경 이벤트 발생
        document.dispatchEvent(new Event('auth-changed'))
        
        // 알림 메시지 (Vuex 스토어가 없으므로 alert 사용)
        alert('계정이 성공적으로 삭제되었습니다.')
        
        // 페이지 새로고침 후 홈페이지로 이동
        window.location.href = '/'
      } catch (error) {
        console.error('계정 삭제 실패:', error)
        
        if (error.response && error.response.data && error.response.data.error) {
          this.deleteAccountError = error.response.data.error
        } else {
          this.deleteAccountError = '계정 삭제 중 오류가 발생했습니다.'
        }
      } finally {
        this.isDeleting = false
      }
    }
  },
  created() {
    this.fetchProfile()
  }
}
</script>

<style scoped>
.mypage {
  padding-top: 40px;
  padding-bottom: 40px;
}

.profile-avatar {
  border: 4px solid #1976d2;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.bio-card {
  background-color: #f5f5f5;
  min-height: 100px;
}

.v-card {
  border-radius: 16px;
}

.v-card-title {
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
}

/* 반응형 디자인을 위한 미디어 쿼리 */
@media (max-width: 600px) {
  .profile-avatar {
    margin-bottom: 20px;
  }
  
  .v-card-title {
    font-size: 1.5rem !important;
  }
}
</style> 