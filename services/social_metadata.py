import json
from services.logger import logger

def generate_metadata_for_rasi(rasi):
    """
    Generates highly optimized SEO titles, descriptions, and tags for YouTube Shorts and Instagram Reels.
    """
    logger.debug(f"Generating SEO Metadata for {rasi} Short")
    title = f"🔥 {rasi} Daily Horoscope: What the stars say today! 🔮✨ #Shorts #Astrology"
    
    description = f"""
Discover your daily destiny! 🌟 Pandit Ji reveals the exact planetary alignments for {rasi} today.
Will you find luck, love, or wealth? Watch to find out!

Don't forget to LIKE and SUBSCRIBE for daily Vedic Astrology updates.

#Astrology #DailyHoroscope #{rasi} #{rasi}Horoscope #VedicAstrology #Hinduism #Shorts #Reels #Trending #Zodiac
    """
    
    tags = ["astrology", "daily horoscope", rasi, f"{rasi} horoscope", "vedic astrology", "zodiac signs", "spirituality", "shorts"]
    
    return {
        "title": title.strip(),
        "description": description.strip(),
        "tags": tags,
        "categoryId": "22" # 22 is usually 'People & Blogs' on YouTube
    }

def generate_metadata_for_master():
    """
    Generates SEO metadata for the combined Master video (all 12 rasis).
    """
    logger.debug("Generating SEO Metadata for Master Video")
    title = "Complete Daily Horoscope for ALL 12 Zodiac Signs! 🔮✨ By Pandit Ji"
    
    description = """
Discover your daily destiny for ALL 12 Rasis! 🌟 Pandit Ji reveals the exact planetary alignments for today based on ancient Vedic Astrology and the Lahiri Ayanamsa.

Timestamps (Coming Soon)

Don't forget to LIKE and SUBSCRIBE for daily Vedic Astrology updates.

#Astrology #DailyHoroscope #VedicAstrology #Hinduism #ZodiacSigns #HoroscopeToday #AstrologyPrediction #Trending
    """
    
    tags = ["astrology", "daily horoscope", "all zodiac signs", "vedic astrology", "zodiac signs", "spirituality", "horoscope today"]
    
    return {
        "title": title.strip(),
        "description": description.strip(),
        "tags": tags,
        "categoryId": "22"
    }
