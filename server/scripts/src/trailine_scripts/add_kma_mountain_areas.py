import argparse

import pandas as pd

from trailine_scripts.common.database import get_db
from trailine_model.models.weather import KmaMountainWeatherArea


def import_kma_mountain_areas(file_path: str):
    print(f"Reading {file_path}...")
    try:
        # 엑셀 파일 읽기
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading excel file: {e}")
        return

    # 필수 컬럼 확인
    required_columns = ['mountainNum', '지점명', '위도(도)', '경도(도)', '고도(m)']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Missing required column '{col}'")
            return

    count = 0
    with get_db() as db:
        for index, row in df.iterrows():
            # WKT 포맷으로 POINT 생성 (경도 위도 순서)
            point_wkt = f"POINT({row['경도(도)']} {row['위도(도)']})"
            
            # 모델 인스턴스 생성
            area = KmaMountainWeatherArea(
                code=int(row['mountainNum']),
                name=str(row['지점명']),
                geom=point_wkt,
                geog=point_wkt,
                elevation=int(row['고도(m)'])
            )
            
            # 동일한 코드가 있는지 확인 (중복 방지 로직이 필요한 경우)
            existing = db.query(KmaMountainWeatherArea).filter_by(code=area.code).first()
            if existing:
                print(f"Skipping duplicate code: {area.code} ({area.name})")
                continue
                
            db.add(area)
            count += 1
            
            if count % 100 == 0:
                print(f"Processed {count} rows...")
    
    print(f"Import completed successfully. {count} rows added.")

def main():
    parser = argparse.ArgumentParser(description="KMA Mountain Weather Areas Excel to DB importer")
    parser.add_argument("--file", required=True, help="Path to the excel file")
    
    args = parser.parse_args()
    import_kma_mountain_areas(args.file)

if __name__ == "__main__":
    main()
