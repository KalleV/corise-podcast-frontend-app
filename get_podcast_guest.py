import modal
import json

def get_podcast_guest():
    """
    This function transcribes a podcast by calling the 'process_podcast' function from the 'corise-podcast-project' modal.
    It takes the podcast URL and the output directory as input parameters.
    """
    with open('./podcast-1.json') as f:
        podcast_transcript = json.load(f)

    f = modal.Function.lookup("corise-podcast-project", "get_podcast_guest")
    output = f.call(podcast_transcript['podcast_details']['episode_transcript'])

    print("Guest information:", output)

get_podcast_guest()
