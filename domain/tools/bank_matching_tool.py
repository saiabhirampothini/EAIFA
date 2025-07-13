from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json
import re
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def find_matching_banks(user_data: dict, loan_type: str) -> list:
    prompt = PromptTemplate.from_template("""
You are a loan officer. Based on user data:
{user_data}

Suggest top 5 UK banks for a {loan_type} loan.

Respond ONLY with a **valid JSON object**. Do not include explanations or markdown. No extra text.

[
  {{
    "bank_name": "Barclays",
    "min_score_required": 730,
    "interest_rate": 5.6,
    "max_ltv": 80,
    "estimated_approval_chance": "Medium"
  }},
  ...
]
""")

    chain = prompt | llm

    # Get model response
    response = chain.invoke({"user_data": str(user_data), "loan_type": loan_type})
    output = response.content.strip()

    # Try to extract JSON array using regex
    try:
        match = re.search(r"\[\s*{.*?}\s*\]", output, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        else:
            print("🔴 No JSON array found in output:\n", output)
            raise ValueError("No valid JSON array found in model output.")
    except json.JSONDecodeError as e:
        print("🔴 JSON decode error.\nModel output was:\n", output)
        raise e
    
def find_matching_banks_wrapper(input_str: str) -> list:
    try:
        user_data, loan_type = json.loads(input_str)
        return find_matching_banks(user_data, loan_type)
    except Exception as e:
        return [{"error": "Invalid input format", "exception": str(e)}]
