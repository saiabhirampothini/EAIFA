from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
import json
from dotenv import load_dotenv
import re

load_dotenv()

# Import your tool functions
from domain.tools.score_forecast_tool import generate_credit_forecast_llm
from domain.tools.inflation_tool import predict_inflation_llm
from domain.tools.dti_emi_tool import explain_emi_dti_llm
from domain.tools.roadmap_tool import generate_roadmap_using_model
from domain.tools.clustering_tool import get_cluster_insights_wrapper
from domain.tools.bank_matching_tool import find_matching_banks_wrapper
from domain.tools.recommendation_tool import generate_recommendations_llm

# Wrap each tool in a LangChain Tool interface (returns raw Python object → not json.dumps)
tools = [
    Tool(
        name="EMI_DTI_Tool",
        func=lambda user_data_str: explain_emi_dti_llm(json.loads(user_data_str)),
        description="Calculate EMI and DTI given user data JSON string."
    ),
    Tool(
        name="Credit_Score_Forecast_Tool",
        func=lambda user_data_str: generate_credit_forecast_llm(json.loads(user_data_str)),
        description="Forecast credit score given user data JSON string."
    ),
    Tool(
        name="Inflation_Prediction_Tool",
        func=lambda date_str: predict_inflation_llm(date_str),
        description="Predict inflation rate given a date string in YYYY-MM format."
    ),
    Tool(
        name="Roadmap_Generation_Tool",
        func=lambda user_data_str: generate_roadmap_using_model(json.loads(user_data_str)),
        description="Generate loan eligibility roadmap given user data JSON string."
    ),
    Tool(
    name="Bank_Matching_Tool",
    func=find_matching_banks_wrapper,
    description="Find top 5 UK banks for a given user and loan type. Input must be a JSON array: [user_data, loan_type]"
    ),

    Tool(
        name="Recommendations_Tool",
        func=lambda user_data_str: generate_recommendations_llm(json.loads(user_data_str)),
        description="Generate AI recommendations given user data JSON string."
    )
]

# Initialize LangChain agent
llm = ChatOpenAI(model="gpt-4o", temperature=0)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=25,
    max_execution_time=300,
    handle_parsing_errors=True
)

# Final agent wrapper function
def eligibility_agent_llm(user_data: dict, all_users_clustered_summary: str, loan_type: str,
                          loan_amount: float, interest_rate: float, loan_months: int,current_income:int) -> dict:
    prompt = f"""
You are a loan eligibility agent with access to the following tools:

- EMI_DTI_Tool
- Credit_Score_Forecast_Tool
- Inflation_Prediction_Tool
- Roadmap_Generation_Tool
- Cluster_Insights_Tool
- Bank_Matching_Tool
- Recommendations_Tool

Your job is to call these tools as needed to analyze the user profile and return a loan eligibility analysis.

User data:
{json.dumps(user_data)}

All users clustered summary:
{all_users_clustered_summary}

Loan parameters:
Loan type: {loan_type}
Loan amount: {loan_amount}
Interest rate: {interest_rate}
Loan months: {loan_months}
Current Income of User: {current_income}

Output a VALID JSON object in the following format:

{{
  "user_id": "{user_data['user_id']}",
  "is_eligible": true or false,
  "income_required": number or null, (it is the min income required to get that loan),
  "min_score_required:number (it is the minimum score required to get any loan of the required amount)
  "loan_approval_probability": number,
  "eligibility_gap_reasons": ["reason1", "reason2"],
  "risk_flags": ["High DTI", "Recent credit inquiry", "Multiple open loans"],
  "analytics": {{
    "dti_percentage": number,
    "credit_score_now": number,
    "credit_score_forecast": {{
      "YYYY-MM": number,
      ...
    }},
    "expected_emi": number,
    "loan_term_months": {loan_months},
    "interest_rate_used": {interest_rate},
    "inflation_rate_applied": number
  }},
  "score_factors_weights": {{
    "payment_history": 35,
    "credit_utilization": 30,
    "credit_age": 15,
    "inquiries": 10,
    "credit_mix": 10
  }},
  "roadmap": [{{"month": "...", "action": "...", "impact": "..."}}],
  "recommendation_priority": [
    "Pay down revolving credit to under 30%",
    "Maintain on-time payments for next 6 months",
    "Avoid applying for any new loans"
  ],
  "ai_recommendations": ["..."],
  "top_bank_matches": [{{"bank_name": "...", "min_score_required": ..., ...}}],
  "cluster_insights": {{
    "cluster_id": "...", "avg_score": ..., ...
  }},
  "inflation_forecast": {{
    "YYYY-MM": number,
    ...
  }}
}}
"""

    try:
        response = agent.run(prompt)

        # Try to extract the first full JSON dict using regex
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            raise ValueError("No valid JSON found in agent output.")

    except Exception as e:
        return {
            "error": "Failed to parse agent output as JSON",
            "exception": str(e),
            "raw_output": response if 'response' in locals() else None
        }


