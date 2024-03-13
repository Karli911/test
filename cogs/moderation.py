import discord
from discord.ext import commands
import datetime

class Moderation(commands.Cog):
  def __init__(self,client):
    self.client = bot
    
    
    
  @commands.command(hidden = true)
  @commands.is_owner()
    await ctx.reply("'''SubUnit\n Rebooting <"+self.bot.user.name+"> : "+str(datetime.datetime.now())+"z'''")
    await self.bot.close()