import spotipy
spotify = spotipy.Spotify(spotipy.oauth2.SpotifyClientCredentials(client_id='CLIENT_ID', client_secret='CLIENT_SECRET').get_access_token())

#lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'
#results = spotify.artist_top_tracks(lz_uri)
#
#for track in results['tracks'][:10]:
    #print('track    : ' + track['name'])
    #print('audio    : ' + track['preview_url'])
    #print('cover art: ' + track['album']['images'][0]['url'])
    #print()
    #print(track)


query = "Shining justice burning in me"
results = spotify.search(q=query, type="track", limit=1, offset=0)

names = ''
for artist in results['tracks']['items'][0]['album']['artists']:
    names += ", {}".format(artist['name'])
names = names[2:]
print(names)



{'album': {'album_type': 'album', 'artists': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/36QJpDe2go2KgaRleHCDTp'}, 'href': 'https://api.spotify.com/v1/artists/36QJpDe2go2KgaRleHCDTp', 'id': '36QJpDe2go2KgaRleHCDTp', 'name': 'Led Zeppelin', 'type': 'artist', 'uri': 'spotify:artist:36QJpDe2go2KgaRleHCDTp'}], 'external_urls': {'spotify': 'https://open.spotify.com/album/4wVHvawxZy52Oemd4sGyUm'}, 'href': 'https://api.spotify.com/v1/albums/4wVHvawxZy52Oemd4sGyUm', 'id': '4wVHvawxZy52Oemd4sGyUm', 'images': [{'height': 640, 'url': 'https://i.scdn.co/image/ab67616d0000b273b66922383836fd1f0973018f', 'width': 640}, 
{'height': 300, 'url': 'https://i.scdn.co/image/ab67616d00001e02b66922383836fd1f0973018f', 'width': 300}, {'height': 64, 'url': 'https://i.scdn.co/image/ab67616d00004851b66922383836fd1f0973018f', 'width': 64}], 'name': 'In Through the out Door (1994 Remaster)', 'release_date': '1979-08-15', 'release_date_precision': 'day', 'total_tracks': 7, 'type': 'album', 'uri': 'spotify:album:4wVHvawxZy52Oemd4sGyUm'}, 'artists': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/36QJpDe2go2KgaRleHCDTp'}, 'href': 'https://api.spotify.com/v1/artists/36QJpDe2go2KgaRleHCDTp', 'id': '36QJpDe2go2KgaRleHCDTp', 'name': 'Led Zeppelin', 'type': 'artist', 'uri': 'spotify:artist:36QJpDe2go2KgaRleHCDTp'}], 'disc_number': 1, 'duration_ms': 351266, 'explicit': False, 'external_ids': {'isrc': 'USAT29900640'}, 'external_urls': {'spotify': 'https://open.spotify.com/track/6lrh9jZ1xoMwoErgPSj2rY'}, 'href': 'https://api.spotify.com/v1/tracks/6lrh9jZ1xoMwoErgPSj2rY', 'id': '6lrh9jZ1xoMwoErgPSj2rY', 'is_local': False, 'is_playable': True, 'name': 'All My Love - 1990 Remaster', 'popularity': 65, 'preview_url': 'https://p.scdn.co/mp3-preview/d03424a544dcc5102703ebb081fd321dc5567b32?cid=48bdbb4c93d549bdb814f8a6c0cc2cfb', 'track_number': 6, 'type': 'track', 'uri': 'spotify:track:6lrh9jZ1xoMwoErgPSj2rY'}