from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from pytube import YouTube
from slugify import slugify
from tqdm import tqdm

import pandas as pd


def create_subtitle_video(_, video_clip: VideoFileClip, clip_folder: str, exported_folder: str):
  video_subtitles = SubtitlesClip(f"{clip_folder}/clip.srt", text_clip_outside_stroke)

  final = CompositeVideoClip([video_clip, video_subtitles.set_position(("center"))])
  final.write_videofile(f'{exported_folder}/subtitles.mp4', fps=video_clip.fps, remove_temp=True, codec="libx264", audio_codec="pcm_s16le")


def create_word_by_word_video(transcription, video_clip: VideoFileClip, clip_folder: str, exported_folder: str):
  subtitle = { "start": [], "end": [], "text": [] }

  for segment in transcription["segments"]:
    for word in segment["words"]:
      subtitle["start"].append(word["start"])
      subtitle["end"].append(word["end"])
      subtitle["text"].append(word["word"])

  subtitles_df = pd.DataFrame.from_dict(subtitle)
  subtitles_df.to_csv(f"{clip_folder}/subtitles_word_by_word.csv")

  subs = tuple(zip(tuple(zip(subtitles_df["start"].values, subtitles_df["end"].values)), subtitles_df["text"].values))
  video_subtitles = SubtitlesClip(subs, lambda text: TextClip(text, font="Arial-Rounded-MT-Bold", fontsize=58, stroke_width=1, bg_color="blue", color="white", stroke_color = "white"))

  final = CompositeVideoClip([video_clip, video_subtitles.set_position(("center"))])
  final.write_videofile(f'{exported_folder}/word_by_word.mp4', fps=video_clip.fps, remove_temp=True, codec="libx264", audio_codec="pcm_s16le")


def download_youtube_video(video_id: str, output_path: str):
  print(f"Downloading video [{video_id}] from youtube...")

  yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
  filename = f"{slugify(yt.title)}.mp4"

  video_stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()

  progress_bar = tqdm(total=video_stream.filesize, unit="B", unit_scale=True)

  def progress_callback(_, __, bytes_remaining):
    progress_bar.update(video_stream.filesize - bytes_remaining)

  yt.register_on_progress_callback(progress_callback)

  video_stream.download(output_path, filename)

  progress_bar.close()

  return filename


def text_clip_outside_stroke(text: str):
  return TextClip(text, bg_color="transparent", color="Gold1", font="Arial-Rounded-MT-Bold", fontsize=54, stroke_color="Gold4", stroke_width=2)
