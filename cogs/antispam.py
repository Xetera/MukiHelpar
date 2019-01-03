import discord
from discord.ext import commands
import aiohttp
import json
import datetime
from datetime import timedelta

def config_load():
    with open('config/settings.json', 'r', encoding='utf-8-sig') as doc:
        return json.load(doc)

class AntiSpam:
    def __init__(self, bot):
        config = config_load()
        self.mute_role_id = config['mute_role']
        self.modlog_channel_id = config['modlog_channel']
        self.bot = bot

    async def detect(self, message):
        if message.channel.permissions_for(message.author).manage_roles:
            return
        counter = 0
        oldMessage = None
        async for m in self.bot.logs_from(message.channel, 6, before=message):
            if m.author.id == message.author.id:
                oldMessage = m
                counter += 1
        if counter > 4:
            timespan = float((datetime.datetime.utcnow()-oldMessage.timestamp)/timedelta(milliseconds=1))   
            #print(str(timespan) + "ms")
            avg = timespan / counter / 1000
            #print(avg)
            if avg < 0.85:
                muteMember = discord.utils.find(lambda m: m.id == message.author.id, message.server.members)
                muteRole = discord.utils.find(lambda r: r.id == self.mute_role_id, message.server.roles) 
                await self.bot.add_roles(muteMember, muteRole)
                await self.bot.send_message(message.channel, message.author.mention +', you are automatically muted for spamming messages. If you feel like this is an error, consult with a moderator in DMs. \n Leaving the server to get your mute removed will result in an automatic ban.')
                await self.bot.send_message(discord.Object(id=self.modlog_channel_id), message.author.name+'#'+message.author.discriminator+ ' (' + message.author.id + ') automatically muted for spamming messages')
                await self.bot.send_message(message.author, 'You just got automatically spamming messages. Leaving the server to get your mute removed will result in an automatic ban.\nYou can be unmuted if you provide a justified reason.(Asking/Begging for an unmute may lead to a mute extension)')
                return
            

def setup(bot):
    a = AntiSpam(bot)
    bot.add_listener(a.detect, "on_message")
    bot.add_cog(a)