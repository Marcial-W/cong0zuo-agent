from typing import Any


REQUIRED_FIELDS = {
    "summary": str,
    "concepts": list,
    "outline": list,
}


def validate_result(result: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in result:
            errors.append(f"缺少字段：{field}")
            continue

        if not isinstance(result[field], expected_type):
            errors.append(f"{field} 类型错误，应该是 {expected_type.__name__}")

    if "concepts" in result and isinstance(result["concepts"], list):
        for concept in result["concepts"]:
            if not isinstance(concept, str):
                errors.append("concepts 里面的每一项都应该是字符串")
                break

    if "outline" in result and isinstance(result["outline"], list):
        for item in result["outline"]:
            if not isinstance(item, str):
                errors.append("outline 里面的每一项都应该是字符串")
                break

    return len(errors) == 0, errors


if __name__ == "__main__":
    good_result = {
        "summary": "Agent 会围绕任务调用工具并保存中间结果。",
        "concepts": ["Agent", "工具", "state"],
        "outline": ["任务", "工具调用", "结果整理"],
    }

    bad_result = {
        "summary": "缺少 concepts，并且 outline 类型不对。",
        "outline": "任务 -> 工具 -> 答案",
    }

    for name, result in [("good_result", good_result), ("bad_result", bad_result)]:
        ok, errors = validate_result(result)
        print(name, "通过" if ok else "失败")
        for error in errors:
            print("-", error)
