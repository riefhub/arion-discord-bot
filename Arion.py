import discord
from discord.ext import commands, tasks
import datetime
import json
import pytz

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Store birthday data
BIRTHDAYS_FILE = 'birthdays.json'

try:
    with open(BIRTHDAYS_FILE, 'r') as f:
        birthdays = json.load(f)
except FileNotFoundError:
    birthdays = {}

# Save birthdays to file
def save_birthdays():
    with open(BIRTHDAYS_FILE, 'w') as f:
        json.dump(birthdays, f)

@bot.event
async def on_ready():
    print(f'Bot is ready: {bot.user.name}')
    check_birthdays.start()

@bot.command()
async def addbirthday(ctx, member: discord.Member, date: str):
    """Add a birthday for a team member. Format: DD-MM-YYYY"""
    try:
        # Validate date format
        datetime.datetime.strptime(date, '%d-%m-%Y')
        
        birthdays[str(member.id)] = {
            'name': member.name,
            'date': date,
            'channel_id': ctx.channel.id
        }
        save_birthdays()
        await ctx.send(f"Birthday added for {member.name}: {date}")
    except ValueError:
        await ctx.send("Invalid date format. Please use DD-MM-YYYY")

@bot.command()
async def listbirthdays(ctx):
    """List all registered birthdays"""
    if not birthdays:
        await ctx.send("No birthdays registered!")
        return

    message = "**Registered Birthdays:**\n"
    for user_id, data in birthdays.items():
        message += f"• {data['name']}: {data['date']}\n"
    await ctx.send(message)

@bot.command()
async def removebirthday(ctx, member: discord.Member):
    """Remove a birthday entry"""
    if str(member.id) in birthdays:
        del birthdays[str(member.id)]
        save_birthdays()
        await ctx.send(f"Birthday removed for {member.name}")
    else:
        await ctx.send(f"No birthday registered for {member.name}")

@tasks.loop(hours=24)
async def check_birthdays():
    # Set timezone to your local timezone
    tz = pytz.timezone('Asia/Jakarta')  # Change this to your timezone
    today = datetime.datetime.now(tz).strftime('%d-%m')
    
    for user_id, data in birthdays.items():
        birthday = datetime.datetime.strptime(data['date'], '%d-%m-%Y').strftime('%d-%m')
        
        if birthday == today:
            channel = bot.get_channel(data['channel_id'])
            if channel:
                embed = discord.Embed(
                    title="🎉 Happy Birthday! 🎂",
                    description=f"Happy birthday to {data['name']}! 🎈",
                    color=discord.Color.purple()
                )
                embed.add_field(
                    name="Wishes", 
                    value="Wishing you a fantastic day filled with joy and celebration! 🎊"
                )
                await channel.send(embed=embed)

@check_birthdays.before_loop
async def before_check_birthdays():
    await bot.wait_until_ready()

# Token
bot.run('your token')

