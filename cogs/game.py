'''
    <sample.py>
    여러분들의 기능을 여기에 마음껏 추가해 봐요!
'''

import asyncio
import random
import os

from discord.ext import commands
import discord
import youtube_dl

from classes.user import User
from classes.game import Game
from utils.util_box import bar
from utils import logger


class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 접두사에 관계없이 누군가가 메시지를 올렸을 때 여기가 실행될 거야
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:  # 봇이 말한 건 무시
            return

        logger.msg(message)  # 메시지를 기록

    @commands.command()
    async def 중지(self, ctx):
        await self.bot.voice_clients[0].disconnect()
        await ctx.send(
            '호애액'
            '\n`❗ 호애애액`'
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def 시작(self, ctx, round=10):

        if round > 30:
            round = 30
        elif round < 5:
            round = 5

        round = int(round)
        score = {}

        # 시작 조건 확인
        if ctx.author.voice is None:
            return await ctx.send(
                '게임 음악 퀴즈를 하려면 음성 채널에 있어야 해!'
                '\n`❗ 게임 음악 퀴즈를 하려면 음성 채널에 들어간 후 이 명령어를 사용해 주세요.`'
            )
        try:
            vchannel = ctx.author.voice.channel
            await vchannel.connect()
        except discord.errors.ClientException:
            return await ctx.send(
                "이미 진행 중인 거 같아! 아니라면 '람다야 중지' 명령어를 써 줘!"
                '\n`❗ 람다가 이미 통화방에 들어 있습니다.`'
            )

        # 참여자 모집
        msg = await ctx.send(
            '**게임 음악 퀴즈 할 사람 여기여기 붙어 봐!**'
            '\n`❗ 붙지 않아도 참여할 수 있지만, 자신의 게임 목록이 퀴즈 범위에 반영되지 않습니다.`'
        )
        userlist, _gamelist = await self.moyeora(msg, ctx)
        await msg.edit(content=f'그럼 게임을 시작해볼게!')

        gamelist = [Game(i) for i in _gamelist]

        count = 0
        while count < round:
            count += 1
            game = random.choice(gamelist)
            logger.info(f'뽑힌 게임 : {game.name}')
            music = random.choice(game.soundtrack)
            url = str(music['url']).split('&list')[0]

            ydl_opts = {'format': 'bestaudio'}
            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
                'executable': 'ffmpeg.exe'
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                URL = info['formats'][0]['url']
            voice = self.bot.voice_clients[0]
            await ctx.send(f'> 🎶 **{count}/{round}**')
            voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))

            try:
                msg = await self.dabmapchugi(game)

                winner = User(msg.author)
                voice.stop()
                if msg.author.id not in score.keys():
                    score[msg.author.id] = 0

                score[msg.author.id] += 1
                await ctx.send(f'{msg.author.mention}님 정답!\n> 🎮 {game.name} ({url})')

            except asyncio.TimeoutError:
                voice.stop()
                await ctx.send(f'아쉽게도 시간초과... <:kemo_cry:869090254315991080>\n> 🎮 {game.name} ({url})')
        await self.bot.voice_clients[0].disconnect()
        await ctx.send(f'{round}곡이 모두 끝났어요! ```{score}```')

    async def dabmapchugi(self, game: Game):
        def check(m):
            if m.content.replace(' ', '').lower() in game.names(no_space=True):
                return True
            else:
                return False

        msg = await self.bot.wait_for('message', timeout=45, check=check)
        return msg

    async def moyeora(self, message, ctx):
        '''지정한 이모지가 눌릴 때까지 기다린 후 눌림 여부에 따라 Bool 방식 반환
        - 시간 초과는 False 반환'''
        await message.add_reaction('✋')

        owner = User(ctx.author)
        gml = owner.gamelist
        userlist = [owner]

        def check(reaction, user):
            if str(reaction.emoji) == '✋' and reaction.message.id == message.id and user.id not in [i.id for i in userlist] and user.id != self.bot.user.id:
                player = User(user)
                userlist.append(player)

                return True
            else:
                return False

        try:
            while True:
                await self.bot.wait_for('reaction_add', timeout=10, check=check)
                gml += userlist[-1].gamelist
                gml = list(set(gml))
                embed = discord.Embed(
                    title='참가자',
                    description=', '.join([i.name for i in userlist]),
                    colour=0xFFE400)
                embed.set_footer(text=f'출제 범위 게임 개수 : {len(gml)}')
                await message.edit(embed=embed)
        except asyncio.TimeoutError:
            return userlist, gml


def setup(bot):
    logger.info(f'{os.path.abspath(__file__)} 로드 완료')
    bot.add_cog(GameCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
