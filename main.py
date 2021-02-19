'''
    <main.py>
    디스코드 봇의 메인이 되는 파일입니다. 이 파일을 실행해야 디스코드 봇을 실행할 수 있어요!
    ※ 봇 개발 초심자라면 이 파일을 수정하지 않는 것을 추천드려요!
    - 키뮤 제작(0127 버전)
'''

import datetime
import os

from discord.ext import commands
import discord

from classes.user import User
from config import Config
from utils import logger


class SetaBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=Config.prefixes,  # 접두사는 config.py에서 설정
            help_command=None
        )

        # Cogs 로드(Cogs 폴더 안에 있는 것이라면 자동으로 인식합니다)
        cog_list = [i[:-3] for i in os.listdir('cogs') if i.endswith('.py') and i != '__init__.py']
        self.add_cog(AdminCog(self))  # 기본 제공 명령어 Cog
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


# 기본 제공 명령어
class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # cogs 폴더 안의 코드를 수정했다면 굳이 껐다 키지 않아도 다시시작 명령어로 적용이 가능해!
    @commands.command(name='')
    async def reload(self, ctx):
        if ctx.author.id not in Config.admin:
            return await ctx.send(
                '권한이 부족해!'
                '\n`❗ 봇 관리자라면 config.py의 admin 리스트에 자신의 디스코드 id가 있는지 확인해 봐!`')

        w = await ctx.send("```모듈을 다시 불러오는 중...```")
        cog_list = [i[:-3] for i in os.listdir('cogs') if i.endswith('.py') and i != '__init__.py']
        for i in cog_list:
            self.bot.reload_extension(f"cogs.{i}")
            logger.info(f"'{i}' 다시 불러옴")

        await w.edit(content="```cs\n'불러오기 성공'```")

    @commands.command()
    async def info(self, ctx):
        ''' 봇 프레임워크 정보를 볼 수 있는 명령어입니다. 명령어를 지우지 말아 주세요! '''
        embed = discord.Embed(
            title='정보',
            description='이 봇은 키뮤소프트의 세타봇 V2.2 프레임워크 기반으로 짜여진 프로젝트입니다.',
            colour=0x1DDB16)
        embed.add_field(
            name='키뮤의 과학실 서버 바로가기',
            value='🔗 https://discord.gg/XQuexpQ',
            inline=True)
        embed.set_footer(text="이 명령어를 지우지 말아 주세요!")
        await ctx.send(embed=embed)

    @commands.command()
    async def exec(self, ctx, *args):
        if ctx.author.id not in Config.admin:
            return await ctx.send(
                '권한이 부족해!'
                '\n`❗ 봇 관리자라면 config.py의 admin 리스트에 자신의 디스코드 id가 있는지 확인해 봐!`')

        text = ' '.join(args)
        me = User(ctx.author)
        logger.info(f'{me.name}이(가) exec 명령어 사용 : {text}')
        try:
            exec(text)
        except Exception as e:
            embed = discord.Embed(
                color=0x980000,
                timestamp=datetime.datetime.today())
            embed.add_field(
                name="🐣  **Cracked!**",
                value=f"```css\n[입구] {text}\n[오류] {e}```",
                inline=False)
            logger.err(e)
        else:
            embed = discord.Embed(
                color=0x00a495,
                timestamp=datetime.datetime.today())
            embed.add_field(
                name="🥚  **Exec**",
                value=f"```css\n[입구] {text}```",
                inline=False)
        embed.set_footer(
            text=f"{ctx.author.name} • exec",
            icon_url=str(ctx.author.avatar_url_as(static_format='png', size=128)))
        await ctx.send(embed=embed, reference=ctx.message)

    @commands.command()
    async def eval(self, ctx, *args):
        if ctx.author.id not in Config.admin:
            return await ctx.send(
                '권한이 부족해!'
                '\n`❗ 봇 관리자라면 config.py의 admin 리스트에 자신의 디스코드 id가 있는지 확인해 봐!`')

        text = ' '.join(args)
        me = User(ctx.author)
        logger.info(f'{me.name}이(가) eval 명령어 사용 : {text}')
        try:
            result = eval(text)
        except Exception as e:
            embed = discord.Embed(
                color=0x980000,
                timestamp=datetime.datetime.today())
            embed.add_field(
                name="🐣  **Cracked!**",
                value=f"```css\n[입구] {text}\n[오류] {e}```",
                inline=False)
            logger.err(e)
        else:
            embed = discord.Embed(
                color=0x00a495,
                timestamp=datetime.datetime.today())
            embed.add_field(
                name="🥚  **Eval**",
                value=f"```css\n[입구] {text}\n[출구] {result}```",
                inline=False)
        embed.set_footer(
            text=f"{ctx.author.name} • eval",
            icon_url=str(ctx.author.avatar_url_as(static_format='png', size=128)))
        await ctx.send(embed=embed, reference=ctx.message)


setabot = SetaBot()
setabot.run()
