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
    
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        # Run the edge-tts CLI command asynchronously
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
        
        if process.returncode == 0:
            logger.debug(f"Generated Audio & VTT for Rasi: {rasi}")
            return safe_filename
            
        err_msg = stderr.decode('utf-8').strip()
        logger.warning(f"edge-tts attempt {attempt} failed for {rasi}. Error: {err_msg}")
        
        if attempt < max_retries:
            await asyncio.sleep(2)  # Wait before retrying
        else:
            logger.error(f"edge-tts completely failed for Rasi {rasi} after {max_retries} attempts.")
            raise RuntimeError(f"edge-tts failed for {rasi}: {err_msg}")

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
        
    logger.info("Dispatching audio generation tasks...")
    tasks = []
    generated_files = []
    
    # Limit concurrency to 3 simultaneous edge-tts processes to avoid rate limiting
    semaphore = asyncio.Semaphore(3)
    
    async def bounded_generate(text_val, filename_val, dir_val):
        async with semaphore:
            return await generate_single_audio(text_val, filename_val, dir_val)
    
    # Generate the intro audio
    if "intro" in predictions:
        tasks.append(asyncio.create_task(bounded_generate(predictions["intro"], "intro", audio_dir)))
        
    rasi_predictions = predictions.get("predictions", {})
    
    for rasi, text in rasi_predictions.items():
        # Schedule the async generation task with concurrency limit
        task = asyncio.create_task(bounded_generate(text, rasi, audio_dir))
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
