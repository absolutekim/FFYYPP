import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/flights/";

// ✈️ 항공편 검색 함수
export async function searchFlights(origin, destination, departDate) {
  try {
    const response = await axios.get(`${API_BASE_URL}search/`, {
      params: { origin, destination, depart_date: departDate },
      headers: {
        "x-rapidapi-host": "booking-com15.p.rapidapi.com",
        "x-rapidapi-key": "14cebd7147msh3dae59f7abf5ec7p131a26jsnd97a65e180b0",
      },
    });

    console.log("✅ API 응답 데이터:", response.data);

    if (response.data && response.data.flights && Array.isArray(response.data.flights)) {
      return response.data;
    } else {
      console.warn("⚠️ API 응답에 항공편 정보가 없습니다.");
      return { flights: [] };
    }
  } catch (error) {
    console.error("🚨 Django API 요청 실패:", error);
    return { flights: [] };
  }
}

// 🏙️ 공항 자동완성 검색 함수
export async function searchAirports(query) {
  try {
    const response = await axios.get(`${API_BASE_URL}search-airports/`, {
      params: { query },
    });

    return response.data.data || []; // ✅ 공항 정보 리스트 반환
  } catch (error) {
    console.error("🚨 공항 검색 실패:", error);
    return [];
  }
}

// ✅ `getFlightDetails` 함수 추가 (Vue에서 사용할 수 있도록 설정)
export async function getFlightDetails(token) {
  try {
    const response = await axios.get(`${API_BASE_URL}details/`, {
      params: { token }
    });

    console.log("✅ Flight Details API 응답:", response.data);

    return response.data;
  } catch (error) {
    console.error("🚨 getFlightDetails API 오류:", error);
    return {};
  }
}
