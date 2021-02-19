'''
    <sample.py>
    여러분들의 기능을 여기에 마음껏 추가해 봐요!
'''

import asyncio
import os

from discord.ext import commands
import discord

from classes.user import User
from utils.util_box import bar
from utils import logger


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def 스탯(self, ctx):
        player = User(ctx.author)
        embed = discord.Embed(
            title=f'{player.name}',
            colour=0x980000)
        embed.add_field(
            name=f'**HP** ( {player.hp} / {player.max_hp} )',
            value=bar(player.hp, player.max_hp))
        embed.add_field(
            name=f'**MP** ( {player.mp} / {player.max_mp} )',
            value=bar(player.mp, player.max_mp))
        embed.add_field(
            name='**━━━━━━━━━━━━━━━━━━━━━**',
            value=f'**Lv. {player.level} ( {player.exp} exp )**',
            inline=False)
        embed.add_field(
            name='**보유 금액**',
            value=f'💰 {player.money:,}')
        embed.add_field(
            name='**공격력**',
            value=f'⚔️ {player.attack}')
        embed.add_field(
            name='**방어력**',
            value=f'🛡️ {player.defend}')
        await ctx.send(embed=embed)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def 공격(self, ctx, arg='NONE'):
        """ '!공격 @멘션'처럼 사용하여 다른 유저를 공격하는 명령어 예시예요! """

        # 멘션을 ID로 변환
        defender_id = arg.replace('<@', '').replace('>', '').replace('!', '')
        if not defender_id.isdigit():
            return await ctx.send(f"공격 대상을 알 수 없습니다 : `{defender_id}`")

        defender = User(int(defender_id))
        attacker = User(ctx.author)

        # 유저의 체력이 이미 없는 경우
        if attacker.hp == 0:
            return await ctx.send("쓰러진 상태에서는 공격할 수 없어...")

        # 이미 공격 대상의 체력이 0이면
        if defender.hp == 0:
            return await ctx.send("이미 쓰러진 사람을 공격하는 건 매너 위반이야...")

        logs = attacker.attack_to(defender)

        logdata = logs[0]
        window = await ctx.send(f"```diff\n{logdata}```", reference=ctx.message)
        for i in logs[1:]:
            logdata += '\n' + i
            await asyncio.sleep(1.5)
            await window.edit(content=f"```diff\n{logdata}```")

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def 회복(self, ctx):
        player = User(ctx.author)
        player.hp = player.max_hp
        await ctx.send("회복했어!", reference=ctx.message)


def setup(bot):
    logger.info(f'{os.path.abspath(__file__)} 로드 완료')
    bot.add_cog(Game(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
