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
        # 1. اطلب ملف مدمج (progressive=true) ويكون mp4
        # 2. امنع (protocol!=*m3u8) أي قايمة تشغيل
        # 3. هات 720p أو الأقل المتاح
        "format": "best[ext=mp4][height<=720][progressive=true][protocol!=*m3u8]/best[ext=mp4][height<=720][protocol!=*m3u8]"
    }
    # --- [ نهاية التعديل ] ---

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[YTDL] Extracting PROGRESSIVE MP4 info for: {video_id}")
            info = ydl.extract_info(video_url, download=False)
            
            stream_url = None
            video_title = info.get('title', 'Video Title')

            # --- [ ✅✅ تعديل: بندور على اللينك اللي طلبناه ] ---
            # (لأننا طلبنا فورمات محدد، لازم ندور عليه في القايمة)
            for f in info.get('formats', []):
                # بنشوف الفورمات اللي بيطابق طلبنا
                if f.get('url') and f.get('ext') == 'mp4' and f.get('progressive') == True:
                    stream_url = f['url']
                    print(f"[YTDL] Found Progressive MP4 format: {f.get('format_id')}")
                    break # لقيناه

            # لو ملقناش فورمات مدمج (لسبب ما)، شوف اللينك الرئيسي
            if not stream_url:
                stream_url = info.get('url') 
                # (ولو ده كان m3u8 برضه، هيفشل في الخطوة الجاية)

            if not stream_url or "m3u8" in stream_url:
                # لو لسه مفيش لينك، أو اللينك اللي رجع m3u8 (رغم إننا منعناه)
                raise Exception("No valid Progressive MP4 stream URL found. Only HLS (m3u8) is available.")

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
