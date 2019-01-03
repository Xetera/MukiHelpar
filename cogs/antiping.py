import discord
from discord.ext import commands
import aiohttp
import json

def config_load():
    with open('config/settings.json', 'r', encoding='utf-8-sig') as doc:
        return json.load(doc)

class AntiPing:
    def __init__(self, bot):
        config = config_load()
        self.mute_role_id = config['mute_role']
        self.modlog_channel_id = config['modlog_channel']
        self.bot = bot

    async def detect(self, message):
        if message.channel.permissions_for(message.author).manage_roles:
            return
        if len(message.raw_mentions) + len(message.raw_role_mentions) > 4:
            muteMember = discord.utils.find(lambda m: m.id == message.author.id, message.server.members)
            muteRole = discord.utils.find(lambda r: r.id == self.mute_role_id, message.server.roles) 
            await self.bot.add_roles(muteMember, muteRole)
            await self.bot.send_message(message.channel, message.author.mention +', you are automatically muted for 5+ mentions in one message. If you feel like this is an error, consult with a moderator in DMs. \n Leaving the server to get your mute removed will result in an automatic ban.')
            await self.bot.send_message(discord.Object(id=self.modlog_channel_id), message.author.name+'#'+message.author.discriminator+ ' (' + message.author.id + ') automatically muted for mass mentioning (5+ pings)')
            await self.bot.send_message(message.author, 'You just got automatically muted for 5+ mentions in one message. Leaving the server to get your mute removed will result in an automatic ban.\nYou can be unmuted if you provide a justified reason.(Asking/Begging for an unmute may lead to a mute extension)')
            return

def setup(bot):
    a = AntiPing(bot)
    bot.add_listener(a.detect, 'on_message')
    bot.add_cog(a)