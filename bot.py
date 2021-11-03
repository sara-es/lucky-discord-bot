import discord
from discord.ext import commands
from private.config import token
from private.config import reaction_roles

class LuckyBot(commands.Bot):

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_command_error(self, ctx, error):
        print(error)
        await ctx.send("I'm sorry, that didn't work. See ``!help`` for more info on this bot.")

intents = discord.Intents.default()
intents.reactions = True

bot = LuckyBot(command_prefix='!', intents=intents)
initial_extensions = [
    'cogs.tempchannels', 
    'cogs.reactionroles', 
    'cogs.ffcards', 
    'cogs.frcards',]

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)
        
# bot.add_cog(TempChannels(bot))
# bot.add_cog(ReactionRoles(bot))
# bot.add_cog(FFCards(bot))

bot.run(token)