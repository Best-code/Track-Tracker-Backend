from app.ingestion.spotify.SpotifyHandler import SpotifyHandler
from app.ingestion.spotify.data_classes import IndividualTrack


def get_tiktok_song_titles() -> list[str]:
    # TODO: Replace with actual TikTok integration
    return [
        "Rihanna - Where Have You Been",
        "Calvin Harris - Feel So Close",
        "David Guetta - Titanium",
        "Calvin Harris - Summer",
        "David Guetta - Without You",
    ]


def tiktok_to_spotify(titles: list[str]) -> list[IndividualTrack]:
    handler = SpotifyHandler()
    tracks = []
    for title in titles:
        track = handler.get_track_by_title(title)
        if track:
            tracks.append(track)
    return tracks


def save_tracks_to_db(tracks: list[IndividualTrack]) -> None:
    # Implement function to save tracks to your database w/ SQLAlchemy models
    pass


def run_pipeline():
    titles = get_tiktok_song_titles()
    tracks = tiktok_to_spotify(titles)
    save_tracks_to_db(tracks)
