import discord
import random
import time
import asyncio
from discord.ext import commands
from config import *
import requests






#defaults
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='$', intents=intents)
messages = 0



#our statistic recorder function. this may require stats.txt file in this directory.
async def update_stats():
    with open(STATS, "a") as f:
        f.write(f"Time: {int(time.time())}, Messages: {messages}\n")


#is our bot active?
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    channel = bot.get_channel(1130847046950191255)  # you should copy your channel ID and paste here.
    if channel:
        await channel.send(BOT_READY_MESSAGE)

#blocking unwanted names
@bot.event
async def on_member_update(before, after):
    n = after.nick
    if n:
        if n.lower().count(UNWANTED_NAME) > 0:
            last = before.nick
            if last:
                await after.edit(nick=last)
            else:
                await after.edit(nick=TO_NAME)

#control the channel message activities
@bot.event
async def on_message(message):
    global messages
    messages += 1
    msg = message.content

    if message.author == bot.user:
        return

    # Reply for sad words
    for word in SAD_WORDS:
        if word in msg:
            response = random.choice(HAPPY_RESPONSES)
            await message.channel.send(response)
            break

    #reply for bad words            
    for word in BAD_WORDS:
        if message.content.count(word) > 0:
            print("A bad word was said")
            await message.channel.purge(limit=1)
            

    await bot.process_commands(message)
    await update_stats()





#HELP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.command()
async def code(ctx):
    embed = discord.Embed(title="Help on BOT", description="Some useful commands")
    embed.add_field(name="$hello", value="Greets the user")
    embed.add_field(name="$users", value="Prints number of users")
    embed.add_field(name="$clean <num>", value="Deletes messages")
    embed.add_field(name="$roll <num>", value="Rolls the dice")
    embed.add_field(name="$quote", value="Prints inspirational quotes")
    embed.add_field(name="$offline <num>", value="Shutdown the bot or turn of some minutes")
    embed.add_field(name="$guess <num>", value="Number guessing game")
    embed.add_field(name="$color_code <renk ismi>", value="Girdiğiniz rengin renk kodunu(hex) döndürür.")
    
    await ctx.send(embed=embed)



#say hi :D
@bot.command()
async def hello(ctx):
    isim = "Ertuğrul"
    await ctx.send(f'Merhaba, hoşgeldin.{isim}')



#will return the server members.
@bot.command()
async def users(ctx):
    try:
        guild = bot.get_guild(1130580376839016488)
        await ctx.send(f"# Members: {guild.member_count}")
    except Exception as e:
        print(f"hata var users komutunda dikkat et!{e}")



#will clean the channel message history.
@bot.command()
async def clean(ctx, limit=10):
    channel = ctx.channel
    await channel.purge(limit=limit + 1)
    await ctx.send(f"{limit} messages deleted.")



#do you need inspiration?
@bot.command()
async def quote(ctx):
    response = requests.get(QUOTEADDRESS)

    if response.status_code == 200:
        lines = response.text.splitlines()
        quote = random.choice(lines).strip()

        while not quote or len(quote) < 20:
            quote = random.choice(lines).strip()

        await ctx.send(quote)



#to turn off the bot
@bot.command()
async def offline(ctx, num: int = None):
    if num is None:
        await ctx.send("Bot is going completely offline. Goodbye!")
        await bot.change_presence(status=discord.Status.offline, activity=None)
    else:
        await ctx.send(f"Bot is going offline for {num} minute(s). Goodbye!")
        await bot.change_presence(status=discord.Status.offline, activity=None)

        await asyncio.sleep(num * 60)

        await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="KODLAND"))
        await ctx.send("Bot is back online!")



#for guess game
async def start_guessing(ctx, num=None):
    if num is None:
        num = "100"

    if not num.isdigit():
        await ctx.send("Please enter a valid number.")
        return

    number_to_guess = random.randint(1, int(num))
    await ctx.send(f"The number guessing game begins! I kept a number between 1 and {num}. Guess!")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit()

    attempts = 0
    while True:
        try:
            user_guess = await bot.wait_for('message', check=check, timeout=30)
            user_guess = int(user_guess.content)
            attempts += 1

            if user_guess == number_to_guess:
                await ctx.send(f"Great! You guessed right! Number: {number_to_guess}, Attempts: {attempts}")
                break
            elif user_guess < number_to_guess:
                await ctx.send("Guess a larger number.")
            else:
                await ctx.send("Guess a smaller number.")

        except asyncio.TimeoutError:
            await ctx.send("Time's up! The game is over.")
            break

#guess what :D
@bot.command()
async def guess(ctx, num: str = None):
    await start_guessing(ctx, num)



# Dice roll function
async def roll_dice(ctx, num=None):
    if num is None:
        num = 6
    try:
        num = int(num)
    except ValueError:
        await ctx.send("Please enter a valid number.")
        return

    result = random.randint(1, num)
    await ctx.send(f"I rolled the dice! Returned a value between 1 and {num} : {result}")

# Roll komutu
@bot.command()
async def roll(ctx, num: str = None):
    await roll_dice(ctx, num)






# Renk kodu gösterme fonksiyonu
async def show_color_code(ctx, color: str = None):
    color_codes = {
        "kırmızı": 0xFF0000,
        "yeşil": 0x00FF00,
        "mavi": 0x0000FF,
        # Diğer renkler buraya eklenebilir
    }

    if color is None:
        await ctx.send("Lütfen bir renk belirtin.")
    else:
        color = color.lower()
        if color in color_codes:
            await ctx.send(f"{color.capitalize()} rengin kodu: #{hex(color_codes[color])[2:].upper()}")
        else:
            await ctx.send("Belirtilen renk bulunamadı.")

@bot.command()
async def color_code(ctx, color: str = None):
    """
    Belirli bir renk kodunu gösterir.
    
    Parametre:
    color -- İstenen renk kodu (isteğe bağlı).
    """
    await show_color_code(ctx, color)



@bot.command()
async def reverse(ctx, text):
    reversed_text = str(text)[::-1]
    await ctx.send(f"{text} verdiğiniz metnin tersi: {reversed_text}")



@bot.command()
async def check_weather(ctx, location: str):
    # Burada hava durumu API'sinden veri çekme işlemi yapılabilir
    # Bu örnek için rastgele bir hava durumu sonucu döndürülecek
    weather_conditions = ["Güneşli", "Bulutlu", "Yağmurlu", "Karlı"]
    weather = random.choice(weather_conditions)
    await ctx.send(f"{location} için hava durumu: {weather}")



@bot.command()
async def random_word(ctx, *, words: str):
    word_list = words.split()
    chosen_word = random.choice(word_list)
    await ctx.send(f"Rasgele seçilen kelime: {chosen_word}")



@bot.command()
async def hesapla(ctx, *, expression: str):
    """
    Belirtilen matematiksel ifadeyi hesaplar.
    
    Parametre:
    expression -- Hesaplanacak matematiksel ifade.
    """
    try:
        result = eval(expression)
        await ctx.send(f"Sonuç: {result}")
    except Exception as e:
        await ctx.send(f"Hesaplama hatası: {e}")




@bot.command()
async def sum_from_to(ctx, from_num, to_num):
    number=0
    for i in range(int(from_num), int(to_num)+1):
        number += i
    await ctx.send(f"Bu sayıdan {from_num}, şu sayıya {to_num} toplam = {number}")









def get_duck_image_url():
    url = 'https://random-d.uk/api/random'
    res = requests.get(url)
    data = res.json()
    return data['url']


@bot.command('duck')
async def duck(ctx):
    '''The duck command returns the photo of the duck'''
    print('hello')
    image_url = get_duck_image_url()
    await ctx.send(image_url)







@bot.command()
async def the_best_song_of_all_time(ctx):
    await ctx.send('You really wanna now?($y for yes $n for no)')

@bot.command()
async def y(ctx):
    await ctx.send('YOU SURE?($yes or $n)') 

@bot.command()
async def yes(ctx):
    await ctx.send('HERE YOU GO https://youtu.be/dQw4w9WgXcQ?t=42')

@bot.command()
async def n(ctx):
    await ctx.send('OK')











#pipenv install pynacl
#pipenv install youtube_dl
import youtube_dl
from discord.ext import commands

@bot.command()
async def play(ctx, url: str):
    # Belirtilen YouTube videosunu ses kanalında çalar.
    # Parametre:
    # url -- YouTube video URL'si.

    voice_state = ctx.author.voice
    if voice_state is None or voice_state.channel is None:
        await ctx.send("Lütfen bir ses kanalına katılın.")
        return

    voice_channel = voice_state.channel
    voice_client = await voice_channel.connect()

    ydl_opts = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(url2), after=lambda e: print('Müzik çalma hatası: %s' % e))

    await ctx.send(f"Müzik çalınıyor: {url}")

@bot.command()
async def stop(ctx):
    # Ses kanalındaki müziği durdurur.
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()






















@bot.command()
async def check(ctx, name):
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file_name = name
            file_url = attachment.url 
            await attachment.save(f"./Yapay_Zeka_Gorselleri\\{file_name}")
            await ctx.send(f"resmin url'si: {file_url}")
    else:
        await ctx.send("You forgot to upload the image :(")



#our bot will run with this TOKEN-----------------------------------------------------------------------
bot.run(DISCORD_TOKEN)
#you should paste your TOKEN inside the brackets here.