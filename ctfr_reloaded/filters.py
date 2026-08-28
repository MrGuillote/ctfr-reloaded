def apply_result_filters(items, resolved_only=False, alive_only=False):
    filtered = items
    if resolved_only:
        filtered = [item for item in filtered if item.get("resolved")]
    if alive_only:
        filtered = [item for item in filtered if item.get("alive")]
    return filtered


def filter_results(results, resolved_only=False, alive_only=False):
    if not resolved_only and not alive_only:
        return results
    return {
        domain: apply_result_filters(items, resolved_only, alive_only)
        for domain, items in results.items()
    }
