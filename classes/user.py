'''
<User 클래스>
- user를 통해 객체를 생성합니다.
- user = User(author)처럼 사용합니다.
- user = User(id)로도 쓸 수 있지만 기능이 제한됩니다.
'''
from typing import Union, Optional

import discord

from utils.sqlite_class import Seta_sqlite
from utils import level_design

db = Seta_sqlite('db/userdata.db')


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

    realname: Optional[str] = None

    def __init__(self, user: Union[discord.User, int]):
        if isinstance(user, int):
            self.id = user
        else:
            self.user = user
            self.id = user.id
            self.realname = user.name.replace("'", '').replace("\"", '')

        try:
            self.load()
        except NotExistUser:
            self.name = self.realname if self.realname is not None else name
            db.insert_sql(
                'users', 'id, name, hp, mp',
                f"{self.id}, '{self.name}', {level_design.level_to_maxhp(1)}, {level_design.level_to_maxmp(1)}"
                )
            self.load()

        if self.realname is not None:
            if self.realname != self.name:
                db.update_sql('users', f"name='{self.name}'", f"id={self.id}")
            self.name = self.realname

    def load(self):
        '''데이터에서 값을 다시 불러옵니다'''
        data = self._load_data()
        if data == []:
            raise NotExistUser

        data = data[0]
        self.name = str(data[0])
        self._money = int(data[1])
        self._exp = int(data[2])
        self._hp = int(data[3])
        self._mp = int(data[4])
        self._is_gaming = bool(data[5])
        return data

    def _load_data(self):
        return db.select_sql(
            'users',
            'name, money, exp, hp, mp, is_gaming',
            f'WHERE id={self.id}'
            )

# --------- Getter/Setter --------- #

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
        db.update_sql('users', f'money=money+{int(value)}', f'WHERE id={self.id}')
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
    def hp(self):
        '''int: 유저의 체력'''
        return self._hp

    @hp.setter
    def hp(self, value: int):
        value = int(value)

        value = self.max_hp if self.max_hp < value else value
        value = 0 if 0 > value else value

        db.update_sql('users', f'hp={value}', f'WHERE id={self.id}')
        self._hp = value

    def add_hp(self, value: int):
        '''유저의 체력(HP)에 value 만큼 더합니다. 유저의 HP를 늘리거나 줄일 때 이 함수의 사용을 권장합니다.
        더해진 값이 최대 HP 값 이상이면 최대 HP 값으로 설정됩니다.
        더해진 값이 0 미만이면 0으로 설정됩니다.

        HP 변화량을 반환합니다.'''
        value = int(value)
        real_value = self.max_hp - self.hp if self.hp + value > self.max_hp else value
        real_value = self.hp * -1 if self.hp + value < 0 else value

        db.update_sql('users', f'hp=hp+{value}', f'WHERE id={self.id}')
        self._hp += real_value
        return real_value

    @property
    def mp(self):
        '''int: 유저의 마력'''
        return self._mp

    @mp.setter
    def mp(self, value: int):
        value = int(value)

        value = self.max_mp if self.max_mp < value else value
        value = 0 if 0 > value else value

        db.update_sql('users', f'mp={value}', f'WHERE id={self.id}')
        self._mp = value

    def add_mp(self, value: int):
        '''유저의 마력(MP)에 value 만큼 더합니다. 유저의 MP를 늘리거나 줄일 때 이 함수의 사용을 권장합니다.
        더해진 값이 최대 MP 값 이상이면 최대 MP 값으로 설정됩니다.
        더해진 값이 0 미만이면 0으로 설정됩니다.

        HP 변화량을 반환합니다.'''
        value = int(value)
        real_value = self.max_mp - self.mp if self.mp + value > self.max_mp else value
        real_value = self.mp * -1 if self.mp + value < 0 else value

        db.update_sql('users', f'mp=mp+{value}', f'WHERE id={self.id}')
        self._mp += real_value
        return real_value

    @property
    def is_gaming(self):
        '''bool: 유저의 게임 진행 중 여부'''
        return db.select_sql('users', 'is_gaming', f'WHERE id={self.id}')[0][0]

    @is_gaming.setter
    def is_gaming(self, value: bool):
        db.update_sql('users', f'is_gaming={int(value)}', f'WHERE id={self.id}')
        self._is_gaming = bool(value)

# --------- 스테이터스 관련 --------- #

    @property
    def level(self):
        '''int: 유저의 레벨'''
        return level_design.exp_to_level(self.exp)

    @property
    def max_hp(self):
        '''int: 유저의 최대 HP'''
        level_design.exp_to_maxhp(3)
        return level_design.exp_to_maxhp(self.exp)

    @property
    def max_mp(self):
        '''int: 유저의 최대 MP'''
        return level_design.exp_to_maxmp(self.exp)

    @property
    def attack(self):
        '''int: 유저의 공격력'''
        return level_design.exp_to_atk(self.exp)

    @property
    def defend(self):
        '''int: 유저의 방어력'''
        return level_design.exp_to_def(self.exp)

# --------- 메서드 --------- #

    def attack_to(self, target, skill=None):
        pass


class NotExistUser(Exception):
    def __init__(self):
        super().__init__('존재하지 않는 유저입니다')
