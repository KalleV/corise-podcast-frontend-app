import modal

def download_whisper():
  """
  Downloads the Whisper model and saves it to Container storage.
  """
  import os
  import whisper
  print ("Download the Whisper model")

  # Perform download only once and save to Container storage
  whisper._download(whisper._MODELS["medium"], '/content/podcast/', False)


stub = modal.Stub("corise-podcast-project")
corise_image = modal.Image.debian_slim().pip_install("feedparser",
                                                     "https://github.com/openai/whisper/archive/9f70a352f9f8630ab3aa0d06af5cb9532bd8c21d.tar.gz",
                                                     "requests",
                                                     "ffmpeg",
                                                     "openai",
                                                     "tiktoken",
                                                     "wikipedia",
                                                     "ffmpeg-python").apt_install("ffmpeg").run_function(download_whisper)

@stub.function(image=corise_image, gpu="any", timeout=600)
def get_transcribe_podcast(rss_url, local_path):
  """
  Downloads a podcast episode from the given RSS feed URL and transcribes it using the Whisper model.

  Args:
  - rss_url (str): The URL of the RSS feed.
  - local_path (str): The local path to save the downloaded podcast episode.

  Returns:
  - dict: A dictionary containing the podcast title, episode title, episode image, and episode transcript.
  """
  print ("Starting Podcast Transcription Function")
  print ("Feed URL: ", rss_url)
  print ("Local Path:", local_path)

  # Read from the RSS Feed URL
  import feedparser
  intelligence_feed = feedparser.parse(rss_url)
  podcast_title = intelligence_feed['feed']['title']
  episode_title = intelligence_feed.entries[0]['title']
  episode_image = intelligence_feed['feed']['image'].href
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
  output = {}
  output['podcast_title'] = podcast_title
  output['episode_title'] = episode_title
  output['episode_image'] = episode_image
  output['episode_transcript'] = result['text']
  return output

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
def get_podcast_summary(podcast_transcript):
  """
  Summarizes the main points of a podcast using OpenAI's GPT-3 model.

  Args:
  - podcast_transcript (str): The transcript of the podcast episode.

  Returns:
  - str: A summary of the main points discussed in the podcast.
  """
  import openai

  instructPrompt = """
     Act as a podcast transcriber. I want you to summarize the main points of the given podcast. Highlight the main points discussed in the podcast. Provide key takeaways.
  """

  request = instructPrompt + podcast_transcript

  chatOutput = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
                                            messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                      {"role": "user", "content": request}
                                                      ]
                                            )

  podcastSummary = chatOutput.choices[0].message.content

  return podcastSummary

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
def get_podcast_guest(podcast_transcript):
  """
  Retrieves information about the guest of a podcast episode using OpenAI's GPT-3 model and Wikipedia.

  Args:
  - podcast_transcript (str): The transcript of the podcast episode.

  Returns:
  - str: Information about the guest of the podcast episode.
  """
  import openai
  import wikipedia
  import json

  from wikipedia.exceptions import PageError, DisambiguationError, HTTPTimeoutError

  request = podcast_transcript[:10000]

  completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "user", "content": request}],
      functions=[
      {
          "name": "get_podcast_guest_information",
          "description": "Get information on the podcast guest using their full name and the name of the organization they are part of to search for them on Wikipedia or Google",
          "parameters": {
              "type": "object",
              "properties": {
                  "guest_name": {
                      "type": "string",
                      "description": "The full name of the guest who is speaking in the podcast",
                  },
                  "guest_organization": {
                      "type": "string",
                      "description": "The full name of the organization that the podcast guest belongs to or runs",
                  },
                  "guest_title": {
                      "type": "string",
                      "description": "The title, designation or role of the podcast guest in their organization",
                  },
              },
              "required": ["guest_name"],
          },
      }
    ],
    function_call={"name": "get_podcast_guest_information"}
  )

  podcast_guest = ""
  podcast_guest_org = ""
  podcast_guest_title = ""
  response_message = completion["choices"][0]["message"]
  if response_message.get("function_call"):
    # Unused:
    # function_name = response_message["function_call"]["name"]
    function_args = json.loads(response_message["function_call"]["arguments"])
    podcast_guest=function_args.get("guest_name")
    podcast_guest_org=function_args.get("guest_organization")
    podcast_guest_title=function_args.get("guest_title")

  if podcast_guest_org is None:
    podcast_guest_org = ""
  if podcast_guest_title is None:
    podcast_guest_title = ""

  output = {
    "name": podcast_guest,
    "summary": ""
  }

  try:
    search_query = f"{podcast_guest} {podcast_guest_org} {podcast_guest_title}"
    page = wikipedia.page(search_query, auto_suggest=False)

    output["summary"] = page.summary
  except DisambiguationError as error:
    options = error.options[:5]  # Limit to first 5 options
    output["summary"] = f"Multiple options found for '{search_query}': {', '.join(options)}"
  except PageError as error:
    output["summary"] = f"No Wikipedia page found for '{search_query}'"
  except HTTPTimeoutError as error:
    output["summary"] = f"Timed out while searching for '{search_query}'"
  except Exception as error:
    output["summary"] = f"Unexpected error: {error}"

    return output
  except wikipedia.exceptions.PageError as error:
    print("Wikipedia PageError:", error)
    output["summary"] = "Unexpected error retrieving information about podcast guest"
    return output

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"))
def get_podcast_highlights(podcast_transcript):
  import openai
  instructPrompt = """
    Given a podcast transcript, I want you to extract the highlights of the show. Capture unexpected or valuable takeaways for the reader.
  """

  request = instructPrompt + podcast_transcript

  chatOutput = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k",
                                            messages=[{"role": "system", "content": "You are a helpful assistant."},
                                                      {"role": "user", "content": request}
                                                      ]
                                            )
  chatOutput.choices[0].message.content

  podcastHighlights = chatOutput.choices[0].message.content
  return podcastHighlights

@stub.function(image=corise_image, secret=modal.Secret.from_name("my-openai-secret"), timeout=1200)
def process_podcast(url, path):
  output = {}
  podcast_details = get_transcribe_podcast.call(url, path)
  podcast_summary = get_podcast_summary.call(podcast_details['episode_transcript'])
  podcast_guest = get_podcast_guest.call(podcast_details['episode_transcript'])
  podcast_highlights = get_podcast_highlights.call(podcast_details['episode_transcript'])
  output['podcast_details'] = podcast_details
  output['podcast_summary'] = podcast_summary
  output['podcast_guest'] = podcast_guest
  output['podcast_highlights'] = podcast_highlights
  return output

@stub.local_entrypoint()
def test_method(url, path):
  podcast_details = get_transcribe_podcast.call(url, path)
  print ("Podcast Summary: ", get_podcast_summary.call(podcast_details['episode_transcript']))
  print ("Podcast Guest Information: ", get_podcast_guest.call(podcast_details['episode_transcript']))
  print ("Podcast Highlights: ", get_podcast_highlights.call(podcast_details['episode_transcript']))
