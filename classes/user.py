'''
<User 클래스>
- user를 통해 객체를 생성합니다.
- user = User(author)처럼 사용합니다.
- user = User(id)로도 쓸 수 있지만 기능이 제한됩니다.
'''
from typing import Union, Optional
import ast

import discord

from utils.theta_sql import SetaSQL
from utils import level_design
from .game import Game

db = SetaSQL('db/db.db', 'user')


class User:
    # 기본 정보 #
    user: Optional[discord.User] = None  # 디스코드의 유저 객체
    id: int = 0  # 유저 아이디
    name: str = '알 수 없는 유저'  # 유저 이름

    # 게임용 변수 # (user.money += 4 같이 값을 직접 바꾸는 사용은 절대 금지! 함수를 쓰세요!)
    _money: int = 0  # 보유한 돈
    _exp: int = 0  # 경험치 (레벨은 경험치에 따라 자동 조정되며, 공격, 방어 등의 스탯은 레벨에 따라 자동 조정 됩니다.)
    _hp: int = 0  # 체력(최대 체력은 레벨에 따라 자동 조정됩니다.)
    _mp: int = 0  # 마나
    items: list = []  # 아이템 목록
    _gamelist: list = []

    realname: Optional[str] = None

    def __init__(self, user: Union[discord.User, int]):
        if isinstance(user, int):
            print('유저로 객체 생성')
            self.id = user
        else:
            self.user = user
            self.id = user.id
            self.realname = user.name.replace("'", '').replace("\"", '')

        try:
            self.load()
        except NotExistUser:
            self.name = self.realname if self.realname is not None else self.name
            userdata = {
                'id': self.id,
                'name': self.name,
                'exp': 0,
                'money': 0,
                'items': [],
                'gamelist': []
            }
            db.insert(**userdata)
            self.load()

        if self.realname is not None:
            if self.realname != self.name:
                print(self.name)
                db.update(name=self.name, where=f'id={self.id}')
            self.name = self.realname

    def load(self):
        '''데이터에서 값을 다시 불러옵니다'''
        data = self._load_data()
        if data is None:
            raise NotExistUser

        self.name = str(data['id'])
        self._money = int(data['money'])
        self._exp = int(data['exp'])
        self.item = ast.literal_eval(str(data['items']))
        self._gamelist = ast.literal_eval(str(data['gamelist']))
        return data

    def _load_data(self):
        return db.selectone(rec=['id', 'name', 'exp', 'money', 'items', 'gamelist'], where=f'id={self.id}')

    def append_gamelist(self, game_id: int):
        if game_id in self.gamelist:
            raise AlreadyAppendedGame
        if not isinstance(game_id, int):
            raise TypeError
        self.gamelist.append(game_id)
        db.update(gamelist=list(set(self.gamelist)), where=f'id={self.id}')

    def append_gamelist_obj(self, game):
        if game.id in self.gamelist:
            raise AlreadyAppendedGame
        self.gamelist.append(game.id)
        db.update(gamelist=self.gamelist, where=f'id={self.id}')

    @property
    def gamelist_class(self):
        return [Game(i) for i in self.gamelist]


# --------- Getter/Setter --------- #


    @property
    def gamelist(self):
        return self._gamelist

    @gamelist.setter
    def gamelist(self, val: list):
        self._gamelist = val
        db.update(gamelist=self._gamelist, where=f'id={self.id}')

    @property
    def money(self):
        '''int: 유저의 돈'''
        return db.select_sql('users', 'money', f'WHERE id={self.id}')[0][0]

    @money.setter
    def money(self, value: int):
        db.update_sql('users', f'money={int(value)}', f'WHERE id={self.id}')
        self._money = int(value)

    def add_money(self, value: int):
        '''유저의 돈을 value 만큼 더합니다. 유저의 돈을 늘리거나 줄일 때 add_money의 사용을 권장합니다.'''
        db.update_sql(
            'users', f'money=money+{int(value)}', f'WHERE id={self.id}')
        self._money += int(value)

    @property
    def exp(self):
        '''int: 유저의 경험치'''
        return db.select_sql('users', 'exp', f'WHERE id={self.id}')[0][0]

    @exp.setter
    def exp(self, value: int):
        db.update_sql('users', f'exp={int(value)}', f'WHERE id={self.id}')
        self._exp = int(value)

    def add_exp(self, value: int):
        '''유저의 경험치를 value 만큼 더합니다. 유저의 경험치를 늘리거나 줄일 때 이 함수의 사용을 권장합니다.'''
        db.update_sql('users', f'exp=exp+{int(value)}', f'WHERE id={self.id}')
        self._exp += int(value)

    @property
    def is_gaming(self):
        '''bool: 유저의 게임 진행 중 여부'''
        return db.select_sql('users', 'is_gaming', f'WHERE id={self.id}')[0][0]

    @is_gaming.setter
    def is_gaming(self, value: bool):
        db.update_sql(
            'users', f'is_gaming={int(value)}', f'WHERE id={self.id}')
        self._is_gaming = bool(value)

# --------- 스테이터스 관련 --------- #

    @property
    def level(self):
        '''int: 유저의 레벨'''
        return level_design.exp_to_level(self.exp)


class NotExistUser(Exception):
    def __init__(self):
        super().__init__('데이터 내에 존재하지 않는 유저입니다')


class AlreadyAppendedGame(Exception):
    def __init__(self):
        super().__init__('이미 해당 유저가 추가한 게임입니다.')
