import modal
import json

def transcribe_podcast_to_json_file():
    """
    This function transcribes a podcast by calling the 'process_podcast' function from the 'corise-podcast-project' modal.
    It takes the podcast URL and the output directory as input parameters.
    """
    f = modal.Function.lookup("corise-podcast-project", "process_podcast")
    output = f.call('https://feeds.megaphone.fm/MLN2155636147', '/content/podcast/')

    with open("./podcast-2.json", "w") as outfile:
        json.dump(output, outfile)

transcribe_podcast_to_json_file();
