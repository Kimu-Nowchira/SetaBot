'''
    <example.py>
    여러 예시들이 있어요! 이해가 됐다면 마음껏 수정해봐요!
    - 키뮤 제작(0127 버전)
'''

# 필수 임포트
from discord.ext import commands
import discord
import os
from utils import logger

# 부가 임포트
from utils import util_box


class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def 테스트(self, ctx):
        window = await ctx.send('테스트!')
        await util_box.ox(self.bot, window, ctx)


def setup(bot):
    logger.info(f'{os.path.abspath(__file__)} 로드 완료')
    bot.add_cog(ExampleCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
