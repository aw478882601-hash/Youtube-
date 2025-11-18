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
    
    # --- [ هذا الفلتر لم يتغير: يجلب أفضل MP4 مدمج ] ---
    ydl_opts = {
        "skip_download": True,
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
                raise Exception("No valid Progressive MP4 stream URL found.")

            print(f"[YTDL - MP4] Success for: {video_title} (Format: {info.get('format_id')})")
            
            return jsonify({
                "streamUrl": stream_url,
                "videoTitle": video_title
            })
            
    except Exception as e:
        print(f"[YTDL - MP4] FAILED: {str(e)}")
        return jsonify({"message": str(e)}), 500

# --- [ 2. مدخل المشاهدة (الأونلاين) - للويب ] ---
# (تم تعديله لإرجاع قائمة بجميع روابط الجودة المنفصلة)
@app.route('/api/get-hls-playlist')
def get_hls_playlist():
    video_id = request.args.get('youtubeId')
    if not video_id: return jsonify({"message": "Missing youtubeId"}), 400
    
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "format": "best" # نطلب جميع الجودات المتاحة
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"[YTDL - HLS] Extracting ALL formats info for: {video_id}")
            info = ydl.extract_info(video_url, download=False)
            
            video_title = info.get('title', 'Video Title')
            available_qualities = []

            # فلترة الجودات: نبحث عن روابط m3u8 التي تحتوي على فيديو (لها ارتفاع)
            for f in info.get('formats', []):
                # نتأكد أن البروتوكول HLS وأن الجودة (height) موجودة
                if (f.get('protocol') in ['m3u8_native', 'm3u8']) and f.get('height'):
                    available_qualities.append({
                        'quality': f['height'],
                        'url': f['url'] # هذا هو رابط m3u8 لجودة معينة
                    })
            
            # إزالة الجودات المكررة والترتيب
            unique_qualities = {q['quality']: q for q in available_qualities}.values()
            sorted_qualities = sorted(list(unique_qualities), key=lambda x: x['quality'], reverse=True)

            if not sorted_qualities:
                 raise Exception("No individual HLS (m3u8) quality links found.")

            print(f"[YTDL - HLS] Success. Found {len(sorted_qualities)} quality links for: {video_title}")
            
            # نرجع قائمة بكل الجودات بدلاً من streamUrl واحد
            return jsonify({
                "availableQualities": sorted_qualities,
                "videoTitle": video_title
            })
            
    except Exception as e:
        print(f"[YTDL - HLS] FAILED: {str(e)}")
        return jsonify({"message": f"Failed to get separate HLS streams: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port)
