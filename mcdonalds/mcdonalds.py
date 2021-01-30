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
            "<:pepe_jord:804810873570852884> {0} just signed up for a shift at McDonald's! You're job today is sorting the trash.\n:sh_space:\nWhen you've finished your shift, type `end` to clock out.\n:sh_space:\n".format(
                ctx.author.display_name
            )
        )
        while x in range(0, 10):
            used = random.choice(self.junk["bin"])
            if used["action"] == "trash":
                opp = "re-serve"
            else:
                opp = "trash"
            await ctx.send(
                "You dug in the trash and found `{}`. {}, will you leave it in the `trash` or `re-serve` it to customers?".format(
                    used["object"], ctx.author.display_name
                )
            )

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                answer = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                answer = None

            if answer is None:
                await ctx.send(
                    "`{}` fell on the floor and needs sorting again!".format(used["object"])
                )
            elif answer.content.lower().strip() == used["action"]:
                await ctx.send(
                    "<:cash:803730921785524234> Good job! Keep this up and you'll be employee of the month! **+$50 {}**".format(
                        await bank.get_currency_name(ctx.guild)
                    )
                )
                reward = 50
                x =+ 1
                await bank.deposit_credits(ctx.author, reward)
            elif answer.content.lower().strip() == opp:
                await ctx.send(
                    "<:wrong:728806094113210369> {}, you moron! That's not how things work here! I'm docking your pay **$50 {}**!".format(
                        ctx.author.display_name, await bank.get_currency_name(ctx.guild)
                    )
                )
                reward = 50
                await bank.withdraw_credits(ctx.author, reward)
            elif answer.content.lower().strip() == "end":
                await ctx.send(
                    "{}, your shift has ended.".format(ctx.author.display_name)
                )
                if reward > 0:
                    finalbank = await bank.get_balance(ctx.author)
                    #endingbal = finalbank
                    earnings = finalbank - currentbank
                    #await bank.deposit_credits(ctx.author, reward)
                    await ctx.send(
                        "\n\nYou earned **${str(humanize_number())} {}** for a hard day's work!".format(
                            earnings, await bank.get_currency_name(ctx.guild)
                        )
                    )
                break
            else:
                await ctx.send(
                    "`{}` fell on the floor and needs sorting again!".format(used["object"])
                )
        else:
            if reward > 0:
                finalbank = await bank.get_balance(ctx.author)
                #endingbal = finalbank
                earnings = finalbank - currentbank
                #await bank.deposit_credits(ctx.author, reward)
                await ctx.send(
                    "{}, your shift has ended. You earned **str(humanize_number({})) {}** for a hard day's work!".format(
                        ctx.author.display_name, earnings, await bank.get_currency_name(ctx.guild)
                    )
                )
