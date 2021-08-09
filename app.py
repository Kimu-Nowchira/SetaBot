# This code will work if you're are willing to use a newer version of Python
from bs4 import BeautifulSoup
import requests


class Playlist():
    def __init__(self, playListUrl):
        self._playListUrl = playListUrl

        # This will take the html text from Youtube playList url and stores it in a variable called html-doc.
        self._htmldoc = requests.get(str(self._playListUrl)).text

        with open('html.html', 'w') as file:
            file.write(self._htmldoc)

        self._soup = BeautifulSoup(self._htmldoc, 'html.parser')
        # This will create a list of all the titles and the youtube url videos using the html-doc.
        self._rawList = self._soup('a', id='video-title')

        # This will loop through a list of titles and Youtube urls and formats it nicely for you.
        for link in self._rawList:
            print('호액')
            print('{0}'.format(link.string) + 'http://youtube.com' +
                  '{0}'.format(link.get('href')))


# To use this class all you got to do is:
# 1 - Create a new object to use the class..
# 2- put a youtube playlist url where it is shown below..
# 3- Run it, and enjoy.
objPlaylist = Playlist(
    'https://www.youtube.com/playlist?list=PLZq7Jn-XiIlskI0PI31tG_nSt8qPDjgsq')
