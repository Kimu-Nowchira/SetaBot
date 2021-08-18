import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse

from . import logger

# from . import seta_json


def gets(url: str) -> list:
    if not url.startswith('https://'):
        return []

    if 'playlist' not in url:
        return [(url, '')]

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
    # seta_json.set_json(f"static/playlist_{url[-10:]}.json", response)

    playlist_items = []
    while request is not None:
        response = request.execute()
        playlist_items += response["items"]
        request = youtube.playlistItems().list_next(request, response)

    print(f"총 {len(playlist_items)}개의 영상을 찾았습니다.")
    res = []
    for t in playlist_items:
        video_id = t["snippet"]["resourceId"]["videoId"]
        view_point = get_view_from_video_id(video_id)
        res.append(
            (
                f'https://www.youtube.com/watch?v={video_id}&list={playlist_id}&t=0s',
                t['snippet']['title'],
                view_point,
            )
        )
    return res


def get_view_from_video_id(id):
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey="AIzaSyBqthrFSyLLlBx4ilpfRnAd7lJT7GWii9E")
    request = youtube.videos().list(part='snippet,contentDetails,statistics', id=id)
    response = request.execute()

    try:
        vc = response['items'][0]['statistics']['viewCount']
        print(f"{id}의 조회수 : {int(vc):,}")
    except:
        logger.warn(f'{id} 영상 조회수 로드에 실패 : {response}')
        return -1
    return int(vc)
