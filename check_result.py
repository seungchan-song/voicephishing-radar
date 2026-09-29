# result.json이 약속한 형식을 지키는지 검사한다.
#   python check_result.py
# analysis.py를 고치거나 진짜 데이터로 바꾼 뒤에 꼭 실행한다.
from common import load_result
from config import TAGS, AGE_GROUPS, REGIONS

KEYS = ["is_fake", "generated_at", "stats_year", "summary", "period",
        "by_age", "by_region", "yearly", "top_methods", "method_counts", "insights"]


def check(result):
    errors = []

    for key in KEYS:
        if key not in result:
            errors.append(f"'{key}' 항목이 없음")
    if errors:
        return errors

    # 연령대 6개가 약속한 순서대로 있는지
    age_groups = []
    age_total = 0
    for row in result["by_age"]:
        age_groups.append(row["group"])
        age_total += row["count"]
    if age_groups != AGE_GROUPS:
        errors.append(f"by_age의 group은 {AGE_GROUPS} 순서여야 함")

    # 시도청 18곳이 모두 있는지
    region_groups = []
    region_total = 0
    amount_total = 0
    for row in result["by_region"]:
        region_groups.append(row["group"])
        region_total += row["count"]
        amount_total += row["amount"]
    if sorted(region_groups) != sorted(REGIONS):
        errors.append("by_region에는 시도청 18곳이 모두 있어야 함")

    # 합계가 서로 맞는지
    summary = result["summary"]
    if not (age_total == region_total == summary["total_count"]):
        errors.append(f"건수 합계 불일치: by_age={age_total}, by_region={region_total}, "
                      f"summary={summary['total_count']}")
    if amount_total != summary["total_amount"]:
        errors.append("summary.total_amount가 by_region의 amount 합과 다름")

    # 수법 이름이 약속한 6개인지
    if sorted(result["method_counts"]) != sorted(TAGS):
        errors.append(f"method_counts의 키는 {TAGS} 6개여야 함")
    for method in result["top_methods"]:
        if method["name"] not in TAGS or method["name"] == "기타":
            errors.append(f"top_methods의 name이 잘못됨: {method['name']}")

    return errors


if __name__ == "__main__":
    result = load_result()
    errors = check(result)
    if errors:
        print(f"result.json 형식 오류 {len(errors)}개")
        for error in errors:
            print(" -", error)
    else:
        print("result.json 형식 정상 / 가짜 데이터:", result["is_fake"])
