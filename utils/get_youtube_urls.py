import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse


def gets(url: str) -> list:
    if not url.startswith('https://'):
        return []

    if 'playlist' not in url:
        return [url]

    return get_url_from_playlist(url)


def get_url_from_playlist(url):
    query = parse_qs(urlparse(url).query, keep_blank_values=True)
    playlist_id = query["list"][0]

    print(f'get all playlist items links from {playlist_id}')
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey="AIzaSyBqthrFSyLLlBx4ilpfRnAd7lJT7GWii9E")

    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()

    playlist_items = []
    while request is not None:
        response = request.execute()
        playlist_items += response["items"]
        request = youtube.playlistItems().list_next(request, response)

    print(f"총 {len(playlist_items)}개의 영상을 찾았습니다.")
    return [
        f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}&list={playlist_id}&t=0s'
        for t in playlist_items
    ]
