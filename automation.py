import os
import json
import asyncio
from services.astronomy import calculate_daily_gochar
from services.ai_generator import generate_daily_horoscopes
from services.audio_producer import generate_all_audio_async
from services.video_renderer import render_single_video, combine_all_videos
from services.social_metadata import generate_metadata_for_rasi, generate_metadata_for_master
from services.youtube_uploader import upload_video_to_youtube
from services.meta_uploader import upload_video_to_facebook
from services.logger import logger

def run_headless_pipeline():
    logger.info("🚀 Starting Automated Pandit Ji Pipeline...")
    
    # PHASE 1: Astronomy
    logger.info("[Phase 1] Calculating Gochar...")
    gochar_data = calculate_daily_gochar()
    
    # PHASE 2: AI Generation
    logger.info("[Phase 2] Invoking Gemini AI...")
    generate_daily_horoscopes(gochar_data["gochar_string"])
    
    # PHASE 3: Audio Production
    logger.info("[Phase 3] Generating Audio & Subtitles...")
    asyncio.run(generate_all_audio_async())
    
    # Load Predictions to loop for Video & Uploads
    with open("data/daily_predictions.json", "r", encoding="utf-8") as f:
        predictions = json.load(f)
        
    rasi_predictions = predictions.get("predictions", {})
        
    # PHASE 4: Video Rendering (Segments & Shorts)
    logger.info("[Phase 4] Rendering Individual Video Segments...")
    
    if "intro" in predictions:
        logger.info("  -> Rendering Intro segment...")
        render_single_video("intro")
        
    for rasi in rasi_predictions.keys():
        logger.info(f"  -> Rendering {rasi} segment...")
        render_single_video(rasi)
        
    logger.info("[Phase 4.5] Building Final Shorts...")
    from services.video_renderer import build_short
    for rasi in rasi_predictions.keys():
        logger.info(f"  -> Building {rasi} Short...")
        build_short(rasi)
        
    # PHASE 5: Combine Master Video
    logger.info("[Phase 5] Combining Master Video...")
    combine_all_videos()
    
    # PHASE 6: Social Media Uploads
    logger.info("[Phase 6] Starting Social Media Uploads...")
    
    # 6A: Upload Master to YouTube
    logger.info("  -> Uploading Master to YouTube...")
    try:
        master_meta = generate_metadata_for_master()
        yt_master_id = upload_video_to_youtube("static/video/master_all_rasis.mp4", master_meta)
        logger.info(f"     Success! YouTube ID: {yt_master_id}")
    except Exception as e:
        logger.error(f"     Failed to upload Master to YouTube: {e}")
        
    # 6B: Upload Shorts to YouTube
    logger.info("[Phase 6B] Uploading Shorts to YouTube...")
    for rasi in rasi_predictions.keys():
        logger.info(f"  -> Uploading {rasi} Short to YouTube...")
        try:
            rasi_meta = generate_metadata_for_rasi(rasi)
            yt_id = upload_video_to_youtube(f"static/video/final_{rasi}.mp4", rasi_meta)
            logger.info(f"     Success! YouTube ID: {yt_id}")
        except Exception as e:
            logger.error(f"     Failed to upload {rasi} to YouTube: {e}")

    # 6C: Upload Shorts to Meta (Facebook/Instagram)
    logger.info("[Phase 6C] Uploading Shorts to Meta...")
    for rasi in rasi_predictions.keys():
        logger.info(f"  -> Uploading {rasi} Short to Meta...")
        try:
            rasi_meta = generate_metadata_for_rasi(rasi)
            fb_id = upload_video_to_facebook(f"static/video/final_{rasi}.mp4", rasi_meta)
            logger.info(f"     Success! Facebook ID: {fb_id}")
        except Exception as e:
            logger.error(f"     Failed to upload {rasi} to Meta: {e}")
            
    logger.info("✨ Pandit Ji Automation Complete!")

if __name__ == "__main__":
    run_headless_pipeline()
