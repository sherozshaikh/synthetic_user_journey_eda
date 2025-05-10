WITH user_summary AS (
    SELECT DISTINCT
        user_keys.session_key AS session_key,
        user_keys.user_key AS user_key,
        group_members.group_code AS group_code,
        users.created_at AS registration_timestamp,
        JSONExtractString(users.properties, '$device_type') AS user_platform
    FROM
        user_keys
    FULL OUTER JOIN
        users
    ON
        user_keys.user_key = users.id
    FULL OUTER JOIN
        group_members
    ON
        user_keys.user_key = group_members.user_key
    WHERE
        group_code IS NOT NULL
    ORDER BY
        registration_timestamp ASC
),

filtered_interactions AS (
    SELECT DISTINCT
        interactions.user_key AS user_key,
        interactions.`$session_id` AS interaction_id,
        JSONExtractString(interactions.properties, '$device_type') AS event_platform
    FROM interactions
),

logs_filtered AS (
    SELECT
        interaction_id,
        TRIM(REPLACE(current_url, 'https://simulation.Banksyde.io/', '')) AS task
    FROM
        interaction_logs
    WHERE 
        urrent_url LIKE 'https://simulation.Banksyde.io/%'
    AND
        current_url != 'https://simulation.Banksyde.io/'
),

pivoted_logs AS (
    SELECT
        interaction_id,
        COUNT(IF(task LIKE 'after-school-plans', 1, NULL)) AS plans_count,
        COUNT(IF(task LIKE 'bank-accounts', 1, NULL)) AS accounts_count,
        COUNT(IF(task LIKE 'banking-module', 1, NULL)) AS banking_usage,
        COUNT(IF(task LIKE 'budget', 1, NULL)) AS budgets_created,
        COUNT(IF(task LIKE 'budgeting-module', 1, NULL)) AS budgeting_usage,
        COUNT(IF(task LIKE 'content-library', 1, NULL)) AS library_views,
        COUNT(IF(task LIKE 'content-library/banking', 1, NULL)) AS library_banking_views,
        COUNT(IF(task LIKE 'content-library/budgeting', 1, NULL)) AS library_budgeting_views,
        COUNT(IF(task LIKE 'content-library/investing', 1, NULL)) AS library_investing_views,
        COUNT(IF(task LIKE 'credit-module', 1, NULL)) AS credit_usage,
        COUNT(IF(task LIKE 'dashboard', 1, NULL)) AS dashboard_visits,
        COUNT(IF(task LIKE 'goals', 1, NULL)) AS goals_created,
        COUNT(IF(task LIKE 'goals-module', 1, NULL)) AS goal_module_usage,
        COUNT(IF(task LIKE 'internship-application', 1, NULL)) AS internship_submissions,
        COUNT(IF(task LIKE 'investing-module', 1, NULL)) AS investing_usage,
        COUNT(IF(task LIKE 'login', 1, NULL)) AS logins,
        COUNT(IF(task LIKE 'onboarding-basic-info', 1, NULL)) AS onboarding_info_completed,
        COUNT(IF(task LIKE 'onboarding-create-avatar', 1, NULL)) AS onboarding_avatar_done,
        COUNT(IF(task LIKE 'onboarding-hobbies', 1, NULL)) AS onboarding_hobbies_set,
        COUNT(IF(task LIKE 'onboarding-questions', 1, NULL)) AS onboarding_questions_answered,
        COUNT(IF(task LIKE 'q-and-a', 1, NULL)) AS qa_interactions,
        COUNT(IF(task LIKE 'saving-habits', 1, NULL)) AS saving_entries,
        COUNT(IF(task LIKE 'settings', 1, NULL)) AS settings_visits,
        COUNT(IF(task LIKE 'signup', 1, NULL)) AS signups,
        COUNT(IF(task LIKE 'summer-job-module', 1, NULL)) AS summerjob_usage,
        COUNT(IF(task LIKE 'taxes-module', 1, NULL)) AS tax_module_usage,
        COUNT(IF(task LIKE 'tuition-and-fees', 1, NULL)) AS tuition_fees_recorded
    FROM
        logs_filtered
    GROUP BY
        interaction_id
),

session_times AS (
    SELECT DISTINCT
        session_data.interaction_id AS interaction_id,
        session_data.$start_timestamp AS session_start_time,
        session_data.$end_timestamp AS session_end_time
    FROM
        session_data
    WHERE
        session_data.$session_duration > 0
    ORDER BY
        session_start_time ASC
),

final_user_details AS (
    SELECT DISTINCT
        user_summary.session_key AS session_key,
        user_summary.user_key AS user_key,
        user_summary.group_code AS group_code,
        filtered_interactions.interaction_id AS interaction_id,
        user_summary.user_platform AS user_platform,
        filtered_interactions.event_platform AS event_platform,
        formatDateTime(user_summary.registration_timestamp, '%D') AS registration_date,
        session_times.session_start_time AS session_start_time,
        session_times.session_end_time AS session_end_time,
        formatDateTime(session_start_time, '%D') AS session_day,
        dateDiff('minute', session_start_time, session_times.session_end_time) AS duration_mins,
        pivoted_logs.plans_count,
        pivoted_logs.accounts_count,
        pivoted_logs.banking_usage,
        pivoted_logs.budgets_created,
        pivoted_logs.budgeting_usage,
        pivoted_logs.library_views,
        pivoted_logs.library_banking_views,
        pivoted_logs.library_budgeting_views,
        pivoted_logs.library_investing_views,
        pivoted_logs.credit_usage,
        pivoted_logs.dashboard_visits,
        pivoted_logs.goals_created,
        pivoted_logs.goal_module_usage,
        pivoted_logs.internship_submissions,
        pivoted_logs.investing_usage,
        pivoted_logs.logins,
        pivoted_logs.onboarding_info_completed,
        pivoted_logs.onboarding_avatar_done,
        pivoted_logs.onboarding_hobbies_set,
        pivoted_logs.onboarding_questions_answered,
        pivoted_logs.qa_interactions,
        pivoted_logs.saving_entries,
        pivoted_logs.settings_visits,
        pivoted_logs.signups,
        pivoted_logs.summerjob_usage,
        pivoted_logs.tax_module_usage,
        pivoted_logs.tuition_fees_recorded
    FROM
        filtered_interactions
    LEFT JOIN
        user_summary
    ON
        filtered_interactions.user_key = user_summary.user_key
    FULL OUTER JOIN
        pivoted_logs
    ON
        pivoted_logs.interaction_id = filtered_interactions.interaction_id
    INNER JOIN
        session_times
    ON
        session_times.interaction_id = filtered_interactions.interaction_id
    WHERE
        dateDiff('day', user_summary.registration_timestamp, session_times.session_start_time) >= 0
)


SELECT * FROM final_user_details

