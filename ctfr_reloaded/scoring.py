HIGH_VALUE_KEYWORDS = (
    "admin", "api", "app", "auth", "backup", "beta", "cms", "console",
    "dashboard", "db", "dev", "ftp", "git", "internal", "jenkins", "jira",
    "login", "mail", "mgmt", "mysql", "panel", "portal", "prod", "redis",
    "sandbox", "secure", "smtp", "ssh", "staging", "test", "uat", "vpn",
    "webmail", "wiki",
)


def score_subdomain(item):
    name = item.get("name", "").lower()
    score = 10

    for keyword in HIGH_VALUE_KEYWORDS:
        if keyword in name:
            score += 15

    if item.get("resolved"):
        score += 10
    if item.get("alive"):
        score += 20
    if item.get("vulnerable") or item.get("takeover"):
        score += 50
    if item.get("cdn"):
        score += 5
    if item.get("tls"):
        score += 5

    parts = name.split(".")
    if len(parts) <= 3:
        score += 5

    return min(score, 100)


def enrich_scores(items):
    for item in items:
        item["score"] = score_subdomain(item)
    return sorted(items, key=lambda x: x.get("score", 0), reverse=True)


def apply_exclude_patterns(items, patterns):
    if not patterns:
        return items
    filtered = []
    for item in items:
        name = item["name"].lower()
        if any(pattern in name for pattern in patterns):
            continue
        filtered.append(item)
    return filtered
