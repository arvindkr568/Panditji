import os
import json
from google import genai
from services.logger import logger
from google.genai import types
from dotenv import load_dotenv
from datetime import datetime
import pytz

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

    # Calculate current date in IST for the prompt
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    
    day = now.day
    suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    eng_months = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
    }
    eng_date_str = f"{day}{suffix} {eng_months[now.month]} {now.year}"
    
    hindi_months = {
        1: "जनवरी", 2: "जनवरी", 3: "मार्च", 4: "अप्रैल", 5: "मई", 6: "जून",
        7: "जुलाई", 8: "अगस्त", 9: "सितंबर", 10: "अक्टूबर", 11: "नवंबर", 12: "दिसंबर"
    }
    # Fix mapping error (2 was duplicate January)
    hindi_months[2] = "फ़रवरी"
    hin_date_str = f"{day} {hindi_months[now.month]} {now.year}"

    # Senior Pandit Ji Prompt
    system_prompt = f"""
    ॐ भूर्भुवः स्वः॥ 
    You are a highly revered, expert Indian Vedic Astrologer (Pandit Ji) with profound knowledge of Jyotish Shastra (Vedic Astrology), Graha Gochar (Planetary Transits), and Kundali analysis.
    
    Today's exact planetary transit (Gochar) is as follows:
    {gochar_string}
    
    Based on this Gochar, you must write the daily horoscope (Rashi Bhavishya) for all 12 Rasis.
    
    CRITICAL RULES:
    1. For each Rasi, write EXACTLY 5 sentences. No more, no less.
    2. The very first sentence MUST start by announcing today's date in both Hindi and English. 
       Format: "आज {hin_date_str}, यानी {eng_date_str} के राशिफल में आपका स्वागत है।"
    3. The remaining 4 sentences must be pure, respectful, and spiritual Hindi, using proper Vedic terminology (e.g., 'धन लाभ', 'स्वास्थ्य', 'मानसिक शांति').
    4. The output MUST be a valid JSON object where the keys are the exact 12 Hindi Rasi names and the values are the 5-sentence Hindi predictions.
    
    Example output format:
    {{
        "मेष": "आज {hin_date_str}, यानी {eng_date_str} के राशिफल में आपका स्वागत है। आज आपका मन शांत रहेगा। कार्यक्षेत्र में सूर्य और मंगल के गोचर से आपको सफलता मिलेगी। धन लाभ के प्रबल योग हैं। स्वास्थ्य का विशेष ध्यान रखें।",
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
