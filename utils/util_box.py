import asyncio
import random


async def ox(bot, message, ctx):
    result = await wait_reaction(bot, message, ['🅾️', '❎'], 10, ctx)
    if not result or result.emoji == '❎':
        await message.clear_reactions()
        return False
    else:
        await message.clear_reactions()
        return True


async def wait_reaction(bot, window, canpress, timeout, ctx, event='reaction_add', add_react=True):
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


async def wait_saying(bot, timeout, ctx, keyword='', user=None):
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
