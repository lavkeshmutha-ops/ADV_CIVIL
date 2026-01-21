
import os
from google.genai import GoogleGenAI

class AIService:
    def __init__(self):
        # Uses process.env.API_KEY as per requirements
        self.ai = GoogleGenAI(apiKey=os.environ.get("API_KEY", ""))
        self.model = 'gemini-3-flash-preview'

    async def summarize_timeline(self, proceedings_text):
        if not proceedings_text:
            return "No data to summarize."
        
        prompt = f"""
        Act as a legal assistant for a civil advocate. 
        Summarize the following court proceedings into a concise memory note (max 3 sentences).
        Focus on facts and procedural updates. 
        DISCLAIMER: This is AI-generated for memory assistance. The advocate must decide all legal actions.
        
        PROCEEDINGS: {proceedings_text}
        """
        
        try:
            response = await self.ai.models.generateContent({
                "model": self.model,
                "contents": prompt
            })
            return response.text
        except Exception as e:
            return f"AI Summary failed: {str(e)}"

    async def suggest_next_steps(self, order_summary):
        prompt = f"""
        Based on this court order summary: "{order_summary}", suggest 3 possible administrative or filing tasks.
        Do not provide legal advice or strategy. Focus on clerical/procedural next steps (e.g., 'Draft rejoinder', 'File process fee').
        Include a disclaimer that the advocate has final authority.
        """
        try:
            response = await self.ai.models.generateContent({
                "model": self.model,
                "contents": prompt
            })
            return response.text
        except Exception as e:
            return "Unable to generate suggestions."
