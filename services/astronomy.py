import swisseph as swe
from datetime import datetime
import pytz
from services.logger import logger

RASIS = [
    "मेष", "वृषभ", "मिथुन", "कर्क", 
    "सिंह", "कन्या", "तुला", "वृश्चिक", 
    "धनु", "मकर", "कुंभ", "मीन"
]

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}

def get_rasi(degree):
    """Maps a 360-degree longitude to the appropriate Vedic Rasi."""
    index = int(degree // 30)
    return RASIS[index % 12]

def calculate_daily_gochar():
    """
    Executes Phase 1 of the architecture: 
    Time -> UTC -> Julian Day -> Swisseph -> Lahiri Ayanamsa -> Gochar String
    """
    logger.info("Starting calculation of daily Gochar")
    now_utc = datetime.now(pytz.utc)
    
    # Calculate Julian Day
    year, month, day = now_utc.year, now_utc.month, now_utc.day
    hour = now_utc.hour + now_utc.minute/60.0 + now_utc.second/3600.0
    jd = swe.julday(year, month, day, hour)
    logger.debug(f"Calculated Julian Day: {jd}")
    
    # Set Lahiri Ayanamsa (Tropical -> Sidereal/Vedic)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    results = []
    gochar_parts = []
    
    # Calculate Celestial Degrees and Map to Rasis
    for name, p_id in PLANETS.items():
        # Using FLG_SIDEREAL to apply the Lahiri ayanamsa subtraction automatically
        pos, ret = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL)
        lon = pos[0] # longitude
        rasi = get_rasi(lon)
        
        logger.debug(f"{name} position calculated at {lon} degrees")
        
        results.append({
            "planet": name,
            "degree": round(lon, 4),
            "rasi": rasi
        })
        gochar_parts.append(f"{name} is in {rasi}")
        
        # Calculate Ketu dynamically (180 degrees from Rahu)
        if name == "Rahu":
            ketu_lon = (lon + 180.0) % 360.0
            ketu_rasi = get_rasi(ketu_lon)
            results.append({
                "planet": "Ketu",
                "degree": round(ketu_lon, 4),
                "rasi": ketu_rasi
            })
            gochar_parts.append(f"Ketu is in {ketu_rasi}")
    
    # Format Gochar String
    gochar_string = ", ".join(gochar_parts) + "."
    
    return {
        "timestamp": now_utc.isoformat(),
        "julian_day": round(jd, 4),
        "planets": results,
        "gochar_string": gochar_string
    }
