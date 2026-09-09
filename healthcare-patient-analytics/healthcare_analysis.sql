-- Healthcare Patient Analytics: core SQL queries

-- 1. Total patient visits
SELECT COUNT(*) AS total_patient_visits
FROM patient_visits;

-- 2. Average waiting time
SELECT ROUND(AVG(waiting_time_minutes), 2) AS avg_waiting_time_minutes
FROM patient_visits;

-- 3. 30-day readmission rate
SELECT ROUND(100.0 * SUM(readmitted_30_days) / COUNT(*), 2) AS readmission_rate_pct
FROM patient_visits;

-- 4. Department-wise performance
SELECT
    department,
    COUNT(*) AS patient_visits,
    ROUND(AVG(waiting_time_minutes), 2) AS avg_waiting_time_minutes,
    ROUND(AVG(length_of_stay_days), 2) AS avg_length_of_stay_days,
    ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction_score,
    ROUND(100.0 * SUM(readmitted_30_days) / COUNT(*), 2) AS readmission_rate_pct
FROM patient_visits
GROUP BY department
ORDER BY patient_visits DESC;

-- 5. Monthly patient visit trend
SELECT
    strftime('%Y-%m', visit_date) AS visit_month,
    COUNT(*) AS patient_visits
FROM patient_visits
GROUP BY strftime('%Y-%m', visit_date)
ORDER BY visit_month;

-- 6. Visit type comparison
SELECT
    visit_type,
    COUNT(*) AS patient_visits,
    ROUND(AVG(waiting_time_minutes), 2) AS avg_waiting_time_minutes,
    ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction_score
FROM patient_visits
GROUP BY visit_type
ORDER BY patient_visits DESC;
