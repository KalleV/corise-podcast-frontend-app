# Corise Podcast Frontend App

## Overview

Corise Podcast Frontend App is a podcast feed parser application built using [Streamlit](https://streamlit.io/), Python 3, [Modal](https://modal.com/), and LLMs like GPT and Whisper. It is designed to parse RSS and summarize podcast episodes from https://www.listennotes.com/.

## Features

- Parses RSS feeds and summarizes podcast episodes
- Retrieves podcast guest information using OpenAI and Google's Programmable Search Engine API

## Technologies Used

- Streamlit
- Python 3
- Modal
- LLMs (GPT and Whisper)
- OpenAI
- Google Programmable Search Engine API

## Installation

1. Clone the repository
2. Install the required packages using `pip install -r requirements.txt`
3. Deploy backend to Modal using `modal deploy ./podcast_backend.py`

## Usage

1. Enter an RSS feed URL in the input box
    - Examples:
        - https://feed.podbean.com/thecurioustanguero/feed.xml
        - https://maestrosdelamusica.libsyn.com/rss
2. Click on the "Summarize" button to generate a summary of the podcast episode
3. The app will also display information about the podcast guests

## Modal Remote Function calls

### Deploy backend to Modal

```bash
modal deploy ./podcast_backend.py
```

### Running commands on Modal

_Note: the /content/podcast/ is a path inside the image rather than local_

```bash
modal run ./podcast_backend.py --url https://access.acast.com/rss/d556eb54-6160-4c85-95f4-47d9f5216c49 --path /content/podcast/
```

### Download a transcription using a remote Modal function

```bash
python3 transcribe_podcast.py
```

### Fetch podcast guest information using remote Modal function

```bash
python3 get_podcast_guest.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
