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

## Installation & Deployment

### Backend

1. Clone the repository
2. Set up a new account on [Modal](https://modal.com/)
3. Follow the set up steps in [Modal Home](https://modal.com/home) to install the `modal-client` and create a set of tokens
4. Create 3 secrets on Modal to run the [Podcast Backend](./podcast_backend.py):

| Secret Name                    | Environment Variable Name    | Description                                                                                                                                                           |
| ------------------------------ | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| my-openai-secret               | OPENAI_API_KEY               | An OpenAI API key with access to gpt-3.5-turbo-16k from [OpenAI Platform](https://platform.openai.com/account/api-keys)                                               |
| google-custom-search-api-key   | GOOGLE_CUSTOM_SEARCH_API_KEY | A programmable Google Search API key. Follow the instructions at https://developers.google.com/custom-search/v1/introduction to set it up.                            |
| google-custom-search-engine-id | GOOGLE_CSE_ID                | This must have a value assigned to the Search Engine ID project. Follow the instructions at https://developers.google.com/custom-search/v1/introduction to set it up. |

5. Deploy the backend to Modal using `modal deploy ./podcast_backend.py`

### Frontend

1. Go to https://share.streamlit.io/ and set up a new account
2. Login, then go to the [Share Apps](https://share.streamlit.io/) page to deploy a new application. Provide the following options:
   - Repository: https://github.com/KalleV/corise-podcast-frontend-app
   - Branch: main
   - Main file path: "podcast_frontend.py"

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
