"""
Data preprocessing script
Loads Seoul daycare data from JSON and inserts into SQLite database
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add app directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app"))

from database import init_db, get_session, DaycareCenter
from config import settings


def clean_value(value, value_type="str"):
    """Clean and convert values from JSON"""
    if value is None or value == "":
        return None

    if value_type == "int":
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    elif value_type == "float":
        try:
            # Handle coordinate values
            val = float(value)
            # Filter out invalid coordinates (0.0 or default values)
            if val == 0.0 or val == 37.566470 or val == 126.977963:
                return None
            return val
        except (ValueError, TypeError):
            return None
    else:  # string
        return str(value).strip() if value else None


def load_json_data(file_path: Path):
    """Load and parse JSON data"""
    print(f"📂 Loading data from: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Expected format: {"DESCRIPTION": {...}, "DATA": [...]}
    if "DATA" not in data:
        raise ValueError("Invalid JSON format: 'DATA' key not found")

    records = data["DATA"]
    print(f"✅ Loaded {len(records)} records from JSON")

    return records


def create_daycare_center(record: dict) -> DaycareCenter:
    """Create DaycareCenter instance from JSON record"""

    return DaycareCenter(
        # Basic info
        stcode=clean_value(record.get("stcode")),
        crname=clean_value(record.get("crname")),
        crtypename=clean_value(record.get("crtypename")),
        crstatusname=clean_value(record.get("crstatusname")),
        craddr=clean_value(record.get("craddr")),
        sigunname=clean_value(record.get("sigunname")),
        zipcode=clean_value(record.get("zipcode")),
        la=clean_value(record.get("la"), "float"),
        lo=clean_value(record.get("lo"), "float"),
        crtelno=clean_value(record.get("crtelno")),
        crfaxno=clean_value(record.get("crfaxno")),
        crhome=clean_value(record.get("crhome")),
        # Operation info
        crcapat=clean_value(record.get("crcapat"), "int"),
        crchcnt=clean_value(record.get("crchcnt"), "int"),
        crcnfmdt=clean_value(record.get("crcnfmdt")),
        crabldt=clean_value(record.get("crabldt")),
        crpausebegindt=clean_value(record.get("crpausebegindt")),
        crpauseenddt=clean_value(record.get("crpauseenddt")),
        # Special services
        crspec=clean_value(record.get("crspec")),
        crcargbname=clean_value(record.get("crcargbname")),
        # Facility info
        nrtrroomcnt=clean_value(record.get("nrtrroomcnt"), "int"),
        nrtrroomsize=clean_value(record.get("nrtrroomsize"), "float"),
        plgrdco=clean_value(record.get("plgrdco"), "int"),
        cctvinstlcnt=clean_value(record.get("cctvinstlcnt"), "int"),
        # Staff info
        chcrtescnt=clean_value(record.get("chcrtescnt"), "int"),
        em_cnt_tot=clean_value(record.get("em_cnt_tot"), "int"),
        em_cnt_a1=clean_value(record.get("em_cnt_a1"), "int"),
        em_cnt_a2=clean_value(record.get("em_cnt_a2"), "int"),
        em_cnt_a3=clean_value(record.get("em_cnt_a3"), "int"),
        em_cnt_a4=clean_value(record.get("em_cnt_a4"), "int"),
        em_cnt_a5=clean_value(record.get("em_cnt_a5"), "int"),
        em_cnt_a6=clean_value(record.get("em_cnt_a6"), "int"),
        em_cnt_a7=clean_value(record.get("em_cnt_a7"), "int"),
        em_cnt_a8=clean_value(record.get("em_cnt_a8"), "int"),
        em_cnt_a10=clean_value(record.get("em_cnt_a10"), "int"),
        # Tenure
        em_cnt_0y=clean_value(record.get("em_cnt_0y"), "int"),
        em_cnt_1y=clean_value(record.get("em_cnt_1y"), "int"),
        em_cnt_2y=clean_value(record.get("em_cnt_2y"), "int"),
        em_cnt_4y=clean_value(record.get("em_cnt_4y"), "int"),
        em_cnt_6y=clean_value(record.get("em_cnt_6y"), "int"),
        # Children by age
        child_cnt_tot=clean_value(record.get("child_cnt_tot"), "int"),
        child_cnt_00=clean_value(record.get("child_cnt_00"), "int"),
        child_cnt_01=clean_value(record.get("child_cnt_01"), "int"),
        child_cnt_02=clean_value(record.get("child_cnt_02"), "int"),
        child_cnt_03=clean_value(record.get("child_cnt_03"), "int"),
        child_cnt_04=clean_value(record.get("child_cnt_04"), "int"),
        child_cnt_05=clean_value(record.get("child_cnt_05"), "int"),
        child_cnt_m2=clean_value(record.get("child_cnt_m2"), "int"),
        child_cnt_m5=clean_value(record.get("child_cnt_m5"), "int"),
        child_cnt_sp=clean_value(record.get("child_cnt_sp"), "int"),
        # Classes by age
        class_cnt_tot=clean_value(record.get("class_cnt_tot"), "int"),
        class_cnt_00=clean_value(record.get("class_cnt_00"), "int"),
        class_cnt_01=clean_value(record.get("class_cnt_01"), "int"),
        class_cnt_02=clean_value(record.get("class_cnt_02"), "int"),
        class_cnt_03=clean_value(record.get("class_cnt_03"), "int"),
        class_cnt_04=clean_value(record.get("class_cnt_04"), "int"),
        class_cnt_05=clean_value(record.get("class_cnt_05"), "int"),
        class_cnt_m2=clean_value(record.get("class_cnt_m2"), "int"),
        class_cnt_m5=clean_value(record.get("class_cnt_m5"), "int"),
        class_cnt_sp=clean_value(record.get("class_cnt_sp"), "int"),
        # Metadata
        datastdrdt=clean_value(record.get("datastdrdt")),
        work_dttm=clean_value(record.get("work_dttm")),
    )


def insert_data(records: list):
    """Insert records into database"""
    print(f"\n📥 Inserting {len(records)} records into database...")

    session = get_session()
    inserted = 0
    skipped = 0
    errors = 0

    try:
        for i, record in enumerate(records, 1):
            try:
                # Check if record already exists
                stcode = record.get("stcode")
                existing = (
                    session.query(DaycareCenter)
                    .filter(DaycareCenter.stcode == stcode)
                    .first()
                )

                if existing:
                    skipped += 1
                    continue

                # Create new record
                daycare = create_daycare_center(record)
                session.add(daycare)
                inserted += 1

                # Commit in batches
                if i % 100 == 0:
                    session.commit()
                    print(f"  ✓ Processed {i}/{len(records)} records...")

            except Exception as e:
                errors += 1
                print(f"  ⚠️  Error processing record {i}: {e}")
                continue

        # Final commit
        session.commit()
        print(f"\n✅ Data insertion complete!")
        print(f"   - Inserted: {inserted}")
        print(f"   - Skipped (duplicates): {skipped}")
        print(f"   - Errors: {errors}")

    except Exception as e:
        session.rollback()
        print(f"❌ Database error: {e}")
        raise
    finally:
        session.close()


def main():
    """Main preprocessing workflow"""
    print("=" * 60)
    print("Seoul Daycare Data Preprocessing")
    print("=" * 60)

    # Initialize database
    print("\n1️⃣  Initializing database...")
    init_db()

    # Load JSON data
    print("\n2️⃣  Loading JSON data...")
    raw_data_path = settings.RAW_DATA_DIR / "seoul_daycare_raw.json"

    if not raw_data_path.exists():
        print(f"❌ Data file not found: {raw_data_path}")
        return

    records = load_json_data(raw_data_path)

    # Insert data
    print("\n3️⃣  Inserting data into database...")
    insert_data(records)

    # Verify
    print("\n4️⃣  Verifying database...")
    session = get_session()
    total_count = session.query(DaycareCenter).count()
    print(f"✅ Total records in database: {total_count}")

    # Show sample
    print("\n📋 Sample records:")
    samples = session.query(DaycareCenter).limit(3).all()
    for sample in samples:
        print(f"   - {sample.crname} ({sample.crtypename}) - {sample.sigunname}")

    session.close()

    print("\n" + "=" * 60)
    print("✅ Preprocessing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
