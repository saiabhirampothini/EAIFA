import pandas as pd
import numpy as np
import json
from sklearn.cluster import KMeans
from collections import defaultdict

def get_cluster_insights_ml(user_profile: dict, all_user_data_summary: str) -> dict:
    try:
        # Step 1: Convert all user data to DataFrame
        all_users_data = json.loads(all_user_data_summary)
        df = pd.DataFrame(all_users_data)

        required_fields = ["monthly_income", "credit_score_now", "dti", "loan_count"]
        for field in required_fields:
            if field not in df.columns:
                raise ValueError(f"Missing required field '{field}' in all_user_data_summary")

        df = df.dropna(subset=required_fields).copy()

        # Step 2: Apply KMeans Clustering
        kmeans = KMeans(n_clusters=5, random_state=42, n_init="auto")
        df["cluster_id"] = kmeans.fit_predict(df[required_fields])

        # Step 3: Prepare user vector from current profile
        user_vector = np.array([[
            user_profile.get("monthly_income", 0),
            user_profile.get("credit_score_now", 0),
            user_profile.get("dti", 0),
            len(user_profile.get("loans", []))
        ]])
        cluster_id = int(kmeans.predict(user_vector)[0])
        cluster_data = df[df["cluster_id"] == cluster_id]

        # Step 4: Score growth rate
        trend = user_profile.get("score_trend_12m", [])
        growth_rate = "unknown"
        if isinstance(trend, list) and len(trend) > 1:
            delta = trend[-1] - trend[0]
            if delta > 20:
                growth_rate = "rising"
            elif delta < -20:
                growth_rate = "declining"
            else:
                growth_rate = "stable"

        # Step 5: Heuristic behaviors
        behaviors = []
        if cluster_data["dti"].mean() < 20:
            behaviors.append("low credit utilization")
        if cluster_data["loan_count"].mean() < 2:
            behaviors.append("low borrowing frequency")
        if cluster_data["credit_score_now"].mean() > 700:
            behaviors.append("pays on time")

        # Step 6: Estimated approval time (simulated heuristic)
        avg_score = cluster_data["credit_score_now"].mean()
        if avg_score >= 740:
            time_to_loan = "1-2 months"
        elif avg_score >= 680:
            time_to_loan = "3-6 months"
        else:
            time_to_loan = "6-9 months"

        # Step 7: Final output
        return {
            "cluster_id": f"C{cluster_id}",
            "avg_score": round(avg_score, 2),
            "avg_income": round(cluster_data["monthly_income"].mean(), 2),
            "score_growth_rate": growth_rate,
            "common_behaviors": behaviors,
            "typical_time_to_loan_approval": time_to_loan
        }

    except Exception as e:
        return {
            "error": "Failed to compute cluster insights",
            "exception": str(e)
        }

def get_cluster_insights_wrapper(user_profile: dict, all_users_summary: str) -> dict:
    return get_cluster_insights_ml(user_profile, all_users_summary)
