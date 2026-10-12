
import pandas as pd
from pathlib import Path

from src.column_mapping import auto_map_columns

from src.preprocessing import (
    create_daily_data,
    create_region_data,
    create_product_data,
    create_category_data,
)

from src.anomaly_detector import (
    detect_overall_sales_drops,
    detect_overall_sales_spikes,
    detect_category_sales_spikes,
    detect_product_sales_spikes,
    detect_profit_margin_drops,
    detect_regional_sales_drops,
)


BASE_DIR = Path(__file__).parent

DATA_PATH = (
    BASE_DIR / "data" / "ecommerce_business_monitoring_dataset.xlsx"
)

ALTERNATIVE_DATA_PATH = (
    BASE_DIR / "data" / "test_ecommerce_alternative_columns.xlsx"
)

passed = 0
failed = 0


def run_test(name, test_function):
    global passed, failed

    try:
        test_function()
        print(f"PASS: {name}")
        passed += 1
    except Exception as error:
        print(f"FAIL: {name} -> {error}")
        failed += 1


def test_dataset():
    global df

    df = pd.read_excel(DATA_PATH, sheet_name="Transactions")

    required_columns = [
        "Order_ID",
        "Date",
        "Product_Name",
        "Category",
        "Region",
        "Quantity",
        "Sales",
        "Profit",
    ]

    missing = set(required_columns) - set(df.columns)

    assert not missing, f"Missing columns: {sorted(missing)}"
    assert not df.empty, "Default dataset is empty"

    print(f"  Rows found: {len(df)}")
    print(f"  Columns found: {len(df.columns)}")


def test_alternative_dataset():
    data = pd.read_excel(
        ALTERNATIVE_DATA_PATH,
        sheet_name="Transactions",
    )

    expected_columns = [
        "Transaction ID",
        "Order Date",
        "Product",
        "Product Category",
        "Sales Region",
        "Units Sold",
        "Revenue",
        "Net Profit",
    ]

    missing = [
        column for column in expected_columns
        if column not in data.columns
    ]

    assert not missing, f"Missing alternative columns: {missing}"
    assert not data.empty, "Alternative dataset is empty"

    print(f"  Rows found: {len(data)}")
    print(f"  Columns found: {len(data.columns)}")


def test_alternative_column_mapping():
    global alternative_df

    data = pd.read_excel(
        ALTERNATIVE_DATA_PATH,
        sheet_name="Transactions",
    )

    alternative_df = auto_map_columns(data)

    required_columns = [
        "Order_ID",
        "Date",
        "Product_Name",
        "Category",
        "Region",
        "Quantity",
        "Sales",
        "Profit",
    ]

    missing = [
        column for column in required_columns
        if column not in alternative_df.columns
    ]

    assert not missing, f"Column mapping failed: {missing}"
    assert not alternative_df.empty, "Mapped dataset is empty"

    print(f"  Mapped rows: {len(alternative_df)}")
    print("  All eight required columns mapped successfully")


def test_preprocessing():
    global daily_data, region_data, product_data, category_data

    daily_data = create_daily_data(df)
    region_data = create_region_data(df)
    product_data = create_product_data(df)
    category_data = create_category_data(df)

    assert not daily_data.empty, "Daily data is empty"
    assert not region_data.empty, "Region data is empty"
    assert not product_data.empty, "Product data is empty"
    assert not category_data.empty, "Category data is empty"


def test_alternative_preprocessing():
    global alt_daily_data, alt_region_data
    global alt_product_data, alt_category_data

    data = alternative_df.copy()

    # Convert mapped columns to appropriate data types.
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    for column in ["Sales", "Profit", "Quantity"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(
        subset=["Order_ID", "Date", "Sales", "Profit", "Quantity"]
    )

    assert not data.empty, "No valid rows after cleaning alternative data"

    alt_daily_data = create_daily_data(data)
    alt_region_data = create_region_data(data)
    alt_product_data = create_product_data(data)
    alt_category_data = create_category_data(data)

    assert not alt_daily_data.empty, "Alternative daily data is empty"
    assert not alt_region_data.empty, "Alternative region data is empty"
    assert not alt_product_data.empty, "Alternative product data is empty"
    assert not alt_category_data.empty, "Alternative category data is empty"


def test_overall_drop():
    _, events = detect_overall_sales_drops(daily_data)
    assert isinstance(events, pd.DataFrame)


def test_overall_spike():
    _, events = detect_overall_sales_spikes(daily_data)
    assert isinstance(events, pd.DataFrame)


def test_category_spike():
    _, events = detect_category_sales_spikes(category_data)
    assert isinstance(events, pd.DataFrame)


def test_product_spike():
    _, events = detect_product_sales_spikes(product_data)
    assert isinstance(events, pd.DataFrame)


def test_profit_margin_drop():
    _, events = detect_profit_margin_drops(category_data)
    assert isinstance(events, pd.DataFrame)


def test_regional_drop():
    _, events = detect_regional_sales_drops(region_data)
    assert isinstance(events, pd.DataFrame)


def test_alternative_detectors():
    test_cases = [
        (
            "Overall sales drop",
            detect_overall_sales_drops,
            alt_daily_data,
        ),
        (
            "Overall sales spike",
            detect_overall_sales_spikes,
            alt_daily_data,
        ),
        (
            "Category sales spike",
            detect_category_sales_spikes,
            alt_category_data,
        ),
        (
            "Product sales spike",
            detect_product_sales_spikes,
            alt_product_data,
        ),
        (
            "Profit margin drop",
            detect_profit_margin_drops,
            alt_category_data,
        ),
        (
            "Regional sales drop",
            detect_regional_sales_drops,
            alt_region_data,
        ),
    ]

    for name, detector, processed_data in test_cases:
        _, events = detector(processed_data)
        assert isinstance(events, pd.DataFrame), (
            f"{name}: expected a DataFrame"
        )


if __name__ == "__main__":
    print("\n=== BUSINESS MONITOR TESTS ===\n")

    # Test both source datasets and actual column mapping first.
    run_test("Default dataset loads", test_dataset)
    run_test("Alternative dataset loads", test_alternative_dataset)
    run_test("Alternative column mapping", test_alternative_column_mapping)

    if failed == 0:
        run_test("Default dataset preprocessing", test_preprocessing)
        run_test(
            "Alternative dataset preprocessing",
            test_alternative_preprocessing,
        )

    if failed == 0:
        run_test("Default overall sales drop detector", test_overall_drop)
        run_test("Default overall sales spike detector", test_overall_spike)
        run_test("Default category sales spike detector", test_category_spike)
        run_test("Default product sales spike detector", test_product_spike)
        run_test("Default profit margin drop detector", test_profit_margin_drop)
        run_test("Default regional sales drop detector", test_regional_drop)

        run_test(
            "All six detectors on alternative dataset",
            test_alternative_detectors,
        )

    print("\n=== TEST SUMMARY ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed:
        print("\nSome tests failed. Check the error messages above.")
    else:
        print("\nAll tests passed successfully!")
