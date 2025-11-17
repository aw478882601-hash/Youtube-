# app.py
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

    # --- [ ✅✅ هذا هو التعديل الأهم ] ---
    ydl_opts = {
        "skip_download": True,
        # 1. اطلب احسن صورة (bv) + احسن صوت (ba)
        # 2. اطلب دمجهم (merger) في فورمات mp4
        "format": "bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b",
        "outtmpl": "%(id)s.%(ext)s",
        "postprocessors": [{
            'key': 'FFmpegVideoRemuxer',
            'preferedformat': 'mp4', # <-- عايزين الناتج mp4
        }],
    }
    # --- [ نهاية التعديل ] ---

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[YTDL] Extracting MERGED info for: {video_id}")
            info = ydl.extract_info(video_url, download=False)
            
            # --- [ ✅✅ تعديل: اختيار الفورمات بعد الدمج ] ---
            # (بعد الدمج، اللينك بيكون موجود في 'url' الرئيسي)
            stream_url = info.get('url')
            video_title = info.get('title', 'Video Title')

            if not stream_url:
                # لو لسبب ما مفيش دمج، حاولنا ناخد أي فورمات mp4 عادي
                print("[YTDL] Merge failed, falling back to regular format...")
                for f in info.get('formats', []):
                   if f.get('ext') == 'mp4' and f.get('url'):
                       stream_url = f['url']
                       break
            
            if not stream_url:
                raise Exception("No valid stream URL found after merge attempt")

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
