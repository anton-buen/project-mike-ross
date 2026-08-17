from datetime import datetime, timedelta
import re

def resolve_relative_date(text_fragment: str, current_date_str: str) -> str | None:
    """
    Resolves relative date words like 'today', 'tomorrow', or 'in N days'
    into a YYYY-MM-DD date string based on current_date_str.
    Implements Section 9.2.
    """
    if not text_fragment:
        return None

    # Parse the incoming reference date string into a Python datetime object
    try:
        base_date = datetime.strptime(current_date_str, "%Y-%m-%d")
    except ValueError:
        base_date = datetime.utcnow()

    text_lower = text_fragment.lower().strip()

    if "today" in text_lower:
        return base_date.strftime("%Y-%m-%d")

    if "tomorrow" in text_lower:
        target_date = base_date + timedelta(days=1)
        return target_date.strftime("%Y-%m-%d")

    # Check for 'in N days' pattern using regular expressions (e.g., 'in 5 days')
    match_in_days = re.search(r"in\s+(\d+)\s+days?", text_lower)
    if match_in_days:
        days_ahead = int(match_in_days.group(1))
        target_date = base_date + timedelta(days=days_ahead)
        return target_date.strftime("%Y-%m-%d")

    return None


def infer_priority_fallback(text: str) -> str:
    """
    Infers priority ('high', 'medium', 'low') from text keywords if the AI omits it.
    Implements Section 9.4.
    """
    high_keywords = ["urgent", "asap", "critical", "immediately", "emergency"]
    medium_keywords = ["important", "soon", "priority"]

    lowercase_text = text.lower()

    if any(keyword in lowercase_text for keyword in high_keywords):
        return "high"
    elif any(keyword in lowercase_text for keyword in medium_keywords):
        return "medium"
    else:
        return "medium"  # Default fallback