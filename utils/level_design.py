'''
    <level_design.py>
    게임 봇을 만드시는 분들을 위한 간단한 레벨 디자인을 제공해요.

    ※ 파이썬 초심자라면 이 파일을 수정하지 않는 것을 추천드려요!
    - 키뮤 제작(0127 버전)
'''
# 기본 레벨 디자인
# n 레벨에서 n+1 레벨이 되기 위해 필요한 경험치 = 10n
# n 레벨이 되기 위해 필요한 총 경험치 5n^2+5n


def exp_to_level(exp: int):
    '''누적 경험치값을 레벨로 전환시켜줍니다. 음수 경험치는 레벨 0으로 처리됩니다.'''
    if exp < 0:
        return 0
    return int(((exp/5)+(1/4))**0.5 + 0.5)


def level_to_atk(level: int):
    '''레벨 -> 공격력'''
    return int(10*(level**1/2))


def level_to_def(level: int):
    '''레벨 -> 방어력'''
    return int(10*(level**1/2))


def level_to_maxhp(level: int):
    '''레벨 -> 최대 HP'''
    return int(25*(level**1/2))


def level_to_maxmp(level: int):
    '''레벨 -> 최대 MP'''
    return int(20*(level**1/2))


def exp_to_atk(exp: int):
    return level_to_atk(exp_to_level(exp))


def exp_to_def(exp: int):
    return level_to_def(exp_to_level(exp))


def exp_to_maxhp(exp: int):
    return level_to_maxhp(exp_to_level(exp))


def exp_to_maxmp(exp: int):
    return level_to_maxmp(exp_to_level(exp))
