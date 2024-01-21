from moviepy.editor import *
from whisper.utils import get_writer

import argparse
import glob
import os
import shutil
import whisper

from utils import create_subtitle_video, create_word_by_word_video, download_youtube_video, rescale_video
from yt import create_diarization_video


print("Setting up requirements")
parser = argparse.ArgumentParser()
print("Defining command line arguments")
parser.add_argument("--video", dest="video", type=str, help="Youtube video ID to split in clips")
parser.add_argument("--home", dest="home", type=str, default=os.getenv('HOME'), help="User home directory")
parser.add_argument("--source", dest="source", type=str, default="Downloads", help="Folder to look for video and write clips")
parser.add_argument("--interval", dest="interval", type=int, default=30, help="Clips duration")
parser.add_argument("--no-subtitles", dest="no_subtitles", type=bool, default=False, help="No export clips with regular subtitles")
parser.add_argument("--no-word-by-word", dest="no_word_by_word", type=bool, default=False, help="No export clips speaking word by word")
parser.add_argument("--no-scrolling", dest="no_scrolling", type=bool, default=False, help="No export clips highlithing the spoken word")
parser.add_argument("--translate", dest="translate", type=str, help="Languge to translate subtitles be translated to")
print("Parsing command line arguments")
args = parser.parse_args()

print("Loading whisper model...")
model = whisper.load_model("large")

def split_video():
  print("Cleaning up temp files")
  for f in glob.glob("*.{mp4,wav}"):
    os.remove(f)

  print("Starting split video task")
  if args.video is None:
    raise FileNotFoundError("You need to provide a youtube video id to be clipped using --video argument")

  print("Getting source folder")
  source_folder = f"{args.home}/{args.source}"
  print("Getting video folder")
  video_folder = f"{source_folder}/{args.video}"
  print("Getting clips folder")
  clips_folder = f"{video_folder}/clips"

  if os.path.isdir(video_folder):
    print("Removing previous video folder")
    shutil.rmtree(video_folder, ignore_errors=True)

  print("Create a new video folder to export all clips")
  os.mkdir(video_folder)
  print("Create a new clips folder to the video")
  os.mkdir(clips_folder)

  video_name = download_youtube_video(args.video, video_folder)

  print("Getting video path")
  video_path = f"{video_folder}/{video_name}"
  print("Getting clip height")
  clip_height = 1920
  print("Getting clip width")
  clip_width = 1080

  print("Creating video file clip")
  original_video = VideoFileClip(video_path)

  print(f"Defining all {args.interval} seconds clips...")
  video_clips = [original_video.subclip(start_time, start_time + args.interval) for start_time in range(0, int(original_video.duration), args.interval)]

  for i, video_clip in enumerate(video_clips):
    print(f"Creating clip {i + 1}")
    print("Getting clip name")
    clip_name = f"clip_{i + 1}"
    print("Getting clip folder")
    clip_folder = f"{clips_folder}/{clip_name}"
    print("Getting clip path")
    clip_path = f"{clip_folder}/clip.mp4"

    print("Creating clip folder to export all final files")
    os.mkdir(clip_folder)

    print(f"Resizing video to 9:16 ({clip_width}x{clip_height}) aspect ratio")
    temp_clip = video_clip.fx(vfx.resize, newsize=(clip_width, clip_height)).set_position("center")

    print("Export base clip")
    temp_clip.write_videofile(clip_path, codec="libx264", audio_codec="pcm_s16le")

    print("Calling subtitles task")
    export_clips(temp_clip, clip_folder)


def export_clips(video_clip: VideoFileClip, clip_folder: str):
  print("Starting export clips task")

  print("Getting exported folder")
  exported_folder = f"{clip_folder}/_exported"

  print("Creating folder to export final clips")
  os.mkdir(exported_folder)

  task = "translate" if args.translate is not None else "transcribe"
  if task != "": 
    print(f"The clips will be translated to {args.translate}")

  print("Getting audio clip name")
  audio_clip = f"{clip_folder}/clip.wav"
  print("Exporting audio wav file")
  video_clip.audio.write_audiofile(audio_clip, codec="pcm_s16le")

  print("Extracting subtitles from audio file...")
  transcription = model.transcribe(audio_clip, language=args.translate, task=task, verbose=True, word_timestamps=True)
  
  print("Getting SRT writter")
  srt_writer = get_writer(output_format="srt", output_dir=clip_folder)
  print("Writing srt file...")
  srt_writer(transcription, audio_clip, {
    "highlight_words": False,
    "max_line_count": 1,
    "max_line_width": 16
  })

  if not args.no_subtitles:
    print("Creating subtitled video...")
    create_subtitle_video(transcription, video_clip, clip_folder, exported_folder)

  if not args.no_word_by_word:
    print("Creating worded by worded video...")
    create_word_by_word_video(transcription, video_clip, clip_folder, exported_folder)

  if not args.no_scrolling:
    print("Creating diarizationed video...")
    create_diarization_video(transcription, video_clip, clip_folder, exported_folder)

  video_clip.close()
  raise RuntimeError("TERMINOU O PRIMEIRO CLIP !!!")


split_video()
