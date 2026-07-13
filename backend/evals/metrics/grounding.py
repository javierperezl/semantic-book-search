def grounding_score(response: dict) -> float:

    return 1.0 if response["grounded"] else 0.0