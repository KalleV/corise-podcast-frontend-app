# corise-podcast-frontend-app

## Deploy backend to Modal

```bash
modal deploy ./podcast_backend.py
```

## Running commands on Modal

_Note: the /content/podcast/ is a path inside the image rather than local_

```bash
modal run ./podcast_backend.py --url https://access.acast.com/rss/d556eb54-6160-4c85-95f4-47d9f5216c49 --path /content/podcast/
```

## Download a transcription using a deployed Modal function

```bash
python3 transcribe_podcast.py
```

## Fetch podcast guest information using Modal function

```bash
python3 get_podcast_guest.py
```
