from agent_40_score_evidence import run_evidence_demo


if __name__ == "__main__":
    response = run_evidence_demo()
    if response.status != "success":
        raise SystemExit(f"Demo failed: {response.status} {response.message}")
    if response.conflict_status != "conflict":
        raise SystemExit(f"Expected conflict, got {response.conflict_status}")
    if len(response.evidence) != 2:
        raise SystemExit("Both evidence items must be retained.")
    print("DEMO_OK")
