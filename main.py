import nextcord as discord
from nextcord.ext import commands, tasks
import os, sys, time, json, base64, requests
from typing import Optional

time_before_start = time.time()

OWNER_ID = 553093932012011520 # for dms
GUILD_ID = 966586000417619998 # for emojis
BOT_ID = 966695034340663367

TOKEN = os.environ['token']

if TOKEN == None:
    print("Could not find token, exiting...")
    sys.exit(1)

with open("db.json", "r") as f:
    db = json.loads(f.read())

with open("aches.json", 'r') as f:
    ach_list: dict[str, dict[str, str|bool]] = json.loads(f.read())

with open("cats.json", "r") as f:
    cats: dict[str, int] = json.loads(f.read())

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="idk how this works but you need to have spaces in it or it may crash", help_command=None, intents=intents)

def save_db():
    with open("backup", "w") as f:
        f.write(str(db))
    with open("db.json", 'w') as f:
        f.write(json.dumps(db))

def register_member(guild_id: int, user_id: int):
    if db['guilds'][str(guild_id)]['users'].get(str(user_id)) is None:
        user_data = {
            "cats": {},
            "achs": {},
            "fastest": None,
            "slowest": None
        }
        for cat in cats.keys():
            user_data["cats"][cat] = 0
        for ach in ach_list.keys():
            user_data["achs"][ach] = False
        db['guilds'][str(guild_id)]['users'][str(user_id)] = user_data

def register_guild(guild_id: int):
    if db['guilds'].get(str(guild_id)) is None:
        db['guilds'][str(guild_id)] = {
            "users": {},
            "channel": None
        }

async def give_cat(guild_id: int, member_id: int, cat_type: str, amount=1, overwrite=False):
    if overwrite:
        db['guilds'][str(guild_id)]['users'][str(member_id)]['cats'][cat_type] = amount
    else:
        db['guilds'][str(guild_id)]['users'][str(member_id)]['cats'][cat_type] += amount
    return db['guilds'][str(guild_id)]['users'][str(member_id)]['cats'][cat_type]

async def remove_cat(guild_id: int, member_id: int, cat_type: str, amount=1):
    db['guilds'][str(guild_id)]['users'][str(member_id)]['cats'][cat_type] -= amount
    return db['guilds'][str(guild_id)]['users'][str(member_id)]['cats'][cat_type]

async def get_cats(guild_id: int, member_id: int) -> dict[str, int]:
    return db['guilds'][str(guild_id)]['users'][str(member_id)]['cats']

async def has_ach(guild_id: int, member_id: int, ach: str):
    return db['guilds'][str(guild_id)]['users'][str(member_id)]['achs'][str(ach)]

async def get_achs(guild_id: int, member_id: int) -> dict[str, bool]:
    return db['guilds'][str(guild_id)]['users'][str(member_id)]['achs']

async def get_slowest(guild_id: int, member_id: int) -> int|None:
    return db['guilds'][str(guild_id)]['users'][str(member_id)]['slowest']

async def set_slowest(guild_id: int, member_id: int, value: int):
    db['guilds'][str(guild_id)]['users'][str(member_id)]['slowest'] = value

async def get_fastest(guild_id: int, member_id: int) -> int|None:
    return db['guilds'][str(guild_id)]['users'][str(member_id)]['fastest']

async def set_fastest(guild_id: int, member_id: int, value: int):
    db['guilds'][str(guild_id)]['users'][str(member_id)]['fastest'] = value

async def get_ach_text(guild_id: int, member_id: int):
    user_achs = await get_achs(guild_id, member_id)
    
    non_hidden = 0
    max_non_hidden = 0
    hidden = 0
    
    for ach_name, has_got in user_achs.items():
        if ach_list[ach_name]['is_hidden']:
            if has_got: hidden += 1
        else:
            max_non_hidden += 1
            if has_got: non_hidden += 1
    
    if hidden >= 1:
        return f"{non_hidden}/{max_non_hidden} + {hidden}"
    else:
        return f"{non_hidden}/{max_non_hidden}"

async def give_ach(guild_int: int, member_id: int, channel: discord.TextChannel, ach: str, remove=False, send_embed=True):
    remove = not remove
    db['guilds'][str(guild_int)]['users'][str(member_id)]['achs'][str(ach)] = remove
    if remove and send_embed:
        ach_data = ach_list[ach]
        embed = discord.Embed(title=ach_data["title"], description=ach_data["description"], color=0x007F0E).set_author(name="Achievement get!", icon_url="https://pomf2.lain.la/f/hbxyiv9l.png")
        await channel.send(embed=embed)

@tasks.loop(seconds = 10)
async def automatic_database_save():
    save_db()

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"/help | Providing life support for {len(bot.guilds)} servers"
        )
    )
    for guild in bot.guilds:
        register_guild(guild.id)
        for user in guild.members:
            register_member(guild.id, user.id)
    automatic_database_save.start()
    print(f"bot has been started in {time.time()-time_before_start:.2f}s")

@bot.event
async def on_guild_join(guild: discord.Guild):
    register_guild(guild.id)
    for member in guild.members:
        register_member(guild.id, member.id)

@bot.slash_command(description="Send Help")
async def help(message: discord.Interaction):
	embedVar = discord.Embed(
		title="Send Help", description=discord.utils.get(bot.get_guild(GUILD_ID).emojis, name="staring_cat"), color=0x6E593C
	).add_field(
		name="Cat Hunt Commands",
		inline=False,
		value="**/inv** - your cats\n**/leaderboards** - da cat leaderboad\n**/donate** - donate your cats to another person\n**/achs** - view your achievements\n**/feedback** - give suggestions, report bugs, and everything in between",
	).add_field(
		name="Info Commands",
		inline=False,
		value="**/random** - get random cat image\n**right click > apps > catch** - catch someone in 4k\n**/tiktok** - read message as tiktok woman tts\n**/help** - this command\n**/admin** - help for server admins\n**/cat** - get staring cat image\n**/info** - get info bout bot and credits",
	)
	await message.response.send_message(embed=embedVar)

@bot.slash_command(description="Give feedback, report bugs or suggest ideas")
async def feedback(message: discord.Interaction, feedback: str):
	if len(str(message.user) + "\n" + feedback) >= 2000:
		await message.response.send_message("ah hell nah man, ur msg is too long :skull:", ephemeral=True)
		return
	milenakoos = await bot.fetch_user(OWNER_ID)
	await milenakoos.send(str(message.user) + "\n" + feedback)
	await message.response.send_message("your feedback was directed to the bot owner!", ephemeral=True)

@bot.slash_command(description="View admin help", default_member_permissions=8)
async def admin(message: discord.Interaction):
	embedVar = discord.Embed(
		title="Send Admin Help", description=discord.utils.get(bot.get_guild(GUILD_ID).emojis, name="staring_cat"), color=0x6E593C
	).add_field(name="Admin Commands", value="**/setup** - makes cat bot send cats in the channel this command is ran in\n**/forget** - reverse of /setup (i forgor :skull:)\n**/summon** - makes cats disappear and reappear out of thin air\n**/giveach** - gib (or take) achievements to people\n**/force** - makes cat appear in chat\n**/say** - chat as cat\n**/reset** - fully resets one's account")
	await message.response.send_message(embed=embedVar)

@bot.slash_command(description="View information about the bot")
async def info(message: discord.Interaction):
	embedVar = discord.Embed(title="Cat Bot", color=0x6E593C, description="[Join support server](https://discord.gg/WCTzD3YQEk)\n[GitHub Page](https://github.com/milena-kos/catbot)\n\nBot made by Milenakos#3310\nThis bot adds Cat Hunt to your server with many different types of cats for people to discover! People can see leaderboards and give cats to each other.\n\nThanks to:\n**???** for the cat image\n**SLOTHS2005#1326** for getting troh to add cat as an emoji\n**aws.random.cat** for random cats API\n**@weilbyte on GitHub** for TikTok TTS API\n**TheTrashCell#0001** for making cat, suggestions, and a lot more.\n\n**CrazyDiamond469#3422, Phace#9474, SLOTHS2005#1326, frinkifail#1809, Aflyde#3846, TheTrashCell#0001 and Sior Simotideis#4198** for being test monkeys\n\n**And everyone for the support!**")
	await message.response.send_message(embed=embedVar)

@bot.slash_command(description="Read text as TikTok's TTS woman")
async def tiktok(message: discord.Interaction, text: str):
	stuff = requests.post("https://tiktok-tts.weilnet.workers.dev/api/generation", headers={"Content-Type": "application/json"}, json={"text": text, "voice": "en_us_002"})
	try:
		data = "" + stuff.json()["data"]
	except TypeError:
		await message.response.send_message("i dont speak your language (remove non-english characters)", ephemeral=True)
		return
	with open("result.mp3", "wb") as f:
		ba = "data:audio/mpeg;base64," + data
		f.write(base64.b64decode(ba))
	file = discord.File("result.mp3", filename="result.mp3")
	await message.response.send_message(file=file)

@bot.slash_command(description="Get Daily cats")
async def daily(message: discord.Interaction):
	await message.response.send_message("there is no daily cats why did you even try this")
	await give_ach(message.guild_id, message.user.id, message.channel, "daily")

@bot.slash_command(description="View your inventory")
async def inv(message: discord.Interaction, user: Optional[discord.Member] = discord.SlashOption(required=False)):
    if user is None:
        self_see = True
        user = message.user
    else:
        self_see = False
    await message.response.defer()
    
    ach_text = await get_ach_text(message.guild_id, user.id)
    
    catch_time = await get_fastest(message.guild_id, user.id)
    slow_time = await get_slowest(message.guild_id, user.id)
    
    if self_see:
        your = "Your"
    else:
        your = user.name + "'s"
    
    embedVar = discord.Embed(
		title=your + " cats:", description=f"{your} fastest catch is: {catch_time // 1000} s\nand {your} slowest catch is: {slow_time // 1000} h\nAchievements unlocked: {ach_text}", color=0x6E593C
	)
    
    user_cats: dict[str, int] = {}
    
    db_cats = await get_cats(message.guild_id, user.id)
    
    for cat_name, cat_amount in db_cats.items():
        if cat_amount >= 0:
            user_cats[cat_name] = cat_amount

    if len(user_cats) >= 0:
        pass
    else:
        embedVar.add_field(name="None", value="u hav no cats :cat_sad:", inline=True)

    await message.followup.send(embed=embedVar)
    
    if self_see and len(db_cats) == len(cats):
        await give_ach(message.guild_id, user.id, message.channel, "collecter")
    if self_see and catch_time <= 5000:
        await give_ach(message.guild_id, user.id, message.channel, "fast_catcher")
    if self_see and slow_time >= 3600000:
        await give_ach(message.guild_id, user.id, message.channel, "slow_catcher")

@bot.slash_command(description="View list of achievements names", default_member_permissions=8)
async def achlist(message: discord.Interaction):
    stringify = ""
    for k,v in ach_list.items():
        stringify = stringify + k + " - " + v["title"] + "\n"
    embed = discord.Embed(title="Ach IDs", description=stringify, color=0x6E593C)
    await message.response.send_message(embed=embed)

@bot.slash_command(description="Pong")
async def ping(message: discord.Interaction):
	await message.response.send_message(f"cat has brain delay of {round(bot.latency * 1000)} ms " + str(discord.utils.get(bot.get_guild(GUILD_ID).emojis, name="staring_cat")))

@bot.slash_command(description="Get Cat")
async def cat(message: discord.Interaction):
	file = discord.File("cat.png", filename="cat.png")
	await message.response.send_message(file=file)

@bot.slash_command(description="Get Cursed Cat")
async def cursed(message: discord.Interaction):
	file = discord.File("cursed.jpg", filename="cursed.jpg")
	await message.response.send_message(file=file)

@bot.slash_command(description="Get Your balance")
async def bal(message: discord.Interaction):
	file = discord.File("money.png", filename="money.png")
	embed = discord.Embed(title="cat coins", color=0x6E593C).set_image(url="attachment://money.png")
	await message.response.send_message(file=file, embed=embed)

@bot.message_command()
async def pointLaugh(message: discord.Interaction, msg):
	icon = discord.utils.get(bot.get_guild(GUILD_ID).emojis, name="pointlaugh")
	await msg.add_reaction(icon)
	await message.response.send_message(icon, ephemeral=True)

@bot.slash_command(description="Say stuff as cat", default_member_permissions=8)
async def say(message: discord.Interaction, text: str):
	await message.response.send_message("success", ephemeral=True)
	await message.channel.send(text)

try:
    bot.run(TOKEN)
except Exception as e:
    save_db() # save if exception occured
    raise e
save_db() # save if exited succesfully