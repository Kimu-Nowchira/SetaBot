'''
    <sample.py>
    여러분들의 기능을 여기에 마음껏 추가해 봐요!
'''

import asyncio
import random
import os
import re

from discord.ext import commands
import discord
import youtube_dl

from classes.user import User
from classes.game import Game
from utils.util_box import bar
from utils import logger
from utils import seta_json
from utils.theta_sql import SetaSQL


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn',
    'executable': 'static/ffmpeg.exe'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


db = SetaSQL('db/db.db', 'music')


class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clear_sound = self.sound('static/clear.mp3')
        self.fail_sound = self.sound('static/fail.mp3')

    def sound(self, source: str, **OPTION):
        return discord.FFmpegPCMAudio(
            source,
            executable='static/ffmpeg.exe',
            **OPTION
        )

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
    async def 시작(self, ctx, *args):
        option = ' ' + ' '.join(args) + ' '

        _OPTION = {}
        OPTION = {
            'round': 10,
            'distribution': 'game',
            'in_playlist': True,
            'popularity': False
        }
        opt = re.findall(r'([^ :]+):([^ :]+) ', option)
        for i in opt:
            _OPTION[i[0]] = i[1]

        if '라운드' in _OPTION.keys():
            if str(_OPTION['라운드']).isdigit():
                OPTION['round'] = int(_OPTION['라운드'])
                if OPTION['round'] < 1 or OPTION['round'] > 30:
                    return await ctx.send('설정이 조금 이상해오...')
            else:
                return await ctx.send('잘못된 라운드 옵션 설정이에요...')

        if '확률' in _OPTION.keys():
            D_EXP = {'유저당': 'user', '게임당': 'game', '음악당': 'music'}
            if _OPTION['확률당'] in D_EXP.keys():
                OPTION['distribution'] = D_EXP[_OPTION['확률당']]
                return await ctx.send('잘못된 확률 설정이에요... (유저당, 게임당, 음악당)')

        if '유명곡' in option:
            OPTION['popularity'] = True

        await ctx.send(OPTION)

        # 시작 조건 확인
        if ctx.author.voice is None:
            return await ctx.send(
                '게임 음악 퀴즈를 하려면 음성 채널에 있어야 해!'
                '\n`❗ 게임 음악 퀴즈를 하려면 음성 채널에 들어간 후 이 명령어를 사용해 주세요.`'
            )
        try:
            vchannel = ctx.author.voice.channel
            voice = await vchannel.connect()
        except discord.errors.ClientException:
            return await ctx.send(
                "이미 진행 중인 거 같아! 아니라면 '람다야 중지' 명령어를 써 줘!"
                '\n`❗ 람다가 이미 통화방에 들어 있습니다.`'
            )

        GAME_RULE = {
            'RANDOM_PER_USER': False,
            'TIME': 45
        }

        if '모든범위' in opt:
            OPTION['in_playlist'] = False
            await ctx.send("그럼 시작하자아")

        else:
            # 참여자 모집
            msg = await ctx.send(
                '**게임 음악 퀴즈 할 사람 여기여기 붙어 봐!**'
                '\n`❗ 붙지 않아도 참여할 수 있지만, 자신의 게임 목록이 퀴즈 범위에 반영되지 않습니다.`'
            )

            score = {}

            userlist, _gamelist = await self.moyeora(msg, ctx)
            await msg.edit(content=f'그럼 게임을 시작해볼게!')

            __gamelist = [Game(i) for i in _gamelist]
            gamelist = []

            for i in __gamelist:
                if i.soundtrack:
                    gamelist.append(i)

            if not gamelist:
                return await ctx.send(
                    "마이리스트가 비어 있습니다! `람다야 추가` 명령어로 게임을 추가해 주세요!"
                    '\n`❗ 출제할 게임이 없습니다.`'
                )

        # 본 게임 파트
        count = 0
        while count < OPTION['round']:
            count += 1

            # 유저 당 확률 게임 룰일 경우
            if OPTION['distribution'] == 'user':
                gamelist = random.choice(userlist).gamelist_class

            game = random.choice(gamelist)
            soundtrack = game.soundtrack

            if OPTION['popularity']:
                if len(soundtrack) >= 3:
                    music = random.choice(soundtrack[0:2])
                else:
                    music = random.choice(soundtrack[0:len(soundtrack)-1])
            else:
                music = random.choice(game.soundtrack)
            url = str(music['url']).split('&list')[0]

            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop)

            await ctx.send(f"> 🎶 { OPTION['round']}문제 중 **{count}번째 문제**")
            ctx.voice_client.play(player, after=lambda e: print(
                'Player error: %s' % e) if e else None)

            embed = discord.Embed(
                title=f"🎮 {game.name}",
                description=f"🎵  [{music['title']}]({url})",
                colour=0xFFE400
            )
            if music['view_count']:
                embed.set_footer(text=f"트랙 조회수 : { music['view_count' ]:,}")

            try:
                msg = await self.dabmapchugi(game, rule=GAME_RULE)

                winner = User(msg.author)
                if msg.author.id not in score.keys():
                    score[msg.author.id] = 0

                score[msg.author.id] += 1
                voice.stop()
                voice.play(self.clear_sound)
                await ctx.send(f'{msg.author.mention}님께서 정답을 맞추셨어요!\n{url}', embed=embed, reference=msg)

            except asyncio.TimeoutError:
                voice.stop()
                voice.play(self.fail_sound)
                await ctx.send(f'아쉽게도 시간초과... <:kemo_cry:869090254315991080>\n{url}', embed=embed)
        await voice.disconnect()
        await ctx.send(f"{OPTION['round']}곡이 모두 끝났어요! ```{score}```")

    async def dabmapchugi(self, game: Game, rule: dict):
        def check(m):
            if m.content.replace(' ', '').lower() in game.names(no_space=True):
                return True
            else:
                return False

        msg = await self.bot.wait_for('message', timeout=rule['TIME'], check=check)
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


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    # Placeholder
    @classmethod
    async def search(cls, search, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def setup(bot):
    logger.info(f'{os.path.abspath(__file__)} 로드 완료')
    bot.add_cog(GameCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!


'''
ydl_opts = {
    # 'format': 'bestaudio'
    'format': 'worstaudio'
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    try:
        info = ydl.extract_info(url, download=False)
        # seta_json.set_json(f'static/info_{url[-10:]}.json', info)
    except youtube_dl.utils.ExtractorError as e:
        await ctx.send(f'잘못된 영상입니다아ㅏㅏ (이 곡은 패스됩니다)\n{url}\n{e}')
        continue
    except youtube_dl.utils.DownloadError as e:
        await ctx.send(f'잘못된 영상입니다아ㅏㅏㅏㅏㅏㅏㅏㅏ (이 곡은 패스됩니다)\n{url}\n{e}')
        continue

    URL = info['formats'][0]['url']
await asyncio.sleep(1)
voice.stop()
duration = int(info['duration'])

db.update(view_count=info['view_count'],
            title=info['title'], where=f"url='{music['url']}'")
ok_duration = duration - GAME_RULE['TIME']
ok_duration = 0 if ok_duration < 0 else ok_duration
start_point = random.randint(0, ok_duration)
OPTION = {
    'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {start_point}',
    "options": '-vn'
}
OPTION2 = {
    'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    "options": '-vn'
}

def replay(error=None):
    try:
        voice.play(self.sound(URL, **OPTION2), after=replay)
    except discord.errors.ClientException:
        pass
if start_point < 10:
    replay()
else:
    voice.play(self.sound(URL, **OPTION), after=replay)
'''
