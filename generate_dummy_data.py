import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "hc_employee.db"

DEPARTMENTS = ["Finance", "HC", "ICT", "Mining", "Processing", "Logistics", "Legal", "Risk Management"]
BUREAUS = ["Bureau A", "Bureau B", "Bureau C", "Bureau D"]
JOB_TITLES = ["Staff", "Supervisor", "Superintendent", "Specialist", "Manager", "Senior Manager"]
WORK_LOCATIONS = ["Jakarta", "Bogor", "Kalikuning", "Pongkor", "UBPN Konut", "UBPN Maluku Utara"]
MPL_LEVELS = ["I", "II", "III", "IV", "V", "VI"]

TECH_SKILLS = ["SAP", "SQL", "Python", "HCIS", "Geology", "Mining Ops", "Finance Control", "Data Analysis"]
SOFT_SKILLS = ["Leadership", "Communication", "Teamwork", "Analytical", "Problem Solving", "Coordination"]
CERTIFICATIONS = ["ISO9001", "ISO14001", "ISO27001", "OHSAS", "Risk Management", "Project Mgmt"]

def generate_random_date():
    days_ago = random.randint(100, 2000)
    return (datetime.now() - timedelta(days=days_ago)).date().isoformat()


def generate_dummy_data(n=50):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for i in range(1, n+1):
        emp_id = f"EMP{str(i).zfill(3)}"
        name = f"Dummy Employee {i}"

        department = random.choice(DEPARTMENTS)
        bureau = random.choice(BUREAUS)
        job_title = random.choice(JOB_TITLES)
        work_loc = random.choice(WORK_LOCATIONS)
        mpl = random.choice(MPL_LEVELS)

        years_bureau = random.randint(0, 20)
        years_dept = years_bureau + random.randint(0, 10)  # dept >= bureau
        avg_perf = round(random.uniform(2.0, 5.0), 2)

        tech = ", ".join(random.sample(TECH_SKILLS, random.randint(1, 4)))
        soft = ", ".join(random.sample(SOFT_SKILLS, random.randint(1, 3)))
        cert = ", ".join(random.sample(CERTIFICATIONS, random.randint(0, 2)))

        discipline = random.choice([0, 0, 0, 1])  # 25% memiliki isu disiplin

        last_updated = datetime.now().isoformat()

        cur.execute("""
            INSERT OR REPLACE INTO employees (
                employee_id, full_name, department, bureau, job_title, work_location,
                mpl_level, years_in_bureau, years_in_department, avg_perf_3yr,
                technical_skills, soft_skills, certifications, has_discipline_issue,
                last_updated
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            emp_id, name, department, bureau, job_title, work_loc,
            mpl, years_bureau, years_dept, avg_perf, tech, soft, cert, discipline,
            last_updated
        ))

    conn.commit()
    conn.close()

    return f"{n} dummy employees berhasil dibuat!"
