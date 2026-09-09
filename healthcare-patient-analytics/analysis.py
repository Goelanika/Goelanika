import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RANDOM_SEED = 42
N_ROWS = 5000
rng = np.random.default_rng(RANDOM_SEED)


def build_dataset(n_rows=N_ROWS):
    departments = np.array(["Cardiology", "General Medicine", "Orthopedics", "Pediatrics", "Neurology"])
    visit_types = np.array(["Outpatient", "Emergency", "Inpatient"])
    genders = np.array(["Female", "Male", "Other"])

    df = pd.DataFrame({
        "patient_id": np.arange(100001, 100001 + n_rows),
        "age": rng.integers(1, 90, n_rows),
        "gender": rng.choice(genders, n_rows, p=[0.49, 0.49, 0.02]),
        "department": rng.choice(departments, n_rows, p=[0.16, 0.30, 0.20, 0.18, 0.16]),
        "visit_type": rng.choice(visit_types, n_rows, p=[0.58, 0.24, 0.18]),
        "waiting_time_minutes": np.clip(rng.normal(38, 17, n_rows), 5, 130).round(0),
        "length_of_stay_days": np.clip(rng.gamma(2.0, 1.7, n_rows), 0.2, 20).round(1),
        "satisfaction_score": np.clip(rng.normal(4.0, 0.7, n_rows), 1, 5).round(1),
        "readmitted_30_days": rng.choice([0, 1], n_rows, p=[0.88, 0.12]),
        "visit_date": pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n_rows), unit="D"),
    })

    # Add a few quality issues for cleaning practice.
    missing_idx = rng.choice(df.index, 40, replace=False)
    df.loc[missing_idx[:20], "satisfaction_score"] = np.nan
    df.loc[missing_idx[20:], "department"] = None
    duplicates = df.sample(15, random_state=RANDOM_SEED)
    return pd.concat([df, duplicates], ignore_index=True)


def clean_data(df):
    cleaned = df.drop_duplicates(subset="patient_id", keep="first").copy()
    cleaned["department"] = cleaned["department"].fillna("Unknown")
    cleaned["satisfaction_score"] = cleaned["satisfaction_score"].fillna(
        cleaned["satisfaction_score"].median()
    )
    cleaned["visit_month"] = cleaned["visit_date"].dt.to_period("M").astype(str)
    return cleaned


def summarize(df):
    total_visits = len(df)
    avg_wait = df["waiting_time_minutes"].mean()
    readmission_rate = df["readmitted_30_days"].mean() * 100
    avg_satisfaction = df["satisfaction_score"].mean()

    print("HEALTHCARE PATIENT ANALYTICS")
    print(f"Total patient visits: {total_visits:,}")
    print(f"Average waiting time: {avg_wait:.1f} minutes")
    print(f"30-day readmission rate: {readmission_rate:.2f}%")
    print(f"Average satisfaction score: {avg_satisfaction:.2f}/5")

    print("\nDepartment summary:")
    department_summary = (
        df.groupby("department")
        .agg(
            patient_visits=("patient_id", "count"),
            avg_waiting_time=("waiting_time_minutes", "mean"),
            readmission_rate=("readmitted_30_days", "mean"),
            avg_satisfaction=("satisfaction_score", "mean"),
        )
        .reset_index()
    )
    department_summary["readmission_rate"] *= 100
    print(department_summary.round(2).to_string(index=False))
    return department_summary


def save_outputs(df, department_summary):
    df.to_csv("cleaned_patient_data.csv", index=False)
    department_summary.to_csv("department_summary.csv", index=False)

    monthly_visits = df.groupby("visit_month")["patient_id"].count()
    plt.figure(figsize=(10, 5))
    monthly_visits.plot(kind="line", marker="o")
    plt.title("Monthly Patient Visits")
    plt.xlabel("Month")
    plt.ylabel("Patient Visits")
    plt.tight_layout()
    plt.savefig("monthly_patient_visits.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    raw = build_dataset()
    cleaned = clean_data(raw)
    department_summary = summarize(cleaned)
    save_outputs(cleaned, department_summary)
