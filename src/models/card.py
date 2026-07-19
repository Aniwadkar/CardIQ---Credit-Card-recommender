"""Pydantic model for credit card data"""
from pydantic import BaseModel
from typing import List, Dict, Optional

class SignupBonus(BaseModel):
    """Signup bonus details"""
    amount: Optional[float]
    currency: Optional[str]
    spend_requirement: Optional[int]
    timeframe_months: Optional[int]
    estimated_value: Optional[float]
    qualification_type: str = "spend"
    details: Optional[str] = None

class Eligibility(BaseModel):
    """Card eligibility requirements"""
    credit_tier: str
    min_credit_score: int

class AnnualCredit(BaseModel):
    """Annual credit/benefit"""
    name: str
    value: float
    category: str

class CreditCard(BaseModel):
    """Complete credit card model"""
    card_id: str
    card_name: str
    issuer: str
    annual_fee: float
    signup_bonus: SignupBonus
    rewards: Dict[str, float]
    rewards_type: str
    point_value: float
    eligibility: Eligibility
    annual_credits: List[AnnualCredit]
    description: str
    best_for: List[str]
    foreign_transaction_fee: float
    special_features: List[str]
    product_status: str = "active"
    source_url: str
    source_last_checked: str
    source_note: Optional[str] = None
