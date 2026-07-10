# agents/verification_agent.py

import requests
from config import CRM_URL

class VerificationAgent:
    """
    The Checker — Validates KYC against Tata Capital CRM.
    Returns full customer profile on success.
    """

    def run(self, phone: str) -> dict:
        try:
            resp = requests.get(f"{CRM_URL}/crm/customer/{phone}", timeout=5)
            resp.raise_for_status()
            data = resp.json()

            if not data["found"]:
                return {
                    "status": "NOT_FOUND",
                    "message": "This mobile number isn't registered with Tata Capital.",
                    "suggestion": "Please use your registered number, or call 1860-267-6060 to register."
                }

            customer = data["data"]

            if not customer.get("kyc_verified"):
                return {
                    "status": "KYC_INCOMPLETE",
                    "message": "Your KYC documents are incomplete in our system.",
                    "suggestion": "Please visit your nearest Tata Capital branch to complete KYC."
                }

            return {
                "status": "VERIFIED",
                "customer": customer,
                "message": f"Identity verified for {customer['name']}",
                "is_existing": customer.get("existing_customer", False),
            }

        except requests.ConnectionError:
            return {
                "status": "SERVICE_UNAVAILABLE",
                "message": "CRM service is temporarily unavailable.",
                "suggestion": "Please try again in a moment."
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Verification error: {str(e)}",
                "suggestion": "Please try again."
            }
        

        