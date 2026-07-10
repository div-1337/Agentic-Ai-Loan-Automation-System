# mock_services/mock_credit_bureau.py
# Run: uvicorn mock_services.mock_credit_bureau:app --port 8002 --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Mock Credit Bureau API v1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SCORES = {
    "9999999999": {
        "score": 780,
        "active_loans": 1,
        "total_outstanding": 85000,
        "payment_history": "Excellent",
        "credit_age_years": 6,
        "hard_inquiries_6m": 1,
    },
    "8888888888": {
        "score": 820,
        "active_loans": 0,
        "total_outstanding": 0,
        "payment_history": "Excellent",
        "credit_age_years": 9,
        "hard_inquiries_6m": 0,
    },
    "7777777777": {
        "score": 650,
        "active_loans": 3,
        "total_outstanding": 320000,
        "payment_history": "Fair — 2 late payments",
        "credit_age_years": 2,
        "hard_inquiries_6m": 4,
    },
    "6666666666": {
        "score": 0,
        "active_loans": 0,
        "total_outstanding": 0,
        "payment_history": "No history",
        "credit_age_years": 0,
        "hard_inquiries_6m": 0,
    },
}

@app.get("/bureau/score/{phone}")
def get_score(phone: str):
    data = SCORES.get(phone, {"score": 720, "active_loans": 1,
                               "total_outstanding": 50000,
                               "payment_history": "Good",
                               "credit_age_years": 3,
                               "hard_inquiries_6m": 2})
    return {
        "phone": phone,
        "credit_score": data["score"],
        "max_score": 900,
        "active_loans": data["active_loans"],
        "total_outstanding": data["total_outstanding"],
        "payment_history": data["payment_history"],
        "credit_age_years": data["credit_age_years"],
        "hard_inquiries_6m": data["hard_inquiries_6m"],
        "bureau": "MockCIBIL India",
        "report_date": datetime.now().strftime("%Y-%m-%d"),
    }

@app.get("/bureau/health")
def health():
    return {"status": "ok", "service": "Mock Credit Bureau"}

