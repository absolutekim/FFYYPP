import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

RAPIDAPI_HOST = "booking-com15.p.rapidapi.com"
RAPIDAPI_KEY = "14cebd7147msh3dae59f7abf5ec7p131a26jsnd97a65e180b0"

@csrf_exempt
def search_airports(request):
    """ 공항 자동완성 API """
    query = request.GET.get("query", "")

    if not query:
        return JsonResponse({"error": "쿼리 파라미터가 필요합니다."}, status=400)

    url = f"https://{RAPIDAPI_HOST}/api/v1/flights/searchDestination"
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    params = {"query": query}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return JsonResponse({"error": "공항 정보를 가져오는 데 실패했습니다."}, status=500)

    return JsonResponse(response.json())


# ✅ Django views.py 수정
@csrf_exempt
def search_flights(request):
    try:
        if request.method == "GET":
            origin = request.GET.get("origin")
            destination = request.GET.get("destination")
            depart_date = request.GET.get("depart_date")

            if not origin or not destination or not depart_date:
                return JsonResponse({"error": "Missing parameters"}, status=400)

            print(f"🛫 Searching airport ID for: {origin}, {destination}")

            # ✅ 공항 ID 변환 함수
            def get_airport_id(query):
                url = f"https://{RAPIDAPI_HOST}/api/v1/flights/searchDestination"
                headers = {
                    "x-rapidapi-host": RAPIDAPI_HOST,
                    "x-rapidapi-key": RAPIDAPI_KEY
                }
                params = {"query": query}
                response = requests.get(url, headers=headers, params=params)
                data = response.json()

                if data["status"] and "data" in data:
                    for item in data["data"]:
                        if item["type"] == "AIRPORT":
                            return item["id"]
                return None

            from_id = get_airport_id(origin)
            to_id = get_airport_id(destination)

            print(f"🛫 Converted airport IDs: {from_id} -> {to_id}")

            if not from_id or not to_id:
                return JsonResponse({"error": "Invalid airport code"}, status=400)

            # ✅ 항공편 검색 API 요청
            url = f"https://{RAPIDAPI_HOST}/api/v1/flights/searchFlights"
            headers = {
                "x-rapidapi-host": RAPIDAPI_HOST,
                "x-rapidapi-key": RAPIDAPI_KEY
            }
            params = {
                "fromId": from_id,
                "toId": to_id,
                "departDate": depart_date,
                "pageNo": "1",
                "adults": "1",
                "children": "0",
                "sort": "BEST",
                "cabinClass": "ECONOMY",
                "currency_code": "KRW"
            }

            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            # ✅ 로그 추가
            print(f"🛫 Flight Search API Response: {data}")

            if "data" in data and "flightOffers" in data["data"]:
                flights = []
                for flight in data["data"]["flightOffers"]:
                    # ✅ airline 정보가 flightOffers에 있을 가능성이 높음
                    airline_info = flight.get("segments", [{}])[0].get("legs", [{}])[0].get("carriersData", [{}])[0]

                    flights.append({
                        "airline": airline_info.get("name", "Unknown Airline"),
                        "logo": airline_info.get("logo", ""),
                        "iata": airline_info.get("code", ""),
                        "price": flight.get("priceBreakdown", {}).get("total", {}).get("units", 0),
                        "currency": flight.get("priceBreakdown", {}).get("total", {}).get("currencyCode", "KRW"),
                        "departureTime": flight.get("segments", [{}])[0].get("legs", [{}])[0].get("departureTime", "데이터 없음"),
                        "arrivalTime": flight.get("segments", [{}])[0].get("legs", [{}])[0].get("arrivalTime", "데이터 없음"),
                        "stops": len(flight.get("segments", [{}])[0].get("legs", [{}])[0].get("flightStops", []))
                    })

                return JsonResponse({"flights": flights}, safe=False)

            return JsonResponse({"error": "No flights found"}, status=404)

    except Exception as e:
        print(f"🚨 ERROR: {e}")
        return JsonResponse({"error": str(e)}, status=500)


# ✅ getFlightDetails API 호출 함수 추가
@csrf_exempt
def get_flight_details(request):
    """ 특정 항공편의 상세 정보를 조회하는 API """
    token = request.GET.get("token")

    if not token:
        return JsonResponse({"error": "Missing flight token"}, status=400)  # ✅ 명확한 오류 메시지

    url = f"https://{RAPIDAPI_HOST}/api/v1/flights/getFlightDetails"
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    params = {"token": token}

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return JsonResponse({"error": "Failed to fetch flight details", "status": response.status_code}, status=response.status_code)

        data = response.json()

        if not data or "status" not in data or data["status"] is False:
            return JsonResponse({"error": "Invalid response from API"}, status=500)

        return JsonResponse(data, safe=False)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Request failed: {str(e)}"}, status=500)

    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
