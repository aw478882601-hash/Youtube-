# app.py (النسخة النهائية - بأولوية للجودة العالية المدمجة)
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, I am the Python Proxy Server on Railway!"

# --- [ 1. مدخل التحميل (الأوفلاين) - للأندرويد ] ---
@app.route('/api/get-video-info')
def get_video_info():
    video_id = request.args.get('youtubeId')
    if not video_id: return jsonify({"message": "Missing youtubeId"}), 400
    
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    # --- [ ✅✅ هذا هو الفلتر الجديد اللي طلبته ] ---
    ydl_opts = {
        "skip_download": True,
        # 1. اطلب "أفضل" ملف يكون MP4 ومدمج (progressive) وجودته <= 720p
        #    (ده هيجيب 720p أو 480p لو متاحين)
        # 2. لو ملقاش، هات "format_id 18" (ده MP4 مدمج 360p مضمون 100%)
        "format": "best[ext=mp4][progressive=true][height<=720]/18"
    }
    # --- [ نهاية التعديل ] ---

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[YTDL - MP4] Extracting BEST PROGRESSIVE MP4 for: {video_id}")
            info = ydl.extract_info(video_url, download=False)
            
            stream_url = info.get('url')
            video_title = info.get('title', 'Video Title')

            if not stream_url or "m3u8" in stream_url:
                # (لو لسبب ما الفلتر مرجعش لينك سليم، ارمي خطأ)
                raise Exception("No valid Progressive MP4 stream URL found.")

            print(f"[YTDL - MP4] Success for: {video_title} (Format: {info.get('format_id')})")
            
            # بنرجع JSON باللينك الـ MP4 اللي لقيناه
            return jsonify({
                "streamUrl": stream_url,
                "videoTitle": video_title
            })
            
    except Exception as e:
        print(f"[YTDL - MP4] FAILED: {str(e)}")
        return jsonify({"message": str(e)}), 500

# --- [ 2. مدخل المشاهدة (الأونلاين) - للويب ] ---
# (ده هيفضل زي ما هو عشان يجيب الجودات المتعددة m3u8)
@app.route('/api/get-hls-playlist')
def get_hls_playlist():
    video_id = request.args.get('youtubeId')
    if not video_id: return jsonify({"message": "Missing youtubeId"}), 400
    
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        "skip_download": True,
        "format": "best[protocol=m3u8_native]/best[protocol=m3u8]"
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[YTDL - HLS] Extracting HLS (m3u8) info for: {video_id}")
            info = ydl.extract_info(video_url, download=False)
            
            stream_url = info.get('url')
            video_title = info.get('title', 'Video Title')

            if not stream_url or "m3u8" not in stream_url:
                 raise Exception("No HLS (m3u8) playlist found.")

            print(f"[YTDL - HLS] Success for: {video_title}")
            
            return jsonify({
                "streamUrl": stream_url,
                "videoTitle": video_title
            })
    except Exception as e:
        print(f"[YTDL - HLS] FAILED: {str(e)}")
        return jsonify({"message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port)
