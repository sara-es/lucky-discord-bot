redirect_uri = "http://localhost:8080"

import re
import discord
from discord.ext import commands
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse

from private.config import fflog_id
from private.config import fflog_secret

# from oauthlib.oauth2 import WebApplicationClient
# from flask import Flask, request, redirect, session

# ensures HTTPS
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

url = "https://www.fflogs.com/api/v2/client"
credentials = {fflog_id : fflog_secret}
authorization_base_url = 'https://fflogs.com/oauth/authorize'
token_url = 'https://www.fflogs.com/oauth/token'
# response = requests.post(url, data = grant_type=client_credentials, auth = credentials)
auth_data = {
    'client_id': fflog_id,
    'client_secret': fflog_secret,
    'grant_type': 'authorization_code',
  }

class FFCards(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def callback(self, session, requested_data):
        # Oauth2 authentication via client credentials
        client = BackendApplicationClient(client_id=fflog_id)
        fflogs = OAuth2Session(client=client)
        token = fflogs.fetch_token(
            token_url, 
            client_id=fflog_id,
            client_secret=fflog_secret
        )

        session['oauth_token'] = token
        api_call_headers = {
            'Authorization': 'Bearer ' + token['access_token'],  
            'Content-Type': 'application/json'
            }

        data = fflogs.get("https://www.fflogs.com/api/v2/client",
                          headers=api_call_headers, data=requested_data)    
        
        # if data.status_code == 400:
        #     await ctx.reply("Requested data not found.")
        if data.status_code != 200:
            print(data.reason)
            return None
        
        return data

    @commands.command(name="get")
    async def getparse(self, ctx, server, firstname, lastname):
        session = {}
        character_name = firstname + ' ' + lastname
        server = server

        requested_data = "{\"query\":\"{\\n  characterData {\\n    character(name: \\\""+ character_name +"\\\", serverSlug: \\\""+server+"\\\", serverRegion: \\\"EU\\\"){\\n      zoneRankings \\n    }\\n  }\\n}\\n\"}"
        data = self.callback(session, requested_data)

        if data is None:
            await ctx.reply("Error requesting data from FFlogs.")
        else: 
            # print(data.content)
            # print(data.text)
            # print(data.json())
            jdata = data.json()
            
            character_data = jdata["data"]["characterData"]["character"]["zoneRankings"]["bestPerformanceAverage"]
            # print(character_data)

            reply_text = (
                f"Character: {character_name} ({server}) \n" +
                f"Current tier best perfomance average: {character_data}" +
                " "
            )
            await ctx.reply(reply_text)
    
    @commands.command(name="emojis")
    async def emojis(self, ctx):
        for emoji in ctx.guild.emojis:
            print(f"<:{emoji.name}:{emoji.id}>")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.content.startswith('https://www.fflogs.com/reports'):
            return
        
        session = {}

        # get parse ID from url
        url = urlparse(message.content.split(' ')[0])
        report_id = url.path.split('/')[-1]
        # print(report_id)

        match = re.search('fight=(\d+)', url.fragment) # I hate regex
        if match:
            fight_id = match.group(1) # I really hate regex
            # print(fight_id)

            requested_data = "{\"query\":\"{\\n  reportData {\\n    report(code: \\\""+ str(report_id) +"\\\"){\\n      rankings(fightIDs: ["+ str(fight_id) +"], timeframe: Historical)\\n    }\\n  }\\n}\\n\"}"
        else: 
            requested_data = "{\"query\":\"{\\n  reportData {\\n    report(code: \\\""+ str(report_id) +"\\\"){\\n      rankings(timeframe: Historical)\\n    }\\n  }\\n}\\n\"}"
        # else:
        #     # get fight ids of cleared fights 
        #     requested_data = "{\"query\":\"{\\n  reportData {\\n    report(code: \\\""+ str(report_id) +"\\\"){\\n      fights(killType: Kills){\\n        id\\n      }\\n    }\\n  }\\n}\\n\"}"
        #     data = self.callback(session, requested_data)
        #     if data is None: 
        #         print("Error requesting data from FFLogs.")
        #         return
            
        #     jdata = data.json()
        #     fight_ids_dict = jdata["data"]["reportData"]["report"]["fights"]
        #     fight_ids = []
        #     for i in range(len(fight_ids_dict)):
        #         fight_ids.append(fight_ids_dict[i]["id"]) 
        #     print(fight_ids)

        #     # pick out the ID of the last cleared fight in log
        #     fight_id = fight_ids[-1]
        #     print("last fight id " + str(fight_id))

        # get ranking data by fight id
        
        # print(requested_data)

        data = self.callback(session, requested_data)   
        if data is None: 
                print("Error requesting data from FFLogs.")
                return    
        
        jdata = data.json()

        icons = {
            # "Warrior" : "<:Warrior_Icon_1:883379748997324890>",
            "Warrior" : "<:40pxWarrior_Icon_8:883379748737269810>",
            "Dragoon" : "<:40pxDragoon_Icon_8:883379748519170130>",
            "Ninja" : "<:40pxNinja_Icon_8:883379748531753061>",
            "BlackMage" : "<:40pxBlack_Mage_Icon_8:883379748628230144>",
            "Monk" : "<:40pxMonk_Icon_8:883379748670169148>",
            "RedMage": "<:40pxRed_Mage_Icon_8:883379748686942248>",
            "Gunbreaker" : "<:40pxGunbreaker_Icon_8:883379748703731762>",
            # "Gunbreaker" : "<:32pxGunbreaker_Icon_1:883379748686942218>",
            "Bard" : "<:40pxBard_Icon_8:883379748720480276>",
            "Paladin" : "<:40pxPaladin_Icon_8:883379748733083708>",
            "Astrologian" : "<:40pxAstrologian_Icon_8:883379748745670657>",
            "Dancer" : "<:40pxDancer_Icon_8:883379748745670707>",
            "WhiteMage" : "<:40pxWhite_Mage_Icon_8:883379748770832424>",
            "DarkKnight" : "<:40pxDark_Knight_Icon_8:883379748779225128>",
            "Summoner" : "<:40pxSummoner_Icon_8:883379748783423538>",
            "Scholar" : "<:40pxScholar_Icon_8:883379748800200764>",
            "Machinist" : "<:40pxMachinist_Icon_8:883379748825362502>",
            "Samurai" : "<:40pxSamurai_Icon_8:883379748997304320>",
        }

        # get the last cleared if multiple fights
        data_path = jdata['data']['reportData']['report']['rankings']['data'][-1]
        
        
        encounter_name = data_path['encounter']['name']
        if data_path["difficulty"] == "101":
            encounter_name += " (Savage)"
        if data_path["difficulty"] == "100":
            encounter_name += " (Extreme)"
            
        """
        # construct the reply text
        reply_text = ""
        reply_text += f"{encounter_name} \n"
        reply_text += "Percentiles listed are rankings for this parse (how it will appear on your profile)."

        for role in data_path['roles']:
            # print(role)
            for character in data_path["roles"][role]["characters"]:
                # for some reason fflogs api combines healer and tank damage as a character entry, so make sure the
                # character is unique by checking if they have a server
                if "server" in character:
                    if character["class"] in icons:
                        reply_text += f"**{character['rankPercent']}** {icons[character['class']]:<4}    {character['name']} \n"
                    else:
                        reply_text += f"     **{character['rankPercent']}**    {character['name']} ({character['class']}) \n"
        await message.channel.send(reply_text)
        """
        
        embed=discord.Embed(
            title=f"{encounter_name}", 
            url=url.geturl(),
            description="Percentiles listed are rankings for this parse (how it will appear on your profile)"
        )

        for role in data_path['roles']:
            # print(role)
            for character in data_path["roles"][role]["characters"]:
                # for some reason fflogs api combines healer and tank damage as a character entry, so make sure the
                # character is unique by checking if they have a server
                if "server" in character:
                    if character["class"] in icons:
                        embed.add_field(
                            name=f"{icons[character['class']]} **{character['rankPercent']}**", 
                            value=f"{character['name']}", 
                            inline=False
                        )
                        # reply_text += f"**{character['rankPercent']}** {icons[character['class']]} {character['name']} \n"
                    else:
                        embed.add_field(
                            name=f"  **{character['rankPercent']}**", 
                            value=f"{character['name']}", 
                            inline=False
                        )
                        # reply_text += f"     **{character['rankPercent']}**    {character['name']} ({character['class']}) \n"
        await message.channel.send(embed=embed)
        

def setup(bot):
    bot.add_cog(FFCards(bot))

