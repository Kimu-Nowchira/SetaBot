'''
    <sample.py>
    여러분들의 기능을 여기에 마음껏 추가해 봐요!
'''

# 필수 임포트
from discord.ext import commands
import os
from utils import logger


class SampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 예시용 명령어(지워도 되요)
    @commands.command()
    async def 예시(self, ctx):
        await ctx.send('예시야!')


def setup(bot):
    logger.info(f'{os.path.abspath(__file__)} 로드 완료')
    bot.add_cog(SampleCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
