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

    # --- [ ✅✅ هذا هو التعديل المطلوب (تقليد كود Colab) ] ---
    ydl_opts = {
        "skip_download": True
        # (تم حذف فلتر "format" بالكامل)
        # (ده هيخلي yt-dlp يجيب "كل المتاح" ويختار الأفضل افتراضياً)
    }
    # --- [ نهاية التعديل ] ---

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[YTDL] Extracting ALL formats for: {video_id}")
            info = ydl.extract_info(video_url, download=False)
            
            stream_url = None
            video_title = info.get('title', 'Video Title')

            # --- [ ✅✅ الفلترة اليدوية (لضمان MP4) ] ---
            
            # (1. بنشوف yt-dlp اختار إيه كـ "أفضل" افتراضي)
            default_url = info.get('url')

            if default_url and ('.mp4' in default_url or '.googlevideo.com/' in default_url) and not ".m3u8" in default_url:
                # لو الاختيار الافتراضي هو MP4، استخدمه
                print(f"[YTDL] Default best format is MP4. Using it.")
                stream_url = default_url
            else:
                # (2. لو الاختيار الافتراضي M3U8، بندور إحنا في "كل المتاح")
                print(f"[YTDL] Default format is M3U8 or invalid. Searching list for MP4...")
                for f in info.get('formats', []):
                    # (بندور على أي حاجة mp4 ليها لينك)
                    if f.get('url') and f.get('ext') == 'mp4':
                        stream_url = f['url']
                        print(f"[YTDL] Found fallback MP4 format: {f.get('format_id')} at {f.get('height')}p")
                        break # لقيناه
            
            if not stream_url:
                raise Exception("No valid MP4 stream URL found in any format.")

            print(f"[YTDL] Railway Success for: {video_title}")
            
            # (بنرجع JSON باللينك الـ MP4 اللي لقيناه)
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
