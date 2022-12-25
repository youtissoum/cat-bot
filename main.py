import nextcord as discord
from nextcord.ext import commands, tasks
import os, sys, time, json

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
bot = commands.Bot(command_prefix="idk how this works but you need to have spaces in it or it may crash", help_command=None, intents=intents)

def save_db():
    with open("backup", "w") as f:
        f.write(str(db))
    with open("db.json", 'w') as f:
        f.write(json.dumps(db))

def register_member(guild_id: int, user_id: int):
    if db['guilds'][str(guild_id)].get(str(user_id)) is None:
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
        save_db()

def register_guild(guild_id: int):
    if db['guilds'].get(str(guild_id)) is None:
        db['guilds'][str(guild_id)] = {
            "users": {},
            "channel": None
        }
        save_db()

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

try:
    bot.run(TOKEN)
except Exception as e:
    save_db() # save if exception occured
    raise e
save_db() # save if exited succesfully