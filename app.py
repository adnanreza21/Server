from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Jalankan yt-dlp untuk dump info dalam format JSON
        result = subprocess.run(
            ['yt-dlp', '--dump-json', url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return jsonify({
                "error": result.stderr.strip()
            }), 500

        # Parsing output JSON dari yt-dlp
        import json
        video_info = json.loads(result.stdout)

        # Contoh ambil beberapa info penting saja
        response_data = {
            "id": video_info.get("id"),
            "title": video_info.get("title"),
            "uploader": video_info.get("uploader"),
            "duration": video_info.get("duration"),
            "formats": [
                {
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "filesize": f.get("filesize"),
                    "url": f.get("url"),
                } for f in video_info.get("formats", []) if f.get("url")
            ]
        }

        return jsonify(response_data)

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Timeout running yt-dlp"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
