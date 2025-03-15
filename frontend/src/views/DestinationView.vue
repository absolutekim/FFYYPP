<template>
  <v-container class="destination-container">
    <h1 class="page-title">여행지 탐색</h1>
    
    <!-- NLP 검색 컴포넌트 추가 -->
    <NLPSearchBar />

    <v-row justify="center">
      <v-col cols="12" md="10">
        <h1 class="text-center text-h3 mb-6 font-weight-bold primary--text">
          Destinations
        </h1>

        <!-- Sort options -->
        <v-card-actions class="mb-4">
          <v-spacer></v-spacer>
          <v-btn-toggle
            v-model="sortOrder"
            color="primary"
            group
            mandatory
          >
            <v-btn value="asc">
              <v-icon>mdi-sort-alphabetical-ascending</v-icon>
              Ascending
            </v-btn>
            <v-btn value="desc">
              <v-icon>mdi-sort-alphabetical-descending</v-icon>
              Descending
            </v-btn>
          </v-btn-toggle>
        </v-card-actions>

        <v-card v-if="loading" class="text-center pa-6" elevation="2">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <div class="mt-4">🔄 Loading data...</div>
        </v-card>

        <v-alert v-else-if="error" type="error" class="text-center">
          🚨 Error: {{ error }}
        </v-alert>

        <v-alert v-else-if="destinations.length === 0" type="info" class="text-center">
          😢 No destinations found.
        </v-alert>

        <div v-else>
          <v-row>
            <v-col v-for="destination in paginatedDestinations" 
                   :key="destination.id" 
                   cols="12" 
                   sm="6" 
                   md="4"
                   class="mb-4">
              <v-card 
                class="destination-card h-100" 
                elevation="3"
                data-aos="fade-up"
                data-aos-duration="800"
                data-aos-delay="100"
                @click="$router.push(`/destinations/${destination.id}`)"
                style="cursor: pointer"
              >
                <v-img
                  v-if="destination.image"
                  :src="destination.image"
                  height="200"
                  cover
                  class="destination-image"
                ></v-img>
                
                <v-card-title class="text-h6 font-weight-bold d-flex align-center">
                  {{ destination.name }}
                  <v-chip
                    color="info"
                    variant="outlined"
                    class="ml-2"
                    x-small
                  >
                    {{ destination.country }}
                  </v-chip>
                </v-card-title>

                <v-card-text>
                  <div class="mb-2">
                    <v-chip
                      color="primary"
                      variant="outlined"
                      small
                    >
                      {{ destination.type }}
                    </v-chip>
                  </div>

                  <div v-if="destination.subcategories" class="mb-2">
                    <v-chip
                      v-for="(subcat, index) in destination.subcategories"
                      :key="index"
                      color="secondary"
                      variant="outlined"
                      class="mr-1 mb-1"
                      x-small
                    >
                      {{ subcat }}
                    </v-chip>
                  </div>

                  <p class="text-body-2">
                    <v-icon small color="grey" class="mr-1">mdi-map-marker</v-icon>
                    {{ destination.address }}
                  </p>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <v-pagination
            v-model="currentPage"
            :length="totalPages"
            :total-visible="5"
            color="primary"
            class="mt-6"
            @update:model-value="handlePageChange"
          ></v-pagination>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';
import NLPSearchBar from '@/components/NLPSearchBar.vue';

export default {
  components: {
    NLPSearchBar
  },
  data() {
    return {
      destinations: [],
      loading: true,
      error: null,
      currentPage: 1,
      itemsPerPage: 12,
      sortOrder: 'asc',
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.destinations.length / this.itemsPerPage);
    },
    sortedDestinations() {
      return [...this.destinations].sort((a, b) => {
        const nameA = a.name.toLowerCase();
        const nameB = b.name.toLowerCase();
        return this.sortOrder === 'asc' 
          ? nameA.localeCompare(nameB)
          : nameB.localeCompare(nameA);
      });
    },
    paginatedDestinations() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.sortedDestinations.slice(start, end);
    }
  },
  watch: {
    sortOrder() {
      this.currentPage = 1;
    }
  },
  async created() {
    try {
      const response = await axios.get("http://localhost:8000/api/destinations/");
      this.destinations = response.data;
    } catch (err) {
      this.error = err.message;
      console.error("🚨 Failed to load data:", err);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    handlePageChange(page) {
      this.currentPage = page;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }
};
</script>

<style scoped>
.destination-container {
  padding-top: 2rem;
  padding-bottom: 2rem;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.destination-card {
  transition: transform 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
}

.destination-card:hover {
  transform: translateY(-5px);
}

.destination-image {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.v-card-title {
  padding: 1rem;
  background-color: white;
}

.v-card-text {
  padding: 1rem;
}

/* AOS 애니메이션 커스텀 */
[data-aos] {
  pointer-events: none;
}

[data-aos].aos-animate {
  pointer-events: auto;
}

/* 반응형 디자인 개선 */
@media (max-width: 600px) {
  .destination-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
}
</style>
