from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json
import re

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def predict_inflation_llm(current_date: str) -> dict:
    prompt = PromptTemplate.from_template("""
You are an economic forecaster. Given the current date: {current_date}, predict the monthly UK inflation rate for the next 12 months.Consider the real world data

Return the result as a valid JSON dict in this format:

{{
  "Aug 2025": 3.1,
  "Sep 2025": 3.0,
  "Oct 2025": 2.8,
  ...
  "Jul 2026": 2.5
}}
""")

    chain = prompt | llm
    response = chain.invoke({"current_date": current_date})
    output = response.content.strip()

    try:
        # Extract the first valid JSON dict block from the output
        match = re.search(r"\{.*?\}", output, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        else:
            print("🔴 No valid JSON object found in output:\n", output)
            raise ValueError("No valid JSON object found.")
    except json.JSONDecodeError as e:
        print("🔴 JSON decode error. Model output was:\n", output)
        raise e
