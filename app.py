from flask import Flask, jsonify, request
from services.astronomy import calculate_daily_gochar
from services.ai_generator import generate_daily_horoscopes
from services.audio_producer import run_audio_production
from services.video_renderer import render_single_video, combine_all_videos
from services.social_metadata import generate_metadata_for_rasi, generate_metadata_for_master
from services.youtube_uploader import upload_video_to_youtube
from services.meta_uploader import upload_video_to_facebook
from services.logger import logger

app = Flask(__name__, static_url_path='', static_folder='static')

@app.route('/')
def index():
    """Serves the main Phase 1 & 2 Dashboard."""
    return app.send_static_file('index.html')

@app.route('/api/phase1/calculate', methods=['GET'])
def phase1_calculate():
    """
    Phase 1: Astronomy Engine API Route
    """
    logger.info("API Request: GET /api/phase1/calculate")
    try:
        data = calculate_daily_gochar()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/phase2/generate', methods=['POST'])
def phase2_generate():
    """
    Phase 2: AI Content Generator API Route
    """
    logger.info("API Request: POST /api/phase2/generate")
    try:
        payload = request.get_json()
        if not payload or 'gochar_string' not in payload:
            return jsonify({"error": "Missing 'gochar_string' in request body."}), 400
            
        gochar_string = payload['gochar_string']
        
        # Call the AI Generator Service
        predictions = generate_daily_horoscopes(gochar_string)
        
        return jsonify({
            "status": "success",
            "predictions": predictions
        })
    except ValueError as ve:
        # Catch missing API key errors
        return jsonify({"error": str(ve)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/phase3/generate', methods=['POST'])
def phase3_generate():
    """
    Phase 3: Neural Audio Producer API Route
    """
    logger.info("API Request: POST /api/phase3/generate")
    try:
        audio_files = run_audio_production()
        return jsonify({
            "status": "success",
            "audio_files": audio_files
        })
    except FileNotFoundError as fnf:
        return jsonify({"error": str(fnf)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/phase4/generate_single', methods=['POST'])
def phase4_generate_single():
    """
    Phase 4: Streaming Video Rendering Engine
    Renders exactly one video per request to prevent browser timeouts.
    """
    logger.info("API Request: POST /api/phase4/generate_single")
    try:
        data = request.json
        rasi = data.get('rasi')
        if not rasi:
            return jsonify({"error": "Missing 'rasi' in request."}), 400
            
        video_data = render_single_video(rasi)
        return jsonify({
            "status": "success",
            "video_file": video_data
        })
    except FileNotFoundError as fnf:
        return jsonify({"error": str(fnf)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/phase4/combine_videos', methods=['POST'])
def phase4_combine_videos():
    """
    Combines the 12 individual videos into one master file.
    """
    logger.info("API Request: POST /api/phase4/combine_videos")
    try:
        video_data = combine_all_videos()
        return jsonify(video_data)
    except FileNotFoundError as fnf:
        return jsonify({"error": str(fnf)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/phase6/upload', methods=['POST'])
def phase6_upload():
    """
    Phase 6: Social Media Auto-Uploader
    Uploads a specified video to YouTube or Meta.
    """
    logger.info("API Request: POST /api/phase6/upload")
    try:
        data = request.json
        video_type = data.get('type') # 'single' or 'master'
        rasi = data.get('rasi')
        platform = data.get('platform') # 'youtube' or 'meta'
        
        if video_type == 'master':
            video_path = "static/video/master_all_rasis.mp4"
            metadata = generate_metadata_for_master()
        else:
            if not rasi:
                return jsonify({"error": "Missing 'rasi' for single video upload."}), 400
            video_path = f"static/video/{rasi}.mp4"
            metadata = generate_metadata_for_rasi(rasi)
            
        if not __import__("os").path.exists(video_path):
            return jsonify({"error": f"Video not found at {video_path}"}), 400
            
        # Execute uploads based on requested platform
        if platform == 'youtube':
            youtube_id = upload_video_to_youtube(video_path, metadata)
            return jsonify({
                "status": "success",
                "youtube_video_id": youtube_id
            })
            
        elif platform == 'meta':
            # This is a stub calling the Meta Uploader which will error out 
            # if META_PAGE_ACCESS_TOKEN is not in the environment.
            facebook_id = upload_video_to_facebook(video_path, metadata)
            
            return jsonify({
                "status": "success",
                "facebook_video_id": facebook_id,
                "instagram_video_id": "STUB_IG_ID" # IG Container API requires public URL
            })
            
        else:
            logger.warning(f"Unknown platform requested: {platform}")
            return jsonify({"error": f"Unknown platform {platform}"}), 400
            
    except Exception as e:
        logger.error(f"Error in phase6_upload: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Pandit Ji Engine Flask Server on port 5002")
    # Running on port 5001 to avoid macOS AirPlay conflict on 5000
    app.run(debug=True, port=5002)
