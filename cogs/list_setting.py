'''
    <sample.py>
    여러분들의 기능을 여기에 마음껏 추가해 봐요!
'''

# 필수 임포트
from discord.ext import commands
import os
from utils import logger, get_youtube_urls
from utils.util_box import ox, wait_for_saying
from utils.theta_sql import SetaSQL
from classes.user import User, AlreadyAppendedGame
from classes.game import Game, NotExistGame, search_game


db = SetaSQL('db/db.db')


class ListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def 마이리스트(self, ctx):
        user = User(ctx.author)
        gl = user.gamelist_class

        st = ''
        for i in gl:
            st += f'[{i.id}] 🎮 {i.name} ( 🎶 {len(i.soundtrack)} )\n'
            if i.nickname:
                st += f"// {', '.join(i.nickname)}\n"
        await ctx.send(f"> **현재 들어 있는 게임 목록**\n```cs\n{st}```", reference=ctx.message)

    @commands.command()
    async def 줄임말(self, ctx, *args):
        name = ' '.join(args)
        if not name:
            return await ctx.send(
                '`람다야 제외 <게임명>`'
            )
        game = search_game(name)

        sn = ', '.join(game.nickname)
        await ctx.send(f"`{game.name}`의 별명을 말해줘! (취소라 말하면 취소됨)```현재 별명 : {sn}```", reference=ctx.message)
        while True:
            res = await wait_for_saying(self.bot, 30, ctx, user=ctx.author)
            if not res:
                break
            if res.content == '취소':
                return await ctx.send('취소오오와아아')
            else:
                msg = await ctx.send(f'`{res.content}`를 별명으로 등록할 거야?', reference=res)
                if not await ox(self.bot, msg, ctx):
                    return await msg.edit(content='> 등록 취소!')
                break

        game.add_nickname(res.content)
        await ctx.send(f'등록해써  >ㅅ<')

    @commands.command()
    async def 제외(self, ctx, *args):
        name = ' '.join(args)
        if not name:
            return await ctx.send(
                '`람다야 제외 <게임명>`'
            )
        user = User(ctx.author)
        try:
            game = search_game(name)
        except NotExistGame:
            return await ctx.send("으음 그런 게임이 있던가아?")

        if game.id not in user.gamelist:
            return await ctx.send(f"{game.name} 게임은 네 리스트에 없는 거 가타!")

        gl = user.gamelist
        gl.remove(game.id)
        user.gamelist = gl
        await ctx.send(f'`{game.name}` 게임을 리스트에서 제외했어!', reference=ctx.message)

    @commands.command()
    async def 음악추가(self, ctx, *args):
        name = ' '.join(args)
        if not name:
            return await ctx.send(
                '`람다야 음악추가 <게임명>`'
            )

        game = search_game(name)
        await ctx.send(f"`{game.name}`에 넣을 유튜브 영상이나 재생목록의 링크를 적어 줘!", reference=ctx.message)
        urls = []
        while True:
            res = await wait_for_saying(self.bot, 30, ctx, user=ctx.author)
            if not res:
                break
            if res.content == '취소':
                return await ctx.send('취소오오와아아')
            elif res.content == '완료':
                break
            else:
                try:
                    urls += get_youtube_urls.gets(res.content)
                    break
                except Exception as e:
                    await ctx.send(f'으음 다시 확인해봐```{e}```')

        await ctx.send(f'`{game.name}` 게임에 음악 {len(urls)}개를 등록 중...')
        for i in urls:
            songdata = {
                'game': game.id,
                'url': i,
                'famous': 0
            }
            db.insert('music', commit=False, **songdata)
        db.commit()
        await ctx.send(f'와아 다해따 >ㅅ<')

    @commands.command()
    async def 음악여러개추가(self, ctx, *args):
        name = ' '.join(args)

        game = Game(name)
        await ctx.send(f"`{game.name}`에 넣을 유튜브 영상이나 재생목록의 링크를 적어 줘!\n(취소하려면 '취소', 다 넣었으면 '완료'라고 말해바)")
        urls = []
        while True:
            res = await wait_for_saying(self.bot, 30, ctx, user=ctx.author)
            if not res:
                break
            if res.content == '취소':
                return await ctx.send('취소오오와아아')
            elif res.content == '완료':
                break
            else:
                try:
                    urls += get_youtube_urls.gets(res.content)
                except Exception as e:
                    await ctx.send(f'으음 다시 확인해봐```{e}```')

        await ctx.send(f'`{name}` 게임에 음악 {len(urls)}개를 등록 중...')
        for i in urls:
            songdata = {
                'game': game.id,
                'url': i,
                'famous': 0
            }
            db.insert('music', commit=False, **songdata)
        db.commit()
        await ctx.send(f'와아 다해따 >ㅅ<')

    @commands.command()
    async def 추가(self, ctx, *args):
        name = ' '.join(args)
        if not name:
            return await ctx.send(
                '`람다야 추가 <게임명>`'
            )
        user = User(ctx.author)

        try:
            game = search_game(name)
            user.append_gamelist_obj(game)
            msg = await ctx.send(f'`{game.name}` 게임을 네 리스트에 넣었어!', reference=ctx.message)
        except NotExistGame:
            msg = await ctx.send(f'`{name}` 게임을 등록할 거야? (처음 등록되는 게임)', reference=ctx.message)
            if not await ox(self.bot, msg, ctx):
                return await msg.edit(content='> 등록 취소!')

            data = {
                'name': name,
                'nickname': [],
                'tags': []
            }

            db.insert('game', **data)
            game_id = db.select(
                'game', rec=['id'], where=f"name=\"{name}\"")[0]['id']
            user.append_gamelist(game_id)

            await ctx.send(f'`{name}` 게임을 추가하고 네 리스트에 등록했어!')
        except AlreadyAppendedGame:
            await ctx.send(f'`{name}` 게임은 이미 네 리스트에 있어...')


def setup(bot):
    logger.info(f'{os.path.abspath(__file__)} 로드 완료')
    bot.add_cog(ListCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
