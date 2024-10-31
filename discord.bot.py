from multiprocessing.connection import Client
from secrets import randbelow
import discord
from discord.utils import get
from discord.ext import commands
from grpc import server
from numpy import diag, source
import aiohttp
import requests
import glob
import random
import os
import time
from PIL import Image
from dotenv import load_dotenv
from sympy import content, true
import youtube_dl
from youtube_dl import YoutubeDL
import asyncio
import dbdmusic
import lxml.html
from urllib.parse import urlparse, parse_qs
import wavelink
# from probnik import shetchik
# from discord import File


# Намерения
intents = discord.Intents.all()
bot = discord.Client(intents=intents)
# Очевидно - префикс для того, чтобы бот реагировал на твои команды
bot = commands.Bot(command_prefix = "?")


# Даёт понять, что бот залогинился и работает
@bot.event
async def on_ready(): #без on_ почему-то не работает даже если по другому переменную назвать. Видимо в event так надо
    print('''Ты сука тупорылая блять не дал мне договорить.
    Ладно, похуй. Чел зарегался под этим логином: {0.user}'''.format(bot))
    await bot.change_presence(activity=discord.Game(name="?zxcкоманды"))


youtube_dl.utils.bug_reports_message = lambda: ''

# Настройки
# ytdl_url = ['https://www.youtube.com/watch?']
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

# Класс для функционала, связанного с музыкой
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename
        
    @bot.command(name='сюда', help='Подключает бота к войсу')
    async def join(ctx):
        if not ctx.message.author.voice:
            await ctx.send("{} Ты не подключен, лошок".format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()
        server = ctx.message.guild
        voice_channel = server.voice_client
        # file = discord.File("C:/Python/dicsord_bot/downloads/Pupich.mp3")
        voice_channel.play(discord.FFmpegPCMAudio(executable="C:/Python/dicsord_bot/ffmpeg-2022-03-03-git-72684d2c2d-full_build/bin/ffmpeg.exe", source = 'C:\Python\dicsord_bot\downloads\Pupich.mp3', **ffmpeg_options))

    @bot.command(name='пиздуй', help='Лив бота с войса')
    async def leave(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        else:
            embed = discord.Embed(title = '🤬', description = 'Суки, выгоняют меня', colour = discord.Color.red())
            await ctx.send(embed = embed)

    @bot.command(name='сыграй', help='Играет музыку')
    async def play(ctx,url):
        try : # Скачивает музло, если это не стрим и воспроизводит. Пока лень переписывать, чтобы не скачивало и не стрим, но похуй. Главное, что это дерьмище работает
            server = ctx.message.guild
            voice_channel = server.voice_client
            async with ctx.typing():
                 with YoutubeDL(ytdl_format_options) as ydl:
                    info = ydl.extract_info(url, download=False)
                    URL = info['formats'][0]['url']
                    voice_channel.play(discord.FFmpegPCMAudio(executable="C:/Python/dicsord_bot/ffmpeg-2022-03-03-git-72684d2c2d-full_build/bin/ffmpeg.exe", source = URL, **ffmpeg_options))
                    embed = discord.Embed(title = '🎼Сейчас играет:', description = format(url), colour = discord.Color.red())
            await ctx.send(embed = embed)
        except: # Воспроизведение стримов
            # await ctx.send("Ошибка где-то здесь!!")
            await ctx.send("Lan...")

    @bot.command(name='притормози', help='Ну пауза типа')
    async def pause(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            embed = discord.Embed(title = '❗️❗️❗️WARNING❗️❗️❗️', description = "Сейчас zxcбот ничего не играет", colour = discord.Color.red())
            await ctx.send(embed = embed)
        
    @bot.command(name='газуй', help='Продолжает воспроизводить')
    async def resume(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("До этого zxcбот нихуя не играл. Юзни '?:Сыграй' ")
    @bot.command(name='стопай', help='Останавливает музыку')
    async def stop(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
        else:
            embed = discord.Embed(title = '❗️❗️❗️WARNING❗️❗️❗️', description = "Сейчас zxcбот ничего не играет", colour = discord.Color.red())
            await ctx.send(embed = embed)
        

@bot.event
async def on_guild_join(guild):
    
    text_channels = guild.text_channels
    
    if text_channels:
        channel = text_channels[0]
        embed = discord.Embed(title = 'Ку👋', description = '''Чтобы авторизоваться на этом сервере, напиши 👉 "дай роль". 
❗️Если тебе интересны мои команды, то пропиши ?zxcкоманды 👀 после авторизации на сервере.
Правила сможешь прочитать в чате "rules" сразу после того, как авторизуешься. 
🤙Кайфуй🤙 {}!'''.format(guild.name), colour = discord.Color.red())
    
    await channel.send(embed = embed)


# Подавление шума об использовании консоли из-за ошибок 


@bot.command()
async def RandomAnime(ctx):

    embed = discord.Embed(title = 'Значит аниме решил посмотреть', description = '''Вот параметры для подбора аниме:
    1 - Сериал или фильм
    2 - Жанр
    3 - Страна
    4 - Год
    По этим 4-м параметрам будет выбираться аниме с сайта. 
    Если в каком-то из параметров вы не смогли определиться, то можно написать так:
    1 - Все Аниме
    2 - Все Жанры
    3 - Все Страны
    4 - Год
    Дальше будет ввод:''', colour = discord.Color.red())
    await ctx.send(embed = embed)

    def check(message): # Все фильтры идут сюда
        return message.author.id == ctx.author.id and message.channel.id == ctx.channel.id
    try:
        await ctx.send(file=discord.File("C:/Python/dicsord_bot/Guide/Гайд по RA.mp4"))
        type_ = await bot.wait_for('message', check=check, timeout=60.0)
        genre = await bot.wait_for('message', check=check, timeout=60.0)
        country = await bot.wait_for('message', check=check, timeout=60.0)
        year = await bot.wait_for('message', check=check, timeout=60.0)

        params = {
            '?type=': type_,
            '&genre=': genre,
            '&country': country,
            '=&year=': year
        }


        headers = {
            'User-Agend': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70 (Edition Yx GX 03)'
        }

        await ctx.send("Вы ввели такие параметры: " + type_.content + ', ' + genre.content + ', ' + country.content + ', ' + year.content + " Вот аниме, которое можете посмотреть" )
        resp = requests.get(f'https://anime777.ru/api/rand/', params, headers = headers).json()

        await ctx.send(resp['title'])
        await ctx.send(resp['other_title'])
    except asyncio.TimeoutError:
        await ctx.send('Время вышло...')



# Проверочная команда на работу бота в дискорде
@bot.command()
async def zxc(ctx):
    embed = discord.Embed(title = 'coil coil coil', description = '''Коил, коил, коил
Сука, прямо подо мною
Каждый рэйз наполнен болью
Кричат души на Стокгольме
Zxc и ты покойник
В моём лобби ты не воин
Не рычи, надень намордник
Requiem, тебе хуёво
Коил, коил, коил
Сука, прямо подо мною
Каждый рэйз наполнен болью
Кричат души на Стокгольме
Zxc и ты покойник
В моём лобби ты не воин
Не рычи, надень намордник
Requiem, тебе хуёво, ха

Shadow-Shadow Fiend, ха
Парень без обид
Raze быстрее чем Stampede
Твой ugly face уже разбит
Слышь, ебучий псих, твой playstyle – это стыд, ха
Я, бля, Shadow Fiend, ты ебучий психокид, х
Ты, блядь, кто такой, а? Сука, чё не нравится?
Triple Raze в ебло и твоё эго, блядь, расплавится
Твоя блядь на пос-пять — она лает и кусается
Я бля perfect player, меня это не касается, сука


Привет, Каспер, помнишь меня?
Как там твой сыночек, безмозглый дегенерат, Стасик, поживает? Никто его ещё не пришиб, как муху ебаную?
А, броу? Как там твоя мать, шлюха гнилозубая, поживает, тоже, рассказывай
До встречи на эпицентре, сын шлюхи


Коил, коил, коил
Сука, прямо подо мною
Каждый рэйз наполнен болью
Кричат души на Стокгольме
Zxc и ты покойник
В моём лобби ты не воин
Не рычи, надень намордник
Requiem, тебе хуёво
Коил, коил, коил
Сука, прямо подо мною
Каждый рэйз наполнен болью
Кричат души на Стокгольме
Zxc и ты покойник
В моём лобби ты не воин
Не рычи, надень намордник
Requiem, тебе хуёво, ха

Triple Raze на шее
Мне не нужно разрешение, ха
Убрал тебя с мида, в моём лобби стал мишенью
Твой Титаник пал, блядь, или сука, потерпел крушение
Ты ебучий dead inside интернетных отношений
Моё лобби zxc, но я не жду больше минуты
В деле топовый SF, мои коилы – терракоты
Мои коилы — zxc, мои души — громче всех
Zxc — ты отлетаешь от раскаста shadowraze''', colour = discord.Color.red())
    await ctx.send(embed = embed)


# Отправляеь случайную псину
@bot.command()
async def dog(ctx):
   async with aiohttp.ClientSession() as session:
      request = await session.get('https://some-random-api.ml/img/dog') # Создем запрос хули
      dogjson = await request.json() # Конвертируем
   embed = discord.Embed(title="Псина(ы) ебаная(учие). Трахнули бы? (?:Да / ?:Нет)", color=discord.Color.red()) # Создаем полосочку слева
   embed.set_image(url=dogjson['link']) # Ключ на апи запросах для того, чтобы он был valuable
   await ctx.send(embed=embed)



# Отправляет имя моей девушки)
@bot.command()
async def MyLove(ctx):
    embed = discord.Embed(title = "Саша", colour = discord.Color.red())
    await ctx.send(embed = embed)


# Случайные мемы с сайта
@bot.command()
async def zxcmeme(ctx):
    response = requests.get('https://some-random-api.ml/meme')
    json_data = response.json()
    embed = discord.Embed(title = json_data['caption'], colour = discord.Color.red())
    embed.set_image(url = json_data ['image'])
    await ctx.send(embed = embed)


# Случайное фото из папки
# Идет обработка под дискорд файлы, чтобы дис увидел файлы и мог отправить + подключение модуля рандом.выбора в выбанной директории
@bot.command()
async def zxcpickh(ctx):
    await ctx.send(file=discord.File("C:\Python\dicsord_bot\Ghoulpikch\\" + random.choice(os.listdir("C:\Python\dicsord_bot\Ghoulpikch\\")))) 



# Разлогинивает бота
@bot.command()
async def Vse(ctx):
    embed = discord.Embed(title = '''Заткнись, ты, son шала...
    *Бот был успешно отключен. Для возобовления его работы необходимо попросить админа запустить код''', colour = discord.Color.red() )
    await ctx.send(embed = embed)
    await bot.logout() 

# Ебаный счет 1000-7 (Не используйте)
@bot.event
async def on_message(message): #без on_ почему-то не работает даже если по другому переменную назвать. Видимо в event так надо

# Реакции на сообщения. Тоже тип команды, только так можно сделать сделать любое сообщение для реакции   
# Показывает существующие команды бота
    if message.content.startswith('?:zxcкоманды'):
        embed = discord.Embed(title = "Ну ты нахуй...👶", description ='''Блять...
        Вот список моих команд
        Во-первых мой префик это '?:' знай.
        Теперь по порядку:
        1 - zxc (Shadowraze? Нет блять, павший)
        2 - 1000-7 (Счет - чисто приколямбус для гулей)
        3 - dog (Получите рандомную псину)
        4 - zxcmeme (Очевидно - zxcmemes)
        5 - zxcpickh (Картинки для настоящих гулей)
        6 - Руководство по использованию музыкальных функций zxcбота:
            6.1 - "Сюда" (Присоединение бота к голосовому каналу)
            6.2 - "Сыграй" (Проигровка музыки)
            6.3 - "Пиздуй"  (Выгнать нахуй ебаклака)
            6.4 - "Притормози" (Поставить паузу)
            6.5 - "Газуй" (Продолжить музыку)
            6.6 - "Стопай" (Фулл остановка музла)
        7 - RandomAnime (Случайное аниме по параметрам с сайта (Находится на стадии фикса. Пробовать использовать можно).)
        ''', colour = discord.Color.red())
        await message.channel.send(embed = embed)

# Счет нормального гулёныша   
    if message.content.startswith('?:1000-7'):
        
        import time
        mass = []
        a = 1000
        while a > 0:
            a = a - 7
            mass.append(a)
            print(str(a))
            time.sleep(0.1)
        print(mass)
        print("???")
        for i in mass:
            await message.channel.send(str(i))
            
        await message.channel.send('Мёртв внутри')
    
    if message.content.startswith('?:да') or message.content.startswith('?:ДА') or message.content.startswith('?:Yes') or message.content.startswith('?:YES'):
        embed = discord.Embed(title = 'Пизда, ахаххахахах😂', description = 'Собакоеб гребаный, пиздуй на кинолога учиться', colour = discord.Color.red())
        await message.channel.send(embed = embed)
    elif message.content.startswith('?:нет') or message.content.startswith('?:НЕТ') or message.content.startswith('?:No') or message.content.startswith('?:NO'):
        embed = discord.Embed(title = 'Пидора ответ, ахахаххах😂', description = 'Чел, ты в муте', colour = discord.Color.red())
        await message.channel.send(embed = embed)
    
    if message.content.startswith('?:пиздуй'):
        embed = discord.Embed(title = '🤬', description = 'Ну и пошли вы все нахуй, гандоны', colour = discord.Color.red())
        await message.channel.send(embed = embed)
    
    if message.content.startswith('?:Любовь Сан'):
        embed = discord.Embed(title = 'Двухметровые мужики', colour = discord.Color.red())
        await message.channel.send(embed = embed)

    if message.content.startswith('хачу роль'):
        member = message.author
        role = get(member.guild.roles, name="Общинники")
        await member.add_roles(role)
        await message.delete()




            
        
    await bot.process_commands(message)






# bot.connect('OTI4OTI0MjI4OTU3Mzg0NzE0.Ydf2Gg.bvbsQipivyyWgu97gllhzZbZn_0')
bot.run('OTI4OTI0MjI4OTU3Mzg0NzE0.Ydf2Gg.TiTDtgvpXT7rycNplh_1s7XNchA')


# ###ПРОВЕРКА
# import os,sys
 
# filename = '14.jpg'
# print(os.path.abspath(filename))

# # либо узнаем директорию нахождения скрипта
# app_dir = sys.path[0] or os.path.dirname(os.path.realpath(sys.argv[0])) or os.getcwd() 
# # os.chdir(app_dir)  # не нужно
 
# print(os.path.join(app_dir,filename))

# from PIL import Image
 
# image = Image.open('C:/Python/dicsord_bot/Ghoulpikch/27.jpg')
# image.show()