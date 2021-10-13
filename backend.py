import requests
import json
import dotenv
import os

dotenv.load_dotenv()


class GetSongs:
    def get_songs(song_name):
        API_KEY = os.environ.get("API_KEY")

        url = "https://unsa-unofficial-spotify-api.p.rapidapi.com/search"

        querystring = {"query": song_name, "count": "1", "type": "tracks"}

        headers = {
            "x-rapidapi-host": "unsa-unofficial-spotify-api.p.rapidapi.com",
            "x-rapidapi-key": API_KEY,
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        try:
            data = response.json()
            songs_list = []
            names = []
            for results in data["Results"]:
                songs = {}
                if len(songs_list) == 4:
                    break

                artists = results["artists"]
                images = results["album"]["images"][0]
                name = results["name"]
                explicity = results["explicit"]
                song_url = results["external_urls"]["spotify"]
                preview_link = results["preview_url"]
                artists_details = []
                popularity = results["popularity"]
                release_date = results["album"]["release_date"]
                duration = results["duration_ms"]
                for i in artists:
                    artists_details.append(
                        [i["name"], i["external_urls"]["spotify"]]
                    )  # use name and spotify link

                if name not in names:
                    names.append(name)
                    songs["artist_details"] = artists_details
                    songs["images"] = images["url"]
                    songs["name"] = name
                    songs["explicity"] = explicity
                    songs["song_url"] = song_url
                    songs["popularity"] = popularity
                    songs["release_date"] = release_date
                    songs["duration"] = duration / 1000
                    songs["preview_link"] = preview_link
                if songs != {}:
                    songs_list.append(songs)
            return songs_list
        except:
            return "Could not find songs"
