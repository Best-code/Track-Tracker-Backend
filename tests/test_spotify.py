"""
Spotify API connectivity tests.

Validates that the Spotify API credentials are configured correctly
and that key API endpoints are accessible.

Usage:
    uv run python -m tests.test_spotify
"""

from app.ingestion.spotify.spotify_to_db import get_spotify_client


def run_api_tests() -> None:
    """
    Execute connectivity tests against Spotify API endpoints.

    Tests search, track retrieval, album retrieval, artist retrieval,
    and new releases endpoints to verify API access.
    """
    print("Running Spotify API tests...\n")
    sp = get_spotify_client()

    # Test 1: Search
    print("1. Search: ", end="")
    results = sp.search(q="Kendrick", type="track", limit=1)
    results
    print("OK")

    # Test 2: Get track by ID
    print("2. Get track: ", end="")
    track = sp.track("4VXIryQMWpIdGgYR4TrjT1")
    print(f"OK - {track['name']}")

    # Test 3: Get album
    print("3. Get album: ", end="")
    album = sp.album("4yP0hdKOZPNshxUOjY0cZj")
    print(f"OK - {album['name']}")

    # Test 4: Get artist
    print("4. Get artist: ", end="")
    artist = sp.artist("2YZyLoL8N0Wb9xBt1NhZWg")
    print(f"OK - {artist['name']}")

    # Test 5: New releases
    print("5. New releases: ", end="")
    new = sp.new_releases(limit=3)
    print(f"OK - {len(new['albums']['items'])} albums")

    print("\nAll Spotify API tests passed!")


if __name__ == "__main__":
    run_api_tests()
