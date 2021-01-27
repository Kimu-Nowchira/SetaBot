'''
<User 클래스>
- user를 통해 객체를 생성합니다.
- user = User(author)처럼 사용합니다.
- user = User(id)로도 쓸 수 있지만 기능이 제한됩니다.
'''

from sqlite_class import Seta_sqlite
import level_design
from discord.errors import Forbidden

db = Seta_sqlite('db/userdata.db')


class User:
    # 기본 정보 #
    user = None  # discord.user
    id = None  # 유저 아이디
    name = None  # 유저 이름

    # 게임용 변수 # (user.money += 4 같이 값을 직접 바꾸는 사용은 절대 금지! 함수를 쓰세요!)
    money = None  # 보유한 돈
    exp = 0  # 경험치 (레벨은 경험치에 따라 자동 조정되며, 공격, 방어 등의 스탯은 레벨에 따라 자동 조정 됩니다.)
    hp = 0  # 체력(최대 체력은 레벨에 따라 자동 조정됩니다.)
    mp = 0  # 마나
    items = {}  # 아이템 목록

    def __init__(self, user):
        if type(user) == int:  # ID로 객체를 생성한 경우(비추천)
            self.id = user

        elif user is None:  # None으로 객체를 생성하려 시도한 경우(get_user()함수를 통해 변환하여 넣는 과정에서 None이 나오는 경우가 있어 예외를 추가해 주었습니다.)
            raise NotVaildType

        else:  # discord.User로 객체를 생성한 경우(추천)
            self.user = user
            self.id = self.user.id
            self.name = self.user.name.replace("'", '').replace("\"", '')  # 이름에 따옴표가 들어간 경우 제거합니다.

        # 데이터에 없는 유저인 경우 자동으로 유저 생성(id와 name을 제외한 나머지는 DB에 기본값이 지정되어 있습니다.)
        if not db.is_sql('users', f'WHERE id={self.user.id}'):
            db.insert_sql(
                'users',
                'id, name, hp, mp',
                f"{self.id}, '{self.name}', {level_design.level_to_maxhp(1)}, {level_design.level_to_maxmp(1)}"
                )

        # 데이터베이스에서 유저 정보 불러오기
        data = db.select_sql(
            'users',
            '*',
            "WHERE id={}".format(self.id)
            )[0]

        self.money = int(data[2])
        self.exp = int(data[3])
        self.hp = int(data[4])
        self.mp = int(data[5])
        db.update_sql('users', f"name='{self.name}'", f"id={self.id}")  # DB의 이름 정보 업데이트

# --------- 스테이터스 관련 --------- #

    def level(self):
        return level_design.exp_to_level(self.exp)

    def max_hp(self):
        level_design.exp_to_maxhp(3)
        return level_design.exp_to_maxhp(self.exp)

    def max_mp(self):
        return level_design.exp_to_maxmp(self.exp)

    def atk(self):
        return level_design.exp_to_atk(self.exp)

    def defe(self):
        '''방어력'''
        return level_design.exp_to_def(self.exp)

# ---------값 변경 관련 --------- #

    def give_money(self, value: int):
        '''
        value만큼 돈을 부여함. (음수일 경우 뺏음)
        - 기본적으로 가진 돈 이상을 뺏으려 할 경우 user.NotEnoughException 오류 발생(상점을 구현한다면 중요)
        '''
        if self.money + value < 0:
            raise NotEnoughException

        self.money += value
        db.update_sql('users', f'money=money+{value}', f'id={self.id}')

    def set_money(self, value: int):
        '''
        value로 돈을 설정함.
        '''
        self.money = value
        db.update_sql('users', f'money={value}', f'id={self.id}')

    def give_exp(self, value: int):
        '''
        value만큼의 경험치를 부여함. (음수일 경우 뺏음)
        - 경험치를 0 이하로 빼려고 하면 user.NotEnoughException 오류가 발생
        '''
        if self.exp + value < 0:
            raise NotEnoughException

        self.exp += value
        db.update_sql('users', f'exp=exp+{value}', f'id={self.id}')

    def set_exp(self, value: int):
        '''
        value로 경험치를 설정함. 음수 경험치부터는 레벨 0으로 취급함.
        '''
        self.exp = value
        db.update_sql('users', f'exp={value}', f'id={self.id}')

    def heal(self, value: int, limit=True):
        '''
        value만큼 체력을 회복함. (음수일 경우 데미지를 입음)
        - 체력을 깎은 값이 0 미만이면 0으로 설정 후 False를 반환함. (음수 체력은 존재하지 않음)
        (False 반환 = 캐릭터 쓰러짐)
        - 체력을 깎은 값이 0 이상이면 True를 반환함
        - limit가 True일 경우(기본값) 최대 HP 이상으로 회복 시 최대 HP로 자동으로 조정됨
        '''
        if self.hp + value < 0:
            value = -1 * self.hp
        elif limit and self.hp + value > level_design.exp_to_maxhp(self.exp):
            value = level_design.exp_to_maxhp(self.exp) - self.hp

        self.hp += value
        db.update_sql('users', f'hp=hp+{value}', f'id={self.id}')
        return self.hp is not 0

    def set_hp(self, value: int):
        '''
        value로 체력(HP)값을 설정함.
        '''
        self.hp = value
        db.update_sql('users', f'hp={value}', f'id={self.id}')

    def heal_mp(self, value: int):
        '''
        value만큼의 마력(MP)를 부여함. (음수일 경우 뺏음)
        - 마나를 0 미만으로 빼려고 하면 user.NotEnoughException 오류가 발생(EX 기술을 사용하기에 마나가 부족할 때)
        - 최대 마나 이상으로 회복하려 하면 최대 마나로 조정됨
        '''
        if self.exp + value < 0:
            raise NotEnoughException
        elif self.mp + value > level_design.exp_to_maxmp(self.exp):
            value = level_design.exp_to_maxmp(self.exp) - self.mp

        self.mp += value
        db.update_sql('users', f'mp=mp+{value}', f'id={self.id}')

    def set_mp(self, value: int):
        '''
        value로 마력(MP)값을 설정함.
        '''
        self.exp = value
        db.update_sql('users', f'mp={value}', f'id={self.id}')

# --------- 게임 진행 여부 관련 --------- #

    def start_game(self):
        '''게임 진행 여부 값을 True로 설정'''
        self.fishing_now = True
        db.update_sql('users', "is_gaming=1", f"id={self.id}")

    def finish_game(self):
        '''게임 진행 여부 값을 False로 설정'''
        self.fishing_now = False
        db.update_sql('users', "is_gaming=0", f"id={self.id}")

    def is_gaming(self):
        '''게임 진행 여부를 bool로 반환'''
        return bool(db.select_sql('users', 'is_gaming', f"WHERE id={self.id}")[0][0])


class NotEnoughException(Exception):
    def __init__(self):
        super().__init__('객체가 보유한 값 이상을 빼려고 시도하여 오류가 발생하였습니다.')


class NotVaildType(Exception):
    def __init__(self):
        super().__init__('올바른 인자값이 아닙니다.')
