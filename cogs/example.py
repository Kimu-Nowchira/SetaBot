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
from config import Config
from utils import util_box


class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 멘션을 하고 이름을 부르며 반갑게 인사해 주는 예시 명령어야!
    @commands.command()
    async def 안녕(self, ctx, *args):
        await ctx.send(f'안녕 {ctx.author.name}!')

    # 답장해 주는 예시 명령어야(최신 discord.py가 설치되어 있어야 해)
    @commands.command()
    async def 답장(self, ctx, *args):
        await ctx.send(content=f'자 답장이야!', reference=ctx.message)

    # '!칭찬 키뮤' 이런 식으로 쓰는 예시 명령어야
    @commands.command()
    async def 칭찬(self, ctx, arg1=None, *args):
        if arg1 is None:
            await ctx.send('뭘 칭찬해야 해?')
            return None

        await ctx.send(f'`{arg1}`을(를) 칭찬할게!')

    # '!발사 우주 로켓' 이런 식으로 쓰는 예시 명령어야
    @commands.command()
    async def 발사(self, ctx, arg1=None, arg2=None, *args):
        if arg1 is None or arg2 is None:
            await ctx.send('뭘 누구한테 발사해야 해?')
            return None

        await ctx.send(f'`{arg1}`에 `{arg2}`를 발사! 퍼퍼벙')

    # 따라말하는 예시 명령어야
    @commands.command()
    async def 말해(self, ctx, *args):
        content = ' '.join(args)  # content에 접두어와 명령어를 제외한 내용이 담김(args는 tuple)
        if args == ():  # 그냥 '!말해' 만 말했다면
            await ctx.send('뭘 말해요?')  # ctx.send('내용')은 봇이 말하는 함수
            return None  # 끝내기

        await ctx.message.delete()  # 유저가 쓴 메시지는 지웁니다.
        await ctx.send(content)

    # 1번 사용하면 5초의 쿨타임이 생기는 예시 명령어
    @commands.cooldown(1, 5)
    @commands.command()
    async def 쿨타임(self, ctx, *args):
        await ctx.send(f'와아아아아아아')

    # 핑 하면 퐁 하면서 봇의 레이턴시(지연 시간)을 알려 주는 예시 명령어야!
    @commands.command()
    async def 핑(self, ctx, *args):
        await ctx.send(f'퐁! 🏓\n`지연 시간 : {int(self.bot.latency * 1000)}ms`')

    # OX 반응 선택을 하는 예시 명령어
    @commands.command()
    async def 탕수육(self, ctx):
        window = await ctx.send('찍먹 좋아해?')
        result = await util_box.ox(self.bot, window, ctx)

        if result == 0:  # X를 눌렀을 때
            await ctx.send('그렇구나아...')
        elif result == 1:  # O를 눌렀을 때
            await ctx.send('와아 나도 좋아해')
        else:  # 그 외(시간 초과)
            await ctx.send('대답 안 해 주는 거야...?')

    # 유저의 프로필을 간단하게 embed로 보여주는 예시 명령어야
    @commands.command()
    async def 프로필(self, ctx, *args):
        embed = discord.Embed(title='여러 가지 잡다한 것들', description=f'많이 알려줄게', colour=0x1DDB16)
        embed.add_field(name='네 이름', value=ctx.author.name, inline=True)
        embed.add_field(name='네 디스코드 ID', value=ctx.author.id, inline=True)
        embed.add_field(name='여기 채널 이름', value=ctx.channel.name, inline=True)
        embed.add_field(name='여기 채널 ID', value=ctx.channel.id, inline=True)
        embed.set_footer(text="아래에 뜨는 조그마한 메시지야")
        await ctx.send(embed=embed)


def setup(bot):
    logger.info(f'{os.path.abspath(__file__)} 로드 완료')
    bot.add_cog(ExampleCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
