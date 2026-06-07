from typing import Tuple

# RISK WEIGHTS
# Higher weight = more severe privacy violation

RISK_WEIGHTS = {
    "selling user data for profit": 3.0,
    "sharing user data with third parties": 2.0,
    "tracking user location or behavior": 2.0,
    "collecting personal data without clear consent": 1.5,
    "storing sensitive information indefinitely": 1.0,
    "data usage for service improvement": 0.5,
    "normal safe statement": 0.0
}

# CALCULATE RISK SCORE
# Returns: (final_score, avg_confidence, num_clauses)
# final_score: 0–10 float
# avg_confidence: 0–1 float
# num_clauses: in

def calculate_risk_score(risky_clauses: list) -> Tuple[float, float, int]:
    """
    Weighted scoring based on risk type severity and model confidence.
    
    Design decision:
    - Pure clause count scoring (old version) ignores severity — 
      10 low-risk clauses scored higher than 1 data-selling clause.
    - Weighted scoring fixes this: selling data (weight 3.0) correctly
      dominates over benign improvement clauses (weight 0.5).
    - Score capped at 10 for consistent 0–10 display range.
    """
    if not risky_clauses:
        return 0.0, 0.0, 0

    total_weighted = 0.0
    total_conf = 0.0

    for clause in risky_clauses:
        risk_type = clause.get("risk_type", "normal safe statement")
        confidence = clause.get("confidence", 0.0) / 100  # normalise to 0–1
        weight = RISK_WEIGHTS.get(risk_type, 1.0)

        total_weighted += weight * confidence
        total_conf += confidence

    num_clauses = len(risky_clauses)
    avg_conf = round(total_conf / num_clauses, 4)
    final_score = round(min((total_weighted / num_clauses) * 5, 10.0), 2)

    return final_score, avg_conf, num_clauses

# Risk label

def get_risk_label(score: float) -> str:
    if score <= 3:
        return "LOW RISK"
    elif score <= 6:
        return "MEDIUM RISK"
    else:
        return "HIGH RISK"


# summary

def summarize_clauses(risky_clauses: list) -> str:
    if not risky_clauses:
        return "This privacy policy appears safe. No major risks detected."

    summary = "The following risks were found:\n\n"
    for i, clause in enumerate(risky_clauses, 1):
        summary += f"{i}. {clause['risk_type'].upper()}\n"
        summary += f"   {clause['clause'][:200]}...\n\n"
        if "explanation" in clause:
            summary += f"   {clause['explanation']}\n\n"
    return summary