import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup
import youtube_dl
from youtube_search import YoutubeSearch
import json
import flask
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp

# Load environment variables from .env file
import os
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client_Id = os.getenv("SPOTIFY_CLIENT_ID")
client_Secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_Uri = os.getenv("REDIRECT_URI")
print(client_Id, client_Secret, redirect_Uri)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=client_Id,
        client_secret=client_Secret,
        redirect_uri=redirect_Uri,
        scope="playlist-read-private",
    )
)

app = flask.Flask(__name__)
# playlist_link = "https://open.spotify.com/playlist/4bcVnuc14zM9z2WJyQMOaD?si=Pf6CfFgbSwq3LI89U2Triw"

CORS(app)


@app.route("/get_music", methods=["GET"])
def get_music():
    playlist_link = request.args.get("playlist")
    playlist_URI = playlist_link.split("/")[-1].split("?")[0]
    track_uris = [x["track"]["uri"] for x in sp.playlist_tracks(playlist_URI)["items"]]

    if not playlist_URI:
        return jsonify({"error": "No playlist URI provided"}), 400
    music_data = []

    for track in sp.playlist_tracks(playlist_URI)["items"]:
        # URI
        track_uri = track["track"]["uri"]

        # Track name
        track_name = track["track"]["name"]

        # Main Artist
        artist_uri = track["track"]["artists"][0]["uri"]
        artist_info = sp.artist(artist_uri)

        # Name, popularity, genre
        artist_name = track["track"]["artists"][0]["name"]
        artist_pop = artist_info["popularity"]
        artist_genres = artist_info["genres"]

        # Album
        album = track["track"]["album"]["name"]

        # Popularity of the track
        track_pop = track["track"]["popularity"]

        # Append track data to the list
        music_data.append(
            {
                "track_uri": track_uri,
                "track_name": track_name,
                "artist_name": artist_name,
                "artist_popularity": artist_pop,
                "artist_genres": artist_genres,
                "album": album,
                "track_popularity": track_pop,
            }
        )

    return json.dumps(music_data, indent=4)


def download_mp3(youtube_url):
    # Specify the output directory where you want to save the media files
    output_dir = "musik"  # Make sure this directory exists or create it

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Specify the path to your FFmpeg executable
    ffmpeg_path = "C:/ffmpeg-2024-09-19-git-0d5b68c27c-full_build/bin"  # Change this to your FFmpeg path

    # yt-dlp options
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
                "nopostoverwrites": True,
            }
        ],
        "ffmpeg_location": ffmpeg_path,  # Set FFmpeg path
        "outtmpl": os.path.join(
            output_dir, "%(title)s.%(ext)s"
        ),  # Save the file with the title as the name
        "quiet": True,
    }

    # Download the MP3
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([youtube_url])
            # After downloading, get the file pat
            downloaded_file_path = f"{ydl.prepare_filename({'title': ydl.extract_info(youtube_url, download=False)['title'], 'ext': 'mp3'})}"
            return downloaded_file_path  # Return the path of the saved file
        except yt_dlp.utils.DownloadError as e:
            print(f"Error: {e}")
            return None


@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    track_name = data["song"]
    results = YoutubeSearch(f"{track_name}", max_results=10).to_json()
    parsed_data = json.loads(results)

    # Extract video IDs
    video_ids = [video["id"] for video in parsed_data["videos"]]

    if not video_ids:
        return jsonify({"message": "No videos found."}), 404

    # Download the MP3 and get the saved file path

    file_path = download_mp3(f"https://www.youtube.com/watch?v={video_ids[0]}")
    file_path = file_path.replace("\\", "/")

    print(file_path)
    if file_path:
        # Send the file to the client
        return send_file(
            file_path,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name=os.path.basename(file_path),
        )
    else:
        return jsonify({"message": "Failed to download the audio."}), 500

    # buffer.seek(0)  # Go back to the start of the BytesIO buffer
    # return buffer


# results = YoutubeSearch(f'${track_name}', max_results=10).to_json()
# parsed_data = json.loads(results)

# # Extract video IDs
# video_ids = [video['id'] for video in parsed_data['videos']]


# import yt_dlp

# import os

# def download_mp3(youtube_url, output_dir, ffmpeg_location="C:/ffmpeg-2024-09-19-git-0d5b68c27c-full_build/bin"):
#     # Ensure output directory exists
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     # yt-dlp options
#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',
#         }],
#         'ffmpeg_location': ffmpeg_location,  # Set the ffmpeg location
#         'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
#     }

#     # Download the mp3
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         try:
#             ydl.download([youtube_url])
#         except yt_dlp.utils.DownloadError as e:
#             print(f"Error: {e}")

# # Example usage

# print(video_ids[0])
# id=video_ids[0]
# download_mp3(f"https://www.youtube.com/watch?v={id}", "musik")


# print(video_ids)

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
