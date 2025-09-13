# src/services/ai_content_service.py - FINAL VERSION (Location, GPT-4, Image Prompt)

import os
import json
import time
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

        system_prompt = """
            You are a world-class social media strategist and creative director for the real estate industry, specializing in the Windsor-Essex, Ontario, Canada market.
            Your goal is to create a complete social media package that maximizes engagement.
            You must generate a JSON object with three keys: "content", "hashtags", and "image_prompt".
            """

        user_prompt = f"""
            Generate a social media post package using these instructions.

            1.  **Primary Topic:**
                "{topic}"

            2.  **Target Market:**
                Windsor-Essex, Ontario, Canada. All content, landmarks, and hashtags must be relevant to this area.

            3.  **Tone and Style Guide (Strictly follow this):**
                Emulate the tone, voice, and structure of this example:
                --- EXAMPLE START ---
                {brand_voice_example}
                --- EXAMPLE END ---

            4.  **Performance Optimization Rules (Apply these insights):**
                - **Content Style:** {performance_insights.get('content_style_suggestions', 'General best practices apply.')}
                - **Engagement Tips:** {performance_insights.get('engagement_optimization_tips', 'Focus on a clear call-to-action.')}
                - **Hashtags:** Your generated hashtags should be inspired by this list of historically effective tags and must be relevant to Windsor-Essex: {performance_insights.get('recommended_hashtags', '["#windsorrealestate", "#yqg", "#essexcounty"]')}

            5.  **Output Requirements (JSON Object):**
                - "content": The full post text, ready to be published.
                - "hashtags": A list of 7-10 highly relevant local hashtags.
                - "image_prompt": A detailed, descriptive prompt for an AI image generator (like Midjourney or DALL-E) to create a visually stunning and relevant image for this post. The prompt should be creative and evocative. Example: "Photorealistic image of a luxurious, modern kitchen with marble countertops and sunlight streaming through large windows, overlooking a lush green backyard in a suburban Ontario home, golden hour lighting."
            """

        last_exception = None
        for attempt in range(3):
            try:
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    timeout=30,
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                last_exception = e
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)

        error_message = f"Failed to generate content after 3 attempts: {last_exception}"
        print(error_message)
        return {"error": error_message}

ai_content_service = AIContentService()
