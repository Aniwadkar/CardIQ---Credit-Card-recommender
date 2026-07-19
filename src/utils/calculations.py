"""Utility functions for reward calculations"""
from typing import Dict
from src.config import POINT_VALUES

def calculate_category_rewards(
    monthly_spending: Dict[str, float],
    card_rewards: Dict[str, float],
    point_value: float
) -> float:
    """Calculate annual rewards for a card given spending pattern

    Note: flights, hotels, and transit are subsets of travel spending.
    We subtract them from travel to avoid double-counting.
    """
    annual_rewards = 0.0

    # Get travel subcategories
    flights = monthly_spending.get('flights', 0)
    hotels = monthly_spending.get('hotels', 0)
    transit = monthly_spending.get('transit', 0)
    travel = monthly_spending.get('travel', 0)

    # Calculate remaining general travel (excluding subcategories)
    remaining_travel = max(travel - (flights + hotels + transit), 0)

    for category, monthly_amount in monthly_spending.items():
        if category in card_rewards:
            reward_rate = card_rewards[category]

            # Special handling for travel to avoid double-counting
            if category == 'travel':
                # Only use the remaining travel amount (excluding subcategories)
                monthly_amount = remaining_travel

            # monthly_spend × 12 months × reward_rate × point_value
            annual_rewards += (monthly_amount * 12 * reward_rate * point_value)

    return annual_rewards

def calculate_net_value(
    annual_rewards: float,
    signup_bonus_value: float,
    annual_fee: float,
    annual_credits_value: float,
    year: int
) -> float:
    """Calculate net value for a specific year"""
    if year == 1:
        return annual_rewards + signup_bonus_value + annual_credits_value - annual_fee
    else:
        # Cumulative: previous year + this year's rewards
        year_1_value = annual_rewards + signup_bonus_value + annual_credits_value - annual_fee
        additional_years = (year - 1) * (annual_rewards + annual_credits_value - annual_fee)
        return year_1_value + additional_years

def get_point_value_for_rewards_type(rewards_type: str) -> float:
    """Get point value in cents based on rewards type"""
    return POINT_VALUES.get(rewards_type.lower(), 1.0)

def calculate_total_annual_credits(annual_credits: list) -> float:
    """Sum up all annual credits"""
    return sum(credit.get('value', 0) for credit in annual_credits)

def calculate_spending_percentages(monthly_spending: Dict[str, float]) -> Dict[str, float]:
    """Calculate percentage of total spend for each category"""
    total = sum(monthly_spending.values())
    if total == 0:
        return {cat: 0.0 for cat in monthly_spending.keys()}
    
    return {
        category: round((amount / total) * 100, 1)
        for category, amount in monthly_spending.items()
    }
