# app.py (النسخة النهائية - مدخلين)
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, I am the Python Proxy Server on Railway!"

# --- [ 1. مدخل التحميل (الأوفلاين) ] ---
# (ده اللي بيجبر الدمج بـ ffmpeg عشان يدينا MP4 واحد)
@app.route('/api/get-video-info')
def get_video_info():
    video_id = request.args.get('youtubeId')
    if not video_id: return jsonify({"message": "Missing youtubeId"}), 400
    
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        "skip_download": True,
        "format": "bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b / best[ext=mp4][progressive=true][height<=720]/18",
        "postprocessors": [{'key': 'FFmpegVideoRemuxer', 'preferedformat': 'mp4'}],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[YTDL - MP4] Extracting MERGED info for: {video_id}")
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            video_title = info.get('title', 'Video Title')
            if not stream_url or "m3u8" in stream_url:
                raise Exception("No valid MP4 stream URL found after merge attempt")
            
            return jsonify({ "streamUrl": stream_url, "videoTitle": video_title })
    except Exception as e:
        print(f"[YTDL - MP4] FAILED: {str(e)}")
        return jsonify({"message": str(e)}), 500

# --- [ 2. مدخل المشاهدة (الأونلاين) ] ---
# (ده اللي بيرجع الفهرس M3U8 عشان الجودات المتعددة)
@app.route('/api/get-hls-playlist')
def get_hls_playlist():
    video_id = request.args.get('youtubeId')
    if not video_id: return jsonify({"message": "Missing youtubeId"}), 400
    
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        "skip_download": True,
        # (بنطلب الفورمات اللي البروتوكول بتاعه m3u8)
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
            
            # (بنرجع نفس الـ JSON بس اللينك ده m3u8)
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
