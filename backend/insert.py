import os
import django
import pandas as pd

# ✅ Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # Django 프로젝트 설정 지정
django.setup()  # Django ORM 사용 가능하도록 설정

from destinations.models import Location  # ✅ Django ORM 사용

# ✅ CSV 파일 로드
csv_path = "dataset_tripadvisor_2025-03-06_08-09-58-598.csv"  # 파일 확장자 확인 필요
df = pd.read_csv(csv_path)

# ✅ 필요한 컬럼만 선택
main_columns = [
    "id", "name", "description", "category",
    "address", "addressObj/city", "addressObj/state", "addressObj/country", "addressObj/postalcode",
    "addressObj/street1", "addressObj/street2",
    "latitude", "longitude", "localAddress", "localName", "locationString",
    "image", "website", "email",
    "type"
]

# ✅ 실제 존재하는 컬럼만 필터링 (원본 유지)
df_filtered = df[[col for col in main_columns if col in df.columns]].copy()

# ✅ `subcategories/`와 `subtype/` 컬럼을 동적으로 가져오기
subcategories_cols = [col for col in df.columns if col.startswith("subcategories/")]
subtypes_cols = [col for col in df.columns if col.startswith("subtype/")]

# ✅ DataFrame에 해당 컬럼이 있는지 확인 후 추가 (원본 유지)
for col in subcategories_cols + subtypes_cols:
    df_filtered.loc[:, col] = df[col].fillna("").copy()

# ✅ Django ORM을 사용해 데이터 삽입 (중복 데이터 방지)
for _, row in df_filtered.iterrows():
    location, created = Location.objects.update_or_create(
        id=row["id"],  # 기준이 되는 키
        defaults={  # ✅ 이미 존재하면 업데이트될 필드
            "name": row["name"],
            "description": row["description"] if pd.notna(row["description"]) else None,
            "category": row["category"] if pd.notna(row["category"]) else None,

            "address": row["address"] if pd.notna(row["address"]) else None,
            "city": row["addressObj/city"] if pd.notna(row["addressObj/city"]) else None,
            "state": row["addressObj/state"] if pd.notna(row["addressObj/state"]) else None,
            "country": row["addressObj/country"] if pd.notna(row["addressObj/country"]) else None,
            "postal_code": row["addressObj/postalcode"] if pd.notna(row["addressObj/postalcode"]) else None,
            "street1": row["addressObj/street1"] if pd.notna(row["addressObj/street1"]) else None,
            "street2": row["addressObj/street2"] if pd.notna(row["addressObj/street2"]) else None,

            "latitude": row["latitude"] if pd.notna(row["latitude"]) else None,
            "longitude": row["longitude"] if pd.notna(row["longitude"]) else None,

            "local_address": row["localAddress"] if pd.notna(row["localAddress"]) else None,
            "local_name": row["localName"] if pd.notna(row["localName"]) else None,
            "location_string": row["locationString"] if pd.notna(row["locationString"]) else None,

            "image": row["image"] if pd.notna(row["image"]) else None,
            "website": row["website"] if pd.notna(row["website"]) else None,
            "email": row["email"] if pd.notna(row["email"]) else None,

            "type": row["type"] if pd.notna(row["type"]) else None,

            # ✅ 존재하는 `subcategories/`와 `subtype/` 컬럼만 리스트로 저장
            "subcategories": [row[col] for col in subcategories_cols if col in row.index and pd.notna(row[col]) and row[col] != ""],
            "subtypes": [row[col] for col in subtypes_cols if col in row.index and pd.notna(row[col]) and row[col] != ""]
        }
    )

    if created:
        print(f"✅ 새 데이터 추가: {location.name}")
    else:
        print(f"🔄 기존 데이터 업데이트: {location.name}")

print("✅ 데이터 삽입 완료!")
