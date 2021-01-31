import discord
from discord.ext import commands


bot=commands.Bot(command_prefix="G!")


@bot.event
async def on_ready():
    print("I am ready")



extensions=[
			'cogs.giveaway'
]
if __name__=="__main__":
	for extension in extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			print(f"error loading {extension}", file=sys.stderr)
			traceback.print_exc()



bot.run("Your Bot Token Goes Here")
#token
