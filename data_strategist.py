# ============================================================
#  data_strategist.py 
#  Transformasi HC: Data Keeper → Data Strategist
# ============================================================

import pandas as pd
import numpy as np

# ============================================================
# 1. ADVANCED DATA QUALITY SCORING
# ============================================================
def compute_data_quality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Skor kualitas data berbasis 5 dimensi:
    - Completeness (20)
    - Consistency (20)
    - Validity (20)
    - Accuracy (20)
    - Timeliness (20)
    """
    df = df.copy()
    score = []

    for idx, row in df.iterrows():

        s = 0

        # COMPLETENESS (kolom wajib)
        required_cols = [
            "employee_id", "full_name", "department", "bureau",
            "job_title", "mpl_level", "work_location",
            "date_joined"
        ]
        completeness_missing = sum([1 for col in required_cols if not row[col]])
        s += max(0, 20 - (completeness_missing * 3))

        # CONSISTENCY (contoh MPL dengan job_grade)
        if isinstance(row["mpl_level"], str) and row["mpl_level"].upper().startswith("M"):
            s += 10
        if row["avg_perf_3yr"] is not None and 0 <= row["avg_perf_3yr"] <= 5:
            s += 10

        # VALIDITY
        if "@" in str(row["email"]):
            s += 10
        if isinstance(row["work_location"], str) and len(row["work_location"]) >= 3:
            s += 10

        # ACCURACY (deteksi data aneh)
        if row["years_in_department"] <= 50:
            s += 10
        if row["years_in_bureau"] <= 50:
            s += 10

        # TIMELINESS
        s += 20  # placeholder, nanti bisa dicek last_updated

        score.append(s)

    df["data_quality_score_adv"] = score
    return df


# ============================================================
# 2. ANOMALY DETECTION (DATA JANGGAL)
# ============================================================
def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mendeteksi:
    - Years in bureau lebih besar dari years in dept
    - MPL tidak sesuai rentang umum M10–M25
    - Kinerja tidak realistis
    """
    df = df.copy()
    issues = []

    for idx, row in df.iterrows():
        anomaly = []

        if row["years_in_bureau"] > row["years_in_department"]:
            anomaly.append("Years bureau > years dept")

        mpl = str(row["mpl_level"]).upper().replace(" ", "")
        if not mpl.startswith("M") or len(mpl) < 2:
            anomaly.append("MPL invalid")
        else:
            try:
                mpl_value = int(mpl[1:])
                if mpl_value < 10 or mpl_value > 30:
                    anomaly.append("MPL out of normal range")
            except:
                anomaly.append("MPL parsing error")

        if row["avg_perf_3yr"] > 5:
            anomaly.append("Performance > 5 (invalid)")

        issues.append(", ".join(anomaly) if anomaly else "OK")

    df["anomaly_flag"] = issues
    return df


# ============================================================
# 3. KOMPETENSI GAP ANALYSIS
# ============================================================
def compute_competency_gap(df: pd.DataFrame, required: dict) -> pd.DataFrame:
    """
    Mengukur gap antara competency employee vs kebutuhan jabatan.
    Parameter 'required' adalah dictionary:
    {
        "technical": ["HCIS", "SQL", "SAP"],
        "soft": ["analytical", "communication", "coordination"]
    }
    """
    df = df.copy()
    gap_scores = []

    for idx, row in df.iterrows():
        emp_tech = [x.strip().lower() for x in str(row["technical_skills"]).split(",")]
        emp_soft = [x.strip().lower() for x in str(row["soft_skills"]).split(",")]

        required_tech = [x.lower() for x in required["technical"]]
        required_soft = [x.lower() for x in required["soft"]]

        tech_gap = len([t for t in required_tech if t not in emp_tech])
        soft_gap = len([s for s in required_soft if s not in emp_soft])

        total_gap = tech_gap + soft_gap
        gap_scores.append(total_gap)

    df["competency_gap_score"] = gap_scores
    return df


# ============================================================
# 4. TALENT READINESS INDEX (untuk kandidat Bureau Head)
# ============================================================
def compute_talent_readiness(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menilai kesiapan talent:
    - Performance (40%)
    - Tenure (20%)
    - Competency gap (20%)
    - No discipline issue (20%)
    """
    df = df.copy()

    scores = []
    for idx, row in df.iterrows():
        s = 0
        s += (row["avg_perf_3yr"] / 5) * 40
        s += min(row["years_in_bureau"] / 5, 1) * 20
        s += (1 - min(row["competency_gap_score"] / 5, 1)) * 20
        if not row["has_discipline_issue"]:
            s += 20

        scores.append(s)

    df["talent_readiness_index"] = [round(x, 1) for x in scores]
    return df


# ============================================================
# 5. AUTO INSIGHT GENERATOR
# ============================================================
def generate_insights(df: pd.DataFrame) -> list:
    """
    Memberikan insight otomatis berbasis kondisi data.
    """
    insights = []

    avg_perf = df["avg_perf_3yr"].mean()
    if avg_perf < 3:
        insights.append("⚠️ Rata-rata kinerja pegawai rendah (<3). Perlu intervensi HC.")
    else:
        insights.append("✅ Kinerja pegawai tergolong baik.")

    high_gap = (df["competency_gap_score"] >= 3).sum()
    if high_gap > 5:
        insights.append("⚠️ Banyak pegawai memiliki gap kompetensi besar.")
    else:
        insights.append("✅ Mayoritas pegawai memiliki kompetensi sesuai kebutuhan.")

    dq = df["data_quality_score_adv"].mean()
    if dq < 70:
        insights.append("⚠️ Kualitas data HC perlu perbaikan segera.")
    else:
        insights.append("✅ Data HC cukup berkualitas.")

    ready = (df["talent_readiness_index"] >= 75).sum()
    insights.append(f"⭐ {ready} kandidat berpotensi untuk pipeline Bureau Head.")

    return insights


# ============================================================
# 6. PIPELINE UTAMA UNTUK DIPANGGIL DARI STREAMLIT
# ============================================================
def run_data_strategist_pipeline(df: pd.DataFrame, required_skills: dict):
    """
    Pipeline lengkap:
    1. Skor kualitas data (advanced)
    2. Deteksi anomali
    3. Competency gap
    4. Talent readiness index
    5. Generate insights
    """
    df1 = compute_data_quality(df)
    df2 = detect_anomalies(df1)
    df3 = compute_competency_gap(df2, required_skills)
    df4 = compute_talent_readiness(df3)
    insights = generate_insights(df4)

    return df4, insights
