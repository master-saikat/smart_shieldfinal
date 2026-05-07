import os
import google.generativeai as genai

# Try Django settings first, then fall back to environment variable directly
try:
    from django.conf import settings
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
except Exception:
    api_key = os.environ.get('GEMINI_API_KEY', '')

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set. "
        "Add it to your .env file: GEMINI_API_KEY=your_key_here"
    )

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_explanation(message, risk_score, label):
    prompt = f"""You are a cybersecurity expert helping regular people understand threats.

Analyze this message:
"{message}"

Risk Score: {risk_score}/100
Label: {label}

Give a clear, simple 2-3 sentence explanation:
- Why it is {label}
- What specific red flags exist (or why it's safe)
- One practical tip for the user

Be direct and avoid technical jargon."""

    response = model.generate_content(prompt)
    return response.text.strip()


def cyber_advice(question):
    prompt = f"""You are SmartShield's cyber safety assistant.

User question: {question}

Respond with:
- A clear, direct answer (2-4 sentences)
- 1-2 practical action steps if relevant
- Keep it friendly and jargon-free"""

    response = model.generate_content(prompt)
    return response.text.strip()