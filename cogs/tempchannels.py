import discord
from discord.ext import commands

import sys
import datetime

temp_channels = {}

class TempChannels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def create_temp_channel(self, member, voice_channel):
        """
        Autocreates a temporary text channel the first time someone joins a voice channel.
            Parameters:
                member (class discord.Member): the user who has joined a voice channel.
                voice_channel (class discord.VoiceChannel): the joined discord voice channel.
            Returns:
                id (int): the channel ID of the newly created channel.
        """
        try:
            guild = member.guild
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True),
                self.bot.user: discord.PermissionOverwrite(view_channel=True, manage_channels=True)
            }

            temp_ch = await guild.create_text_channel(str(voice_channel.name) + " temp", overwrites=overwrites,
                                                      category=voice_channel.category)
            await temp_ch.send(
                        "This is a temporary channel. This text channel will "
                        + "disappear when all users leave the voice channel."
                        )
            return temp_ch.id
        except discord.Forbidden:
            print('Bot does not have the proper permissions to create this channel.')
        except:
            print(f'Unexpected error when creating temporary channel: {sys.exc_info()[0]}')

    async def update_temp_channel_permissions(self, member, channel, view_permissions=True):
        """
        Updates permissions when someone joins or leaves a voice channel.
            Parameters:
                member (class discord.Member): the user who has joined/left a voice channel.
                channel (class discord.abc.GuildChannel): the VoiceChannel the member has joined or
                                                        left.
                view_permissions (bool): whether the member should gain (True) or lose (False) view
                                        permissions of the channel
            Returns:
        """
        # get the temp ch id value from associated voice channel key and update permissions
        temp_ch_id = temp_channels.get(channel.id)
        if temp_ch_id is not None:
            temp_ch = channel.guild.get_channel(temp_ch_id)
            overwrite = discord.PermissionOverwrite()
            overwrite.view_channel = view_permissions
            try:
                await temp_ch.set_permissions(member, overwrite=overwrite)
            except discord.Forbidden:
                print('Bot does not have proper permissions to manage this channel.')
            except (discord.HTTPException, discord.NotFound, discord.InvalidArgument) as err:
                print(f'The channel was not found, or setting permissions failed: {err}.')
        else:
            print('Could not find corresponding temporary channel (temp channel ID is '
                + f'{temp_ch_id}).')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, prev_state, new_state):
        """
        Triggers when someone joins or leaves a voice channel.
            Parameters:
                member (class discord.Member): the user who has changed state in a voice channel.
                prev_state (class discord.VoiceState): the user's previous voice state.
                new_state (class discord.VoiceState): the user's current (new) voice state.
            Returns: None
        """

        if prev_state.channel != new_state.channel:

            if new_state.channel is not None: # user joins channel

                if len(new_state.channel.members) == 1:
                    # user is the only one in the channel they joined
                    # create temp channel. Add to dict with voice ch ID as key and text ch ID as value
                    temp_channels[new_state.channel.id] = await self.create_temp_channel(
                        member, new_state.channel)
                    print(f'Created a temporary channel at {datetime.datetime.now()}.')

                # give user permissions to see temp channel
                await self.update_temp_channel_permissions(member, new_state.channel, view_permissions=True)

            if prev_state.channel is not None: # user left channel

                if len(prev_state.channel.members) == 0:
                    # user left a channel that is now empty
                    # get the temp ch id value from associated voice channel key and delete
                    # the temp channel
                    temp_ch_id = temp_channels.get(prev_state.channel.id)
                    if temp_ch_id is not None:
                        try:
                            await prev_state.channel.guild.get_channel(temp_ch_id).delete()
                        except discord.Forbidden:
                            print('Bot does not have the proper permissions to delete this channel.')
                        except (discord.NotFound, discord.HTTPException) as err:
                            print(f'The channel was not found, or deletion failed: {err}.')

                else:
                    # user left channel but channel still has members; remove their permissions
                    await self.update_temp_channel_permissions(member, prev_state.channel, view_permissions=False)

def setup(bot):
    bot.add_cog(TempChannels(bot))