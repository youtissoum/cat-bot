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
    ach_list = json.loads(f.read())

with open("cats.json", "r") as f:
    cats = json.loads(f.read())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="idk how this works but you need to have spaces in it or it may crash", help_command=None, intents=intents)

def save_db():
    with open("backup", "r") as f:
        f.write(str(db))
    with open("db.json", 'w') as f:
        f.write(json.dumps(db))

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
    automatic_database_save.start()
    print(f"bot has been started in {time.time()-time_before_start:.2f}s")

try:
    bot.run(TOKEN)
except Exception as e:
    save_db() # save if exception occured
    raise e
save_db() # save if exited succesfully