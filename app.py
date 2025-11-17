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

    # --- [ ✅✅ هذا هو التعديل الأهم (صياغة جديدة) ] ---
    ydl_opts = {
        "skip_download": True,
        # 1. حاول تجيب ملف مدمج 720p (أفضل سيناريو)
        # 2. لو فشلت، هات أي ملف 720p (فيديو بس أو أي حاجة)
        # 3. لو فشلت، هات أي ملف mp4 وخلاص
        "format": "best[ext=mp4][height<=720][progressive=true]/best[ext=mp4][height<=720]/best[ext=mp4]/best"
    }
    # --- [ نهاية التعديل ] ---

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[YTDL] Extracting MP4 info for: {video_id}")
            info = ydl.extract_info(video_url, download=False)

            stream_url = None
            video_title = info.get('title', 'Video Title')

            # --- [ ✅✅ تعديل: بندور على اللينك اللي طلبناه ] ---
            # (لأننا طلبنا فورمات محدد، لازم ندور عليه في القايمة)

            # (أولاً، بنشوف اللينك الرئيسي اللي yt-dlp اختاره)
            stream_url = info.get('url')

            if not stream_url or "m3u8" in stream_url:
                # لو اللينك الرئيسي m3u8، بندور في القايمة
                print(f"[YTDL] Main URL is m3u8, searching formats list...")
                for f in info.get('formats', []):
                    # بندور على أي حاجة mp4 ليها لينك
                    if f.get('url') and f.get('ext') == 'mp4':
                        stream_url = f['url']
                        print(f"[YTDL] Found fallback MP4 format: {f.get('format_id')}")
                        break # لقيناه

            if not stream_url or "m3u8" in stream_url:
                raise Exception("No valid MP4 stream URL found. Only HLS (m3u8) is available.")

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
