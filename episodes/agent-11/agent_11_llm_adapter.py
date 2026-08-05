import os


def fake_llm(prompt: str) -> str:
    return "模拟回答：我已经收到问题，会先用 fake_llm 跑通流程。"


def api_llm(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 OPENAI_API_KEY，不能调用真实 API。")

    model = os.getenv("OPENAI_MODEL", "需要脚本定稿前确认模型名")

    # 这里是安全占位：真实项目可以在这里接入 OpenAI SDK 或 HTTP 请求。
    # 重点是：密钥来自环境变量，外层代码只认识 llm_adapter(prompt)。
    return f"真实 API 占位：将使用 {model} 处理 prompt，密钥不会写进代码。"


def llm_adapter(prompt: str) -> str:
    use_real_api = os.getenv("AGENT_USE_REAL_API") == "1"
    if not use_real_api:
        return fake_llm(prompt)

    try:
        return api_llm(prompt)
    except Exception as error:
        return fake_llm(prompt) + f"\n备用原因：{error}"


if __name__ == "__main__":
    prompt = "请用一句话解释什么是 Agent。"
    print(llm_adapter(prompt))
