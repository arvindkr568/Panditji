# Pandit Ji - AI Daily Horoscope Automation Engine 🕉️🔮

Welcome to the **Pandit Ji Engine**! This is a complete, end-to-end automated pipeline that calculates astrological planetary positions (Gochar), generates beautiful Hindi horoscopes using Google Gemini, synthesizes a pristine neural voice, stitches everything into cinematic videos, and publishes them automatically to YouTube, Instagram, and Facebook.

---

## 🛠️ Tech Stack & Architecture

The system is broken down into **6 Phases**:

- **Phase 1: Astronomy Engine (`pyswisseph`)** - Calculates real-time planetary positions using the Lahiri Ayanamsa.
- **Phase 2: AI Content Generator (`google-genai`)** - Uses Gemini 2.5 Flash to write engaging, pure Hindi horoscope scripts.
- **Phase 3: Audio Production (`edge-tts`)** - Synthesizes the text into a premium Hindi neural voice (`hi-IN-MadhurNeural`) and extracts precise WebVTT subtitles.
- **Phase 4 & 5: Video Rendering (`moviepy` & `Pillow`)** - Composites a cinematic "breathing" animation of Pandit Ji, overlays dynamic VTT subtitles, and renders them into high-quality vertical `.mp4` videos (perfect for Shorts/Reels).
- **Phase 6: Social Media Publisher (`google-api-python-client` & `requests`)** - Automatically pushes the final videos to YouTube Studio and Meta (Facebook/Instagram) with highly-optimized SEO metadata and hashtags.

---

## 📦 Prerequisites

1. **Python 3.13** or higher.
2. A **Gemini API Key** (Get one at [Google AI Studio](https://aistudio.google.com/)).
3. *(Optional)* **YouTube API Credentials**: A `client_secrets.json` file from Google Cloud Console (OAuth 2.0 Client ID) to upload to YouTube.
4. *(Optional)* **Meta API Credentials**: A Facebook Page Access Token to upload to Facebook/Instagram.

---

## 🚀 Installation & Setup

**1. Clone the repository and navigate to the directory:**
```bash
cd /Users/arvindkumar/R-D/Arvind/PanditJi
```

**2. Install all Python dependencies:**
```bash
pip install -r requirements.txt
```

**3. Configure Environment Variables:**
You must set your Gemini API key in your terminal before running the app. You can also optionally set the Meta variables if you intend to use the Meta auto-uploader.

```bash
export GEMINI_API_KEY="your_actual_gemini_api_key_here"

# (Optional Phase 6)
export META_PAGE_ACCESS_TOKEN="your_meta_page_access_token_here"
export META_PAGE_ID="your_meta_page_id_here"
```

**4. YouTube Setup (Optional Phase 6):**
If you intend to use the YouTube auto-uploader, you MUST download your `client_secrets.json` file from your Google Cloud Console and place it directly into the root folder (`/Users/arvindkumar/R-D/Arvind/PanditJi/client_secrets.json`).

---

## 💻 How to Run

Start the Flask server by running:
```bash
python3 app.py
```

Then, open your web browser and go to:
**[http://127.0.0.1:5002](http://127.0.0.1:5002)**

---

## 🌐 Staging & Production Environments

The engine supports isolated **Staging** and **Production** environments to ensure you can test modifications safely without publishing mock videos to your public audience.

### Local Execution Configuration

You can change the environment locally by setting standard environment variables in your terminal:

* **Staging Mode (Default / Safe Mode)**
  * Sets YouTube uploads as `private` or `unlisted` for review.
  * Mocks Facebook/Instagram uploads (skips hitting Meta API and logs a mock success).
  ```bash
  export YOUTUBE_PRIVACY_STATUS="private"
  export META_DRY_RUN="true"
  python app.py
  ```

* **Production Mode (Go-Live)**
  * Uploads YouTube videos as `public` instantly.
  * Uploads and publishes videos to the live Facebook Page.
  ```bash
  export YOUTUBE_PRIVACY_STATUS="public"
  export META_DRY_RUN="false"
  python app.py
  ```

---

## 📈 GitHub Actions (4:00 AM Automation)

GitHub Actions runs the pipeline automatically at **4:00 AM IST** daily. You can also trigger it manually:

1. Go to your GitHub repository -> **Actions** -> select **Daily Pandit Ji Publisher**.
2. Click **Run workflow**.
3. Choose the branch and select the target environment from the dropdown (`staging` or `production`).

To set up these environments on GitHub, configure two GitHub Environments (`staging` and `production`) under **Repository Settings -> Environments** and add the corresponding variables:
- **Staging**: `YOUTUBE_PRIVACY_STATUS=private`, `META_DRY_RUN=true`
- **Production**: `YOUTUBE_PRIVACY_STATUS=public`, `META_DRY_RUN=false`

---

## 📝 Logging & Debugging

The application utilizes a centralized global logging system. 
- Log statements are printed with timestamp and severity to the **Console**.
- Log statements are permanently saved and rotated in **`logs/panditji.log`** (maximum 5MB per file, keeps 3 backups).

---

## 🎮 Usage Guide

Once you open the web dashboard, simply follow the red/blue buttons sequentially down the page:

1. **Calculate Daily Gochar**: Crunches the astrological math.
2. **Invoke Pandit Ji AI**: Sends the math to Gemini to generate 12 Hindi horoscopes.
3. **Generate Pandit Ji Audio**: Synthesizes the `.mp3` and `.vtt` subtitle files.
4. **Render Final Videos**: Queues up and renders the 12 individual `.mp4` vertical videos.
5. **Combine All Videos**: Stitches the 12 individual videos into one massive master video file.
6. **Upload to YouTube / Meta**: Bulk uploads the videos to your connected social media channels!
