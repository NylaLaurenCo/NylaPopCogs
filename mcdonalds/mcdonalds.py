import asyncio
import json
import random
import math

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
            await ctx.send(
                "<:simp_hand:802963169576222770> You dug in the trash and found `{}`.\n{}, will you leave it in the `trash` or `serve` it to customers?".format(
                    used["object"], ctx.author.mention
                )
            )

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                answer = await self.bot.wait_for("message", timeout=90, check=check)
            except asyncio.TimeoutError:
                answer = None

            if answer is None:
                await ctx.send(
                    "<a:this_is_fine:804822485282324580> `{}` fell on the floor and needs sorting again!".format(used["object"])
                )
            elif answer.content.lower().strip() == used["action"]:
                await ctx.send(
                    "<:cash:803730921785524234> Good job! Keep this up and you'll be employee of the month!\n**+$50 {}**\n<:sh_space:755971083210981426>\n".format(
                        await bank.get_currency_name(ctx.guild)
                    )
                )
                reward = 50
                x =+ 1
                await bank.deposit_credits(ctx.author, reward)
            elif answer.content.lower().strip() == opp:
                await ctx.send(
                    "<:wrong:728806094113210369> {}, you moron! That's not how things work here! I'm docking your pay!\n**-$50 {}**\n<:sh_space:755971083210981426>\n".format(
                        ctx.author.display_name, await bank.get_currency_name(ctx.guild)
                    )
                )
                reward = 50
                await bank.withdraw_credits(ctx.author, reward)
            elif answer.content.lower().strip() == "end":
                await ctx.send(
                    ":fries: Great job, today, {}! ...kinda <:pepe_jord:804810873570852884>\n<:sh_space:755971083210981426>\n".format(ctx.author.display_name)
                )
                finalbank = await bank.get_balance(ctx.author)
                earnings = str(humanize_number(int(finalbank - currentbank)))
                if earnings > 0:                    
                    #endingbal = finalbank                    
                    #await bank.deposit_credits(ctx.author, reward)
                    await ctx.send(
                        "You earned **${} {}** for a hard day's work!".format(
                            earnings, await bank.get_currency_name(ctx.guild)
                        )
                    )
                else:
                    await ctx.send(
                        "Dude... you may want to consider a different job."
                    )
                break
            else:
                await ctx.send(
                    "\n<:sh_space:755971083210981426>\n<a:this_is_fine:804822485282324580> `{}` fell on the floor and needs sorting again!\n<:sh_space:755971083210981426>\n".format(used["object"])
                )
        else:
            finalbank = await bank.get_balance(ctx.author)
            earnings = str(humanize_number(int(finalbank - currentbank)))
            if earnings > 0:
                #finalbank = await bank.get_balance(ctx.author)
                #endingbal = finalbank
                #earnings = str(humanize_number(int(finalbank - currentbank)))
                #await bank.deposit_credits(ctx.author, reward)
                await ctx.send(
                    ":fries: Great job, today, {}! ...kinda <:pepe_jord:804810873570852884>\n<:sh_space:755971083210981426>\nYou earned **${} {}** for a hard day's work!".format(
                        ctx.author.display_name, earnings, await bank.get_currency_name(ctx.guild)
                    )
                )
                else:
                    await ctx.send(
                        "Dude... you may want to consider a different job."
                    )
