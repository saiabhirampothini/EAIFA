from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json
import re

llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

def get_cluster_insights_llm(user_profile: dict, all_user_data_summary: str) -> dict:
    prompt = PromptTemplate.from_template("""
You are a credit analyst. Based on the user's profile:
{user_profile}

And the summary of other users:
{all_user_data_summary}

Cluster the user into a group with similar profiles and provide:
- cluster_id
- avg_score
- avg_income
- score_growth_rate
- common_behaviors (list)
- typical_time_to_loan_approval

Respond as a valid JSON dict, like:
{{
  "cluster_id": "A2",
  "avg_score": 710,
  "avg_income": 55000,
  "score_growth_rate": "moderate",
  "common_behaviors": ["pays on time", "low credit utilization"],
  "typical_time_to_loan_approval": "3-6 months"
}}
""")

    chain = prompt | llm
    response = chain.invoke({
        "user_profile": str(user_profile),
        "all_user_data_summary": all_user_data_summary
    })

    output = response.content.strip()

    try:
        # Extract first valid JSON object using regex
        match = re.search(r"\{.*\}", output, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        else:
            print("🔴 No JSON object found in output:\n", output)
            raise ValueError("No valid JSON object found.")
    except json.JSONDecodeError as e:
        print("🔴 JSON parsing failed. Model output was:\n", output)
        raise e