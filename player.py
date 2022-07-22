import discord
import os
import ffmpeg
import random
import nacl
import time
import api
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel
from youtube_dl import YoutubeDL

load_dotenv()
client = commands.Bot(command_prefix='..')  # prefix commands with '..'

players = {}

mc = api.MusicCrawler()


@client.event  # check if bot is ready
async def on_ready():
    print('Bot online')


@client.command()
async def random(ctx, num_range):
    num = random.randint(1, int(num_range))
    await ctx.send(str("num"))


@client.command()
async def reset(ctx):
    try:
        global mc
        mc = api.MusicCrawler()
    except Exception as e:
        await ctx.send("Reset failed")
        print(e)


@client.command()
async def user(ctx, qq_id: int):
    titles = mc.set_user(qq_id)
    count = 1
    await ctx.send("------------Titles------------")
    for item in titles:
        await ctx.send(str(count) + ": " + item)
        count = count + 1
    await ctx.send("------------End----------------")


@client.command()
async def playlist(ctx, selection):
    global mc
    mc.set_song_list(int(selection))
    urls = mc.get_playlist_urls()
    for url in urls:
        while 1:
            # join the channel
            channel = ctx.message.author.voice.channel
            voice = get(client.voice_clients, guild=ctx.guild)
            if voice and voice.is_connected():
                await voice.move_to(channel)
            else:
                voice = await channel.connect()

            # play the song
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            voice = get(client.voice_clients, guild=ctx.guild)
            if not voice.is_playing():
                with YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                URL = info['url']
                voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS, executable=os.getenv('FFMPEG_EXECUTABLE2')))
                voice.is_playing()
                break


@client.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()


# command to play sound from a youtube URL
@client.command()
async def play(ctx, url):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = get(client.voice_clients, guild=ctx.guild)
    if not voice.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        print(URL)
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS, executable=os.getenv('FFMPEG_EXECUTABLE2')))
        voice.is_playing()
        await ctx.send('Bot is playing')



# command to resume voice if it is paused
@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Bot is resuming')


# command to pause voice if it is playing
@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Bot has been paused')


# command to stop voice
@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        await ctx.send('Stopping...')


# command to clear channel messages
@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)
    await ctx.send("Messages have been cleared")


TOKEN = os.getenv('DISCORD_TOKEN')
client.run(TOKEN)
