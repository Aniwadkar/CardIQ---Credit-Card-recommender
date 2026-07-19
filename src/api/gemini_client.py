"""Gemini Client using Vertex AI."""
import os

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
except ModuleNotFoundError:
    vertexai = None
    GenerativeModel = None

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "project-dda6cdb1-a2ba-470b-a47")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

class GeminiClient:
    """Client for Gemini via Vertex AI - billed to GCP credits"""
    
    def __init__(self):
        if vertexai is None or GenerativeModel is None:
            raise RuntimeError(
                "Vertex AI dependencies are not installed. Install google-cloud-aiplatform "
                "or use the deterministic RecommendationService path."
            )
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model = GenerativeModel("gemini-2.0-flash")
        self.mock_mode = False
    
    def _call(self, system_prompt: str, user_message: str, max_tokens: int = 2000) -> str:
        full_prompt = f"{system_prompt}\n\n{user_message}"
        response = self.model.generate_content(
            full_prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": 0.1,
            }
        )
        return response.text
    
    def call_haiku(self, system_prompt: str, user_message: str, max_tokens: int = 2000) -> str:
        return self._call(system_prompt, user_message, max_tokens)
    
    def call_sonnet(self, system_prompt: str, user_message: str, max_tokens: int = 2000) -> str:
        return self._call(system_prompt, user_message, max_tokens)


# Compatibility alias for older imports while the project migrates from Claude to Gemini.
ClaudeClient = GeminiClient
