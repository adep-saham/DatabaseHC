def normalize(v):
    if v is None:
        return ""
    return str(v)

def diff_changes(before: dict, after: dict):
    changes = []
    skip = {"last_updated", "data_quality_score", "id"}

    for key in after:
        if key in skip:
            continue
        b = normalize(before.get(key))
        a = normalize(after.get(key))
        if b != a:
            changes.append({"field": key, "before": b, "after": a})
    return changes

def calculate_data_quality(row):
    score = 0
    if row.get("employee_id") and row.get("full_name"): score += 20
    if row.get("job_title") and row.get("department") and row.get("bureau"): score += 20
    if row.get("mpl_level") and row.get("work_location"): score += 20
    if row.get("date_joined") and row.get("avg_perf_3yr") is not None: score += 20
    if row.get("technical_skills") or row.get("soft_skills") or row.get("certifications"): score += 20
    return score

def is_candidate_bureau_head(row):
    mpl = (row.get("mpl_level") or "").upper()
    perf = row.get("avg_perf_3yr") or 0
    disc = row.get("has_discipline_issue")
    thnb = row.get("years_in_bureau") or 0
    thnd = row.get("years_in_department") or 0

    return (
        (mpl.startswith("M2") or mpl.startswith("M1"))
        and perf >= 3.5
        and not disc
        and (thnb >= 1 or thnd >= 4)
    )
