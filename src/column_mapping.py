
import pandas as pd


COLUMN_ALIASES = {
    "Order_ID": [
        "order id", "order_id", "order number",
        "order no", "transaction id", "order",
    ],
    "Date": [
        "date", "order date", "transaction date",
        "sale date", "sales date",
    ],
    "Product_Name": [
        "product name", "product_name", "product",
        "item", "item name",
    ],
    "Category": [
        "category", "product category",
        "product_type", "product type",
    ],
    "Region": [
        "region", "location", "area",
        "sales region", "sales area",
    ],
    "Quantity": [
        "quantity", "qty", "units sold",
        "units", "number of units",
    ],
    "Sales": [
        "sales", "revenue", "total sales",
        "sales amount", "total revenue",
    ],
    "Profit": [
        "profit", "net profit",
        "profit amount", "total profit",
    ],
}


def normalize_column_name(column):
    """Normalize column names for reliable matching."""
    return " ".join(str(column).strip().lower().replace("_", " ").split())


def auto_map_columns(data):
    """Map common alternative column names to canonical names."""
    data = data.copy()

    normalized_columns = {
        normalize_column_name(column): column
        for column in data.columns
    }

    rename_map = {}

    for canonical_name, aliases in COLUMN_ALIASES.items():
        # Already has the expected name
        if canonical_name in data.columns:
            continue

        possible_names = [
            normalize_column_name(canonical_name),
            *[normalize_column_name(alias) for alias in aliases],
        ]

        for possible_name in possible_names:
            if possible_name in normalized_columns:
                original_name = normalized_columns[possible_name]
                rename_map[original_name] = canonical_name
                break

    return data.rename(columns=rename_map)
