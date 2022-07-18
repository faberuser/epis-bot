import discord

def view_channels(guild, channel): # check for channel chat permissions
    if (guild.me.permissions_in(channel)).view_channel == False:
        return True
    else:
        return False