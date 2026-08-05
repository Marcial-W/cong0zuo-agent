import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any, Callable


def fake_llm(prompt: str) -> dict[str, Any]:
    return {
        "summary": "fallback 回答：真实 API 暂时不可用，先返回一个可展示结果。",
        "concepts": ["fallback", "错误兜底"],
        "outline": ["记录错误", "返回备用结果", "不中断流程"],
    }


def call_with_timeout(
    func: Callable[[str], dict[str, Any]],
    prompt: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(func, prompt)
    try:
        return future.result(timeout=timeout_seconds)
    except TimeoutError as error:
        raise TimeoutError(f"调用超过 {timeout_seconds} 秒") from error
    finally:
        future.cancel()
        executor.shutdown(wait=False, cancel_futures=True)


def safe_call_llm(
    prompt: str,
    llm_func: Callable[[str], dict[str, Any]],
    retries: int = 2,
    timeout_seconds: float = 3,
    fallback_func: Callable[[str], dict[str, Any]] = fake_llm,
) -> dict[str, Any]:
    errors: list[str] = []

    for attempt in range(retries + 1):
        try:
            result = call_with_timeout(llm_func, prompt, timeout_seconds)
            return {
                "result": result,
                "errors": errors,
                "used_fallback": False,
            }
        except Exception as error:
            errors.append(f"第 {attempt + 1} 次调用失败：{type(error).__name__}: {error}")

    return {
        "result": fallback_func(prompt),
        "errors": errors,
        "used_fallback": True,
    }


def slow_llm(prompt: str) -> dict[str, Any]:
    time.sleep(0.5)
    return {
        "summary": "真实 API 回答：" + prompt,
        "concepts": ["真实 API"],
        "outline": ["调用模型", "返回结果"],
    }


if __name__ == "__main__":
    prompt = "请总结这段资料。"
    response = safe_call_llm(prompt, slow_llm, retries=1, timeout_seconds=0.1)
    print("used_fallback:", response["used_fallback"])
    print("result:", response["result"])
    print("errors:")
    for error in response["errors"]:
        print("-", error)
