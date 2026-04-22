import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from app.db.models import Artist, Track
from app.ingestion.data_classes import ParsedTrack


class SpotifyHandler:
    def __init__(self):
        self._client = self._create_client()

    def _create_client(self) -> spotipy.Spotify:
        return spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            )
        )

    def _paginate(self, fetch_fn, *args, limit: int = 50, **kwargs) -> list[dict]:
        results = []
        offset = 0

        while True:
            batch = fetch_fn(*args, limit=limit, offset=offset, **kwargs)
            items = batch.get("items", [])
            if not items:
                break

            results.extend(items)
            offset += len(items)

            if not batch.get("next"):
                break
        return results

    @property
    def client(self) -> spotipy.Spotify:
        return self._client

    """ User functions """

    def get_current_user_profile(self) -> list[dict]:
        return self.client.current_user()

    def get_user_playlists(self) -> dict:
        return self._paginate(self.client.current_user_playlists)

    """Artist and Track Parsing Functions"""

    def _parse_artist(self, artist_data: dict) -> Artist:
        return Artist(
            spotify_id=artist_data["id"],
            name=artist_data.get("name"),
            spotify_type=artist_data.get("type"),
            spotify_external_urls=artist_data.get("external_urls"),
            spotify_genres=artist_data.get("genres", []),
            spotify_images=artist_data.get("images", []),
            spotify_popularity=artist_data.get("popularity"),
        )

    def get_artist(self, artist_id: str) -> Artist:
        artist_data = self.client.artist(artist_id)
        return self._parse_artist(artist_data)

    def _parse_track(self, track_data: dict) -> ParsedTrack:
        artists = [self._parse_artist(a) for a in track_data.get("artists", [])]

        track = Track(
            spotify_id=track_data["id"],
            name=track_data.get("name"),
            spotify_type=track_data.get("type"),
            spotify_duration_ms=track_data.get("duration_ms"),
            spotify_explicit=track_data.get("explicit"),
            spotify_popularity=track_data.get("popularity"),
            spotify_preview_url=track_data.get("preview_url"),
            spotify_available_markets=track_data.get("available_markets", []),
            spotify_external_urls=track_data.get("external_urls"),
            spotify_external_ids=track_data.get("external_ids"),
        )

        return ParsedTrack(track=track, artists=artists)

    def get_track_by_title(self, title: str) -> ParsedTrack | None:
        results = self.client.search(q=title, type="track", limit=1)
        items = results.get("tracks", {}).get("items", [])
        if not items:
            return None

        track_data = items[0]
        return self._parse_track(track_data=track_data)

    # Current User Information

    def get_saved_tracks(self) -> list[ParsedTrack]:
        results = self._paginate(self.client.current_user_saved_tracks)
        parsed: list[ParsedTrack] = []

        for item in results:
            track_data = item["track"]
            if track_data:
                parsed.append(self._parse_track(track_data))
        return parsed

    def get_playlist_tracks(self, playlist_id: str) -> list[ParsedTrack]:
        results = self._paginate(self.client.playlist_items, playlist_id)
        parsed: list[ParsedTrack] = []

        for item in results:
            track_data = item["track"]
            if track_data:
                parsed.append(self._parse_track(track_data))
        return parsed
