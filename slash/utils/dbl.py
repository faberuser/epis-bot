import discord, dbl, json

from config import config

class Vote:
    def __init__(self, client):
        dbl_token = config.DBL_TOKEN
        self.vote_url = config.DBL_VOTE
        self.check = None
        if dbl_token == "":
            self.check = False
            print('Discord Bot List Token has been passed. Vote-checking has been disabled.')
        else:
            self.dblclient = dbl.DBLClient(client, dbl_token, autopost=True)
            self.check = True

    async def vote(self, context): # vote
        if self.check == False:
            return True
        else:
            pass
        check = await self.dblclient.get_user_vote(context.author.id)
        if check == True:
            return True
        elif check == False:
            embed = discord.Embed(
                title=f"Vote for me to use this command.",
                url=self.vote_url,
                description="If the command doesn't work after vote, please try again in a few minutes because of the API delay.",
                colour=config.embed_color,
            )
            await context.send(embed=embed)
            return False
        else:
            return True
