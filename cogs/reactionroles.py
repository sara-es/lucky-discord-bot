import discord
from discord.ext import commands
from private.config import reaction_roles

class ReactionRoles(commands.Cog, name="Roles"):
    """
    Handles reaction role events.
    """

    def __init__(self, bot):
        self.bot = bot

    async def process_reaction(self, payload: discord.RawReactionActionEvent, reaction_type=None):
        """
        A handler for RawReactionActionEvents that will assign or remove user roles based on reaction emoji.
            Parameters:
                payload (class discord.RawReactionActionEvent): the payload data from the discord API.
                reaction_type (str): whether the reaction was added or removed.
            Returns: None 
        """

        if payload.message_id in reaction_roles.keys():
            # check if we're watching this message's reactions
            for role_entry in reaction_roles[payload.message_id]:
                
                if role_entry[0] == payload.emoji.name: # if the emoji corresponds to a role

                    guild = self.bot.get_guild(payload.guild_id)
                    user = await guild.fetch_member(payload.user_id)
                    role = guild.get_role(role_entry[1])

                    if role is None:
                        print(f"An invalid role ID ({role_entry[0]}, {role_entry[1]}) was provided for"
                              f" message with ID: {payload.message_id}.")    

                    elif reaction_type == "add":
                        if role in user.roles:
                            await user.send("You already have that role. Remove your reaction to remove it.")                 
                        else:
                            try: 
                                # add the role and DM the user confirmation
                                await user.add_roles(role)
                                await user.send( 
                                    f"I've assigned you the {role.name} role. You'll be pinged for FC events "
                                    + "and other content. See you soon!")
                            except discord.Forbidden:
                                print("Bot does not have permissions to add this role.")
                            except discord.HTTPException:
                                print("HTTPException: adding roles failed.")

                    elif reaction_type == "remove":
                        try: 
                            await user.remove_roles(role)
                            await user.send(
                                    f"I've removed the {role.name} role. You won't be pinged for FC events, "
                                    + "but will still be able to check the #exile-fc-schedule channel for announcements.")
                        except discord.Forbidden:
                            print("Bot does not have permissions to remove or manage this role.")
                        except discord.HTTPException:
                            print("HTTPException: removing role failed.")

                    else:
                        print("Invalid reaction type was provided in `process_reaction`.")

                    break               

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self.process_reaction(payload, "add")
        # print("reaction add event.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self.process_reaction(payload, "remove")

def setup(bot):
    bot.add_cog(ReactionRoles(bot))            