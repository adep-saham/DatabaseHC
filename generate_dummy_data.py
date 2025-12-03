import sqlite3
import json
from datetime import datetime, date
import random

DB = "hc_employee.db"


# =========================================================
# Utility Dummy Generator
# =========================================================
names = [
    "Andi Pratama", "Rina Sari", "Budi Santoso", "Siti Aminah",
    "Joko Waluyo", "Mira Ayuningtyas", "Dedi Firmansyah",
    "Cindy Oktaviani", "Yudi Hartono", "Agus Prabowo"
]

departments = [
    "Internal Audit", "Finance", "HR", "Mining Operation",
    "IT", "Logistic", "Procurement", "Legal", "Risk Management"
]

bureaus = [
    "HC System", "Data Management", "Payroll", "Talent Acquisition",
    "IT Support", "Internal Control", "Audit Operation"
]

job_titles = [
    "Officer", "Senior Officer", "Supervisor", "Analyst",
    "Senior Analyst", "Manager"
]

skills_tech = [
    "HCIS", "SQL", "Python", "SAP", "Data Governance", "Reporting"
]

skills_soft = [
    "Communication", "Leadership", "Analytical",
    "Teamwork", "Problem Solving"
]


def random_date():
    return date(
        random.randint(2010, 2022),
        random.randint(1, 12),
        random.randint(1, 28)
    ).isoformat()


def generate_employee(emp_id):
    name = random.choice(names)
    dept = random.choice(departments)
    bureau = random.choice(bureaus)
    title = random.choice(job_titles)

    return {
        "employee_id": f"EMP{emp_id:03d}",
        "full_name": name,
        "email": f"{name.split()[0].lower()}{emp_id}@example.com",
        "department": dept,
        "bureau": bureau,
        "job_title": title,
        "mpl_level": f"M{random.randint(1, 3)}{random.randint(1, 9)}",
        "work_location": random.choice(["Jakarta", "Bogor", "Bandung", "Medan"]),
        "date_joined": random_date(),
        "years_in_bureau": round(random.uniform(0, 10), 1),
        "years_in_department": round(random.uniform(0, 10), 1),
        "avg_perf_3yr": round(random.uniform(2.5, 4.9), 2),
        "has_discipline_issue": random.choice([0, 0, 0, 1]),
        "technical_skills": ", ".join(random.sample(skills_tech, random.randint(1, 3))),
        "soft_skills": ", ".join(random.sample(skills_soft, random.randint(1, 3))),
        "certifications": random.choice(["HC Cert", "Data Cert", "Audit Cert", ""]),
        "notes": "",
        "is_candidate_bureau_head": random.choice([0, 0, 1]),
        "data_quality_score": random.choice([80, 90, 100]),
        "last_updated": datetime.now().isoformat(timespec="seconds")
    }


# =========================================================
# INSERT PROCESS
# =========================================================
def generate_dummy_data(count=15):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    for i in range(1, count + 1):
        emp = generate_employee(i)

        cur.execute("""
            INSERT INTO employees (
                employee_id, full_name, email, department, bureau, job_title,
                mpl_level, work_location, date_joined, years_in_bureau,
                years_in_department, avg_perf_3yr, has_discipline_issue,
                technical_skills, soft_skills, certifications, notes,
                is_candidate_bureau_head, data_quality_score, last_updated
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            emp["employee_id"], emp["full_name"], emp["email"],
            emp["department"], emp["bureau"], emp["job_title"],
            emp["mpl_level"], emp["work_location"], emp["date_joined"],
            emp["years_in_bureau"], emp["years_in_department"],
            emp["avg_perf_3yr"], emp["has_discipline_issue"],
            emp["technical_skills"], emp["soft_skills"], emp["certifications"],
            emp["notes"], emp["is_candidate_bureau_head"],
            emp["data_quality_score"], emp["last_updated"]
        ))

        # AUDIT LOG INSERT
        cur.execute("""
            INSERT INTO audit_log (
                action_time, user_role, action_type, employee_id,
                detail, before_data, after_data, ip_address
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            "SYSTEM",
            "INSERT_DUMMY",
            emp["employee_id"],
            "Dummy Insert",
            None,
            json.dumps(emp),
            "127.0.0.1"
        ))

    conn.commit()
    conn.close()

    print(f"🎉 {count} dummy employees inserted successfully!")


if __name__ == "__main__":
    insert_dummy(15)

