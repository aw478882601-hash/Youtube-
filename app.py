# app.py (النسخة النهائية للإنتاج)
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, I am the Python Proxy Server on Railway!"

@app.route('/api/get-video-info')
def get_video_info():
    video_id = request.args.get('youtubeId')
    if not video_id:
        return jsonify({"message": "Missing youtubeId"}), 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # --- [ ✅✅ هذا هو الفلتر النهائي ] ---
    ydl_opts = {
        "skip_download": True,
        # 1. اطلب "أفضل" ملف يكون MP4 ومدمج (progressive)
        # 2. لو ملقاش، هات format_id 18 (ده MP4 مدمج 360p مضمون)
        "format": "best[ext=mp4][progressive=true]/18"
    }
    # --- [ نهاية الفلتر ] ---

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[YTDL] Extracting PROGRESSIVE MP4 for: {video_id}")
            info = ydl.extract_info(video_url, download=False)
            
            # --- [ ✅✅ تعديل: بنجيب اللينك اللي الفلتر اختاره ] ---
            # (الفلتر ده هيختار 18 أو أحسن MP4 مدمج)
            stream_url = info.get('url')
            video_title = info.get('title', 'Video Title')

            if not stream_url or "m3u8" in stream_url:
                raise Exception("No valid Progressive MP4 stream URL found.")

            print(f"[YTDL] Railway Success for: {video_title}")
            
            # بنرجع JSON زي ما الأندرويد و Vercel مستنيين
            return jsonify({
                "streamUrl": stream_url,
                "videoTitle": video_title
            })
            
    except Exception as e:
        print(f"[YTDL] Railway FAILED: {str(e)}")
        return jsonify({"message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port)
