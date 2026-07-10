# mock_services/mock_crm.py
# Run: uvicorn mock_services.mock_crm:app --port 8001 --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Tata Capital Mock CRM API v1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Comprehensive mock customer database
CUSTOMERS = {
    # Happy path — instant approval
    "9999999999": {
        "name": "Rahul Sharma",
        "phone": "9999999999",
        "email": "rahul.sharma@gmail.com",
        "address": "12, MG Road, Bengaluru - 560001",
        "city": "Bengaluru",
        "kyc_verified": True,
        "kyc_type": "Aadhaar + PAN",
        "pre_approved_limit": 300000,
        "existing_customer": True,
        "tenure_years": 3,
        "account_type": "Salary Account",
        "employer": "Infosys Ltd",
        "dob": "1990-05-15",
    },
    # Salary slip path — loan > pre-approved but < 2x
    "8888888888": {
        "name": "Priya Patel",
        "phone": "8888888888",
        "email": "priya.patel@hotmail.com",
        "address": "45, Linking Road, Mumbai - 400050",
        "city": "Mumbai",
        "kyc_verified": True,
        "kyc_type": "Aadhaar + PAN",
        "pre_approved_limit": 500000,
        "existing_customer": True,
        "tenure_years": 5,
        "account_type": "Premium Account",
        "employer": "HDFC Bank",
        "dob": "1988-11-22",
    },
    # Rejection path — low credit score
    "7777777777": {
        "name": "Amit Verma",
        "phone": "7777777777",
        "email": "amit.verma@yahoo.com",
        "address": "8, Civil Lines, Jaipur - 302006",
        "city": "Jaipur",
        "kyc_verified": True,
        "kyc_type": "Voter ID + PAN",
        "pre_approved_limit": 200000,
        "existing_customer": False,
        "tenure_years": 0,
        "account_type": "Basic Account",
        "employer": "Self-Employed",
        "dob": "1995-03-08",
    },
    # KYC failed path
    "6666666666": {
        "name": "Sunita Devi",
        "phone": "6666666666",
        "email": "sunita@email.com",
        "address": "Pending update",
        "city": "Delhi",
        "kyc_verified": False,
        "kyc_type": "Pending",
        "pre_approved_limit": 0,
        "existing_customer": False,
        "tenure_years": 0,
        "account_type": "Basic Account",
        "employer": "Unknown",
        "dob": "1992-07-30",
    },
}

@app.get("/crm/customer/{phone}")
def get_customer(phone: str):
    c = CUSTOMERS.get(phone)
    if not c:
        return {"found": False, "message": "Customer not registered with Tata Capital"}
    return {"found": True, "data": c}

@app.get("/crm/health")
def health():
    return {"status": "ok", "service": "Mock CRM", "records": len(CUSTOMERS)}


    