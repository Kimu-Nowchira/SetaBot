'''
    <util_box.py>
    자잘하지만 있으면 편한 함수들이 많이 있답니다.
    제가 쓰던 거 그대로여서 지저분해요. 나중에 정리해서 업데이트할게요.
    ※ 봇 개발 초심자라면 이 파일을 수정하지 않는 것을 추천드려요!
    - 키뮤 제작(0127 버전)
'''

import asyncio
import random
import math


def bar(value: int, full: int, block: int = 10, theme: dict = {'fill': '■', 'empty': '□'}):
    bar_str = ''
    bar_str += theme['fill'] * math.ceil(value / full * block)
    bar_str += theme['empty'] * (block - len(bar_str))
    return bar_str


async def ox(bot, message, ctx):
    '''
    🅾️❎ 이모지 선택지를 만들어 줘요!
    ❎를 누르면 False를 반환하고(0)
    🅾️를 누르면 True를 반환해요(1)
    만약 시간이 초과되면 2를 반환해요(False)
    '''
    result = await wait_for_reaction(bot, message, ['🅾️', '❎'], 10, ctx)
    if not result:
        await message.clear_reactions()
        return 2
    elif result.emoji == '❎':
        await message.clear_reactions()
        return False
    else:
        await message.clear_reactions()
        return True


async def wait_for_reaction(bot, window, canpress, timeout, ctx, event='reaction_add', add_react=True):
    '''지정한 이모지가 눌릴 때까지 기다린 후 눌림 여부에 따라 Bool 방식 반환
    - 시간 초과는 False 반환'''
    if add_react:
        for i in list(canpress):
            await window.add_reaction(i)

    def check(reaction, user):
        if user == ctx.author and str(reaction.emoji) in canpress and reaction.message.id == window.id:
            return True
        else:
            return False

    try:
        reaction = await bot.wait_for(event, timeout=timeout, check=check)

    except asyncio.TimeoutError:
        return False

    else:
        return reaction[0]


async def wait_for_saying(bot, timeout, ctx, keyword='', user=None):
    if user is None:
        for_user = ctx.author
    else:
        for_user = user

    def check(m):
        if m.author == for_user and keyword in m.content:
            return True
        else:
            return False

    try:
        msg = await bot.wait_for('message', timeout=timeout, check=check)

    except asyncio.TimeoutError:
        return False

    else:
        return msg


def rdpc(percentage):
    '''RanDom PerCents
    퍼센트를 넣으면 그 확률로 Bool 뱉음'''
    F = random.randrange(1, 101)
    if F <= percentage:
        return True
    else:
        return False
