def generate_explanation(text, risk_score, label):
    """
    Fallback rule-based explanation used when the AI (genai) is unavailable.
    Signature matches the call in views.py: generate_explanation(message, risk_score, label)
    """
    reasons = []

    text_lower = text.lower()

    if "http" in text_lower:
        reasons.append("contains a suspicious link")

    if "urgent" in text_lower or "immediately" in text_lower:
        reasons.append("uses urgent language")

    if "otp" in text_lower or "password" in text_lower:
        reasons.append("asks for sensitive information")

    if "free" in text_lower or "winner" in text_lower or "prize" in text_lower:
        reasons.append("promises a free reward or prize")

    if not reasons:
        if label == "Safe":
            return "No obvious scam patterns were detected in this message."
        reasons.append("contains patterns associated with scam messages")

    return f"This message is labelled {label} (risk score {risk_score}/100) because it " + " and ".join(reasons) + "."