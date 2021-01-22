import asyncio
import discord
import random
import calendar

from typing import Any, Union
from discord.utils import get
from datetime import datetime

from redbot.core import Config, checks, commands, bank
from redbot.core.utils.chat_formatting import pagify, box
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

from redbot.core.bot import Red

_MAX_BALANCE = 2 ** 63 - 1


class Marshmallows(commands.Cog):
    """
    Collect marshmallows.
    """

    __author__ = "saurichable"
    __version__ = "1.1.3"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=16548964843212314, force_registration=True
        )
        self.config.register_guild(
            amount=1,
            minimum=0,
            maximum=0,
            cooldown=86400,
            stealing=False,
            stealcd=43200,
            rate=0.5,
        )
        self.config.register_member(marshmallows=0, next_marshmallow=0, next_steal=0)
        self.config.register_role(marshmallows=0, multiplier=1)

    @commands.command()
    @commands.guild_only()
    async def openmallows(self, ctx: commands.Context):
        """Get your daily dose of marshmallows."""
        amount = int(await self.config.guild(ctx.guild).amount())
        marshmallows = int(await self.config.member(ctx.author).marshmallows())
        cur_time = calendar.timegm(ctx.message.created_at.utctimetuple())
        next_marshmallow = await self.config.member(ctx.author).next_marshmallow()
        if cur_time >= next_marshmallow:
            if amount != 0:
                multipliers = []
                for role in ctx.author.roles:
                    role_multiplier = await self.config.role(role).multiplier()
                    if not role_multiplier:
                        role_multiplier = 1
                    multipliers.append(role_multiplier)
                marshmallows += (amount * max(multipliers)) 
            else:
                minimum = int(await self.config.guild(ctx.guild).minimum())
                maximum = int(await self.config.guild(ctx.guild).maximum())
                amount = int(random.choice(list(range(minimum, maximum))))
                marshmallows += amount
            if self._max_balance_check(marshmallows):
                return await ctx.send(
                    "LOL you can't hoard anymore marshmallows fatty! <a:13lol_point:743118114019082241>"
                )
            next_marshmallow = cur_time + await self.config.guild(ctx.guild).cooldown()
            await self.config.member(ctx.author).next_marshmallow.set(next_marshmallow)
            await self.config.member(ctx.author).marshmallows.set(marshmallows)
            await ctx.send(f"You opened a bag of marshmallows and found {amount} <:so_love:754613619836321892> inside! Yumm!")
        else:
            dtime = self.display_time(next_marshmallow - cur_time)
            await ctx.send(f"Stop being greedy. You can get another bag of marshmallows in {dtime}.")

    @commands.command()
    @commands.guild_only()
    async def stealmallows(self, ctx: commands.Context, target: discord.Member = None):
        """Steal marshmallows from members."""
        cur_time = calendar.timegm(ctx.message.created_at.utctimetuple())
        next_steal = await self.config.member(ctx.author).next_steal()
        enabled = await self.config.guild(ctx.guild).stealing()
        author_marshmallows = int(await self.config.member(ctx.author).marshmallows())
        if not enabled:
            return await ctx.send("lol stealing isn't allowed... loser.")
        if cur_time < next_steal:
            dtime = self.display_time(next_steal - cur_time)
            return await ctx.send(f"Uh oh, you have to wait {dtime}.")
        if not target:
            ids = await self._get_ids(ctx)
            while not target:
                target_id = random.choice(ids)
                target = ctx.guild.get_member(target_id)
        if target.id == ctx.author.id:
            return await ctx.send("Dude... did you really just try to steal from yourself?? <:13bruh_tf:743113446127698040>")
        target_marshmallows = int(await self.config.member(target).marshmallows())
        if target_marshmallows == 0:
            return await ctx.send(
                f"OMG GUYS {target.display_name} DOESN'T HAVE ANY MARSHMALLOWS LOL! WHAT A POOR!!! <:13lol_bitch_please:728864625352900638> <a:13lol_point:743118114019082241>"
            )
        success_chance = random.randint(30, 100)
        mallows_int = random.randint(1, 100)
        mallows_stolen = float(mallows_int / 100)
        if success_chance > 69:
            marshmallows_stolen = int(target_marshmallows * mallows_stolen)
            if marshmallows_stolen == 0:
                marshmallows_stolen = 1
            stolen = random.randint(1, marshmallows_stolen)
            author_marshmallows += stolen
            if self._max_balance_check(author_marshmallows):
                return await ctx.send(
                    "LOL you can't hoard anymore marshmallows fatty! <a:13lol_point:743118114019082241>\n"
                    f"You stole ZERO <:so_love:754613619836321892> from {target.display_name}."
                )
            target_marshmallows -= stolen
            await ctx.send(f"You stole {stolen} <:so_love:754613619836321892> from {target.display_name}!")
        else:
            marshmallows_penalty = int(author_marshmallows * mallows_stolen)
            if marshmallows_penalty == 0:
                marshmallows_penalty = 1
            penalty = random.randint(1, marshmallows_penalty)
            target_marshmallows += penalty
            if self._max_balance_check(target_marshmallows):
                return await ctx.send(
                    f"You got caught trying to steal {target.display_name}'s <:so_love:754613619836321892>!\n"
                    f"Lucky for you {target.display_name} is a fatass. They don't have room to hoard anymore marshmallows, "
                    "so you haven't lost any."
                )
            author_marshmallows -= penalty
            await ctx.send(
                f"You got caught trying to steal {target.display_name}'s <:so_love:754613619836321892>!\nThey took {penalty} of **YOUR** <:so_love:754613619836321892> marshmallows in return. lol get rekt!"
            )
        next_steal = cur_time + await self.config.guild(ctx.guild).stealcd()
        await self.config.member(target).marshmallows.set(target_marshmallows)
        await self.config.member(ctx.author).marshmallows.set(author_marshmallows)
        await self.config.member(ctx.author).next_steal.set(next_steal)

    @commands.command()
    @commands.guild_only()
    async def gibbmallows(self, ctx: commands.Context, target: discord.Member, amount: int):
        """Gift someone some yummy marshmallows."""
        author_marshmallows = int(await self.config.member(ctx.author).marshmallows())
        if amount <= 0:
            return await ctx.send("I can't give nothing, dude.")
        if target.id == ctx.author.id:
            return await ctx.send("Why would you do that?")
        if amount > author_marshmallows:
            return await ctx.send("You don't have enough marshmallows yourself! lol... lesser.")
        target_marshmallows = int(await self.config.member(target).marshmallows())
        target_marshmallows += amount
        if self._max_balance_check(target_marshmallows):
            return await ctx.send(
                f"Geezus. {target.display_name} has been hoarding marshmallows as if the world is ending. I'm putting a stop to this."
            )
        author_marshmallows -= amount
        await self.config.member(ctx.author).marshmallows.set(author_marshmallows)
        await self.config.member(target).marshmallows.set(target_marshmallows)
        await ctx.send(
            f"Aww {ctx.author.mention} gave {amount} <:so_love:754613619836321892> to {target.mention}. So sweet."
        )

    @commands.command(aliases=["jar"])
    @commands.guild_only()
    async def marshmallows(self, ctx: commands.Context, target: discord.Member = None):
        """Check how many marshmallows you have."""
        if not target:
            marshmallows = int(await self.config.member(ctx.author).marshmallows())
            await ctx.send(f"You have {marshmallows} <:so_love:754613619836321892> Yum!")
        else:
            marshmallows = int(await self.config.member(target).marshmallows())
            await ctx.send(f"{target.display_name} has {marshmallows} <:so_love:754613619836321892>. Sweet!")

    @commands.command()
    @commands.guild_only()
    async def buymallows(self, ctx: commands.Context, amount: int):
        """Buy marshmallows."""
        if amount <= 0:
            return await ctx.send("Are you okay?")

        if not await bank.can_spend(ctx.author, amount):
            return await ctx.send(f"lol check your balance and think about your life choices")
        await bank.withdraw_credits(ctx.author, amount)

        rate = await self.config.guild(ctx.guild).rate()
        new_marshmallows = amount * rate

        marshmallows = await self.config.member(ctx.author).marshmallows()
        marshmallows += new_marshmallows
        await self.config.member(ctx.author).marshmallows.set(marshmallows)
        currency = await bank.get_currency_name(ctx.guild)
        await ctx.send(f"You bought {new_marshmallows} <:so_love:754613619836321892> for {amount} {currency}.\n**Current Stash**: {marshmallows} <:so_love:754613619836321892>")

    @commands.command(aliases=["marshmallowleaderboard"])
    @commands.guild_only()
    async def hoarders(self, ctx: commands.Context):
        """See the server's top marshmallow hoarders."""
        ids = await self._get_ids(ctx)
        lst = []
        pos = 1
        pound_len = len(str(len(ids)))
        header = "{pound:{pound_len}}{score:{bar_len}}{name:2}\n".format(
            pound="Rank",
            name="Member",
            score="#",
            pound_len=pound_len + 3,
            bar_len=pound_len + 9,
        )
        temp_msg = header
        for a_id in ids:
            a = get(ctx.guild.members, id=int(a_id))
            if not a:
                continue
            name = a.display_name
            marshmallows = await self.config.member(a).marshmallows()
            if marshmallows == 0:
                continue
            score = "Marshmallows"
            if a_id != ctx.author.id:
                temp_msg += (
                    f"{f'{pos}.': <{pound_len+2}} {marshmallows: <{pound_len+8}} {name}\n"
                )
            else:
                temp_msg += (
                    f"{f'{pos}.': <{pound_len+2}} "
                    f"{marshmallows: <{pound_len+8}} "
                    f"<<{name}>>\n"
                )
            if pos % 10 == 0:
                lst.append(box(temp_msg, lang="md"))
                temp_msg = header
            pos += 1
        if temp_msg != header:
            lst.append(box(temp_msg, lang="md"))
        if lst:
            if len(lst) > 1:
                await menu(ctx, lst, DEFAULT_CONTROLS)
            else:
                await ctx.send(lst[0])
        else:
            empty = "Nothing to see here."
            await ctx.send(box(empty, lang="md"))

    @commands.group(autohelp=True)
    @checks.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    async def setmarshmallows(self, ctx):
        """Admin settings for marshmallows."""
        pass

    @setmarshmallows.command(name="amount")
    async def setmarshmallows_amount(self, ctx: commands.Context, amount: int):
        """Set the amount of marshmallows members can obtain.

        If 0, members will get a random amount."""
        if amount < 0:
            return await ctx.send("The amount cannot be negative.")
        if self._max_balance_check(amount):
            return await ctx.send(
                f"You can't set an amount greater than {_MAX_BALANCE:,}."
            )
        await self.config.guild(ctx.guild).amount.set(amount)
        if amount != 0:
            await ctx.send(f"Members will receive {amount} marshmallows.")
        else:
            pred = MessagePredicate.valid_int(ctx)
            await ctx.send("What's the minimum amount of marshmallows members can obtain?")
            try:
                await self.bot.wait_for("message", timeout=30, check=pred)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            minimum = pred.result
            await self.config.guild(ctx.guild).minimum.set(minimum)

            await ctx.send("What's the maximum amount of marshmallows members can obtain?")
            try:
                await self.bot.wait_for("message", timeout=30, check=pred)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            maximum = pred.result
            await self.config.guild(ctx.guild).maximum.set(maximum)

            await ctx.send(
                f"Members will receive a random amount of marshmallows between {minimum} and {maximum}."
            )

    @setmarshmallows.command(name="cooldown", aliases=["cd"])
    async def setmarshmallows_cd(self, ctx: commands.Context, seconds: int):
        """Set the cooldown for `[p]openmallows`.

        This is in seconds! Default is 86400 seconds (24 hours)."""
        if seconds <= 0:
            return await ctx.send("Uh oh, cooldown has to be more than 0 seconds.")
        await self.config.guild(ctx.guild).cooldown.set(seconds)
        await ctx.send(f"Set the cooldown to {seconds} seconds.")

    @setmarshmallows.command(name="stealcooldown", aliases=["stealcd"])
    async def setmarshmallows_stealcd(self, ctx: commands.Context, seconds: int):
        """Set the cooldown for `[p]stealmallows`.

        This is in seconds! Default is 43200 seconds (12 hours)."""
        if seconds <= 0:
            return await ctx.send("Uh oh, cooldown has to be more than 0 seconds.")
        await self.config.guild(ctx.guild).stealcd.set(seconds)
        await ctx.send(f"Set the cooldown to {seconds} seconds.")

    @setmarshmallows.command(name="steal")
    async def setmarshmallows_steal(self, ctx: commands.Context, on_off: bool = None):
        """Toggle marshmallow stealing for current server. 

        If `on_off` is not provided, the state will be flipped."""
        target_state = (
            on_off
            if on_off
            else not (await self.config.guild(ctx.guild).stealing())
        )
        await self.config.guild(ctx.guild).stealing.set(target_state)
        if target_state:
            await ctx.send("Stealing is now enabled.")
        else:
            await ctx.send("Stealing is now disabled.")

    @setmarshmallows.command(name="set")
    async def setmarshmallows_set(
        self, ctx: commands.Context, target: discord.Member, amount: int
    ):
        """Set someone's amount of marshmallows."""
        if amount <= 0:
            return await ctx.send("Uh oh, amount has to be more than 0.")
        if self._max_balance_check(amount):
            return await ctx.send(
                f"Uh oh, amount can't be greater than {_MAX_BALANCE:,}."
            )
        await self.config.member(target).marshmallows.set(amount)
        await ctx.send(f"Set {target.mention}'s balance to {amount} <:so_love:754613619836321892>")

    @setmarshmallows.command(name="add")
    async def setmarshmallows_add(
        self, ctx: commands.Context, target: discord.Member, amount: int
    ):
        """Add marshmallows to someone."""
        if amount <= 0:
            return await ctx.send("Uh oh, amount has to be more than 0.")
        target_marshmallows = int(await self.config.member(target).marshmallows())
        target_marshmallows += amount
        if self._max_balance_check(target_marshmallows):
            return await ctx.send(
                f"Uh oh, {target.display_name} has reached the maximum amount of marshmallows."
            )
        await self.config.member(target).marshmallows.set(target_marshmallows)
        await ctx.send(f"Added {amount} <:so_love:754613619836321892> to {target.mention}'s balance.")

    @setmarshmallows.command(name="take")
    async def setmarshmallows_take(
        self, ctx: commands.Context, target: discord.Member, amount: int
    ):
        """Take marshmallows away from someone."""
        if amount <= 0:
            return await ctx.send("Uh oh, amount has to be more than 0.")
        target_marshmallows = int(await self.config.member(target).marshmallows())
        if amount <= target_marshmallows:
            target_marshmallows -= amount
            await self.config.member(target).marshmallows.set(target_marshmallows)
            await ctx.send(
                f"Took away {amount} <:so_love:754613619836321892> from {target.mention}'s balance."
            )
        else:
            await ctx.send(f"{target.mention} doesn't have enough :marshmallows:")

    @setmarshmallows.command(name="reset")
    async def setmarshmallows_reset(self, ctx: commands.Context, confirmation: bool = False):
        """Delete all marshmallows from all members."""
        if not confirmation:
            return await ctx.send(
                "This will delete **all** marshmallows from all members. This action **cannot** be undone.\n"
                f"If you're sure, type `{ctx.clean_prefix}setmarshmallows reset yes`."
            )
        for member in ctx.guild.members:
            marshmallows = int(await self.config.member(member).marshmallows())
            if marshmallows != 0:
                await self.config.member(member).marshmallows.set(0)
        await ctx.send("All marshmallows have been deleted from all members.")

    @setmarshmallows.command(name="rate")
    async def setmarshmallows_rate(self, ctx: commands.Context, rate: Union[int, float]):
        """Set the exchange rate for `[p]marshmallowexchange`."""
        if rate <= 0:
            return await ctx.send("Uh oh, rate has to be more than 0.")
        await self.config.guild(ctx.guild).rate.set(rate)
        currency = await bank.get_currency_name(ctx.guild)
        test_amount = 100*rate
        await ctx.send(f"Set the exchange rate {rate}. This means that 100 {currency} will give you {test_amount} <:so_love:754613619836321892>")

    @setmarshmallows.group(autohelp=True)
    async def role(self, ctx):
        """Marshmallow rewards for roles."""
        pass

    @role.command(name="add")
    async def setmarshmallows_role_add(
        self, ctx: commands.Context, role: discord.Role, amount: int
    ):
        """Set marshmallows for role."""
        if amount <= 0:
            return await ctx.send("Uh oh, amount has to be more than 0.")
        await self.config.role(role).marshmallows.set(amount)
        await ctx.send(f"Gaining {role.name} will now give {amount} <:so_love:754613619836321892>")

    @role.command(name="del")
    async def setmarshmallows_role_del(self, ctx: commands.Context, role: discord.Role):
        """Delete marshmallows for role."""
        await self.config.role(role).marshmallows.set(0)
        await ctx.send(f"Gaining {role.name} will now not give any <:so_love:754613619836321892>")

    @role.command(name="show")
    async def setmarshmallows_role_show(self, ctx: commands.Context, role: discord.Role):
        """Show how many marshmallows a role gives."""
        marshmallows = int(await self.config.role(role).marshmallows())
        await ctx.send(f"Gaining {role.name} gives {marshmallows} <:so_love:754613619836321892>")

    @role.command(name="multiplier")
    async def setmarshmallows_role_multiplier(
        self, ctx: commands.Context, role: discord.Role, multiplier: int
    ):
        """Set marshmallows multipler for role. Disabled when random amount is enabled.
        
        Default is 1 (aka the same amount)."""
        if multiplier <= 0:
            return await ctx.send("Uh oh, multiplier has to be more than 0.")
        await self.config.role(role).multiplier.set(multiplier)
        await ctx.send(f"Users with {role.name} will now get {multiplier} times more <:so_love:754613619836321892>")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        b = set(before.roles)
        a = set(after.roles)
        after_roles = [list(a - b)][0]
        if after_roles:
            for role in after_roles:
                marshmallows = int(await self.config.role(role).marshmallows())
                if marshmallows != 0:
                    old_marshmallows = int(await self.config.member(after).marshmallows())
                    new_marshmallows = old_marshmallows + marshmallows
                    if self._max_balance_check(new_marshmallows):
                        continue
                    await self.config.member(after).marshmallows.set(new_marshmallows)

    async def _get_ids(self, ctx):
        data = await self.config.all_members(ctx.guild)
        ids = sorted(data, key=lambda x: data[x]["marshmallows"], reverse=True)
        return ids

    @staticmethod
    def display_time(seconds, granularity=2):
        intervals = (  # Source: from economy.py
            (("weeks"), 604800),  # 60 * 60 * 24 * 7
            (("days"), 86400),  # 60 * 60 * 24
            (("hours"), 3600),  # 60 * 60
            (("minutes"), 60),
            (("seconds"), 1),
        )

        result = []

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip("s")
                result.append(f"{value} {name}")
        return ", ".join(result[:granularity])

    @staticmethod
    def _max_balance_check(value: int):
        if value > _MAX_BALANCE:
            return True
