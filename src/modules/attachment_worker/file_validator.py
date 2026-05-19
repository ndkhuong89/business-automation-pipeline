import pandas as pd

REQUIRED_COLUMNS = [
    "order_id",
    "customer_name",
    "product_sku",
    "product_name",
    "quantity",
    "unit_price"
]


def validate_excel_file(filepath):

    if not filepath.endswith(".xlsx"):
        return False, "invalid_file_extension"

    try:
        df = pd.read_excel(filepath)

    except Exception as e:
        return False, f"cannot_read_excel: {str(e)}"

    if df.empty:
        return False, "empty_excel_file"

    missing_columns = [
        col
        for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        return False, (
            "missing_columns: "
            + ", ".join(missing_columns)
        )

    return True, None