import discord
import asyncio
import aiohttp
import json
from discord.ext import commands

def config_load():
    with open('config/settings.json', 'r', encoding='utf-8-sig') as doc:
        return json.load(doc)

class Moderation:

    def __init__(self, bot):
        config = config_load()
        self.mute_role_id = config['mute_role']
        self.modlog_channel_id = config['modlog_channel']
        self.loop = asyncio.get_event_loop()
        self.bot = bot 
        self.aiosession = aiohttp.ClientSession(loop=self.loop)
         
    @commands.command(pass_context=True)
    async def prune(self, ctx):
        if not ctx.message.channel.permissions_for(ctx.message.author).manage_messages:
            await self.bot.say("You don't have permission to do this.")
            return   
        try:
            def is_mention(m):
                if len(ctx.message.mentions)>0:
                    for mention in ctx.message.mentions:
                        if mention == m.author:
                            return True
                    return False        
                else:
                    return True
            deleted = await self.bot.purge_from(ctx.message.channel, limit=int(ctx.message.content.split(' ')[1]), check=is_mention)
            await self.bot.send_message(ctx.message.channel, 'Deleted {} message(s)'.format(len(deleted)))        
        except:
            pass
    
    @commands.command(pass_context=True)
    async def ban(self, ctx):
        if not ctx.message.channel.permissions_for(ctx.message.author).ban_members:
            await self.bot.say("You don't have permission to do this.")
            return
        if len(ctx.message.mentions)==1:
            try:
                await self.bot.send_message(discord.User(id=ctx.message.mentions[0].id), 'You have been banned from Miki server. If you believe this is an error, consult with mods.')
            except:
                pass
            try:
                temp_member = discord.Object(id=ctx.message.mentions[0].id)
                temp_member.server = discord.Object(id=ctx.message.server.id)
                await self.bot.ban(temp_member)
                await self.bot.send_message(discord.Object(id=self.modlog_channel_id), ' (' + temp_member.id + ') banned for ' +ctx.message.content.split(' ',2)[2] + ' by ' + ctx.message.author.name)
            except:
                temp_member = discord.Object(id=ctx.message.mentions[0].id)
                temp_member.server = discord.Object(id=ctx.message.server.id)
                await self.bot.ban(temp_member)
                await self.bot.send_message(discord.Object(id=self.modlog_channel_id), ' (' + temp_member.id + ') banned for (blank) by ' + ctx.message.author.name)
            return    
        try:
            await self.bot.send_message(discord.User(id=ctx.message.content.split(' ',2)[1]), 'You have been banned from Miki server. If you believe this is an error, consult with mods.')
        except:
            pass
        try:
            temp_member = discord.Object(id=ctx.message.content.split(' ',2)[1])
            temp_member.server = discord.Object(id=ctx.message.server.id)
            await self.bot.ban(temp_member)
            await self.bot.send_message(discord.Object(id=self.modlog_channel_id), ' (' + temp_member.id + ') banned for ' +ctx.message.content.split(' ',2)[2] + ' by ' + ctx.message.author.name)
        except:
            temp_member = discord.Object(id=ctx.message.content.split(' ',1)[1])
            temp_member.server = discord.Object(id=ctx.message.server.id)
            await self.bot.ban(temp_member)
            await self.bot.send_message(discord.Object(id=self.modlog_channel_id), ' (' + temp_member.id + ') banned for (blank) by ' + ctx.message.author.name)
    
    @commands.command(pass_context=True)
    async def kick(self, ctx):
        if not ctx.message.channel.permissions_for(ctx.message.author).kick_members:
            await self.bot.say("You don't have permission to do this.")
            return
        if len(ctx.message.mentions)==1:
            try:
                await self.bot.send_message(discord.User(id=ctx.message.mentions[0].id), "You have been kicked from Miki server. You can rejoin via <https://discord.gg/veUGD9t>; just don't make the same mistake again or it will lead to a ban.")
            except:
                pass
            try:
                temp_member = discord.Object(id=ctx.message.mentions[0].id)
                temp_member.server = discord.Object(id=ctx.message.server.id)
                await self.bot.kick(temp_member)
                await self.bot.send_message(discord.Object(id=self.modlog_channel_id), ctx.message.mentions[0].name + ' (' + temp_member.id + ') kicked for ' +ctx.message.content.split(' ',2)[2] + ' by ' + ctx.message.author.name)
            except:
                temp_member = discord.Object(id=ctx.message.mentions[0].id)
                temp_member.server = discord.Object(id=ctx.message.server.id)
                await self.bot.kick(temp_member)
                await self.bot.send_message(discord.Object(id=self.modlog_channel_id), ctx.message.mentions[0].name + ' (' + temp_member.id + ') kicked for (blank) by ' + ctx.message.author.name)
            return    
        try:
            await self.bot.send_message(discord.User(id=ctx.message.content.split(' ',2)[1]), 'You have been banned from Miki server. If you believe this is an error, consult with mods.')
        except:
            pass
        try:
            temp_member = discord.Object(id=ctx.message.content.split(' ',2)[1])
            temp_member.server = discord.Object(id=ctx.message.server.id)
            await self.bot.kick(temp_member)
            await self.bot.send_message(discord.Object(id=self.modlog_channel_id), ' (' + temp_member.id + ') kicked for ' +ctx.message.content.split(' ',2)[2] + ' by ' + ctx.message.author.name)
        except:
            temp_member = discord.Object(id=ctx.message.content.split(' ',1)[1])
            temp_member.server = discord.Object(id=ctx.message.server.id)
            await self.bot.kick(temp_member)
            await self.bot.send_message(discord.Object(id=self.modlog_channel_id), ' (' + temp_member.id + ') kicked for (blank) by ' + ctx.message.author.name)
    
    
    @commands.command(pass_context=True)
    async def mute(self, ctx):
        '''>mute <Mention 1> [Mention 2] [Mention 3]...'''
        if not ctx.message.channel.permissions_for(ctx.message.author).manage_roles:
            return
        for diffrole in ctx.message.server.roles:
            if diffrole.id == self.mute_role_id:
                actual_role = diffrole
                break    
        if len(ctx.message.mentions)> 0:
            for mention in ctx.message.mentions:
                await self.bot.add_roles(mention, actual_role)
          
    @commands.command(pass_context=True)
    async def cleanroles(self, ctx):
        '''>cleanroles'''
        if not ctx.message.channel.permissions_for(ctx.message.author).manage_roles:
            return
        rolesRemoved = []
        removeRole = True
        for diffrole in ctx.message.server.roles:
            if diffrole.name.startswith('#'):
                for member in ctx.message.server.members:
                    findRole = discord.utils.find(lambda r: r.name == diffrole.name, member.roles) 
                    if findRole != None:
                        removeRole = False
                        break
                if removeRole:
                    rolesRemoved.append(diffrole.name)
                    await self.bot.delete_role(ctx.message.server, diffrole)
                removeRole = True
        tempM = 'Roles Deleted: '
        if len(rolesRemoved)==0:
            tempM = tempM + 'None'
        else:
            for deadRole in rolesRemoved:
                tempM = tempM + deadRole + ', '
        await self.bot.say(tempM)        
                  
            
        
def setup(bot):
    bot.add_cog(Moderation(bot))
