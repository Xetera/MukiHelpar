import discord
import asyncio

from discord.ext import commands



class Donator:

    def __init__(self, bot):
        self.bot = bot 
        self.counter = 0

    @commands.command(pass_context=True)
    async def setcolor(self, ctx, *, colorHex : str):
        '''>setcolor <color>'''
        tempRole = discord.utils.find(lambda r: r.name == 'Donators', ctx.message.author.roles)
        if tempRole == None:
            await self.bot.say(ctx.message.author.name + ", You're not an active patron of Miki. You can be one by donating monthly on <https://www.patreon.com/mikibot>")
            return
        else:
            existRole = discord.utils.find(lambda r: r.name.upper() == '#' + colorHex.upper().replace(' ','').replace('#',''), ctx.message.server.roles)
            if existRole != None:
                print('Role already Exists')
                await self.bot.say(existRole.name + ' given to ' +ctx.message.author.name)
                await self.bot.add_roles(ctx.message.author, existRole)
                return
            for role in ctx.message.author.roles:
                if role.name.startswith('#'):
                    await self.bot.remove_roles(ctx.message.author, role)
            try:
                niceMeme = '0x' + colorHex.replace('#','').upper()
                newRole = await self.bot.create_role(ctx.message.server, name='#' + colorHex.replace('#','').upper(), colour=discord.Colour(eval(niceMeme)))
                await self.bot.add_roles(ctx.message.author, newRole)
                regularMikiRole = discord.utils.find(lambda r: r.name == 'Regular Miki', ctx.message.server.roles)
                await self.bot.move_role(ctx.message.server, newRole, regularMikiRole.position)
                await self.bot.say('#' + colorHex.replace('#','') + ' given to ' + ctx.message.author.name)
            except:
                pass
    
          
        
def setup(bot):
    bot.add_cog(Donator(bot))