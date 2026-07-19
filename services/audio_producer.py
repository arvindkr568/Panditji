import os
import json
import asyncio
import subprocess
from services.logger import logger

# We use MadhurNeural for a deep, premium male Hindi voice
VOICE_MODEL = "hi-IN-MadhurNeural"

async def generate_single_audio(text: str, rasi: str, audio_dir: str):
    """Generates audio and VTT subtitles for a single text chunk using edge-tts CLI."""
    safe_filename = f"{rasi}"
    mp3_path = os.path.join(audio_dir, f"{safe_filename}.mp3")
    vtt_path = os.path.join(audio_dir, f"{safe_filename}.vtt")
    
    # Run the edge-tts CLI command asynchronously to generate both media and subtitles
    process = await asyncio.create_subprocess_exec(
        "edge-tts", 
        "--voice", VOICE_MODEL,
        "--text", text, 
        "--write-media", mp3_path, 
        "--write-subtitles", vtt_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        err_msg = stderr.decode('utf-8').strip()
        logger.error(f"edge-tts failed for Rasi {rasi} (Exit Code: {process.returncode}). Error: {err_msg}")
        raise RuntimeError(f"edge-tts failed for {rasi}: {err_msg}")
        
    logger.debug(f"Generated Audio & VTT for Rasi: {rasi}")
    return safe_filename

async def generate_all_audio_async():
    """
    Reads the daily predictions JSON and generates an MP3 and VTT for each Rasi.
    """
    logger.info("Starting Phase 3: Generating Neural Audio and Subtitles via Edge-TTS")
    json_path = "data/daily_predictions.json"
    audio_dir = "static/audio"
    
    # Ensure audio directory exists
    os.makedirs(audio_dir, exist_ok=True)
    
    if not os.path.exists(json_path):
        logger.error("daily_predictions.json not found. User must run Phase 2 first.")
        raise FileNotFoundError("daily_predictions.json not found. Please run Phase 2 first.")
        
    with open(json_path, "r", encoding="utf-8") as f:
        predictions = json.load(f)
        
    logger.info(f"Loaded {len(predictions)} predictions. Dispatching audio generation tasks...")
    tasks = []
    generated_files = []
    
    for rasi, text in predictions.items():
        # Schedule the async generation task
        task = asyncio.create_task(generate_single_audio(text, rasi, audio_dir))
        tasks.append(task)
        
        # Keep track of the URL path for the frontend
        generated_files.append({
            "rasi": rasi,
            "url": f"/audio/{rasi}.mp3"
        })
        
    # Wait for all 12 audio/subtitle files to be generated concurrently
    await asyncio.gather(*tasks)
    
    logger.info("Phase 3 Complete: All Audio & VTT files generated successfully.")
    return generated_files

def run_audio_production():
    """Synchronous wrapper for the Flask route."""
    return asyncio.run(generate_all_audio_async())
