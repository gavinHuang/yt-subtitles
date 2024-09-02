import yt_dlp
import webvtt
import os
import re

def download_subtitles(video_url):
    print(video_url)
    ydl_opts = {
        'writeautomaticsub': True,  # Download automatic captions
        'subtitleslangs': ['en','zh'],
        'skip_download': True,
        'forcetitle': True,
        'outtmpl': '%(id)s.%(ext)s'
    }
    retcode= -1
    video_title=None
    video_id = extract_youtube_id(video_url)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        retcode = ydl.download([video_url])
        info_dict = ydl.extract_info(video_url, download=False)
        video_title = info_dict.get('title', None)
        path = ydl.get_output_path()
        print(path)
        print(video_id)
        if retcode == 0:
            downloaded_subtitle_file = find_subtitle_file(".", video_id)
            if downloaded_subtitle_file.endswith('.vtt'):
                text_file = vtt_to_text(downloaded_subtitle_file)
            else:
                text_file = srt_to_text(downloaded_subtitle_file)
            return (video_title,text_file)
        else:
            print("download failed")
            return None

def extract_youtube_id(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^\s&]+)'
    )
    match = re.search(youtube_regex, url)
    if match:
        # The video ID is the fourth group in the match
        return match.group(4)
    else:
        return None

def vtt_to_text(vtt_filename):
    text_filename = vtt_filename.replace('.vtt', '.txt')
    vtt = webvtt.read(vtt_filename)
    previous_text = ""
    with open(text_filename, 'w', encoding="utf-8") as text_file:
        for caption in vtt:
            caption_text = caption.text.strip()
            lines = caption_text.split("\n")
            for line in lines:
                if line != previous_text:
                    text_file.write(line + '\n')
                    previous_text =line
    return text_filename

def srt_to_text(srt_filename):
    text_filename = srt_filename.replace('.srt', '.txt')
    
    dialogues = []
    
    with open(srt_filename, 'r', encoding="UTF-8") as file:
        lines = file.readlines()
    
    is_text = False
    last_dialogue = None

    # Process each line in the file
    for line in lines:
        # Strip whitespace from the line
        stripped_line = line.strip()
        
        # Skip empty lines and lines containing indices
        if stripped_line.isdigit():
            is_text = False
            continue
        
        # Check if the line contains the timestamp format
        if '-->' in stripped_line:
            is_text = True
            continue
        
        # If the line is part of a dialogue, check if it's not duplicated
        if is_text and stripped_line and stripped_line != last_dialogue:
            dialogues.append(stripped_line)
            last_dialogue = stripped_line  # Update the last added dialogue
    
    # Write the dialogues to the text file, separated by newlines
    with open(text_filename, 'w', encoding="UTF-8") as text_file:
        for dialogue in dialogues:
            text_file.write(dialogue + '\n')

    return text_filename

def find_subtitle_file(download_dir, video_id):
    # Look for both SRT and VTT files
    possible_extensions = ['.en.srt', '.en.vtt','.zh.srt', '.zh.vtt']
    for ext in possible_extensions:
        file_name = video_id + ext
        file = os.path.join(download_dir, file_name)
        if os.path.exists(file):
            return file
    return None
