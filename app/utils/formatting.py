"""
Apeiron CostEstimation Pro – Formatting Utilities
==================================================
Currency formatting and display helpers.
Importable by any layer.
"""


def format_inr(amount: float) -> str:
    """
    Format amount in Indian Rupees with commas (₹1,23,456.78).
    Uses the Indian number system: last 3 digits, then groups of 2.
    """
    if amount < 0:
        return f"-₹{format_inr(-amount)[1:]}"
    # Indian number system: last 3 digits, then groups of 2
    s = f"{amount:,.2f}"
    parts = s.split(".")
    integer_part = parts[0].replace(",", "")
    decimal_part = parts[1] if len(parts) > 1 else "00"

    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        last_three = integer_part[-3:]
        rest = integer_part[:-3]
        # Group in twos from right
        groups: list[str] = []
        while rest:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        formatted = ",".join(groups) + "," + last_three

    return f"₹{formatted}.{decimal_part}"
