from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json
import re

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

def generate_recommendations_llm(user_profile: dict) -> list:
    prompt = PromptTemplate.from_template("""
You are a credit expert. Based on this user's profile:
{user_profile}

Give 3 to 5 AI-based recommendations to help them improve their credit score and loan eligibility.

Respond ONLY as a valid JSON list of strings, like:
[
  "Reduce credit utilization below 30%",
  "Pay all bills on time consistently",
  "Avoid applying for multiple loans in a short period"
]
""")

    chain = prompt | llm
    response = chain.invoke({"user_profile": str(user_profile)})
    output = response.content.strip()

    try:
        match = re.search(r"\[\s*\".*?\"\s*\]", output, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        else:
            print("🔴 No valid JSON list found in output:\n", output)
            raise ValueError("No valid JSON list found.")
    except json.JSONDecodeError as e:
        print("🔴 JSON decode error. Raw model output:\n", output)
        raise e
