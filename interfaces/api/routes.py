from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import SessionLocal
from database.repositories.user_repo_sql import UserRepositorySQL
from application.services.user_service import UserService
from interfaces.request_models.api_models import EligibilityRequest, ChatQuery
from domain.agents.evaluate_agent import eligibility_agent_llm
from domain.tools.clustering_tool import get_cluster_insights_wrapper
from database.models import ChatHistory
import json
import google.generativeai as genai
import os 

# Configure Gemini once
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/user/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user_repo = UserRepositorySQL(db)
    user_service = UserService(user_repo)

    try:
        user = user_service.get_user_by_id(user_id)
        return {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "city": user.city,
            "country": user.country,
            "monthly_income": user.monthly_income,
            "credit_score_now": user.credit_score_now,
            "score_trend_12m": user.score_trend_12m,
            "score_factors_12m": user.score_factors_12m,
            "loans": [vars(loan) for loan in user.loans]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/api/user/eligibility-request")
def check_loan_eligibility(request: EligibilityRequest,db: Session = Depends(get_db)):
    user_repo = UserRepositorySQL(db)
    user_service = UserService(user_repo)
    try:
        user = user_service.get_user_by_id(request.user_id)
        all_users_summary = user_service.get_all_users_summary()

        user_data = {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "city": user.city,
            "country": user.country,
            "monthly_income": user.monthly_income,
            "credit_score_now": user.credit_score_now,
            "score_trend_12m": user.score_trend_12m,
            "score_factors_12m": user.score_factors_12m,
            "loans": [vars(loan) for loan in user.loans]
        }

        all_users_clustered_summary = get_cluster_insights_wrapper(user_data,all_users_summary)

        result = eligibility_agent_llm(
            user_data= user_data ,
            all_users_clustered_summary=all_users_clustered_summary,
            loan_type=request.loan_type,
            loan_amount=request.loan_amount,
            interest_rate=request.interest_rate,
            loan_months=request.loan_months,
            current_income=request.current_income
        )

        try:
            db.add(ChatHistory(
            user_id=request.user_id,
            message_type="user",
            content=f"Eligibility Request:\n{request.model_dump_json()}",
            ))
            # Save LLM result as a chat message
            db.add(ChatHistory(
                user_id=request.user_id,
                message_type="agent",
                content=json.dumps(result),
            ))
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



@router.post("/api/user/{user_id}/chat")
def user_chat(user_id: str, request_payload: ChatQuery, db: Session = Depends(get_db)):
    try:
        query = request_payload.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # 1. Fetch user's chat history
        chat_history = db.query(ChatHistory).filter_by(user_id=user_id).order_by(ChatHistory.timestamp).all()

        # 2. Convert to Gemini-compatible format
        gemini_history = [{
            "role": "model",
            "parts": ["You are Experian's AI financial advisor, your name is EAIFA. Be friendly, motivational, and data-driven. Your goal is to guide users toward improving loan eligibility with actionable insights and clear support. You have already given a detailed analysis of the user's profile and loans, along with much data like probability of getting a loan in future, with road map, score predection, inflation prediction, banks that gives loan in future with probability, score factors, dti ratios, recommendations, future salary required, credit score required to get the desired loan etc.., With lot more data and detailed analysis. Now, focus on answering the user's query with precision and clarity.And a note dont mention the implementation details of you, as well as the code level terms like json, model type,tech stacks etc.., **** And the reponses should be based on the details of the json object only****"]
        }]
        for msg in chat_history:
            role = "user" if msg.message_type == "user" else "model"  # Gemini uses 'model', not 'agent'
            gemini_history.append({"role": role, "parts": [msg.content]})

        # 3. Append current query
        gemini_history.append({"role": "user", "parts": [query]})

        # 4. Start Gemini chat with full history
        model = genai.GenerativeModel("gemini-1.5-flash")
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(query)

        # 5. Store messages in DB
        db.add(ChatHistory(user_id=user_id, message_type="user", content=query))
        db.add(ChatHistory(user_id=user_id, message_type="agent", content=response.text))
        db.commit()

        return {"response": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
