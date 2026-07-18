import os
import json
from google import genai
from services.logger import logger
from google.genai import types
from dotenv import load_dotenv

def generate_daily_horoscopes(gochar_string: str) -> dict:
    """
    Executes Phase 2 of the architecture:
    Construct Prompt -> Call Gemini API -> Parse JSON -> Return Dict
    """
    # Load environment variables dynamically to pick up recent changes
    load_dotenv(override=True)
    logger.info("Starting Phase 2: Generating Daily Horoscopes via Gemini")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("GEMINI_API_KEY is not set correctly in the .env file. Please add your real key and try again.")
        
    # Initialize the new SDK client
    client = genai.Client(api_key=api_key)

    # Senior Pandit Ji Prompt
    system_prompt = f"""
    ॐ भूर्भुवः स्वः॥ 
    You are a highly revered, expert Indian Vedic Astrologer (Pandit Ji) with profound knowledge of Jyotish Shastra (Vedic Astrology), Graha Gochar (Planetary Transits), and Kundali analysis.
    
    Today's exact planetary transit (Gochar) is as follows:
    {gochar_string}
    
    Based on this Gochar, you must write the daily horoscope (Rashi Bhavishya) for all 12 Rasis.
    
    CRITICAL RULES:
    1. For each Rasi, write EXACTLY 3 sentences. No more, no less.
    2. The language MUST be pure, respectful, and spiritual Hindi, using proper Vedic terminology (e.g., 'धन लाभ', 'स्वास्थ्य', 'मानसिक शांति').
    3. The output MUST be a valid JSON object where the keys are the exact 12 Hindi Rasi names and the values are the 3-sentence Hindi predictions.
    
    Example output format:
    {{
        "मेष": "आज आपका मन शांत रहेगा। कार्यक्षेत्र में सूर्य और मंगल के गोचर से आपको सफलता मिलेगी। स्वास्थ्य का विशेष ध्यान रखें।",
        "वृषभ": "...",
        ...
    }}
    """
    
    try:
        # Enforce JSON output natively using the new GenerateContentConfig
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7,
            )
        )
        
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        logger.debug("Successfully received response from Gemini API.")
        
        # Parse the guaranteed JSON response
        predictions = json.loads(raw_text)
        
        # Save to local file (Database placeholder)
        os.makedirs("data", exist_ok=True)
        with open("data/daily_predictions.json", "w", encoding="utf-8") as f:
            json.dump(predictions, f, ensure_ascii=False, indent=4)
            
        logger.info("Phase 2 Complete: Horoscopes saved to data/daily_predictions.json")
        return predictions

    except Exception as e:
        logger.error(f"Error in AI Generation: {e}")
        raise e
