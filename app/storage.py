from typing import Dict, List, Optional
from datetime import datetime, timezone
from uuid import uuid4
from app.models import ExpenseClaimResponse, ClaimStatus


class ExpenseClaimStore:
    def __init__(self):
        self.claims: Dict[str, dict] = {}
        self.claim_counter = 0

    def create_claim(
        self,
        employee_id: str,
        amount: float,
        description: str,
        receipt_path: str,
        category: Optional[str] = None,
        manager_id: Optional[str] = None,
    ) -> ExpenseClaimResponse:
        self.claim_counter += 1
        claim_id = f"CLM{self.claim_counter:05d}"
        now = datetime.now(timezone.utc)

        claim = {
            "claim_id": claim_id,
            "employee_id": employee_id,
            "amount": amount,
            "description": description,
            "receipt_path": receipt_path,
            "category": category,
            "status": ClaimStatus.DRAFT,
            "manager_id": manager_id,
            "submission_date": None,
            "approval_reason": None,
            "processed_date": None,
            "created_at": now,
            "updated_at": now,
        }

        self.claims[claim_id] = claim
        return ExpenseClaimResponse(**claim)

    def get_claim(self, claim_id: str) -> Optional[ExpenseClaimResponse]:
        if claim_id not in self.claims:
            return None
        return ExpenseClaimResponse(**self.claims[claim_id])

    def update_claim(
        self,
        claim_id: str,
        amount: Optional[float] = None,
        description: Optional[str] = None,
        receipt_path: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Optional[ExpenseClaimResponse]:
        if claim_id not in self.claims:
            return None

        claim = self.claims[claim_id]

        if amount is not None:
            claim["amount"] = amount
        if description is not None:
            claim["description"] = description
        if receipt_path is not None:
            claim["receipt_path"] = receipt_path
        if category is not None:
            claim["category"] = category

        claim["updated_at"] = datetime.now(timezone.utc)
        return ExpenseClaimResponse(**claim)

    def list_claims(self) -> List[ExpenseClaimResponse]:
        return [ExpenseClaimResponse(**claim) for claim in self.claims.values()]

    def submit_claim(self, claim_id: str) -> Optional[ExpenseClaimResponse]:
        if claim_id not in self.claims:
            return None

        claim = self.claims[claim_id]
        claim["status"] = ClaimStatus.SUBMITTED
        claim["submission_date"] = datetime.now(timezone.utc)
        claim["updated_at"] = datetime.now(timezone.utc)
        return ExpenseClaimResponse(**claim)

    def approve_claim(
        self, claim_id: str, approval_reason: str
    ) -> Optional[ExpenseClaimResponse]:
        if claim_id not in self.claims:
            return None

        claim = self.claims[claim_id]
        claim["status"] = ClaimStatus.APPROVED
        claim["approval_reason"] = approval_reason
        claim["updated_at"] = datetime.now(timezone.utc)
        return ExpenseClaimResponse(**claim)

    def reject_claim(
        self, claim_id: str, rejection_reason: str
    ) -> Optional[ExpenseClaimResponse]:
        if claim_id not in self.claims:
            return None

        claim = self.claims[claim_id]
        claim["status"] = ClaimStatus.REJECTED
        claim["approval_reason"] = rejection_reason
        claim["updated_at"] = datetime.now(timezone.utc)
        return ExpenseClaimResponse(**claim)

    def process_claim(self, claim_id: str) -> Optional[ExpenseClaimResponse]:
        if claim_id not in self.claims:
            return None

        claim = self.claims[claim_id]
        claim["status"] = ClaimStatus.PROCESSED
        claim["processed_date"] = datetime.now(timezone.utc)
        claim["updated_at"] = datetime.now(timezone.utc)
        return ExpenseClaimResponse(**claim)

    def cancel_claim(self, claim_id: str) -> Optional[ExpenseClaimResponse]:
        if claim_id not in self.claims:
            return None

        claim = self.claims[claim_id]
        claim["status"] = ClaimStatus.CANCELLED
        claim["updated_at"] = datetime.now(timezone.utc)
        return ExpenseClaimResponse(**claim)


# Global store instance
store = ExpenseClaimStore()
