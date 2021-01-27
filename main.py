'''
    <main.py>
    디스코드 봇의 메인이 되는 파일입니다. 이 파일을 실행해야 디스코드 봇을 실행할 수 있어요!
    ※ 봇 개발 초심자라면 이 파일을 수정하지 않는 것을 추천드려요!
    - 키뮤 제작(0127 버전)
'''

from discord.ext import commands
import discord

from config import Config
from utils import logger
import re
import os


class SetaBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=Config.prefixes,  # 접두사는 config.py에서 설정
            help_command=None,
        )

        # Cogs 로드(Cogs 폴더 안에 있는 것이라면 자동으로 인식합니다)
        cog_list = [i.split('.')[0] for i in os.listdir('cogs') if '.py' in i]
        cog_list.remove('__init__')
        for i in cog_list:
            self.load_extension(f"cogs.{i}")

    async def on_ready(self):  # 봇이 구동되면 실행
        logger.info('======================')
        logger.info('< 구동 완료 >')
        logger.info(f'봇 이름 : {self.user.name}')
        logger.info(f'봇 아이디 : {self.user.id}')
        logger.info('======================')

        await self.change_presence(
            status=discord.Status.online,  # 상태 설정
            activity=discord.Game(name=Config.activity))  # 하고 있는 게임으로 표시되는 것 설정

    def run(self):
        super().run(Config().using_token(), reconnect=True)


setabot = SetaBot()
setabot.run()
