from app.ingestion.spotify.SpotifyHandler import SpotifyHandler
from app.ingestion.data_classes import ParsedTrack
from app.db.models import Artist, Track, TrackArtist
from app.db.session import SessionLocal


def get_tiktok_song_titles() -> list[str]:
    # TODO: Replace with actual TikTok integration
    return [
        "Rihanna - Where Have You Been",
        "Calvin Harris - Feel So Close",
        "David Guetta - Titanium",
        "Calvin Harris - Summer",
        "David Guetta - Without You",
    ]


def tiktok_to_spotify(titles: list[str]) -> list[ParsedTrack]:
    handler = SpotifyHandler()
    results = []
    for title in titles:
        result = handler.get_track_by_title(title)
        if result:
            results.append(result)
    return results


def save_tracks_to_db(parsed_tracks: list[ParsedTrack]) -> None:
    with SessionLocal() as session:
        for parsed in parsed_tracks:
            track, artists = parsed.track, parsed.artists
            # Upsert artists
            db_artists = []
            for artist in artists:
                existing = (
                    session.query(Artist)
                    .filter_by(spotify_id=artist.spotify_id)
                    .first()
                )
                if existing:
                    db_artists.append(existing)
                else:
                    session.add(artist)
                    session.flush()
                    db_artists.append(artist)

            # Upsert track
            existing_track = (
                session.query(Track).filter_by(spotify_id=track.spotify_id).first()
            )
            if existing_track:
                db_track = existing_track
            else:
                session.add(track)
                session.flush()
                db_track = track

            # Create TrackArtist junction rows
            for artist in db_artists:
                exists = (
                    session.query(TrackArtist)
                    .filter_by(track_id=db_track.id, artist_id=artist.id)
                    .first()
                )
                if not exists:
                    link = TrackArtist(
                        track_id=db_track.id,
                        artist_id=artist.id,
                        role="primary",
                    )
                    session.add(link)

        session.commit()


def run_pipeline():
    titles = get_tiktok_song_titles()
    parsed_tracks = tiktok_to_spotify(titles)
    save_tracks_to_db(parsed_tracks)
