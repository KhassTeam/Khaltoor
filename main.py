import os
import spotipy
import pytablewriter
from spotipy.oauth2 import SpotifyClientCredentials
from dateutil import parser

CLIENT_ID = 'fill me!'
CLIENT_SECRET = 'fill me!'
PLAYLIST_URI = 'spotify:user:ftaheri96:playlist:0c6vHqSegYiJYLegscZmte'


def get_playlist_tracks():
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    username = PLAYLIST_URI.split(':')[2]
    playlist_id = PLAYLIST_URI.split(':')[4]
    offset = 0
    items = []

    while True:
        res = sp.user_playlist_tracks(username, playlist_id, offset=offset)
        items = items + res['items']
        if res['next'] is not None:
            offset = offset + 100
        else:
            break

    tracks = []
    for item in items:
        track = {
            'added_at': parser.parse(item['added_at']),
            'user': {
                'name': item['added_by']['id'],
                'url': item['added_by']['external_urls']['spotify'],
            },
            'title': item['track']['name'],
            'track_url': item['track']['external_urls']['spotify'],
            'album': {
                'name': item['track']['album']['name'],
                'url': item['track']['album']['external_urls']['spotify'],
            },
            'artists': []
        }
        for artist_item in item['track']['artists']:
            artist = artist_item['name']
            artist_url = artist_item['external_urls']['spotify']
            track['artists'].append({
                'name': artist,
                'url': artist_url
            })
        tracks.append(track)

    tracks.reverse()
    return tracks


def get_md_link(text, url):
    return '[%s](%s)' % (text, url)


def write_table(tracks, output_path):
    writer = pytablewriter.MarkdownTableWriter()
    writer.header_list = ['Title', 'Artist', 'Album', 'User', 'Added at']
    value_matrix = []
    for track in tracks:
        print(track['title'])
        cur = [
            get_md_link(track['title'], track['track_url']),
            ', '.join(map(lambda x: x['name'], track['artists'])),
            track['album']['name'],
            get_md_link(track['user']['name'], track['user']['url']),
            track['added_at'].strftime('%Y-%m-%d')
        ]
        value_matrix.append(cur)
    writer.value_matrix = value_matrix
    with open(output_path, 'w') as f:
        writer.stream = f
        writer.write_table()


def merge_md_files(inputs, output):
    with open(output, 'w') as out_file:
        for inp in inputs:
            with open(inp, 'r') as in_file:
                out_file.writelines(in_file.readlines())


def main():
    tracks_temp_file = 'tracks.md'
    try:
        tracks = get_playlist_tracks()
        write_table(tracks, tracks_temp_file)
        merge_md_files(inputs=['Intro.md', tracks_temp_file], output='README.md')
    except Exception as e:
        print(e)
    finally:
        if os.path.exists(tracks_temp_file):
            os.remove(tracks_temp_file)


if __name__ == '__main__':
    main()
