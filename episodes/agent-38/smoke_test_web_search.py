from agent_38_web_search import run_smoke_test


if __name__ == "__main__":
    result = run_smoke_test()
    if result.status != "success":
        raise SystemExit(f"Smoke test failed: {result.status} {result.message}")
    if not result.results:
        raise SystemExit("Smoke test returned no results.")
    print("SMOKE_OK")
