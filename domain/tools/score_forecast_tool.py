from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json
import re

llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

def generate_credit_forecast_llm(user_profile: dict) -> dict:
    prompt = PromptTemplate.from_template("""
You are a credit bureau analyst. The user has the following monthly credit score history for the past 12 months:
{user_profile}

Based on this trend, forecast the user's credit score for the next 12 months.

Respond ONLY with a **valid JSON object**. Do not include explanations or markdown. No extra text.
{{
  "2025-08": 670,
  "2025-09": 675,
  ...
  "2026-07": 700
}}
""")

    chain = prompt | llm
    response = chain.invoke({"user_profile": str(user_profile)})
    output = response.content.strip()

    try:
        match = re.search(r"\{.*?\}", output, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        else:
            print("🔴 No valid JSON object found in output:\n", output)
            raise ValueError("No valid JSON forecast dict found.")
    except json.JSONDecodeError as e:
        print("🔴 JSON decode error. Raw model output:\n", output)
        raise e
