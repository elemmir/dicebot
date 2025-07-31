import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
bot_token = os.getenv("DISCORD_TOKEN")

# --- Bot Setup ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Cog Loading
initial_extensions = [
    'cogs.pnp'
]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Discord.py API version: {discord.__version__}')

    # Set Bot Status
    game = discord.Game("Prowlers & Paragons: Ultimate Edition")
    await bot.change_presence(status=discord.Status.online, activity=game)

    # Load cogs
    print("Loading cogs...")
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"Successfully loaded extension: {extension}")
        except Exception as e:
            import traceback
            print(f'Failed to load extension {extension}.')
            traceback.print_exc()

    # Sync Slash Commands
    print("Syncing commands...")
    try:

        # Global Command Sync:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) globally.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Run Bot
if bot_token:
    bot.run(bot_token)
else:
    print("Error: DISCORD_TOKEN environment variable not set or token is missing.")