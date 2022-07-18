from config import config

async def embed_file(client, embed, file): # send file via embed
    msg = await client.get_channel(config.cache_channel).send(file=file, embed=embed)
    return msg.embeds[0]