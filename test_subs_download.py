import yt_dlp
import os
import glob

def test_download_subs(video_url):
    output_template = 'temp_subs_%(id)s'
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'subtitlesformat': 'vtt',
        'outtmpl': output_template,
    }

    # Clean up previous runs
    for f in glob.glob('temp_subs_*'):
        os.remove(f)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        print(f"Downloaded info for {info['id']}")
        
        # Check for files
        files = glob.glob('temp_subs_*')
        print(f"Files found: {files}")
        
        for f in files:
            with open(f, 'r', encoding='utf-8') as file:
                print(f"--- Content of {f} ---")
                print(file.read()[:200])
                print("--- End Content ---")

if __name__ == "__main__":
    test_download_subs("https://www.youtube.com/watch?v=nC3T4sHo9eQ")
