import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import asyncio
import random
import json

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot




    @commands.Cog.listener()
    async def on_ready(self):
        print("Giveaways are now ready!")


    def convert(self, time):
        pos = ["s","m","h","d"]

        time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

        unit = time[-1]

        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2

        return val * time_dict[unit]
        
    def dump(self,id, dur, ended, deleted, chann, prize):
    	with open("data/gw.json","r") as f:
    		gg = json.load(f)
    	
    	gg[str(id)] = {
    					"ended": ended,
    					"deleted": deleted,
    					"chann": chann,
    					"dur": dur,
    					"prize": prize
    	}
    	
    	with open("data/gw.json", "w") as f:
    		json.dump(gg,f, indent=4)
    		
    	
    	
    def get_ch(self, id):
    	with open("data/gw.json","r") as f:
    		ih = json.load(f)
    		
    	if str(id) in ih:
    		hh = ih[str(id)]
    		if hh["deleted"] == "y":
    			return "del"
    		elif hh["ended"] == "y":
    			return "une"
    		else:
    			ok = hh["chann"]
    			return ok
    	else:
    		return "nil"
    	

		
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def gstart(self, ctx):
        await ctx.send("Let's start with this giveaway! Answer these questions within 15 seconds!")

        questions = ["Which channel should it be hosted in?",
                    "What should be the duration of the giveaway? (s|m|h|d)",
                    "What is the prize of the giveaway?"]

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i in questions:
            await ctx.send(i)

            try:
                msg = await self.bot.wait_for('message', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("You didn't answer in time, please be quicker next time!")
                return
            else:
                answers.append(msg.content)

        try:
            c_id = int(answers[0][2:-1])
        except:
            await ctx.send(f"You didn't mention a channel properly. Do it like this {ctx.channel.mention} next time.")
            return

        channel = self.bot.get_channel(c_id)

        time = self.convert(answers[1])
        if time == -1:
            await ctx.send(f"You didn't answer the time with a proper unit. Use (s|m|h|d) next time!")
            return
        elif time == -2:
            await ctx.send(f"The time must be an integer. Please enter an integer next time")
            return

        prize = answers[2]

        # send a message for the user to know the giveaway started!
        await ctx.send(f"The Giveaway will be in {channel.mention} and will last {answers[1]}!")
        # now send the embed in the channel!
        embed = discord.Embed(title = "Giveaway!", description = f"{prize}", color = ctx.author.color)
        embed.add_field(name = "Hosted by:", value = ctx.author.mention)
        embed.set_footer(text = f"Ends {answers[1]} from now!")
        my_msg = await channel.send(embed = embed)
        # and then add the reactions
        await my_msg.add_reaction('🎉')
        self.dump(my_msg.id, time, "n", "n", channel.id, prize)
        # sleep for the time!
        await asyncio.sleep(time)
        
        with open("data/gw.json","r") as f:
        	kk = json.load()
        
        wow = kk[str(my_msg.id)]
        
        if wow["ended"] == "y":
        	return
        elif wow["deleted"] == "y":
        	return
        else:
	        # and then fetch it back
	        new_msg = await channel.fetch_message(my_msg.id)
	        # get a list of users
	        users = await new_msg.reactions[0].users().flatten()
	        users.pop(users.index(self.bot.user))
	        winner = random.choice(users)
	        # now have some checks
	        if len(users) == 0:
	            em = discord.Embed(title = 'Giveaway Failed', color = ctx.author.color)
	            em.add_field(name = "Reason:", value = "No one joined")
	            em.add_field(name = "Next steps:", value = "Dont make a giveaway which you don't enter!")
	            await channel.send(embed = em)
	            return
	
	        # edit embed to show winner
	        newembed = discord.Embed(title = "Giveaway Ended!", description = f"{prize}", color = ctx.author.color)
	        newembed.add_field(name = "Hosted by:", value = ctx.author.mention)
	        # now do winers gizmo
	        newembed.add_field(name = "Winner", value = f"{winner.mention}")
	        await my_msg.edit(embed = newembed)
	        await channel.send(f"Congratulations! {winner.mention} won {prize}!")
	        self.dump(my_msg.id, time, "y", "n", prize)
	
    @gstart.error
    async def gstart_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title = "Can't start giveaway", color = ctx.author.color)
            embed.add_field(name = "Reason:", value = "`Administrator Permission is missing!`")
            embed.add_field(name = "Ideal Solution:", value = "Get the perms, lmao!")
            await ctx.send(embed = embed)

    @commands.command()
    @has_permissions(administrator = True)
    async def greroll(self,ctx, id_ : int):
    	with open("data/gw.json","r") as f:
    		tin = json.load(f)
    	
    	ih = tin
    	
    	if str(id_) in ih:
    		hh = ih[str(id_)]
    		if hh["deleted"] == "y":
    			await ctx.send("This giveaway has been deleted")
    		elif hh["ended"] == "n":
    			await ctx.send("This giveaway has not been ended")
    		else:
    			ok = hh["chann"]
    			
    	else:
    		await ctx.send("Incorrect id was entered")
    		ok = "lol"
    		
    	if ok == "lol":
    		return
    	else:
    		che = self.bot.get_channel(int(ok))
    		my_msg = await che.fetch_message(id_)
    		
    		kk = tin[str(id_)]
    		prize = kk["prize"]
    		
    		users = await my_msg.reactions[0].users().flatten()
    		users.pop(users.index(self.bot.user))
    		
    		winner = random.choice(users)
    		await che.send(f"Congratulations! The new winner is {winner.mention}!")
    		
    		if len(users) == 0:
    		    em = discord.Embed(title = 'Giveaway Failed', color = ctx.author.color)
    		    em.add_field(name = "Reason:", value = "No one joined")
    		    em.add_field(name = "Next steps:", value = "Dont make a giveaway which you don't enter!")
    		    await che.send(embed = em)
    		    return
    		
    		prize = hh["prize"]
    		time = hh["dur"]
    		newembed = discord.Embed(title = "Giveaway Ended!", description = f"{prize}", color = ctx.author.color)
    		newembed.add_field(name = "Hosted by:", value = ctx.author.mention)
    		newembed.add_field(name = "Winner", value = f"{winner.mention}")
    		await my_msg.edit(embed = newembed)
    		self.dump(my_msg.id, time, "y", "n", prize)

        






    @greroll.error
    async def reroll_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title = "Can't reroll giveaway", color = ctx.author.color)
            embed.add_field(name = "Reason:", value = "`Administrator is missing!`")
            embed.add_field(name = "Ideal Solution:", value = "Get the perms, lmao!")
            await ctx.send(embed = embed)
        
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def gend(self, ctx, id_: int):
    	with open("data/gw.json","r") as f:
    		tin = json.load(f)
    	
    		
    		
    	tingd = self.get_ch(id_)
    	
    	
    	
    	if tingd == "nil":
    		await ctx.send("Incorrect id was entered")
    	elif tingd == "une":
    		await ctx.send("This giveaway has already been ended")
    	elif tingd == "del":
    		await ctx.send("This giveaway has been deleted")
    	else:
    		
    		che = self.bot.get_channel(int(tingd))
    		my_msg = await che.fetch_message(id_)
    		
    		kk = tin[str(id_)]
    		prize = kk["prize"]
    		
    		users = await my_msg.reactions[0].users().flatten()
    		users.pop(users.index(self.bot.user))
    		
    		winner = random.choice(users)
    	 		
    		if len(users) == 0:
    		    em = discord.Embed(title = 'Giveaway Failed', color = ctx.author.color)
    		    em.add_field(name = "Reason:", value = "No one joined")
    		    em.add_field(name = "Next steps:", value = "Dont make a giveaway which you don't enter!")
    		    await che.send(embed = em)
    		    return
    		
    		newembed = discord.Embed(title = "Giveaway Ended!", description = f"{prize}", color = ctx.author.color)
    		newembed.add_field(name = "Hosted by:", value = ctx.author.mention)
    		newembed.add_field(name = "Winner", value = f"{winner.mention}")
    		await my_msg.edit(embed = newembed)
    		await che.send(f"Congratulations! {winner.mention} won {prize}!")
    		time = "ended"
    		self.dump(my_msg.id, time, "y", "n", che.id, prize)
    		
    @gend.error
    async def gend_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title = "Can't end giveaway", color = ctx.author.color)
            embed.add_field(name = "Reason:", value = "`Administrator is missing!`")
            embed.add_field(name = "Ideal Solution:", value = "Get the perms, lmao!")
            await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Giveaways(bot))
