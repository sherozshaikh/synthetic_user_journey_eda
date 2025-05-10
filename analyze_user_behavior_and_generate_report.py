# pip3 install lifelines

from io import BytesIO
import base64
import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
from lifelines import KaplanMeierFitter

class Analysis():
    def __init__(self, df, churn_thresholds=[15, 30, 45, 60, 90]):
        self.req_cols = [
            "user_key",
            "group_code",
            "session_key",
            "registration_date",
            "session_day",
            "session_start_time",
            "duration_mins",
            "event_platform",
            "user_platform",
            "plans_count",
            "accounts_count",
            "banking_usage",
            "budgets_created",
            "budgeting_usage",
            "library_banking_views",
            "library_budgeting_views",
            "library_views",
            "library_investing_views",
            "credit_usage",
            "dashboard_visits",
            "goals_created",
            "goal_module_usage",
            "internship_submissions",
            "investing_usage",
            "logins",
            "onboarding_info_completed",
            "onboarding_avatar_done",
            "onboarding_hobbies_set",
            "onboarding_questions_answered",
            "qa_interactions",
            "saving_entries",
            "settings_visits",
            "signups",
            "summerjob_usage",
            "tax_module_usage",
            "tuition_fees_recorded",
        ]
        self.feature_columns = [
            "plans_count",
            "accounts_count",
            "banking_usage",
            "budgets_created",
            "budgeting_usage",
            "library_views",
            "library_banking_views",
            "library_budgeting_views",
            "library_investing_views",
            "credit_usage",
            "dashboard_visits",
            "goals_created",
            "goal_module_usage",
            "internship_submissions",
            "investing_usage",
            "logins",
            "onboarding_info_completed",
            "onboarding_avatar_done",
            "onboarding_hobbies_set",
            "onboarding_questions_answered",
            "qa_interactions",
            "saving_entries",
            "settings_visits",
            "signups",
            "summerjob_usage",
            "tax_module_usage",
            "tuition_fees_recorded",
        ]
        self.df = (
            df[self.req_cols].dropna(axis=0, subset=["group_code"], how="all").copy()
        )
        self.figsize = (14, 8)
        self.churn_thresholds = churn_thresholds

    def preprocess(self):
        self.df["group_code"] = (
            self.df["group_code"].astype(str).str.replace(".0", "", regex=False)
        )
        self.df["session_start_time"] = pd.to_datetime(
            self.df["session_start_time"]
        )
        self.df["session_hour"] = pd.to_datetime(
            self.df["session_start_time"]
        ).dt.hour
        self.df["session_weekday"] = pd.to_datetime(
            self.df["session_start_time"]
        ).dt.day_name()
        self.df["session_start_date_only"] = self.df["session_start_time"].dt.date
        self.df["session_day"] = pd.to_datetime(self.df["session_day"])
        self.df = self.df.sort_values(by=["session_day"], ascending=True, inplace=False)
        self.df["registration_date"] = pd.to_datetime(self.df["registration_date"])
        self.df["days_since_signup"] = (
            self.df["session_day"] - self.df["registration_date"]
        )
        self.df["session_rank"] = self.df.groupby("user_key")[
            "session_start_time"
        ].rank(method="first")

    def create_plot_page(
        self,
        page_num,
        title,
        plot_html,
        description,
        insight,
        icon=None,
        section_id=None,
    ):
        icon_html = f"<span class='icon'>{icon}</span>" if icon else ""
        section_id_attr = f"id='{section_id}'" if section_id else ""
        return f"""<div class="page" {section_id_attr}><h2>{icon_html}{title}</h2>{plot_html}<p class="description">{description}</p><p class="insight"><strong>How to interpret:</strong> {insight}</p><div class="footer">Page {page_num}</div></div>"""

    def mpl_to_base64(self):
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("UTF-8")

    def annotate_bars(self, ax, int_=True):
        for p in ax.patches:
            height = p.get_height()
            if int_:
                if height > 0:
                    ax.annotate(
                        f"{int(height)}",
                        (p.get_x() + p.get_width() / 2, height),
                        ha="center",
                        va="center",
                        fontsize=8,
                        color="black",
                        xytext=(0, 5),
                        textcoords="offset points",
                    )
            else:
                if p.get_height() > 0.0:
                    ax.annotate(
                        f"{round(number=p.get_height(), ndigits=2)}",
                        (p.get_x() + p.get_width() / 2, p.get_height()),
                        ha="center",
                        va="center",
                        fontsize=8,
                        color="black",
                        xytext=(0, 5),
                        textcoords="offset points",
                    )

    def plot_users_per_cohort(self):
        plt.figure(figsize=self.figsize)
        ax = sns.barplot(
            data=self.df.drop_duplicates(subset=["group_code", "user_key"])
            .groupby("group_code")
            .size()
            .reset_index(name="count")
            .sort_values(by="count", ascending=False),
            x="group_code",
            hue="group_code",
            legend=False,
            y="count",
            palette="pastel",
        )
        self.annotate_bars(ax)
        plt.xlabel("Cohort")
        plt.ylabel("Count")
        plt.tight_layout()
        return f"<img src='data:image/png;base64,{self.mpl_to_base64()}'/>"

    def plot_device_usage(self):
        plt.figure(figsize=self.figsize)
        ax = sns.barplot(
            data=self.df.groupby(["group_code", "user_platform", "event_platform"])
            .size()
            .reset_index(name="count"),
            x="user_platform",
            y="count",
            hue="event_platform",
            palette="pastel",
        )
        self.annotate_bars(ax)
        plt.xlabel("Device Type at Signup")
        plt.ylabel("Count")
        plt.tight_layout()
        return f"<img src='data:image/png;base64,{self.mpl_to_base64()}'/>"

    def plot_hourly_activity(self):
        plt.figure(figsize=self.figsize)
        ax = sns.histplot(self.df["session_hour"], bins=24, kde=True, color="skyblue")
        self.annotate_bars(ax)
        plt.xlabel("Hour of Day")
        plt.ylabel("Session Count")
        plt.tight_layout()
        return f"<img src='data:image/png;base64,{self.mpl_to_base64()}'/>"

    def plot_weekday_activity(self):
        plt.figure(figsize=self.figsize)
        ax = sns.countplot(
            data=self.df,
            x="session_weekday",
            hue="session_weekday",
            legend=False,
            order=[
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
            palette="pastel",
        )
        self.annotate_bars(ax)
        plt.xlabel("Weekday")
        plt.ylabel("Session Count")
        plt.tight_layout()
        return f"<img src='data:image/png;base64,{self.mpl_to_base64()}'/>"

    def plot_login_by_weekday(self):
        plt.figure(figsize=self.figsize)
        weekday_login = (
            self.df.groupby("session_weekday")["logins"]
            .sum()
            .reindex(
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
            )
        )
        ax = sns.barplot(
            x=weekday_login.index, y=weekday_login.values, palette="pastel", hue=weekday_login.index, legend=False,
        )
        self.annotate_bars(ax)
        plt.xlabel("Weekday")
        plt.ylabel("Total Logins")
        plt.tight_layout()
        return f"<img src='data:image/png;base64,{self.mpl_to_base64()}'/>"

    def plot_feature_engagement(self):
        plt.figure(figsize=self.figsize)
        feature_engagement = (
            self.df.melt(
                id_vars=["group_code"],
                value_vars=self.feature_columns,
                var_name="feature",
                value_name="usage_count",
            )
            .groupby(by=["group_code", "feature"])["usage_count"]
            .sum()
            .reset_index()
        )
        feature_engagement["feature"] = feature_engagement["feature"].str.replace(
            "_count", "", regex=False
        )
        total_usage = feature_engagement.groupby("feature")["usage_count"].sum()
        non_zero_features = total_usage[total_usage > 0].index.tolist()
        feature_engagement = feature_engagement[
            feature_engagement["feature"].isin(non_zero_features)
        ]
        feature_order = (
            feature_engagement.groupby("feature")["usage_count"]
            .sum()
            .sort_values(ascending=False)
            .index.tolist()
        )
        ax = sns.barplot(
            data=feature_engagement,
            x="feature",
            y="usage_count",
            hue="group_code",
            palette="pastel",
            order=feature_order,
        )
        self.annotate_bars(ax)
        plt.xticks(rotation=90)
        plt.xlabel("Features")
        plt.ylabel("Total Usage Count")
        plt.legend(title="Cohort")
        plt.tight_layout()
        return f"<img src='data:image/png;base64,{self.mpl_to_base64()}'/>"

    def plot_repeat_feature_usage(self):
        avg_feature_usage = self.df[self.feature_columns].mean()
        avg_feature_usage = avg_feature_usage[avg_feature_usage > 0.01]
        avg_feature_usage = avg_feature_usage.sort_values(ascending=False)
        avg_feature_usage.index = [
            col.replace("_count", "") for col in avg_feature_usage.index
        ]
        plt.figure(figsize=self.figsize)
        ax = sns.barplot(
            x=avg_feature_usage.index, y=avg_feature_usage.values, palette="pastel", hue=avg_feature_usage.index, legend=False,
        )
        self.annotate_bars(ax, int_=False)
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Average Usage Count")
        plt.xlabel("Features")
        plt.tight_layout()
        return f"<img src='data:image/png;base64,{self.mpl_to_base64()}'/>"

    def plot_feature_usage_distribution(self):
        feature_usage = (
            self.df[self.feature_columns]
            .sum()
            .sort_values(ascending=False)
            .reset_index(name="count")
        )
        feature_usage["index"] = feature_usage["index"].str.replace(
            "_count", "", regex=False
        )
        feature_usage = feature_usage[feature_usage["count"] > 0]
        plt.figure(figsize=self.figsize)
        ax = sns.barplot(
            x=feature_usage["index"], y=feature_usage["count"], palette="pastel", hue=feature_usage["index"], legend=False,
        )
        self.annotate_bars(ax)
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Total Count")
        plt.xlabel("Features")
        plt.tight_layout()
        return f"<img src='data:image/png;base64,{self.mpl_to_base64()}'/>"

    def plot_session_frequency(self):
        plt.figure(figsize=self.figsize)
        ax = sns.histplot(
            self.df.groupby("user_key")["session_key"]
            .nunique()
            .reset_index()["session_key"],
            bins=50,
            kde=True,
            color="purple",
        )
        self.annotate_bars(ax)
        plt.xlabel("Number of Sessions")
        plt.ylabel("Number of Users")
        plt.yscale("log")
        plt.tight_layout()
        return f"<img src='data:image/png;base64,{self.mpl_to_base64()}'/>"

    def plot_first_vs_later_session_duration(self):
        plt.figure(figsize=self.figsize)
        sns.kdeplot(
            self.df[self.df["session_rank"] == 1]["duration_mins"],
            label="First Session",
            fill=True,
        )
        sns.kdeplot(
            self.df[self.df["session_rank"] > 1]["duration_mins"],
            label="Later Sessions",
            fill=True,
            color="orange",
        )
        plt.title("First vs. Later Session Duration")
        plt.xlabel("Session Duration (minutes)")
        plt.ylabel("Density")
        plt.legend()
        plt.tight_layout()
        return f"<img src='data:image/png;base64,{self.mpl_to_base64()}'/>"

    def plot_session_duration_over_time(self):
        grouped = (
            self.df.groupby(["session_start_date_only", "group_code"])["duration_mins"]
            .mean()
            .reset_index()
        )
        fig = go.Figure()
        for cohort in grouped["group_code"].unique():
            cohort_data = grouped[grouped["group_code"] == cohort]
            fig.add_trace(
                go.Scatter(
                    x=cohort_data["session_start_date_only"],
                    y=cohort_data["duration_mins"],
                    mode="lines+markers",
                    name=f"Cohort {cohort}",
                )
            )
        fig.update_layout(
            title="Average Session Duration Over Time",
            xaxis_title="Date",
            yaxis_title="Avg Duration (minutes)",
            legend_title="Cohort ID",
            template="plotly_white",
        )
        return pio.to_html(fig, include_plotlyjs="cdn", full_html=False)

    def plot_kmf_over_thresholds(self):
        fig = go.Figure()
        for threshold in self.churn_thresholds:
            self.df["churned"] = self.df["days_since_signup"] < pd.Timedelta(
                days=threshold
            )
            kmf_df = self.df[self.df["days_since_signup"] > pd.Timedelta(0)][
                ["days_since_signup", "churned"]
            ]
            kmf = KaplanMeierFitter()
            kmf.fit(
                durations=kmf_df["days_since_signup"].dt.days,
                event_observed=~kmf_df["churned"],
            )
            fig.add_trace(
                go.Scatter(
                    x=kmf.survival_function_.index,
                    y=kmf.survival_function_["KM_estimate"],
                    mode="lines",
                    name=f"Churn-Threshold: {threshold} days",
                )
            )
        fig.update_layout(
            title="User Retention Curve Over Varying Churn Thresholds",
            xaxis_title="Days Since Signup",
            yaxis_title="Survival Probability",
            legend_title="Churn Thresholds",
            template="plotly_white",
        )
        return pio.to_html(fig, include_plotlyjs="cdn", full_html=False)

    def run(self):
        self.preprocess()
        page_num = 3
        toc_entries = [
            ("Users per Cohort", "users-cohort"),
            ("Device Usage", "device-usage"),
            ("Hourly Activity", "hourly-activity"),
            ("Weekday Activity", "weekday-activity"),
            ("Login by Weekday", "login-weekday"),
            ("Feature Engagement", "feature-engagement"),
            ("Repeat Feature Usage", "repeat-usage"),
            ("Feature Usage Distribution", "usage-distribution"),
            ("Session Frequency", "session-frequency"),
            ("First vs. Later Sessions", "first-vs-later"),
            ("Session Duration Over Time", "duration-over-time"),
            ("Retention Curve", "retention"),
        ]
        pages = [
            f"""<div class="page"><h1>🧠 Data Insight Studio</h1><p>Welcome to interactive user intelligence report designed to provide a comprehensive overview of key user behaviors, feature usage, retention trends and more-using visualizations and smart insights to help you understand your data in a deeper way.</p><p>Built for industry-level use cases, this report aims to help product teams, analysts and stakeholders make data-informed decisions quickly and confidently.</p><div class="footer">Page 1</div></div>""",
            f"""<div class="page" id="table-of-contents"><h2>📘 Table of Contents</h2><ul class="toc">{"".join(f"<li><a href='#{id_}'>{title}</a></li>" for title, id_ in toc_entries)}</ul><div class="footer">Page 2</div></div>""",
        ]
        reader_content = [
            (
                toc_entries[0],
                self.plot_users_per_cohort(),
                "This visualization displays the number of unique users in each cohort, where it uses a bar chart to show cohort sizes, sorted in descending order, giving a clear sense of relative cohort volumes. Each user is counted once per cohort, ensuring accuracy in representation and avoiding duplication. This is particularly valuable in understanding the distribution of user acquisition over time or across campaigns.",
                "Larger cohorts may point to successful acquisition campaigns, seasonal spikes, or effective onboarding strategies. Identifying top-performing cohorts allows product and growth teams to investigate what drove their success-be it marketing efforts, referral programs, feature rollouts, or user incentives. Conversely, smaller cohorts may highlight missed opportunities or signal areas for improvement in outreach or conversion. By analyzing user volume per cohort, teams can prioritize retention strategies for high-value groups and replicate successful acquisition patterns in future growth initiatives.",
                "👥",
            ),
            (
                toc_entries[1],
                self.plot_device_usage(),
                "This chart compares the device type used during signup with the devices users actually use during their session activities. The bar plot groups users by their signup device and breaks down session activity across different platforms (e.g., desktop, mobile, tablet) for each cohort. By visualizing device transition patterns-such as users signing up on one platform but engaging primarily on another-this analysis offers a layered view of how and where users choose to interact post-onboarding.",
                "Understanding device migration and multi-platform behavior is critical for optimizing user experience. For example, if a large share of users signs up on desktop but later shifts to mobile for engagement, it suggests the need for mobile-first design considerations, especially for retention-critical features. This insight also helps teams identify inconsistencies between acquisition and engagement platforms, guiding where to invest in UI/UX improvements, performance optimization, or cross-platform messaging. It's especially valuable for tailoring onboarding flows and anticipating support or functionality needs specific to each device type.",
                "📱",
            ),
            (
                toc_entries[2],
                self.plot_hourly_activity(),
                "This histogram illustrates user session volume across each hour of the day (0-23), revealing patterns in diurnal engagement behavior. The plot includes a kernel density estimate (KDE) to highlight underlying trends in hourly activity beyond raw session counts. This visualization is particularly useful for identifying time-based usage spikes and quiet periods, helping teams understand when users are most likely to interact with the product.",
                "By recognizing peak activity hours, you can better time product updates, support availability, push notifications, or marketing messages for maximum impact. If user engagement is heavily skewed toward specific times of day, it may also influence infrastructure scaling decisions or indicate opportunities to personalize time-sensitive features. For global platforms, time zone clustering may be inferred and teams can further explore regional segmentation to fine-tune the timing of in-app events or campaigns.",
                "⏰",
            ),
            (
                toc_entries[3],
                self.plot_weekday_activity(),
                "This count plot summarizes session activity across the days of the week, offering a view into weekly behavioral rhythms. The days are ordered from Monday through Sunday, making trends in weekday versus weekend engagement easy to interpret at a glance. Understanding these patterns is valuable for mapping user intent and planning time-sensitive interactions.",
                "Weekday activity spikes may reflect work or productivity related usage, while weekend patterns can suggest casual or leisure-time engagement. This insight helps tailor product experiences to match user expectations-for instance, prioritizing content or features with different use cases during the weekend vs. workdays. It can also support scheduling feature rollouts, downtime planning, or content marketing for maximum reach. Identifying dips may highlight disengagement windows or inspire experiments to increase stickiness on low-activity days.",
                "📅",
            ),
            (
                toc_entries[4],
                self.plot_login_by_weekday(),
                "This bar chart presents the total number of login events per weekday by aggregating login counts across all user sessions. It follows a chronological weekday order (Monday through Sunday), allowing for intuitive identification of access patterns throughout the week. Unlike raw session activity, this chart specifically focuses on login actions-offering a closer look at authentication frequency rather than general engagement.",
                "Understanding when users log in most often is crucial for identifying behavioral habits and platform touchpoints. A high volume of logins early in the week may indicate productivity-oriented use cases, while weekend spikes may point toward recreational or casual usage. This insight can inform everything from customer support hours and authentication system load management to the strategic timing of security features (e.g., 2FA prompts) or login-driven campaigns (e.g., streaks, reward activations). Identifying login drop-offs may also help surface friction in reactivation or accessibility.",
                "🔐",
            ),
            (
                toc_entries[5],
                self.plot_feature_engagement(),
                "This visualization breaks down feature usage counts across different user cohorts, showcasing which features are most heavily interacted with-and by whom. The chart uses a bar plot grouped by feature, with each bar segmented by cohort, enabling comparisons of feature adoption across time-based or campaign-driven user groups. Before plotting, the data filters out unused or zero-usage features, ensuring that the analysis focuses only on relevant interactions.",
                "Mapping feature usage by cohort reveals how different user segments interact with your product and whether recent cohorts are engaging differently compared to earlier ones. This is key for tracking feature adoption over time, validating product launches and tailoring onboarding to highlight the most relevant tools for each group. Disparities in feature usage between cohorts may indicate changes in user needs, gaps in discoverability, or the success of recent UX or product updates. This analysis can directly support roadmap prioritization by showing which features deliver value to key growth-driving segments.",
                "📊",
            ),
            (
                toc_entries[6],
                self.plot_repeat_feature_usage(),
                "This chart highlights the average usage frequency of individual features across all user sessions, excluding features with negligible interaction (less than 0.01 average usage). By focusing on features that demonstrate recurring use, it surfaces which tools or capabilities consistently attract user attention and engagement. The bars represent normalized usage across the entire dataset, offering a standardized view of which features are habitually used across your user base.",
                "This analysis is instrumental in identifying 'sticky' features-those that users return to repeatedly, indicating high utility, satisfaction, or value. These features often form the core of the product experience and can serve as anchors for onboarding, upsell paths, or habit-building strategies. Understanding which features are habitually used allows teams to allocate development and UX resources more effectively, double down on what's working and potentially deprecate or rework less relevant capabilities.",
                "🔁",
            ),
            (
                toc_entries[7],
                self.plot_feature_usage_distribution(),
                "This visualization presents the total usage count for each tracked feature, sorted in descending order. It offers a raw, unnormalized view of absolute engagement-highlighting the most frequently accessed functionalities across the entire user base. By filtering out features with zero interactions, the chart ensures a clean and focused representation of actual user behavior.",
                "This distribution uncovers which features are driving the bulk of user engagement. High-frequency features are likely central to user workflows, whereas low-frequency ones may suffer from discoverability issues, usability friction, or lack of perceived value. The analysis can guide product strategy by validating the prominence of flagship features and surfacing potential gaps in feature adoption. It's particularly valuable when assessing return on investment for recent launches or deciding which features should be promoted or simplified.",
                "📈",
            ),
            (
                toc_entries[8],
                self.plot_session_frequency(),
                "This histogram visualizes the distribution of how many sessions each user has initiated, based on a count of unique session IDs per user. The plot uses a log-scaled y-axis to accommodate the wide variance between casual and highly active users and includes a KDE (density curve) to illustrate underlying trends. This gives a quantitative overview of engagement intensity across your entire user base.",
                "Understanding session frequency is key to identifying distinct user segments-from one-time visitors to highly engaged power users. A long-tail distribution (many low-frequency users, few high-frequency ones) is typical in most digital products, but the shape and slope of this tail can signal product health. This insight enables tailored lifecycle messaging, supports feature targeting strategies and informs monetization opportunities (e.g., identifying high-frequency users for upsell or loyalty programs).",
                "🧍‍♂️",
            ),
            (
                toc_entries[9],
                self.plot_first_vs_later_session_duration(),
                "This dual KDE (Kernel Density Estimate) plot compares session duration between users' first sessions and all subsequent sessions. By analyzing the distribution of time spent, this chart reveals how user engagement evolves after the initial interaction. First sessions are separated using session rank, making it easy to evaluate onboarding quality versus ongoing engagement.",
                "If first sessions are short and later sessions are longer, it may indicate that users need time to discover value-or that your onboarding is insufficient. Conversely, if early sessions are long but drop off later, it may suggest initial curiosity followed by disengagement. These patterns help diagnose onboarding effectiveness, inform activation metrics and reveal whether users are building long-term habits or experiencing early drop-off after exploration.",
                "🎯",
            ),
            (
                toc_entries[10],
                self.plot_session_duration_over_time(),
                "This time-series line chart tracks the average session duration per cohort across calendar dates. Each line represents a distinct user cohort, enabling longitudinal comparison of how engagement depth (measured in minutes) changes over time. The function aggregates session duration daily and segments it by cohort, giving a detailed look at how different user groups interact over the lifecycle.",
                "Fluctuations in session duration can signal changes in product experience, content quality, or feature relevance. A steady increase over time may reflect improved user understanding or stickier functionality, while drops might point to usability issues, disengagement, or product fatigue. Cohort-based trends allow you to assess the long-term impact of product changes and differentiate between temporary dips and structural engagement shifts-helping you fine-tune retention strategies and feature optimization.",
                "📉",
            ),
            (
                toc_entries[11],
                self.plot_kmf_over_thresholds(),
                "This interactive chart presents Kaplan-Meier survival curves, visualizing user retention across different churn threshold definitions (e.g., 7, 14, 30 days without return). Each curve represents the probability of a user remaining active as a function of time since signup, calculated using survival analysis. The analysis excludes users with zero days of activity and dynamically adjusts the 'churned' label based on configurable thresholds. This allows for a more flexible, scenario-based exploration of how retention behaves under various business rules or lifecycle definitions.",
                "Kaplan-Meier curves provide a statistically grounded method for evaluating retention over time. Unlike basic retention metrics, these curves account for censored data-users who haven't yet churned-which makes them more robust, especially for products with long user lifecycles. Comparing curves across thresholds reveals how sensitive retention performance is to changes in your churn definition. A steep early drop-off might signal onboarding issues, while a gradual decline suggests sustained engagement. Identifying crossover points or stability plateaus helps inform when to invest in reactivation strategies, loyalty programs, or habit-forming features. This visualization is particularly powerful for benchmarking the effectiveness of lifecycle interventions and understanding how engagement decays across different user cohorts.",
                "📉",
            ),
        ]
        for (title, id_), plot_func, desc, insight, icon in reader_content:
            pages.append(self.create_plot_page(page_num, title, plot_func, desc, insight, icon=icon, section_id=id_))
            page_num += 1
        full_html = f"""<html><head><meta charset="utf-8"><title>🧠 Data Insight Studio</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet"><style>body {{font-family: 'Inter', sans-serif;margin: 0;padding: 0;background-color: #f9fafb;color: #2c3e50;}}.page {{max-width: 960px;margin: 80px auto;background: white;padding: 60px 40px;border-radius: 10px;box-shadow: 0 0 12px rgba(0,0,0,0.05);page-break-after: always;}}h1 {{font-size: 2.4rem;color: #1a202c;text-align: center;margin-bottom: 40px;}}h2 {{font-size: 1.8rem;color: #1a202c;margin-bottom: 20px;display: flex;align-items: center;}}.icon {{margin-right: 10px;}}.description {{font-size: 1rem;color: #444;margin-top: 20px;}}.insight {{font-size: 0.95rem;font-style: italic;color: #555;margin-top: 10px;}}.footer {{text-align: right;margin-top: 60px;font-size: 0.9rem;color: #aaa;}}img {{width: 100%;max-width: 800px;display: block;margin: 20px auto;border-radius: 8px;box-shadow: 0 2px 4px rgba(0,0,0,0.05);}}.toc {{list-style-type: none;padding-left: 0;font-size: 1rem;}}.toc li {{margin-bottom: 12px;}}.toc a {{text-decoration: none;color: #1f7aec;}}.toc a:hover {{text-decoration: underline;}}@media print {{body {{margin: 0;}}.page {{max-width: 100%;margin: 0;padding: 20px;}}.footer {{position: fixed;bottom: 0;width: 100%;text-align: center;}}.toc {{page-break-before: always;}}}}</style></head><body>{"".join(pages)}</body></html>"""

        with open(f"Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html","wb") as f:
            f.write(full_html.encode("UTF-8"))
        return None
