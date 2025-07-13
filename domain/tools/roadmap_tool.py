from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json
import re
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

def generate_roadmap_using_model(user_data: dict) -> list:
    prompt = PromptTemplate.from_template("""
You are a credit advisor. Given this user's data:
{user_data}

Generate a 12-month roadmap to improve loan eligibility. 

Respond as a JSON list of 12 dicts with the following keys:
- "month": str (e.g., "Aug 2025")
- "action": str
- "impact": str
- "how much score can be improved":str   
- "oldScore":int
- "newScore":int
- "increasingTheIncome" : int                                                                                                                                                                

Example format:
[
  {{
    "month": "Aug 2025",
    "action": "Pay down credit card debt below 30%",
    "impact": "Improves credit utilization score",
    "how much score can be improved" : "This month 5 points score could be improved,
    "oldScore" : "what was the score before this month",
    "newScore" : "What will be the score that user can get after following the road map for this month, which takes the user a step closer to the credit score needed to get the loan",
    "increasedIncome: "How much income should be increased by the user in GBP [oldIncome,newIncome,delta]                                                                                                                                                
  }},
  ...
]
""")

    chain = prompt | llm
    response = chain.invoke({"user_data": str(user_data)})
    output = response.content.strip()

    try:
        match = re.search(r"\[\s*{.*?}\s*\]", output, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        else:
            print("🔴 No valid JSON list of dicts found in output:\n", output)
            raise ValueError("No valid roadmap JSON found.")
    except json.JSONDecodeError as e:
        print("🔴 JSON decode error. Raw model output:\n", output)
        raise e
