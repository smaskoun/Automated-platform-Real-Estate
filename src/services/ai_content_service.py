# src/services/ai_content_service.py - FULL REPLACEMENT

import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()

class AIContentService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        openai.api_key = self.api_key

    def generate_optimized_post(self, topic: str, brand_voice_example: str, performance_insights: dict) -> dict:
        if not topic or not brand_voice_example:
            raise ValueError("Topic and brand voice example cannot be empty.")

        try:
            system_prompt = """
            You are a world-class social media strategist for the real estate industry. Your goal is to create a viral-worthy post that maximizes engagement and follows SEO best practices. You must generate a JSON object with two keys: "content" and "hashtags".
            """

            user_prompt = f"""
            Generate a social media post using these instructions:

            1.  **Primary Topic:**
                "{topic}"

            2.  **Tone and Style Guide (Strictly follow this):**
                Emulate the tone, voice, and structure of this example:
                --- EXAMPLE START ---
                {brand_voice_example}
                --- EXAMPLE END ---

            3.  **Performance Optimization Rules (Apply these insights):**
                - **Content Style:** {performance_insights.get('content_style_suggestions', 'General best practices apply.')}
                - **Engagement Tips:** {performance_insights.get('engagement_optimization_tips', 'Focus on a clear call-to-action.')}
                - **Hashtags:** Your generated hashtags should be inspired by this list of historically effective tags: {performance_insights.get('recommended_hashtags', '["#realestate", "#property", "#home"]')}

            4.  **Output Requirements:**
                - The final output must be a single JSON object.
                - The "content" field should contain the full post text.
                - The "hashtags" field should contain a list of 7-10 highly relevant hashtags.
            """

            response = openai.chat.completions.create(
                # --- THIS IS THE ONLY LINE THAT HAS CHANGED ---
                model="gpt-3.5-turbo",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            print(f"Error in AI content generation: {e}")
            return {"error": str(e)}

ai_content_service = AIContentService()
