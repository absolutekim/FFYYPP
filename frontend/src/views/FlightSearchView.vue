<template>
  <div>
    <h1>항공권 검색</h1>
    <form @submit.prevent="searchFlights">
      <!-- ✅ 출발 공항 검색 -->
      <label>출발 공항:</label>
      <input v-model="origin" @input="fetchAirports('origin')" placeholder="출발지 입력" required />
      <ul v-if="originAirports.length">
        <li v-for="airport in originAirports" :key="airport.id" @click="selectAirport('origin', airport)">
          {{ airport.name }} ({{ airport.code }})
        </li>
      </ul>

      <!-- ✅ 도착 공항 검색 -->
      <label>도착 공항:</label>
      <input v-model="destination" @input="fetchAirports('destination')" placeholder="도착지 입력" required />
      <ul v-if="destinationAirports.length">
        <li v-for="airport in destinationAirports" :key="airport.id" @click="selectAirport('destination', airport)">
          {{ airport.name }} ({{ airport.code }})
        </li>
      </ul>

      <label>출발 날짜:</label>
      <input type="date" v-model="departureDate" required />

      <button type="submit">검색</button>
    </form>

    <!-- ✅ 검색 결과 표시 -->
    <div v-if="flights.length">
      <h2>검색 결과</h2>
      <ul>
        <li v-for="flight in flights" :key="flight.iata" @click="fetchFlightDetails(flight)">
          <img :src="flight.logo" alt="항공사 로고" width="50" />
          <strong>{{ flight.airline }}</strong> - {{ flight.price }} {{ flight.currency }}
          <p>🛫 출발: {{ flight.departureTime || '-' }} | 🛬 도착: {{ flight.arrivalTime || '-' }}</p>
          <p>⏳ 경유 횟수: {{ flight.stops !== undefined ? flight.stops : '데이터 없음' }}</p>
        </li>
      </ul>
    </div>
    <p v-else-if="flights !== null">검색된 항공편이 없습니다.</p>
  </div>
</template>

<script>
import { searchFlights, searchAirports, getFlightDetails } from '@/api/flight';

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
