import os
from asyncio import run as arun
import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import Intents
import ffmpeg
import youtube_dl
from youtubesearchpython import VideosSearch
from keep_alive import keep_alive

intents = Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
queues = {}

@bot.event
async def on_ready():
  guild_count = 0
  for guild in bot.guilds:
    print(f"- {guild.id} (name: {guild.name})")
    guild_count = guild_count + 1
    print(f"{bot.user} is online and present in " + "[" + str(guild_count) +"]" + " guilds.")
  
@bot.event
async def on_message(message):
  if message.content == "hello":
    await  message.channel.send(f"Hello there {message.author.name}")
  await bot.process_commands(message)

@bot.command()
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned.')


ytdlopts = { 
  'format': 'bestaudio/best',
  'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
  'restrictfilenames': True,
  'noplaylist': True,
  'nocheckcertificate': True,
  'ignoreerrors': False,
  'logtostderr': False,
  'quiet': True,
  'no_warnings': True,
  'default_search': 'auto',
  'source_address': '0.0.0.0',  
  'force-ipv4': True,
  'preferredcodec': 'mp3',
  'cachedir': False

  }

ffmpeg_options = {
        'options': '-vn'
    }

ytdl = youtube_dl.YoutubeDL(ytdlopts)



@bot.command()
async def join(ctx, *, query):
  channel = ctx.message.author.voice.channel
  await channel.connect()

@bot.command()
async def leave(ctx):
  await ctx.voice_client.disconnect()
  if ctx.guild.id in queues:
    del queues[ctx.guild.id]




@bot.command()
async def play(ctx, *, query):

    try:
        voice_channel = ctx.author.voice.channel #checking if user is in a voice channel
    except AttributeError:
        return await ctx.send("No channel to join. Make sure you are in a voice channel.") #member is not in a voice channel

    permissions = voice_channel.permissions_for(ctx.me)
    if not permissions.connect or not permissions.speak:
        await ctx.send("I don't have permission to join or speak in that voice channel.")
        return

    voice_client = ctx.guild.voice_client
    if not voice_client:
        await voice_channel.connect()
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=query, download=False)) #extracting the info and not downloading the source


    title = data['title'] #getting the title
    song = data['url'] #getting the url

    if 'entries' in data: #checking if the url is a playlist or not
            data = data['entries'][0] #if its a playlist, we get the first item of it

    try:
        voice_client.play(discord.FFmpegPCMAudio(source=song,**ffmpeg_options, executable="ffmpeg")) #playing the audio
    except Exception as e:
        print(e)

    await ctx.send(f'**Now playing:** {title}') #sending the title of the video



#@bot.command()
#async def play(ctx, *args):
  #query = ' '.join(args)

  #videos_search = VideosSearch(query, limit = 1)
  #results = videos_search.result()

  #if not results.get('result', None):
    #await ctx.send("No results found for the given query.")
    #return

  #video_url = results['result'][0]['link']
  
  #voice_channel = ctx.message.author.voice.channel
  #if ctx.guild.id not in queues:
    #queues[ctx.guild.id] = []
    #queues[ctx.guild.id].append(video_url)

  #voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
  #if voice is None or not voice.is_connected():
    #await voice_channel.connect()
    #voice = discord.utils.get(bot.voice_clients,guild=ctx.guild)

@bot.command()
async def pause(ctx):
    ctx.voice_client.pause()

@bot.command()
async def skip(ctx):
  dj_role = discord.utils.get(ctx.guild.roles, name="DJ")  # Replace "DJ" with your desired DJ role
  admin_permissions = ctx.message.author.guild_permissions.administrator

  if dj_role in ctx.message.author.roles or admin_permissions:
    ctx.voice_client.stop()
  else:
    await ctx.send("You don't have permission to skip songs.")

@bot.command()
async def queue(ctx):
  if ctx.guild.id in queues and queues[ctx.guild.id]:
    queue_list = "\n".join([f"{index + 1}. {song}" for index, song in enumerate(queues[ctx.guild.id])])
    await ctx.send(f"Queue:\n{queue_list}")
  else:
    await ctx.send("The queue is currently empty.")

@bot.command()
async def current(ctx):
  current_song = "Get the currently playing song logic here"  # Replace with your logic
  await ctx.send(f"Currently playing: {current_song}")

async def play_next(ctx):
  if ctx.guild.id in queues and queues[ctx.guild.id]:
    url = queues[ctx.guild.id].pop(0)
    ctx.voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e:
                          print(f'Finished playing: {e}'))
  else:
    await ctx.send("Queue is empty. Leaving the voice channel.")
    await ctx.voice_client.disconnect()


keep_alive()
TOKEN = "NzY5NTUzNDcwNjAwMTE4Mjgz.GeYxPr.U8xNio4uEZD4ospIkF7Ju0jzDbIuAEa0VBLOcg"
bot.run(TOKEN)