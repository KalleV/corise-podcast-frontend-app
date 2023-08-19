import modal

def download_whisper():
  """
  Downloads the Whisper model and saves it to Container storage.
  """
  # Load the Whisper model
  import os
  import whisper
  print ("Download the Whisper model")

  # Perform download only once and save to Container storage
  whisper._download(whisper._MODELS["medium"], '/content/podcast/', False)


stub = modal.Stub("corise-podcast-project")
corise_image = modal.Image.debian_slim().pip_install("feedparser",
                                                     "https://github.com/openai/whisper/archive/9f70a352f9f8630ab3aa0d06af5cb9532bd8c21d.tar.gz",
                                                     "requests",
                                                     "ffmpeg").apt_install("ffmpeg").run_function(download_whisper)

@stub.function(image=corise_image, gpu="any")
def get_transcribe_podcast(rss_url, local_path):
  """
  Transcribes the podcast episode from the given RSS feed URL and saves the transcribed text to a file.

  Args:
    rss_url (str): The URL of the RSS feed.
    local_path (str): The local path to save the downloaded podcast episode.

  Returns:
    str: The transcribed text of the podcast episode.
  """
  print ("Starting Podcast Transcription Function")
  print ("Feed URL: ", rss_url)
  print ("Local Path:", local_path)

  # Read from the RSS Feed URL
  import feedparser
  intelligence_feed = feedparser.parse(rss_url)
  for item in intelligence_feed.entries[0].links:
    if (item['type'] == 'audio/mpeg'):
      episode_url = item.href
  episode_name = "podcast_episode.mp3"
  print ("RSS URL read and episode URL: ", episode_url)

  # Download the podcast episode by parsing the RSS feed
  from pathlib import Path
  p = Path(local_path)
  p.mkdir(exist_ok=True)

  print ("Downloading the podcast episode")
  import requests
  with requests.get(episode_url, stream=True) as r:
    r.raise_for_status()
    episode_path = p.joinpath(episode_name)
    with open(episode_path, 'wb') as f:
      for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

  print ("Podcast Episode downloaded")

  # Load the Whisper model
  import os
  import whisper

  # Load model from saved location
  print ("Load the Whisper model")
  model = whisper.load_model('medium', device='cuda', download_root='/content/podcast/')

  # Perform the transcription
  print ("Starting podcast transcription")
  result = model.transcribe(local_path + episode_name)

  # Return the transcribed text
  print ("Podcast transcription completed, returning results...")
  return result

@stub.local_entrypoint()
def main(url, path):
  """
  Calls the get_transcribe_podcast function with the given URL and path.

  Args:
    url (str): The URL of the RSS feed.
    path (str): The local path to save the downloaded podcast episode.

  Returns:
    None
  """
  output = get_transcribe_podcast.call(url, path)
  print (output['text'])
