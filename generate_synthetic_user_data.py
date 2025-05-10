# pip3 install pandas numpy datetime faker

import time
import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
from typing import List, Dict

fake = Faker()
random.seed(123)
np.random.seed(123)

# Create User Base (3K unique users)
def create_users(num_users:int=3_000, max_groups:int=20)->pd.DataFrame:
    user_data:List[Dict] = []
    start_date = datetime(2123, 1, 1)
    end_date = datetime(2127, 12, 31)
    for _ in range(num_users):
        user_id = fake.uuid4()
        created_at = fake.date_time_between(start_date=start_date, end_date=end_date)
        platform = np.random.choice(a=["Desktop", "Mobile", "Tablet"], size=None, replace=False, p=None)
        group_id = f"group_{np.random.randint(low=1, high=max_groups+1, size=None, dtype=int)}"

        user_data.append({
            "user_key": user_id,
            "registration_date": created_at,
            "user_platform": platform,
            "group_code": group_id
        })
    return pd.DataFrame(user_data)

# Generate User Sessions for Each User
def create_sessions(df:pd.DataFrame, max_sessions_per_user:int=30)->pd.DataFrame:
    session_data:List[Dict] = []
    for _, row in df.iterrows():
        user_id = row["user_key"]
        for _ in range(random.randint(1, max_sessions_per_user)):
            session_key = fake.uuid4()
            session_date = fake.date_time_between(start_date=row["registration_date"], end_date=datetime(2127, 12, 31))
            duration = random.randint(1, 120)
            session_end = session_date + timedelta(minutes=duration)
            event_platform = random.choice(["Desktop", "Mobile", "Tablet"])
            session_data.append({
                "session_key": session_key,
                "user_key": user_id,
                "session_start_time": session_date,
                "session_end_time": session_end,
                "duration_mins": duration,
                "event_platform": event_platform
            })
    return pd.DataFrame(session_data)

# Generate Features
def generate_behavior_features(df:pd.DataFrame)->pd.DataFrame:
    behaviors:List[str] = [
        "plans_count", "accounts_count", "banking_usage", "budgets_created", "budgeting_usage",
        "library_views", "library_banking_views", "library_budgeting_views", "library_investing_views",
        "credit_usage", "dashboard_visits", "goals_created", "goal_module_usage", "internship_submissions",
        "investing_usage", "logins", "onboarding_info_completed", "onboarding_avatar_done",
        "onboarding_hobbies_set", "onboarding_questions_answered", "qa_interactions",
        "saving_entries", "settings_visits", "signups", "summerjob_usage", "tax_module_usage",
        "tuition_fees_recorded",
    ]
    
    feature_data:List[Dict] = []
    for _, row in df.iterrows():
        feature_row = {col: np.random.poisson(0.5) if "usage" in col else random.randint(0, 5) for col in behaviors}
        feature_row.update({
            "session_key": row["session_key"]
        })
        feature_data.append(feature_row)
    
    return pd.DataFrame(feature_data)

# Generate Fake Dataset
def generate_fake_dataset(total_users:int=3_000, max_cohort_groups:int=20, maximum_session_per_user:int=30, output_path:str="synthetic_user_sessions_data.csv")->None:
    arranged_cols:list[str] = ["session_key","user_key","group_code","registration_date","user_platform","event_platform","session_start_time","session_day","session_end_time","duration_mins","plans_count","accounts_count","banking_usage","budgets_created","budgeting_usage","library_views","library_banking_views","library_budgeting_views","library_investing_views","credit_usage","dashboard_visits","goals_created","goal_module_usage","internship_submissions","investing_usage","logins","onboarding_info_completed","onboarding_avatar_done","onboarding_hobbies_set","onboarding_questions_answered","qa_interactions","saving_entries","settings_visits","signups","summerjob_usage","tax_module_usage","tuition_fees_recorded",]
    users:pd.DataFrame = create_users(num_users=total_users, max_groups=max_cohort_groups)
    sessions:pd.DataFrame = create_sessions(df=users, max_sessions_per_user=maximum_session_per_user)
    features:pd.DataFrame = generate_behavior_features(df=sessions)
    df:pd.DataFrame = sessions.merge(users, on="user_key").merge(features, on="session_key")
    df["session_day"]:pd.Series = df["session_start_time"].dt.date
    df:pd.DataFrame = df[arranged_cols]
    print(f'[INFO] {time.ctime()} | Fake Data Shape: {df.shape}')
    df.to_csv(path_or_buf=output_path, sep=',', na_rep='', header=True, index=False, mode='w', encoding='utf-8')
    del df
    return None


if __name__ == "__main__":

    generate_fake_dataset(
          total_users=50,
          max_cohort_groups=3,
          maximum_session_per_user=10,
          output_path="synthetic_user_sessions.csv",
      )

