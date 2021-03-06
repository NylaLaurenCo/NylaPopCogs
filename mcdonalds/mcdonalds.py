import asyncio
import json
import random
import math
import discord

from redbot.core import bank, commands
from redbot.core.commands import Cog
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.chat_formatting import humanize_number, humanize_timedelta, pagify

class McDonalds(Cog):
    """Pick up a shift at McDonald's!"""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.junk = None

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete"""
        return

    def load_junk(self):
        junk_path = bundled_data_path(self) / "junk.json"
        with junk_path.open() as json_data:
            self.junk = json.load(json_data)

    #def earnings(x):
    #    reward = 0
    #    for item in x:
    #        reward += item
    #        yield reward

    @commands.command(aliases=["fastfood"])
    async def mcdonalds(self, ctx: commands.Context):
        currentbank = await bank.get_balance(ctx.author)
        #startingbal = currentbank
        """Pick up a shift at McDonald's!"""
        if self.junk is None:
            self.load_junk()

        x = 0
        reward = 0
        await ctx.send(
            "<:pepe_jord:804810873570852884> {0} just signed up for a shift at McDonald's! Your job today is sorting the trash.\n<:sh_space:755971083210981426>\nWhen you've finished your shift, type `end` to clock out.\n<:sh_space:755971083210981426>\n".format(
                ctx.author.display_name
            )
        )
        while x in range(0, 10):
            used = random.choice(self.junk["bin"])
            if used["action"] == "trash":
                opp = "serve"
            else:
                opp = "trash"
            embed = discord.Embed(
                colour=discord.Color.from_rgb(255,227,1),
                description="<:simp_hand:802963169576222770> You dug in the trash and found `{}`.\n{}, will you leave it in the `trash` or `serve` it to customers?\n\n`Type end to quit.`".format(used["object"], ctx.author.mention),
                timestamp=ctx.message.created_at,
            )
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            #await ctx.send(
            #    "<:simp_hand:802963169576222770> You dug in the trash and found `{}`.\n{}, will you leave it in the `trash` or `serve` it to customers?".format(
            #        used["object"], ctx.author.mention
            #    )
            #)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                answer = await self.bot.wait_for("message", timeout=90, check=check)
            except asyncio.TimeoutError:
                answer = None

            if answer is None:
                embed = discord.Embed(
                    colour=discord.Color.from_rgb(233,60,56),
                    description=":x:<:sh_space:755971083210981426><a:this_is_fine:804822485282324580> `{}` fell on the floor and got eaten by rats. You're making our infestation worse! Do your job!".format(used["object"]),
                    timestamp=ctx.message.created_at,
                )
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            elif answer.content.lower().strip() == used["action"]:
                embed = discord.Embed(
                    colour=discord.Color.from_rgb(165,205,65),
                    description="<:cash:803730921785524234> Good job, {}! Keep this up and you'll be employee of the month!\n**+$100 {}**".format(ctx.author.mention, await bank.get_currency_name(ctx.guild)),
                    timestamp=ctx.message.created_at,
                )
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
                reward = 100
                x =+ 1
                await bank.deposit_credits(ctx.author, reward)
            elif answer.content.lower().strip() == opp:
                embed = discord.Embed(
                    colour=discord.Color.from_rgb(233,60,56),
                    description=":x:<:sh_space:755971083210981426><:wrong:728806094113210369> {}, you moron! That's not how things work here! I'm docking your pay!\n**-$100 {}**".format(ctx.author.mention, await bank.get_currency_name(ctx.guild)),
                    timestamp=ctx.message.created_at,
                )
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
                reward = 100
                await bank.withdraw_credits(ctx.author, reward)
            elif answer.content.lower().strip() == "end":
                finalbank = await bank.get_balance(ctx.author)
                earnings = int(finalbank - currentbank)
                paycheck = str(humanize_number(earnings))
                if earnings > 0:
                    await ctx.send(
                        ":fries: Great job, today, {}! ...kinda <:pepe_jord:804810873570852884>\n<:sh_space:755971083210981426>\n".format(ctx.author.display_name)
                    )                    
                    #endingbal = finalbank                    
                    #await bank.deposit_credits(ctx.author, reward)
                    await ctx.send(
                        "You earned **${} {}** for a hard day's work!".format(
                            paycheck, await bank.get_currency_name(ctx.guild)
                        )
                    )
                else:
                    await ctx.send(
                        "Dude... you may want to consider a different job."
                    )
                break
            else:
                embed = discord.Embed(
                    colour=discord.Color.from_rgb(233,60,56),
                    description=":x:<:sh_space:755971083210981426><a:this_is_fine:804822485282324580> `{}` fell on the floor and got eaten by rats. You're making our infestation worse! Do your job!".format(used["object"]),
                    timestamp=ctx.message.created_at,
                )
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
        else:
            finalbank = await bank.get_balance(ctx.author)
            earnings = int(finalbank - currentbank)
            paycheck = str(humanize_number(earnings))
            if earnings > 0:
                #finalbank = await bank.get_balance(ctx.author)
                #endingbal = finalbank
                #earnings = str(humanize_number(int(finalbank - currentbank)))
                #await bank.deposit_credits(ctx.author, reward)
                await ctx.send(
                    ":fries: Great job, today, {}! ...kinda <:pepe_jord:804810873570852884>\n<:sh_space:755971083210981426>\nYou earned **${} {}** for a hard day's work!".format(
                        ctx.author.display_name, paycheck, await bank.get_currency_name(ctx.guild)
                    )
                )
