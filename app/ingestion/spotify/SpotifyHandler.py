import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from app.ingestion.spotify.data_classes import Artist, IndividualTrack


class SpotifyHandler:
    def __init__(self):
        self._client = self._create_client()

    def _create_client(self) -> spotipy.Spotify:
        return spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                # redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
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
            id=artist_data["id"],
            href=artist_data["href"],
            name=artist_data.get("name"),
            uri=artist_data.get("uri"),
            type=artist_data.get("type"),
            external_urls=artist_data.get("external_urls"),
            followers=artist_data.get("followers"),
            genres=artist_data.get("genres", []),
            images=artist_data.get("images", []),
            popularity=artist_data.get("popularity"),
        )

    def get_artist(self, artist_id: str) -> Artist:
        artist_data = self.client.artist(artist_id)
        return self._parse_artist(artist_data)

    def _parse_track(self, track_data: dict) -> IndividualTrack:
        artists = [self._parse_artist(a) for a in track_data.get("artists", [])]

        return IndividualTrack(
            id=track_data["id"],
            href=track_data["href"],
            artist_ids=[a.id for a in artists],
            artists=artists,
            name=track_data.get("name"),
            uri=track_data.get("uri"),
            type=track_data.get("type"),
            duration_ms=track_data.get("duration_ms"),
            explicit=track_data.get("explicit"),
            popularity=track_data.get("popularity"),
            disc_number=track_data.get("disc_number"),
            track_number=track_data.get("track_number"),
            is_local=track_data.get("is_local"),
            preview_url=track_data.get("preview_url"),
            available_markets=track_data.get("available_markets", []),
            external_urls=track_data.get("external_urls"),
            external_ids=track_data.get("external_ids"),
        )

    """ Track Fetching Functions """

    def get_track_id_by_title(self, title: str) -> str | None:
        results = self.client.search(q=title, type="track", limit=1)
        items = results.get("tracks", {}).get("items", [])
        if not items:
            return None
        
        return self._parse_track(items[0].get("id"))

    def get_saved_tracks(self) -> list[IndividualTrack]:
        results = self._paginate(self.client.current_user_saved_tracks)
        tracks: list[IndividualTrack] = []

        for item in results:
            track_data = item["track"]
            if track_data:
                tracks.append(self._parse_track(track_data))
        return tracks

    def get_playlist_tracks(self, playlist_id: str) -> list[IndividualTrack]:
        results = self._paginate(self.client.playlist_items, playlist_id)
        tracks: list[IndividualTrack] = []

        for item in results:
            track_data = item["track"]
            if track_data:
                tracks.append(self._parse_track(track_data))
        return tracks