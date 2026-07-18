# Pandit Ji Engine - Deployment Guide 🚀

Deploying the Pandit Ji Engine to a production environment requires some specific considerations because the application relies heavily on **file system writes** (saving MP3s, MP4s, and JSON files) and performs **heavy CPU processing** (video rendering via `moviepy` and `imageio-ffmpeg`).

Because of these requirements, **you cannot deploy this app to Serverless platforms like Vercel, Netlify, or AWS Lambda**. Those platforms have strict 30-second timeouts and read-only filesystems.

The best deployment strategy is a **Virtual Private Server (VPS)** like a DigitalOcean Droplet, AWS EC2, or Google Compute Engine running Linux (Ubuntu 22.04+).

---

## 1. Server Requirements
- **OS**: Ubuntu 22.04 LTS (Recommended)
- **RAM**: Minimum 2GB (4GB Highly Recommended for MoviePy video compositing).
- **CPU**: 2+ Cores (Video rendering is CPU-intensive).

## 2. Initial Server Setup

SSH into your VPS and update the system:
```bash
sudo apt update && sudo apt upgrade -y
```

Install Python, pip, and system dependencies:
```bash
sudo apt install python3 python3-pip python3-venv nginx -y
```

*(Note: `moviepy` 2.x and `edge-tts` do not require external FFmpeg binaries on Linux as they download static binaries automatically, but if you run into issues, you can install FFmpeg via `sudo apt install ffmpeg`).*

## 3. Clone and Setup the Project

Navigate to your web directory and clone the project:
```bash
cd /var/www/
git clone <your-repository-url> panditji
cd panditji
```

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

*(For Production, we also need Gunicorn to serve the Flask app securely)*
```bash
pip install gunicorn
```

## 4. Environment Variables Configuration

Create a `.env` file in the project root:
```bash
nano .env
```
Paste your API keys:
```env
GEMINI_API_KEY="your_google_ai_studio_key"
META_PAGE_ACCESS_TOKEN="your_facebook_token"
META_PAGE_ID="your_facebook_page_id"
```

If you are using the **YouTube Auto-Uploader**, do not forget to securely upload your `client_secrets.json` to the `/var/www/panditji/` directory on the server!

*(Note: The YouTube OAuth flow requires a browser the first time to generate `token.json`. You should run the YouTube upload locally once, generate the `token.json`, and upload BOTH `client_secrets.json` and `token.json` to your server).*

## 5. Setting up Gunicorn and Systemd

We want the Pandit Ji Engine to run in the background forever and restart automatically if the server crashes. We will use `systemd`.

Create a new service file:
```bash
sudo nano /etc/systemd/system/panditji.service
```

Add the following configuration:
```ini
[Unit]
Description=Gunicorn instance to serve PanditJi Engine
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/panditji
Environment="PATH=/var/www/panditji/venv/bin"
# Read environment variables
EnvironmentFile=/var/www/panditji/.env
# Set timeout to 300 seconds (5 mins) because Video Rendering takes a long time!
ExecStart=/var/www/panditji/venv/bin/gunicorn --workers 2 --timeout 300 --bind unix:panditji.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

Start and enable the service:
```bash
sudo systemctl start panditji
sudo systemctl enable panditji
```

## 6. Configuring Nginx (Reverse Proxy)

Now we configure Nginx to route web traffic to our Gunicorn socket.

Create a new Nginx configuration block:
```bash
sudo nano /etc/nginx/sites-available/panditji
```

Add the following (replace `your_domain.com` with your actual domain or server IP):
```nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/panditji/panditji.sock;
        
        # Increase proxy timeouts to prevent Nginx from dropping the connection during video renders!
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    location /static {
        alias /var/www/panditji/static;
    }
}
```

Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/panditji /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

## 7. Fixing Permissions (Important!)

Since Flask needs to create new files in `data/`, `static/audio/`, and `static/video/`, you must grant the correct write permissions to the web server:

```bash
sudo chown -R root:www-data /var/www/panditji/data
sudo chown -R root:www-data /var/www/panditji/static
sudo chmod -R 775 /var/www/panditji/data
sudo chmod -R 775 /var/www/panditji/static
```

---

## 🎉 You're Live!

You can now navigate to `http://your_domain.com` and use the fully automated Pandit Ji Engine in production! All generated videos and audio will be saved directly on your VPS, and hitting "Upload" will dispatch them to social media straight from your server!
