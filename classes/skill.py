from utils import seta_json

skills: dict = seta_json.get_json("db/skills.json")


class Skill():
    code: str = 'NONE'
    name: str = '알 수 없는 기술'
    power: str = 0
    description: str = '설명이 없습니다.'

    def __init__(self, code: str):
        code = code.upper()
        if code not in skills.keys():
            raise NotExistSkill

        self.code = code
        self.name = skills[code]["name"]
        self.power = skills[code]["power"]
        if "description" in skills[code].keys():
            self.description = skills[code]["description"]

    def damage(self, attacker, defender):
        ''' 이 기술로 공격했을 때 나오는 데미지를 반환합니다.
        단, 방어자의 체력은 고려하지 않습니다. '''
        return self.power * attacker.attack / defender.defend

    def use(self, attacker, defender):
        ''' 이 기술을 사용합니다. 로그가 담긴 리스트를 반환합니다.'''
        logs = []

        # 공격 데미지 처리
        dam = -1 * defender.add_hp(-1 * self.damage(attacker, defender))
        if dam > 0:
            logs.append(f"+ {attacker.name}의 {self.name}!")
            logs.append(f"- {defender.name}는(은) {dam}의 피해를 입었다!")

        # 아무런 효과도 없었을 시
        if logs == []:
            logs = ["= 하지만 아무 일도 일어나지 않았다..."]

        # 방어자의 체력이 0이면
        if defender.hp == 0:
            logs.append(f"- {defender.name}는(은) 쓰러졌다...")
        return logs


class NotExistSkill(Exception):
    def __init__(self):
        super().__init__('존재하지 않는 기술입니다.')
