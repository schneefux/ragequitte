#!/usr/bin/python3

import logging
import asyncio

import discord
import redis

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = discord.Client()
r = redis.StrictRedis(**{ **config.redis, "decode_responses": True })

"""
Save a message to redis and store statistics.
@return True if the message belongs to a channel without known history.
"""
def store_message(message):
    if message.author.bot:
        return False

    r.set("message:{}".format(message.id), message.content)
    r.incr("stats:{}:{}:{}".format(message.server.id, message.channel.id, message.author.id))
    return r.incr("stats:{}:{}".format(message.server.id, message.channel.id)) == 1


@client.event
async def on_message(message):
    logging.info("{}#{}@{}: {}".format(message.server.name, message.channel.name, message.author.name, message.clean_content))

    fetch_history = store_message(message)
    if fetch_history:
        logging.info("+++ fetching channel history +++")
        try:
            async for logmsg in client.logs_from(message.channel, before=message, limit=100000):
                store_message(logmsg)
        except Exception as e:
            pass  # forbidden, TODO use proper error code

    r.publish("discord_to_redis", "")  # notify of new content


client.run(*config.discord, bot=False)
