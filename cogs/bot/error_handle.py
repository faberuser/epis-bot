import discord, logging, json, asyncio
from discord.ext import commands

from ..utils import info_embed, paginator
from cogs.utils.blacklist import blacklist_check

from config import config

client = discord.Client()


class Error(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.info_embed_ = info_embed.Info_Embed()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument) or \
            isinstance(error, commands.errors.CommandInvokeError):
            pass

        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                "You don't have enough permission(s) to use this command. <:broken:652813264778166278>"
            )

        if isinstance(error, commands.errors.CommandOnCooldown):
            msg = await ctx.reply(f'{ctx.author.mention} {error}')
            await ctx.message.delete()
            await asyncio.sleep(2)
            await msg.delete()
        
        if isinstance(error, commands.CommandNotFound):
            with open('./data/commands', 'r') as f:
                cmds = f.readlines()
                for cmd_ in cmds:
                    cmd = cmd_.replace('\n', '')
                    if f'"{cmd}"' in str(error):
                        await ctx.reply(f'The `{cmd}` command has temporarily disabled.')
                    else:
                        pass

        if isinstance(error, commands.CheckFailure):
            return await ctx.send('You have been blacklisted from this command.')

        else:
            #await ctx.send(f'An unexpected error has been occured.\n`{str(error)}`')
            print("ERROR | " + str(error) + " | Content: '" +
                  str(ctx.message.content) + "' | Server: " + str(ctx.guild) +
                  " | Owner: " + str(ctx.guild.owner) + " | User: " +
                  str(ctx.author))
            logging.info("ERROR | " + str(error) + " | Content: '" +
                         str(ctx.message.content) + "' | Server: " +
                         str(ctx.guild) + " | Owner: " + str(ctx.guild.owner) +
                         " | User: " + str(ctx.author))
            pass

    @commands.command(aliases=['report']) # feedback command
    @commands.check(blacklist_check)
    async def feedback(self, ctx, *, text:str=None):
        if text is None:
            embed = self.info_embed_.info_embed('Feedback')
            await ctx.reply(embed=embed)
        else:
            with open('./data/feedback.json', 'r') as f:
                fb = json.load(f)
                for cases in fb:
                    case = int(cases) + 1
            if '"' in text:
                text.replace('"', "'")
            fb[str(case)] = {
                "user_id": f"{ctx.author.id}",
                "description": f"{text}",
                "response": None
            }
            with open('./data/feedback.json', 'w') as e:
                json.dump(fb, e, indent=4)
            embed = discord.Embed(
                title='Case #' + str(case) + ' | @' + str(ctx.author.id),
                description=text,
                colour=config.embed_color,
            )
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            owners = []
            try:
                members = (await self.client.application_info()).team.members
                for member in members:
                    owner = await self.client.fetch_user(int(member.id))
                    owners.append(owner)
            except:
                owner = (await self.client.application_info()).owner
                owners.append(owner)
            try:
                await ctx.author.send('Added to Case #' + str(case))
                for owner in owners:
                    await owner.send(embed=embed)
            except discord.Forbidden:
                await ctx.reply("I can't send message to you. Did you turn `Allow direct messages from server members.` on?")
                del_()
            except Exception as e:
                owners_ = ''
                for owner in owners:
                    owners_ += f"`{owner.name}#{owner.discriminator}` "
                await ctx.reply(f"An unexpected Exception occured. If this message keeps appearing, pleases try to DM to {owners_}.\n```{e}```")
                del_()

        def del_():
            fb.pop(str(case), None)
            with open('./data/feedback.json', 'w') as e:
                json.dump(fb, e, indent=4)

    @commands.command(aliases=['response']) # reply feedback
    @commands.is_owner()
    async def reply(self, ctx, id:int=None, send:bool=None, *, msg:str=None):
        if id is None or msg is None or send is None:
            embed = discord.Embed(
                title='Reply Command (Bot owner)',
                description=f'Syntax:\n`reply <user_id/case> <send:True/False> <message>`\nReply to a feedback/report.',
                colour=config.embed_color,
            )
            await ctx.reply(embed=embed)
        else:
            with open('./data/feedback.json') as f:
                fb = json.load(f)
            for cases in fb:
                if int(cases) == id:
                    embed = discord.Embed(
                        title='Case #' + str(cases),
                        description='Description: '+fb[str(cases)]['description']+'\nResponse: '+msg,
                        colour=config.embed_color,
                    )
                    fb[str(cases)]['response'] = msg
                    with open('./data/feedback.json', 'w') as e:
                        json.dump(fb, e, indent=4)
                    if send is True:
                        usr = await self.client.fetch_user(int(fb[str(cases)]['user_id']))
                        try:
                            await usr.send(embed=embed)
                        except Exception as e:
                            await ctx.reply(f"Can't send message to `@{fb[str(cases)]['user_id']}`.\n```{e}```")
                        await ctx.reply('Sent response in Case #' + str(cases))
                    else:
                        pass
                    await ctx.reply('Added response to Case #' + str(cases))
                    break

    @commands.command(aliases=['case']) # all cases/feedback
    @commands.is_owner()
    async def cases(self, ctx, arg:str=None):
        if arg == 'all':
            with open('./data/feedback.json') as f:
                fb = json.load(f)
            cases_ = []
            for cases in fb:
                cases_.append(f"**Case #{cases}**\nUser: {fb[cases]['user_id']}\nDescription: {fb[cases]['description']}\nResponse: {fb[cases]['response']}")
            count = 1
            embeds = []
            for case in cases_:
                embed = discord.Embed(
                    title=f'All feedback/report cases (Page {count})',
                    description=case,
                    colour=config.embed_color,
                )
                embed.set_footer(text=f'Page {count}/{len(cases_)}')
                embeds.append(embed)
                count+=1
            await paginator.Paginator(self.client).pag(ctx, embeds)

        elif arg == 'not':
            with open('./data/feedback.json') as f:
                fb = json.load(f)
            cases_ = []
            for cases in fb:
                if fb[cases]['response'] == None:
                    cases_.append(f"**Case #{cases}**\nUser: {fb[cases]['user_id']}\nDescription: {fb[cases]['description']}")
            count = 1
            embeds = []
            for case in cases_:
                embed = discord.Embed(
                    title=f"All feedback/report cases haven't been replied (Page {count})",
                    description=case,
                    colour=config.embed_color,
                )
                embed.set_footer(text=f'Page {count}/{len(cases_)}')
                embeds.append(embed)
                count+=1
            await paginator.Paginator(self.client).pag(ctx, embeds)

        else:
            embed = discord.Embed(
                title='Cases Command (Bot owner)',
                description=f'Syntax:\n`cases <all/not>`\nShows a table of all/not reply cases.',
                colour=config.embed_color,
                )
            await ctx.reply(embed=embed)


def setup(client):
    client.add_cog(Error(client))