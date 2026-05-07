import re
import requests
from urllib.parse import urlparse
from django.conf import settings


def check_https(url):
    return url.startswith("https://")


def suspicious_domain(url):
    domain = urlparse(url).netloc
    patterns = [
        "login", "verify", "secure", "update", "bank",
        "account", "free", "bonus", "winner", "claim",
        "paypal", "amazon", "apple", "microsoft", "support"
    ]
    for p in patterns:
        if p in domain.lower():
            return True
    return False


def is_ip_url(url):
    pattern = r"http[s]?://\d{1,3}(\.\d{1,3}){3}"
    return re.match(pattern, url) is not None


def has_excessive_subdomains(url):
    domain = urlparse(url).netloc
    parts = domain.split(".")
    return len(parts) > 4


def has_suspicious_tld(url):
    domain = urlparse(url).netloc
    suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".click"]
    for tld in suspicious_tlds:
        if domain.endswith(tld):
            return True
    return False


def google_safe_browsing(url):
    api_key = getattr(settings, "GOOGLE_SAFE_BROWSING_API_KEY", "")
    if not api_key or api_key == "YOUR_GOOGLE_SAFE_BROWSING_KEY":
        return False  # skip if key not set

    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    payload = {
        "client": {"clientId": "smartshield", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        result = response.json()
        return "matches" in result
    except Exception:
        return False


def analyze_url(url):
    risk = 0
    reasons = []

    if not check_https(url):
        risk += 25
        reasons.append("does not use HTTPS (insecure connection)")

    if suspicious_domain(url):
        risk += 25
        reasons.append("domain contains suspicious keywords")

    if is_ip_url(url):
        risk += 30
        reasons.append("uses raw IP address instead of a domain name")

    if has_excessive_subdomains(url):
        risk += 15
        reasons.append("has too many subdomains (common phishing trick)")

    if has_suspicious_tld(url):
        risk += 20
        reasons.append("uses a suspicious top-level domain")

    if google_safe_browsing(url):
        risk += 50
        reasons.append("flagged by Google Safe Browsing")

    risk = min(risk, 100)

    if risk < 30:
        label = "Safe"
    elif risk < 65:
        label = "Suspicious"
    else:
        label = "Dangerous"

    return risk, label, reasons