'''
    <event.py>
    이벤트 예시들이 모여있어요. 마음껏 수정해 보세요!
'''

# 필수 임포트
from discord.ext import commands
import discord
import os
from utils import logger


class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 접두사에 관계없이 누군가가 메시지를 올렸을 때 여기가 실행될 거야
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:  # 봇이 말한 건 무시
            return None

        logger.msg(message)  # 메시지를 기록

        if message.content == '세타봇 바보':  # 만약 누가 '세타봇 바보'라고 말하면
            await message.channel.send('바보 아니야')  # 바보 아니라고 답변

    # 오류 발생 시 여기가 실행될 거야
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            raise error
        except discord.errors.Forbidden:  # 권한 부족 오류
            try:
                await ctx.send('어어... 권한이 없네?')
            except discord.errors.Forbidden:  # 여기는 봇이 볼 수는 있지만 메시지를 쓸 수 조차 없는 경우야
                logger.warn('채팅 쓰기 권한 부족 오류 발생')

        except commands.errors.CommandNotFound:  # 해당하는 명령어가 없는 경우
            await ctx.send('그런 명령어는 없어!')

        else:
            await ctx.send(f'으앙 오류가 발생했어...\n`{str(error)}`')
            logger.err(error)


def setup(bot):
    logger.info(f'{os.path.abspath(__file__)} 로드 완료')
    bot.add_cog(EventCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
