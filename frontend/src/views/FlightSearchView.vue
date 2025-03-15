<template>
  <v-container class="search-container">
    <v-row justify="center">
      <v-col cols="12" md="6">
        <v-card class="search-box" data-aos="fade-up" elevation="10">
          <v-card-title class="text-h4 font-weight-bold">
            ✈️ 항공권 검색
          </v-card-title>

          <v-card-text>
            <form @submit.prevent="searchFlights" class="search-form">
              <div class="form-group">
                <v-text-field
                  v-model="origin"
                  @input="fetchAirports('origin')"
                  label="출발 공항"
                  placeholder="출발지 입력"
                  outlined
                  dense
                  required
                ></v-text-field>
                <v-list v-if="originAirports.length" class="dropdown">
                  <v-list-item
                    v-for="airport in originAirports"
                    :key="airport.id"
                    @click="selectAirport('origin', airport)"
                  >
                    {{ airport.name }} ({{ airport.code }})
                  </v-list-item>
                </v-list>
              </div>

              <div class="form-group">
                <v-text-field
                  v-model="destination"
                  @input="fetchAirports('destination')"
                  label="도착 공항"
                  placeholder="도착지 입력"
                  outlined
                  dense
                  required
                ></v-text-field>
                <v-list v-if="destinationAirports.length" class="dropdown">
                  <v-list-item
                    v-for="airport in destinationAirports"
                    :key="airport.id"
                    @click="selectAirport('destination', airport)"
                  >
                    {{ airport.name }} ({{ airport.code }})
                  </v-list-item>
                </v-list>
              </div>

              <div class="form-group">
                <v-text-field
                  v-model="departureDate"
                  label="출발 날짜"
                  type="date"
                  outlined
                  dense
                  required
                  :min="new Date().toISOString().substr(0, 10)"
                ></v-text-field>
              </div>

              <v-btn
                type="submit"
                color="primary"
                block
                large
                class="mt-4"
                elevation="2"
              >
                <v-icon left>mdi-magnify</v-icon>
                검색
              </v-btn>
            </form>
          </v-card-text>
        </v-card>

        <!-- 검색 결과 -->
        <div v-if="flights.length" class="results-container" data-aos="fade-up" data-aos-delay="200">
          <h2 class="text-h4 font-weight-bold white--text mb-4">🔎 검색 결과</h2>

          <v-card
            v-for="flight in flights"
            :key="flight.iata"
            class="mb-4"
            elevation="4"
            data-aos="fade-up"
            data-aos-delay="300"
          >
            <v-card-text class="flight-card">
              <img :src="flight.logo" alt="항공사 로고" class="flight-logo" />
              <div class="flight-info">
                <div class="text-h6">{{ flight.airline }}</div>
                <div class="text-h5 primary--text">{{ flight.price }} {{ flight.currency }}</div>
                <div>🛫 {{ flight.departureTime || '-' }} | 🛬 {{ flight.arrivalTime || '-' }}</div>
                <div>⏳ 경유 횟수: {{ flight.stops !== undefined ? flight.stops : '데이터 없음' }}</div>
              </div>
            </v-card-text>
          </v-card>
        </div>

        <v-alert
          v-else-if="flights !== null"
          type="info"
          class="mt-4"
          data-aos="fade-up"
          data-aos-delay="200"
        >
          검색된 항공편이 없습니다.
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { searchFlights, searchAirports, getFlightDetails } from '@/api/flight';
import AOS from 'aos';
import 'aos/dist/aos.css';

export default {
  data() {
    return {
      origin: '',
      destination: '',
      departureDate: '',
      flights: [],
      originAirports: [],
      destinationAirports: [],
    };
  },
  mounted() {
    AOS.init({
      duration: 800,
      once: true
    });
  },
  methods: {
    async searchFlights() {
      this.flights = []; // ✅ 기존 데이터 초기화
      try {
        const results = await searchFlights(this.origin, this.destination, this.departureDate);
        console.log("✅ API 응답 데이터:", results);

        if (results && results.flights && Array.isArray(results.flights)) {
          this.flights = results.flights.map(flight => ({
            airline: flight.airline,
            logo: flight.logo,
            iata: flight.iata,
            price: flight.price,
            currency: flight.currency,
            departureTime: flight.departureTime || "데이터 없음", // ✅ API 응답에서 가져옴
            arrivalTime: flight.arrivalTime || "데이터 없음",
            stops: flight.stops !== undefined ? flight.stops : "데이터 없음",
          }));
        } else {
          console.warn("⚠️ API 응답에 항공편 정보 없음.");
          this.flights = [];
        }
      } catch (error) {
        console.error("🚨 항공편 검색 실패:", error);
        this.flights = [];
      }
    },

    async fetchFlightDetails(flight) {
      if (!flight.token) {
        console.warn("⚠️ 항공편 토큰이 없습니다. 요청을 보내지 않습니다.");
        return; // ✅ token이 없는 경우 API 요청을 보내지 않음
      }

      try {
        console.log("📡 `getFlightDetails` API 호출:", flight.token);
        const details = await getFlightDetails(flight.token);

        if (details && details.departureTime && details.arrivalTime) {
          flight.departureTime = details.departureTime;
          flight.arrivalTime = details.arrivalTime;
        } else {
          console.warn("⚠️ 상세 정보 없음.");
          flight.departureTime = "정보 없음";
          flight.arrivalTime = "정보 없음";
        }
      } catch (error) {
        console.error("🚨 `getFlightDetails` API 오류:", error);
        flight.departureTime = "정보 없음"; // 오류 발생 시 기본값 유지
        flight.arrivalTime = "정보 없음";
      }
    },

    async fetchAirports(type) {
      const query = type === 'origin' ? this.origin : this.destination;
      if (query.length < 2) return;

      const airports = await searchAirports(query);
      if (type === 'origin') {
        this.originAirports = airports;
      } else {
        this.destinationAirports = airports;
      }
    },

    selectAirport(type, airport) {
      if (type === 'origin') {
        this.origin = airport.code;
        this.originAirports = [];
      } else {
        this.destination = airport.code;
        this.destinationAirports = [];
      }

      console.log(`✅ ${type} 공항 선택됨:`, airport);

      // ✅ 공항을 선택한 후 기존 검색 결과를 초기화하지 않도록 변경
      // this.flights = [];  // ❌ 기존 검색 결과 초기화 X
    }
  }
};
</script>

<style scoped>
.search-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #e39047 0%, #65b009 100%);
  padding: 40px 0;
}

.flight-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.flight-logo {
  width: 60px;
  height: 60px;
  object-fit: contain;
}

.flight-info {
  flex: 1;
}

.dropdown {
  position: absolute;
  width: 100%;
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}
</style>