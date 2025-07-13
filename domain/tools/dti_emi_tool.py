from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json
import re

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def explain_emi_dti_llm(user_details: dict) -> dict:
    prompt = PromptTemplate.from_template("""
You are a financial calculator. Given the user's details:
{user_details}

Calculate:
- expected_emi
- dti_percentage
- credit_score_now

Respond ONLY with a **valid JSON object**. Do not include explanations or markdown. No extra text.

Example format:
{{
  "expected_emi": 1234,
  "dti_percentage": 20.5,
  "credit_score_now": 680
}}
""")

    chain = prompt | llm
    response = chain.invoke({"user_details": str(user_details)})
    output = response.content.strip()

    try:
        match = re.search(r"\{.*\}", output, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        else:
            print("🔴 No valid JSON object found in output:\n", output)
            raise ValueError("No valid JSON object found.")
    except json.JSONDecodeError as e:
        print("🔴 JSON decode failed. Raw model output:\n", output)
        raise e
