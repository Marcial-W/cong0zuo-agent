from agent_39_extract_page import run_smoke_test


if __name__ == "__main__":
    extraction = run_smoke_test()
    if extraction.status != "success":
        raise SystemExit(f"Smoke test failed: {extraction.status} {extraction.message}")
    print("SMOKE_OK")
