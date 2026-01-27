"""Claude API client wrapper"""
from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY, HAIKU_MODEL, SONNET_MODEL, USE_MOCK_MODE
import json

class MockClaudeClient:
    """Mock client for demo mode (no API key required)"""
    
    def __init__(self):
        self.haiku_model = "mock-haiku"
        self.sonnet_model = "mock-sonnet"
    
    def call_haiku(self, system_prompt: str, user_message: str, max_tokens: int = 2000) -> str:
        """Simulate Haiku responses for demo"""
        # Check what kind of response is needed based on system prompt
        if "spending analyzer" in system_prompt.lower():
            return self._mock_spending_analysis(user_message)
        elif "card evaluator" in system_prompt.lower():
            return self._mock_card_evaluation(user_message)
        elif "orchestrator" in system_prompt.lower():
            return self._mock_orchestrator(user_message)
        return '{"status": "mock_response"}'
    
    def call_sonnet(self, system_prompt: str, user_message: str, max_tokens: int = 3000) -> str:
        """Simulate Sonnet responses for demo"""
        if "recommendation synthesizer" in system_prompt.lower():
            return self._mock_recommendations(user_message)
        return '{"status": "mock_response"}'
    
    def _mock_spending_analysis(self, user_message: str) -> str:
        # Extract spending values from message (simple parsing)
        return '''{
  "total_monthly_spend": 2100.0,
  "total_annual_spend": 25200.0,
  "top_categories": ["dining", "groceries", "travel"],
  "spending_profile": "dining_focused",
  "insights": [
    "Your dining spend of $1,200/month represents 57% of total spending",
    "Strong candidate for dining rewards cards with 3x-4x multipliers",
    "Travel spending suggests benefit from travel perks and lounge access"
  ],
  "category_percentages": {
    "dining": 57.1,
    "groceries": 9.5,
    "travel": 9.5,
    "gas": 7.1,
    "streaming": 2.4,
    "other": 14.3
  }
}'''
    
    def _mock_card_evaluation(self, user_message: str) -> str:
        return '''{
  "total_cards_evaluated": 25,
  "top_cards": [
    {
      "card_id": "amex_gold",
      "card_name": "American Express Gold",
      "annual_rewards": 1440.0,
      "signup_bonus_value": 0.0,
      "annual_fee": 325.0,
      "annual_credits_value": 0.0,
      "net_value_year_1": 1115.0,
      "net_value_year_2": 1440.0,
      "net_value_year_3": 1440.0,
      "ranking_score": 95.0
    },
    {
      "card_id": "csp",
      "card_name": "Chase Sapphire Preferred",
      "annual_rewards": 850.0,
      "signup_bonus_value": 0.0,
      "annual_fee": 95.0,
      "annual_credits_value": 0.0,
      "net_value_year_1": 755.0,
      "net_value_year_2": 850.0,
      "net_value_year_3": 850.0,
      "ranking_score": 88.0
    },
    {
      "card_id": "citi_double",
      "card_name": "Citi Double Cash",
      "annual_rewards": 420.0,
      "signup_bonus_value": 0.0,
      "annual_fee": 0.0,
      "annual_credits_value": 0.0,
      "net_value_year_1": 420.0,
      "net_value_year_2": 420.0,
      "net_value_year_3": 420.0,
      "ranking_score": 82.0
    }
  ]
}'''
    
    def _mock_recommendations(self, user_message: str) -> str:
        # Parse card name from the user message
        import re
        card_match = re.search(r'CARD:\s*(.+?)(?:\n|$)', user_message)
        card_name = card_match.group(1).strip() if card_match else "Unknown Card"
        
        rank_match = re.search(r'RANK:\s*#(\d+)', user_message)
        rank = int(rank_match.group(1)) if rank_match else 1
        
        # Generic response that works for any card
        return f'''{{
  "why_this_card": "This {card_name} is an excellent choice for your spending profile. Based on your spending patterns, this card will maximize your rewards in your top categories while providing strong value.",
  "how_to_maximize": [
    "Use this card for your highest spending categories to maximize rewards",
    "Take advantage of any bonus categories or promotional offers",
    "Consider pairing with other cards for complete coverage",
    "Pay in full each month to avoid interest charges"
  ],
  "watch_out_for": [
    "Check annual fee value against your spending levels",
    "Be aware of any spending caps or category restrictions",
    "Consider merchant acceptance in your area",
    "Review terms for foreign transaction fees if traveling"
  ],
  "optimization_strategy": {{
    "use_this_card_for": ["primary_categories", "bonus_spending"],
    "pair_with": "2% cash back card",
    "avoid_using_for": ["low_value_categories"]
  }},
  "long_term_projection": {{
    "3_year_total": "Strong value over 3 years",
    "breakeven": "Within first year"
  }}
}}'''
    
    def _mock_orchestrator(self, user_message: str) -> str:
        return '{"status": "orchestrator_complete"}'

class ClaudeClient:
    """Wrapper for Claude API calls"""
    
    def __init__(self, api_key: str = ANTHROPIC_API_KEY):
        if USE_MOCK_MODE:
            print("\n⚠️  Running in DEMO MODE (no API key required)")
            print("   Recommendations are simulated for demonstration purposes.")
            print("   To use real AI, set ANTHROPIC_API_KEY in .env and USE_MOCK_MODE=false\n")
        self.client = Anthropic(api_key=api_key) if not USE_MOCK_MODE else None
        self.haiku_model = HAIKU_MODEL
        self.sonnet_model = SONNET_MODEL
        self.mock_mode = USE_MOCK_MODE
    
    def call_haiku(self, system_prompt: str, user_message: str, max_tokens: int = 2000) -> str:
        """Call Claude Haiku (faster, cheaper)"""
        if self.mock_mode:
            mock_client = MockClaudeClient()
            return mock_client.call_haiku(system_prompt, user_message, max_tokens)
        
        message = self.client.messages.create(
            model=self.haiku_model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        return message.content[0].text
    
    def call_sonnet(self, system_prompt: str, user_message: str, max_tokens: int = 3000) -> str:
        """Call Claude Sonnet (better quality)"""
        if self.mock_mode:
            mock_client = MockClaudeClient()
            return mock_client.call_sonnet(system_prompt, user_message, max_tokens)
        
        message = self.client.messages.create(
            model=self.sonnet_model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        return message.content[0].text
