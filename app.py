from flask import Flask, request, jsonify
import os

app = Flask(__name__)

from youtube import download_subtitles

@app.route('/', methods=['GET'])
def download_subtitles_api():
    video_url = request.args.get('video')
    if not video_url:
        return jsonify({'error': 'No video URL provided'}), 400
    
    try:
        result = download_subtitles(video_url)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)