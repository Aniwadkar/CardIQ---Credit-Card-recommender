"""Orchestrator Agent - Coordinates all agents"""
from src.agents.base_agent import BaseAgent
from src.agents.spending_analyzer import SpendingAnalyzerAgent
from src.agents.card_evaluator import CardEvaluatorAgent
from src.agents.recommendation_synthesizer import RecommendationSynthesizerAgent
from src.models.user_input import UserProfile
from src.models.agent_outputs import RecommendationOutput
from src.prompts import ORCHESTRATOR_SYSTEM_PROMPT

class Orchestrator(BaseAgent):
    """Main orchestrator that coordinates all agents"""
    
    def __init__(self, claude_client=None):
        super().__init__(claude_client)
        
        # Initialize all agents
        self.spending_analyzer = SpendingAnalyzerAgent(claude_client)
        self.card_evaluator = CardEvaluatorAgent(claude_client)
        self.recommendation_synthesizer = RecommendationSynthesizerAgent(claude_client)
    
    def get_system_prompt(self) -> str:
        return ORCHESTRATOR_SYSTEM_PROMPT
    
    def process(self, user_profile: UserProfile, verbose: bool = True) -> RecommendationOutput:
        """
        Main workflow:
        1. Analyze spending
        2. Evaluate cards
        3. Synthesize recommendations
        """
        
        if verbose:
            print("=" * 60)
            print("CardIQ Recommendation System")
            print("=" * 60)
        
        # Step 1: Analyze spending
        if verbose:
            print("\n[1/3] Analyzing spending patterns...")
        spending_analysis = self.spending_analyzer.process(user_profile)
        if verbose:
            print(f"✓ Analysis complete:")
            print(f"  - Total monthly spend: ${spending_analysis.total_monthly_spend:,.2f}")
            print(f"  - Top categories: {', '.join(spending_analysis.top_categories)}")
            print(f"  - Profile: {spending_analysis.spending_profile}")
        
        # Step 2: Evaluate cards
        if verbose:
            print("\n[2/3] Evaluating credit cards...")
        card_evaluations = self.card_evaluator.process(spending_analysis, user_profile)
        if verbose:
            print(f"✓ Evaluated {card_evaluations.total_cards_evaluated} cards")
            print(f"  Top 3 cards:")
            for i, card_eval in enumerate(card_evaluations.top_cards[:3], 1):
                print(f"    {i}. {card_eval.card_name} (Year 1 value: ${card_eval.net_value_year_1:,.2f})")
        
        # Step 3: Synthesize recommendations
        if verbose:
            print("\n[3/3] Creating personalized recommendations...")
        recommendations = self.recommendation_synthesizer.process(
            spending_analysis=spending_analysis,
            card_evaluations=card_evaluations,
            user_profile=user_profile
        )
        if verbose:
            print(f"✓ Generated {len(recommendations.recommendations)} detailed recommendations")
        
        if verbose:
            print("\n" + "=" * 60)
            print("Recommendation Generation Complete!")
            print("=" * 60)
        
        return recommendations
    
    def get_quick_recommendation(self, user_profile: UserProfile) -> str:
        """Get a quick text recommendation (simplified)"""
        recommendations = self.process(user_profile)
        return self.format_recommendation_output(recommendations)

    def format_recommendation_output(self, recommendations: RecommendationOutput) -> str:
        """Format recommendation output model as readable text."""
        
        # Format as readable text
        output = "\n\n"
        output += "🎯 YOUR PERSONALIZED CREDIT CARD RECOMMENDATIONS\n"
        output += "=" * 60 + "\n\n"
        
        for rec in recommendations.recommendations:
            output += f"{'🥇' if rec.rank == 1 else '🥈' if rec.rank == 2 else '🥉'} RANK #{rec.rank}: {rec.card_name}\n"
            output += "-" * 60 + "\n\n"
            
            output += f"WHY THIS CARD:\n{rec.why_this_card}\n\n"
            
            output += f"FINANCIAL SUMMARY:\n"
            output += f"  • Year 1 Value: ${rec.financial_summary['year_1_value']:,.2f}\n"
            output += f"  • Year 2 Value: ${rec.financial_summary['year_2_value']:,.2f}\n"
            output += f"  • Year 3 Value: ${rec.financial_summary['year_3_value']:,.2f}\n"
            output += f"  • Annual Fee: ${rec.financial_summary['annual_fee']:,.2f}\n\n"
            
            output += f"HOW TO MAXIMIZE:\n"
            for tip in rec.how_to_maximize:
                output += f"  ✓ {tip}\n"
            output += "\n"
            
            output += f"WATCH OUT FOR:\n"
            for warning in rec.watch_out_for:
                output += f"  ⚠  {warning}\n"
            output += "\n"
            
            output += "=" * 60 + "\n\n"
        
        output += f"💡 PORTFOLIO STRATEGY:\n{recommendations.portfolio_strategy}\n"
        
        return output
