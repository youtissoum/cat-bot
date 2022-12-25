import nextcord as discord
from nextcord.ext import commands
import os, sys, time

time_before_start = time.time()

OWNER_ID = 553093932012011520 # for dms
GUILD_ID = 966586000417619998 # for emojis
BOT_ID = 966695034340663367

TOKEN = os.environ['token']

if TOKEN == None:
    print("Could not find token, exiting...")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="", help_command=None, intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"/help | Providing life support for {len(bot.guilds)} servers"
        )
    )
    print(f"bot has been started in {time.time()-time_before_start:.2f}s")

bot.run(TOKEN)