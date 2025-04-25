def get_result(scores: dict) -> str:
    return max(scores, key=scores.get)
