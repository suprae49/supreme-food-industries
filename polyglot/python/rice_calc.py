"""Python helper used by Flask /api/calc (fallback if native binary missing)."""

def calc_bags(bags: int, kg_per_bag: float = 25.0) -> dict:
    total = bags * kg_per_bag
    return {
        "ok": True,
        "lang": "python",
        "bags": bags,
        "kg_per_bag": kg_per_bag,
        "total_kg": round(total, 2),
        "total_quintal": round(total / 100.0, 3),
        "csr_fund_npr": bags * 25,  # Rs 1/kg => Rs 25 per 25kg bag
    }


if __name__ == "__main__":
    import json
    import sys

    b = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    k = float(sys.argv[2]) if len(sys.argv) > 2 else 25.0
    print(json.dumps(calc_bags(b, k), ensure_ascii=False))
