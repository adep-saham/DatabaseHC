def diff_changes(before, after):
    diffs = []
    for key in after:
        if key in before and before[key] != after[key]:
            diffs.append({
                "field": key,
                "before": before[key],
                "after": after[key]
            })
    return diffs
