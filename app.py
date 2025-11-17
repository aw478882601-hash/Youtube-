# app.py (للتجربة فقط - سيبوظ التطبيقات)
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

    # --- [ ✅✅ تعديل: تقليد كود Colab (بدون فلتر) ] ---
    ydl_opts = {
        "skip_download": True
        # (تم حذف فلتر "format" بالكامل زي ما طلبت)
    }
    # --- [ نهاية التعديل ] ---

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[YTDL] Extracting ALL formats for: {video_id}")
            info = ydl.extract_info(video_url, download=False)
            
            video_title = info.get('title', 'Video Title')
            formats_list = info.get('formats', [])

            # --- [ ✅✅ تعديل: تنظيف الليستة زي Colab ] ---
            # (بنعمل ليستة جديدة بالمعلومات اللي إنت عاوزها)
            clean_formats = []
            for f in formats_list:
                clean_formats.append({
                    "format_id": f.get('format_id'),
                    "height": f.get('height'),
                    "ext": f.get('ext'),
                    "protocol": f.get('protocol'), # (مهم عشان نشوف m3u8)
                    "note": f.get('format_note'),
                    "url": f.get('url') # اللينك
                })

            print(f"[YTDL] Railway Success. Found {len(clean_formats)} formats.")
            
            # --- [ ✅✅ الأهم: بنرجع "الليستة الكاملة" للتجربة ] ---
            # (ده اللي هيبوظ التطبيقات، بس هتشوفه في المتصفح)
            return jsonify({
                "videoTitle": video_title,
                "available_formats": clean_formats 
            })
            
    except Exception as e:
        print(f"[YTDL] Railway FAILED: {str(e)}")
        return jsonify({"message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port)
