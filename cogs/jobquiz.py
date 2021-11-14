from discord.ext import commands
# from discord import Embed
from discord import RawReactionActionEvent
import asyncio
import csv
import os 
# from private.config import reaction_roles



class JobQuiz(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.emojis = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣'] #'<:fellcleave:886051923977994260>'
        self.users = {}
        self.CSV_PATH = os.path.join(os.getcwd(), "personalitytypes.csv")
        
        with open(self.CSV_PATH, 'r', newline='') as f:
            self.jobs = list(csv.reader(f))
        f.close()

    def check_author(self, message, ctx): #makes sure that the person who requested confirms
        return message.author == ctx.author

    def sum_digits(self, digits): 
        return digits[4]*1 + digits[3]*2+ digits[2]*4+ digits[1]*8+ digits[0]*16

    async def question_response(self, ctx, q):
        # embed = Embed(title='question')
        message = await ctx.author.send(q) #embed=embed
        for emoji in self.emojis:
            await message.add_reaction(emoji)
        return message
    
    async def process_add_reaction(self, payload: RawReactionActionEvent, ctx, message, q_idx=None):
        # idx is the index of the question to which user is replying. Overwrites other responses.
        # await payload.member.send(f"{payload.user_id}")
        # print("reaction detected.")
        # print(f"{payload.user_id}")
        
        if payload.user_id==ctx.author.id and q_idx != None:
            # print("a")
            for e_idx, e in enumerate(self.emojis):
                if payload.emoji.name == e:     
                    # print("b")       
                    self.users[payload.user_id][q_idx] = int(e_idx*0.35) #if <= 2, replace with 0; otherwise 1; if all fellcleave, 2
                    # print(self.users[payload.user_id])
                    return True
        elif payload.user_id==ctx.author.id and q_idx != None:
            print('please react to the right message.') 
        elif q_idx == None:
            print(f"{q_idx}")
            return False
        else:
            print("User ID not found.")
            return False
    
    # def calculate_result(self):

    @commands.command(name="startquiz", aliases=["jobquiz", "quiz"])
    async def job_quiz(self, ctx):
        questions = [
            "At social events, you rarely try to introduce yourself to new people and mostly talk to the ones you already know.", #E (0) or I (5)
            "You spend a lot of your free time exploring various random topics that pique your interest.", #S or N (5)
            "You are more inclined to follow your head than your heart.", #F or T (5)
            "You often make a backup plan for a backup plan.", #P (0) or J (5)
            "You rarely worry about whether you make a good impression on people you meet.", #T or A (5)
        ]
        # add user to dictionary, with empty array which we will populate with responses
        self.users[ctx.author.id] = [None]*5

        await ctx.author.send("Hi, welcome to the job quiz! This is just for fun!")
        await ctx.author.send("I'm going to ask five questions. Please choose a number "+
                              "between 0 (I strongly disagree with this statement) and 5 (I strongly " +
                              "agree with this statement).")
        await ctx.author.send("(Please also be nice to the bot, and wait " +
                              "until all reactions have appeared to choose your answer.)")
        await ctx.author.send("First question...")

        for idx, q in enumerate(questions):
            message = await self.question_response(ctx, q)

            def check_response(payload):
                return payload.user_id == ctx.author.id and payload.message_id==message.id 

            try:
                # returns RawReactionActionEvent
                reaction = await self.bot.wait_for('raw_reaction_add', check=check_response)
                # append numerical response to the author's list
                await self.process_add_reaction(reaction, ctx, message, idx)
            except asyncio.TimeoutError:
                await ctx.author.send("No response... please select a number to continue (or wait until all numbers are posted before reacting)!")
        
        if None not in self.users[ctx.author.id]:
            type_nb = self.sum_digits(self.users[ctx.author.id])
            print(type_nb)
            # print(self.jobs)
            await ctx.author.send(self.jobs[type_nb][1])

                

        # await ctx.author.send(q)

    # @commands.Cog.listener()
    # async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
    #     if payload.user_id != self.bot.user.id:
    #         await self.process_reaction(payload)
        # print("reaction add event.")

    # @commands.Cog.listener()
    # async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
    #     await self.process_reaction(payload, "remove")


def setup(bot):
    bot.add_cog(JobQuiz(bot))