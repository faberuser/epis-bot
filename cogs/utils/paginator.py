import asyncio


class Paginator:
    def __init__(self, client):
        self.client = client

        self.left = "\u25c0"
        self.right = "\u25b6"

    async def pag(self, message, embeds): # embeds paginator
        index = 0
        msg = None
        action = message.reply
        while True:
            res = await action(embed=embeds[index])
            if res is not None:
                msg = res
            l = index != 0
            r = index != len(embeds) - 1
            if l:
                await msg.add_reaction(self.left)
            if r:
                await msg.add_reaction(self.right)
            try:
                react, user = await self.client.wait_for(
                    "reaction_add",
                    check=self.predicate(msg, message, l, r),
                    timeout=60.0,
                )
            except asyncio.TimeoutError:
                await msg.edit(content="Timeout! Please try again.")
                try:
                    await msg.clear_reactions()
                except:
                    pass
                break

            if str(react.emoji) in self.left:
                index -= 1
                try:
                    await msg.remove_reaction(self.left, message.author)
                except:
                    pass
            elif str(react.emoji) in self.right:
                index += 1
                try:
                    await msg.remove_reaction(self.right, message.author)
                except:
                    pass
            action = msg.edit

    def predicate(self, message, msg, l, r):
        def check(reaction, user):
            if (
                reaction.message.id != message.id
                or user != msg.author
                or user == self.client.user
            ):
                return False
            if l and str(reaction.emoji) in self.left:
                return True
            if r and str(reaction.emoji) in self.right:
                return True
            return False

        return check
