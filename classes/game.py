from typing import Union
import ast

from utils.theta_sql import SetaSQL

db = SetaSQL('db/db.db', 'game')


class Game:
    def __init__(self, search: Union[int, str], register: bool = False):
        # ID로 검색 시
        if isinstance(search, int):
            data = db.selectone(
                rec=['id', 'name', 'nickname', 'series', 'tags'], where=f"id={search}")
            if data is None:
                raise NotExistGame

        # 제목으로 검색 시
        else:
            data = db.selectone(
                rec=['id', 'name', 'nickname', 'series', 'tags'], where=f"replace(name, ' ', '')='{search.replace(' ', '')}'")

            if data is None:
                if not register:
                    raise NotExistGame
            # TODO register하는 경우 추가

        self.id = data['id']
        self.name = data['name']
        self.nickname = ast.literal_eval(data['nickname'])
        self.series = data['series']
        self.tags = ast.literal_eval(data['tags'])

    def names(self, no_space: bool = False) -> list:
        names = [self.name] + self.nickname
        if no_space:
            return [i.replace(' ', '').lower() for i in names]
        else:
            return names

    def add_nickname(self, nickname: str):
        if nickname in self.nickname:
            raise AlreadyAppendedNickname
        self.nickname.append(nickname)
        db.update(nickname=self.nickname, where=f'id={self.id}')

    @property
    def soundtrack(self):
        ''' RETURN EXAMPLE >> [{'id': 2, 'url': '대충 주소'}, {'id': 3, 'url': '대충 주소'}]'''
        return db.select('music', ['id', 'url'], where=f"game={self.id}")

    def compare(self, keyword: str) -> bool:
        if keyword in self.names:
            return True
        if len(self.name) >= 9 and keyword in self.name:
            return True
        return False

    def __str__(self):
        return self.name


def add_game(name: str, nickname: list = [], tags: list = []):
    data = {
        'name': name,
        'nickname': nickname,
        'tags': tags
    }

    db.insert('game', **data)


class NotExistGame(Exception):
    def __init__(self):
        super().__init__('데이터 내에 존재하지 않는 게임입니다')


class AlreadyAppendedNickname(Exception):
    def __init__(self):
        super().__init__('이미 존재하는 닉네임입니다.')


def search_game(keyword):
    if isinstance(keyword, int) or str(keyword).isdigit():
        return Game(keyword)
    try:
        return Game(keyword)
    except NotExistGame:
        keyword = keyword.replace(' ', '')
        res = db.selectone(
            rec=['id'], where=f"replace(nickname, ' ', '') LIKE '%{keyword}%'")
        if res is None:
            raise NotExistGame
        return Game(res['id'])
