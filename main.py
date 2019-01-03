import requests
import json
import asyncio
import datetime
import logging
import random

import urllib.request

from datetime import timedelta
from pathlib import Path

import discord
from discord.ext import commands


def config_load():
    with open('config/settings.json', 'r', encoding='utf-8-sig') as doc:
        return json.load(doc)

def keys_load():
    with open('config/keys.json', 'r', encoding='utf-8-sig') as doc:
        return json.load(doc)

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=self.get_prefix_
        )
        config = config_load()
        self.server_id = config['server']
        self.mute_role_id = config['mute_role']
        self.modlog_channel_id = config['modlog_channel']
        self.log_channel_id = config['log_channel']
        self.remove_command('help') #Fuck Discord.py default help command
        self.app_info = None
        self.loop.create_task(self.load_all_extensions())

    async def get_prefix_(self, bot, message):
        config = config_load()
        prefix = config['prefix']
        return commands.when_mentioned_or(*prefix)(bot, message)

    async def load_all_extensions(self):
        await self.wait_until_ready()
        await asyncio.sleep(3)
        cogs = [x.stem for x in Path('cogs').glob('*.py')]
        for extension in cogs:
            try:
                self.load_extension(f'cogs.{extension}')
                print(f'loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                print(f'failed to load extension {error}')
            print('-' * 10)

    async def on_ready(self):
        await self.change_presence(game=discord.Game(name='around'))
        print(str(len(self.servers))+' servers.')
        print('-' * 10)
        self.app_info = await self.application_info()
        print(f'Logged in as: {self.user.name}\n'
              f'Owner: {self.app_info.owner}\n')
        print('-' * 10)

    async def on_message_delete(self, message):
        if message.author.bot:
            return
        if message.server.id != self.server_id:
            return
        try:    
            if message.author in await self.get_bans(message.server):
                return
        except discord.errors.Forbidden:
            pass
        em = discord.Embed(title='Message Deleted', color=0xFF0000) 
        if len(message.content)>1000:
            em.add_field(name='Content', value=message.content[:1000]+'...', inline=False)
        elif len(message.content)<1:
            em.add_field(name='Content', value='(Empty Message)', inline=False)
        else:    
            em.add_field(name='Content', value=message.content, inline=False)
        if len(message.attachments)>0:
            em.add_field(name='Attachment', value=message.attachments[0]['proxy_url'], inline=False)
        em.add_field(name='Author', value=message.author.name+'#'+message.author.discriminator+ ' (' + message.author.id + ')', inline=False)
        em.add_field(name='Channel', value=message.channel.mention, inline=False)
        await self.send_message(discord.Object(id=self.log_channel_id), embed=em)
        
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.server.id != self.server_id:
            return
        if before.content == after.content:
            return
        em = discord.Embed(title='Message Edited', color=0xFFFF00)    
        if len(before.content)>500:
            em.add_field(name='Before', value=before.content[:500]+'...', inline=False)
        else:
            em.add_field(name='Before', value=before.content, inline=False)
        if len(after.content)>500:
            em.add_field(name='After', value=after.content[:500]+'...', inline=False)
        else:
            em.add_field(name='After', value=after.content, inline=False)    
        em.add_field(name='Author', value=before.author.name+'#'+before.author.discriminator+ ' (' + before.author.id + ')', inline=False)
        em.add_field(name='Channel', value=before.channel.mention, inline=False)
        await self.send_message(discord.Object(id=self.log_channel_id), embed=em)    

    async def on_member_remove(self, member):
        if member.server.id == self.server_id:
            '''
            try:
                await self.send_message(discord.Object(id='413418208247283722'), member.name + ' (' + member.id + ') left')
            except:
                await self.send_message(discord.Object(id='413418208247283722'), ' (' + member.id + ') left')
            '''    
            rol = discord.utils.find(lambda r: r.id == self.mute_role_id, member.roles)
            if rol!= None:
                try:
                    await self.send_message(discord.Object(id=self.modlog_channel_id), member.name + ' (' + member.id + ') banned for mute evasion.')
                except:
                    await self.send_message(discord.Object(id=self.modlog_channel_id), ' (' + member.id + ') banned for mute evasion.')
                await self.ban(member)
                
    async def on_message(self, message):
        if message.channel.is_private or message.author.bot:
            return      
        if message.server.id == self.server_id:
            await self.process_commands(message)
                 
async def run():
    config = config_load()
    bot = Bot(config=config)
    try:
        await bot.start(config['token'])
    except KeyboardInterrupt:
        await bot.close()     
       
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
