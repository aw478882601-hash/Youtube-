from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

# --- روت عشان نتأكد إن السيرفر شغال ---
@app.route('/')
def hello_world():
    return "Hello, I am the Python Proxy Server on Railway!"

# --- الروت الأساسي اللي الأندرويد و Vercel هيكلموه ---
@app.route('/api/get-video-info')
def get_video_info():
    # بياخد الـ ID من اللينك
    video_id = request.args.get('youtubeId')
    if not video_id:
        return jsonify({"message": "Missing youtubeId"}), 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # --- خيارات السحب (للفيديوهات العامة - مش محتاجين كوكيز) ---
    ydl_opts = {
        "skip_download": True,
        "format": "best[height<=720][ext=mp4]" # بنطلب 720p عشان يكون سريع
    }

    try:
        # --- تشغيل yt-dlp ---
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[YTDL] Railway: Extracting PUBLIC info for: {video_id}")
            info = ydl.extract_info(video_url, download=False)
            
            stream_url = info.get('url')
            video_title = info.get('title', 'Video Title')

            # --- fallback لو ملقاش 720p ---
            if not stream_url:
                 for f in info.get('formats', []):
                    if f.get('ext') == 'mp4' and f.get('url'):
                        stream_url = f['url']
                        break
            
            if not stream_url:
                raise Exception("No valid MP4 stream URL found")

            print(f"[YTDL] Railway: Success for: {video_title}")
            
            # --- [✅ الأهم] بنرجع JSON بنفس الشكل اللي الأندرويد مستنيه ---
            return jsonify({
                "streamUrl": stream_url,
                "videoTitle": video_title
            })
            
    except Exception as e:
        print(f"[YTDL] Railway FAILED: {str(e)}")
        return jsonify({"message": str(e)}), 500

if __name__ == "__main__":
    # --- Railway بيدور على متغير PORT ده ---
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port)
