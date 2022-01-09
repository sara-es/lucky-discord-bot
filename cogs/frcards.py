from time import time
from discord.ext import commands
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import datetime
from dateutil.relativedelta import relativedelta, TU
from dateutil import parser

from private.config import twitter_id
from private.config import twitter_secret
from private.config import twitter_bearer_token

class FashionReportCard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def callback(self, request_url_string, ): #payload=None
        # Oauth2 authentication via client credentials
        client = BackendApplicationClient(client_id=twitter_id)
        twitter = OAuth2Session(client=client)

        # session['oauth_token'] = token
        api_call_headers = {
            "Authorization": "Bearer " + twitter_bearer_token,  
            "User-Agent": "v2FilteredStreamPython"
            }

        data = twitter.get(f"https://api.twitter.com/2/{request_url_string}",
                          headers=api_call_headers, )    #payload=payload
        
        if data.status_code != 200:
            print(data.status_code)
            print(data.reason)
            return None
        
        return data

    # def fashion_report(self):
    #     userid = "4826718276"
    #     data = self.callback("tweets/search/recent?query=(fashion report) has:images from:KaiyokoStar -is:retweet")

    def set_stream_rules(self):
        rule = [
            {
                "value": "(fashion report) has:images from:KaiyokoStar -is:retweet",
                "tag": ""
            },
        ]
        payload = {"add": rule}
        response = self.callback("tweets/search/stream/rules", json=payload)
        if response.json()['meta']['summary']['created'] == 0:
            return 1
        else: return 0

    def get_next_reset(self):    
        next_reset = datetime.datetime.now() + relativedelta(hour=9, minute=0, weekday=TU(1))
        time_to_next_reset = relativedelta(next_reset, datetime.datetime.now())
        days = f"{time_to_next_reset.days} days, " if time_to_next_reset.days > 0 else ""
        hours = f"{time_to_next_reset.hours} hours, " if time_to_next_reset.hours > 0 else ""
        minutes = f"{time_to_next_reset.minutes} minutes" if time_to_next_reset.minutes > 0 else ""

        return f"Resets in {days}{hours}{minutes}."

    def get_last_reset(self):
        last_tuesday_reset = datetime.date.today() + relativedelta(weekday=TU(-1))

    @commands.command(name="fashionreport", aliases=['fr'])
    async def get_fr(self, ctx):
        data = self.callback("tweets/search/recent?query=(fashion report week) has:images from:KaiyokoStar -is:retweet&expansions=attachments.media_keys&media.fields=url&tweet.fields=created_at")
        """Example return: 
        {
            "data": [
                {
                    "attachments": {
                        "media_keys": [
                            "3_1454018852992393220"
                        ]
                    },
                    "id": "1454018883908608004",
                    "text": "Fashion Report Week 196 - Full Details #ffxiv #ff14 #ファッションチェック https://t.co/3yk3fmaWno"
                }
            ],
            "includes": {
                "media": [
                    {
                        "media_key": "3_1454018852992393220",
                        "type": "photo",
                        "url": "https://pbs.twimg.com/media/FC22cW1VIAQ5J67.jpg"
                    }
                ]
            },
            "meta": {
                "newest_id": "1454018883908608004",
                "oldest_id": "1454018883908608004",
                "result_count": 1
            }
        }
        """
        time_to_next_reset = self.get_next_reset()
        # print(data)

        if data is None:
            await ctx.reply("Error requesting data from Twitter.")
        else: jdata = data.json()
        if jdata["meta"]["result_count"] == 0:
            await ctx.reply("I can't find this week's fashion report, sorry! :(")
        else:
            # jdata = data.json()
            # print(jdata)
            post_time = jdata['data'][0]['created_at']
            last_tuesday_reset = datetime.date.today() + relativedelta(weekday=TU(-1))
            last_reset_iso = last_tuesday_reset.isoformat()

            # check to see if it's current for this week (after reset)
            if post_time > last_reset_iso: # can compare as strings
                retrieved_tweet_url = jdata['includes']['media'][0]['url']
                await ctx.reply(f"{time_to_next_reset} {retrieved_tweet_url}")
            else: 
                await ctx.reply("Fashion report for this week has not yet been posted. Please check back later.")
    
    @commands.command(name="fr-reminder")
    async def set_fr_reminder(self, ctx, on=True):
        self.set_stream_rules()


def setup(bot):
    bot.add_cog(FashionReportCard(bot))