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
        self.hug_gif_params = {
            'api_key': self.GIPHY_KEY,
            'q': "hug",
            'limit': 100
        }
        self.punch_gif_params = {
            'api_key': self.GIPHY_KEY,
            'q': "punch",
            'limit': 100
        }
        self.dance_gif_params = {
            'api_key': self.GIPHY_KEY,
            'q': "dance",
            'limit': 100
        }
        
        self.gifs = {
            "slap":[],
            "punch":[],
            "hug":[],
            "dance":[]
        }

        # --
        self.gif_params = {
            "slap":self.slap_gif_params,
            "hug":self.hug_gif_params,
            "punch":self.punch_gif_params,
            "dance":self.dance_gif_params
        }

    def load_gifs(self):
        # Endpoint for Giphy search API
        url = f"https://api.giphy.com/v1/gifs/search"
        # Make the GET request to the Giphy API
        try:
            for name, gif_param in self.gif_params.items():
                t = time.time()
                response = requests.get(url, params=gif_param)
                if response.status_code == 200:
                    data = response.json()
                    if data['data']:
                        self.gifs[name] = data["data"]
                print(f"loaded {name} gifs of quantity {len(data['data'])} in {round(time.time()-t,3)}s")
        except Exception as e:
            print(f"failed to load slap gif\nERROR: {e}")