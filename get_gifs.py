import requests
import random
from funcs import *

class Gifs():
    def __init__(self):
        self.GIPHY_KEY = load_giphy_token()
        self.slap_gif_params = {
            'api_key': self.GIPHY_KEY,
            'q': "slap face",
            'limit': 100
        }
        self.slap_gifs = []

    def load_gifs(self):
        t = time.time()
        # Endpoint for Giphy search API
        url = f"https://api.giphy.com/v1/gifs/search"
        # Make the GET request to the Giphy API
        try:
            print("loading gif")
            response = requests.get(url, params=self.slap_gif_params)
            if response.status_code == 200:
                data = response.json()
                if data['data']:
                    self.slap_gifs = data["data"]
            print(f"loaded {len(data['data'])} gifs in {round(time.time()-t,3)}s")
        except Exception as e:
            print(f"failed to load slap gif\nERROR: {e}")