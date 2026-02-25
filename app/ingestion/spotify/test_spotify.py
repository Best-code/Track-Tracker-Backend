from unittest.mock import MagicMock

from .SpotifyHandler import SpotifyHandler

MOCK_SEARCH_RESPONSE = {
    "tracks": {
        "href": "https://api.spotify.com/v1/search?offset=0&limit=1&query=Rihana%20-%20Where%20Have%20You%20Been&type=track",
        "limit": 1,
        "next": "https://api.spotify.com/v1/search?offset=1&limit=1&query=Rihana%20-%20Where%20Have%20You%20Been&type=track",
        "offset": 0,
        "previous": None,
        "total": 1000,
        "items": [
            {
                "album": {
                    "album_type": "album",
                    "artists": [
                        {
                            "external_urls": {
                                "spotify": "https://open.spotify.com/artist/5pKCCKE2ajJHZ9KAiaK11H"
                            },
                            "href": "https://api.spotify.com/v1/artists/5pKCCKE2ajJHZ9KAiaK11H",
                            "id": "5pKCCKE2ajJHZ9KAiaK11H",
                            "name": "Rihanna",
                            "type": "artist",
                            "uri": "spotify:artist:5pKCCKE2ajJHZ9KAiaK11H",
                        }
                    ],
                    "available_markets": ["US"],
                    "external_urls": {
                        "spotify": "https://open.spotify.com/album/2g1EakEaW7fPTZC6vBmBCn"
                    },
                    "href": "https://api.spotify.com/v1/albums/2g1EakEaW7fPTZC6vBmBCn",
                    "id": "2g1EakEaW7fPTZC6vBmBCn",
                    "images": [],
                    "is_playable": True,
                    "name": "Talk That Talk",
                    "release_date": "2011-11-18",
                    "release_date_precision": "day",
                    "total_tracks": 11,
                    "type": "album",
                    "uri": "spotify:album:2g1EakEaW7fPTZC6vBmBCn",
                },
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/5pKCCKE2ajJHZ9KAiaK11H"
                        },
                        "href": "https://api.spotify.com/v1/artists/5pKCCKE2ajJHZ9KAiaK11H",
                        "id": "5pKCCKE2ajJHZ9KAiaK11H",
                        "name": "Rihanna",
                        "type": "artist",
                        "uri": "spotify:artist:5pKCCKE2ajJHZ9KAiaK11H",
                    }
                ],
                "available_markets": ["US"],
                "disc_number": 1,
                "duration_ms": 242680,
                "explicit": False,
                "external_ids": {"isrc": "USUM71118074"},
                "external_urls": {
                    "spotify": "https://open.spotify.com/track/5WQQIDU3HRaMyPkob8mpFb"
                },
                "href": "https://api.spotify.com/v1/tracks/5WQQIDU3HRaMyPkob8mpFb",
                "id": "5WQQIDU3HRaMyPkob8mpFb",
                "is_local": False,
                "is_playable": True,
                "name": "Where Have You Been",
                "popularity": 83,
                "preview_url": None,
                "track_number": 2,
                "type": "track",
                "uri": "spotify:track:5WQQIDU3HRaMyPkob8mpFb",
            }
        ],
    }
}


def test_where_have_you_been(monkeypatch):
    mock_client = MagicMock()
    mock_client.search.return_value = MOCK_SEARCH_RESPONSE
    monkeypatch.setattr(SpotifyHandler, "_create_client", lambda self: mock_client)

    handler = SpotifyHandler()
    track = handler.get_track_by_title("Rihana - Where Have You Been")
    assert track.id == "5WQQIDU3HRaMyPkob8mpFb"
    assert track.name == "Where Have You Been"
    assert track.duration_ms == 242680
    assert track.explicit is False
    assert track.artists[0].name == "Rihanna"
    assert track.artists[0].id == "5pKCCKE2ajJHZ9KAiaK11H"
