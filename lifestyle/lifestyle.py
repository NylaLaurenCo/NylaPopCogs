import datetime
import random
from abc import ABC
from io import BytesIO
from typing import Literal, Optional

import discord
import tabulate
from redbot.core import Config, bank, checks, commands
from redbot.core.errors import BalanceTooHigh
from redbot.core.utils.chat_formatting import humanize_number, humanize_timedelta, pagify

from .checks import check_global_setting_admin, briefcase_disabled_check
from .defaultreplies import crimes, work, slut
from .functions import roll
from .roulette import Roulette
from .settings import SettingsMixin
from .briefcase import Briefcase


class CompositeMetaClass(type(commands.Cog), type(ABC)):
    """This allows the metaclass used for proper type detection to coexist with discord.py's
    metaclass."""


class Lifestyle(Briefcase, Roulette, SettingsMixin, commands.Cog, metaclass=CompositeMetaClass):
    """Lifestyle Commands."""

    __version__ = "0.5.4"

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}"

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        defaults = {
            "cooldowns": {
                "workcd": 14400,
                "crimecd": 14400,
                "robcd": 86400,
                "slutcd": 14400,
                "withdrawcd": 1,
                "depositcd": 1,
            },
            "defaultreplies": True,
            "replies": {"slutreplies": [], "crimereplies": [], "workreplies": []},
            "rob": [],
            "payouts": {"slut": {"max": 300, "min": 10}, "crime": {"max": 300, "min": 10}, "work": {"max": 250, "min": 10}},
            "failrates": {"slut": 2, "crime": 16, "rob": 14},
            "bailamounts": {"max": 250, "min": 10},
            "fine": 30,
            "disable_briefcase": False,
            "roulette_toggle": True,
            "roulette_time": 60,
            "roulette_payouts": {
                "zero": 36,
                "single": 17,
                "color": 1,
                "dozen": 2,
                "odd_or_even": 1,
                "halfs": 1,
                "column": 2,
            },
            "betting": {"max": 10000, "min": 100},
            "briefcase_max": 50000,
        }
        defaults_member = {
            "cooldowns": {
                "workcd": None,
                "crimecd": None,
                "robcd": None,
                "slutcd": None,
                "depositcd": None,
                "withdrawcd": None,
            },
            "briefcase": 0,
            "winnings": 0,
            "losses": 0,
        }
        self.roulettegames = {}
        self.config = Config.get_conf(self, identifier=95932766180343808, force_registration=True)
        self.config.register_global(**defaults)
        self.config.register_guild(**defaults)
        self.config.register_member(**defaults_member)
        self.config.register_user(**defaults_member)

    async def red_get_data_for_user(self, *, user_id: int):
        data = await self.config.user_from_id(user_id).all()
        all_members = await self.config.all_members()
        briefcases = []
        for guild_id, member_dict in all_members.items():
            if user_id in member_dict:
                usr = await self.config.member_from_ids(guild_id, user_id).all()
                briefcases.append(guild_id, usr["briefcase"])
        contents = f"Lifestyle Account for Discord user with ID {user_id}:\n**Global**\n- Briefcase: {data['briefcase']}\n"
        if briefcases:
            contents += "**Guilds**"
            for bal in briefcases:
                contents += f"Guild: {bal[0]} | Briefcase: {bal[1]}"
        return {"user_data.txt": BytesIO(contents.encode())}

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):

        await self.config.user_from_id(user_id).clear()
        all_members = await self.config.all_members()
        for guild_id, member_dict in all_members.items():
            if user_id in member_dict:
                await self.config.member_from_ids(guild_id, user_id).clear()

    async def configglobalcheck(self, ctx):
        if await bank.is_global():
            return self.config
        return self.config.guild(ctx.guild)

    async def configglobalcheckuser(self, user):
        if await bank.is_global():
            return self.config.user(user)
        return self.config.member(user)

    async def cdcheck(self, ctx, job):
        conf = await self.configglobalcheck(ctx)
        userconf = await self.configglobalcheckuser(ctx.author)
        cd = await userconf.cooldowns()
        jobcd = await conf.cooldowns()
        if cd[job] is None:
            async with userconf.cooldowns() as cd:
                cd[job] = int(datetime.datetime.utcnow().timestamp())
            return True
        time = int(datetime.datetime.utcnow().timestamp()) - cd[job]
        if time < jobcd[job]:
            return (False, humanize_timedelta(seconds=jobcd[job] - time))
        async with userconf.cooldowns() as cd:
            cd[job] = int(datetime.datetime.utcnow().timestamp())
        return True

    async def bail(self, ctx, job):
        conf = await self.configglobalcheck(ctx)
        bailamounts = await conf.bailamounts()
        randint = random.randint(bailamounts["min"], bailamounts["max"])
        userconf = await self.configglobalcheckuser(ctx.author)
        currentbank = await bank.get_balance(ctx.author)
        bailbond = currentbank - int(float(random.randint(1, 100) / 100) * currentbank)
        #await userconf.briefcase()
        amount = "$" + str(humanize_number(int(bailbond))) + " " + await bank.get_currency_name(ctx.guild)
        if not await self.briefcasedisabledcheck(ctx):
            if bailbond < await userconf.briefcase():
                await self.briefcaseremove(ctx.author, bailbond)
                embed = discord.Embed(
                    colour=discord.Color.from_rgb(233,60,56),
                    description=f":x: <a:hatsu_police:804202668440420353> You were caught by the police and posted bail for {amount}.",
                )
            else:
                finepercent = await self.config.guild(ctx.guild).fine()
                fee = int(
                    bailbond * float(f"1.{finepercent if finepercent >= 10 else f'0{finepercent}'}")
                )
                if await bank.can_spend(ctx.author, fee):
                    await bank.withdraw_credits(ctx.author, fee)
                    embed = discord.Embed(
                        colour=discord.Color.from_rgb(233,60,56),
                        description=f":x: <a:hatsu_police:804202668440420353> You were caught by the police and posted bail for {amount}. You didn't have enough cash so it was taken from your bank + a {finepercent}% fine (${str(humanize_number(fee))} {await bank.get_currency_name(ctx.guild)}).",
                    )
                else:
                    await bank.set_balance(ctx.author, 0)
                    embed = discord.Embed(
                        colour=discord.Color.from_rgb(233,60,56),
                        description=f":x: <a:hatsu_police:804202668440420353> You were caught by the police and posted bail for {amount}. You didn't have enough cash to pay bail and are now bankrupt.",
                    )
        else:
            if await bank.can_spend(ctx.author, bailbond):
                await bank.withdraw_credits(ctx.author, bailbond)
                embed = discord.Embed(
                    colour=discord.Color.from_rgb(233,60,56),
                    description=f":x: <a:hatsu_police:804202668440420353> You were caught by the police and posted bail for {amount}.",
                )
            else:
                await bank.set_balance(ctx.author, 0)
                embed = discord.Embed(
                    colour=discord.Color.from_rgb(233,60,56),
                    description=f":x: <a:hatsu_police:804202668440420353> You were caught by the police and posted bail for {amount}. You didn't have enough cash to pay bail and are now bankrupt.",
                )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    async def cdnotice(self, user, cooldown, job):
        response = {
            "work": f":x: You won't get promoted being a kiss ass. You're on break for {cooldown}.",
            "crime": f":x: Dude you're going to get arrested at that rate. Wait {cooldown} to commit another crime.",
            "slut": f":x: Geez slow down. You can't slut for {cooldown}.",
            "rob": f":x: <:pepe_police:804630118257524786> The police are still on your trail. Wait {cooldown} for things to cool down.",
            "withdraw": f":x: The bank is suspicious. You must wait {cooldown} to withdraw more cash.",
            "deposit": f":x: Geezus, the Teller is still counting your deposit from last time! Give them {cooldown} to finish up.",
        }
        embed = discord.Embed(colour=discord.Color.from_rgb(233,60,56), description=response[job])
        embed.set_author(name=user, icon_url=user.avatar_url)
        return embed

    @checks.admin_or_permissions(manage_guild=True)
    @check_global_setting_admin()
    @commands.guild_only()
    @commands.command(aliases=["addcashrole"])
    async def addmoneyrole(
        self, ctx, amount: int, role: discord.Role, destination: Optional[str] = "briefcase"
    ):
        """Add money to the balance of all users within a role.

        Valid options are 'bank' or 'briefcase'.
        """
        if destination.lower() not in ["bank", "briefcase"]:
            return await ctx.send(
                "Do you **want** people to get robbed?? Choose their bank or their briefcase.\nOr choose nothing, and I'll give it in cash."
            )

        failedmsg = ""
        if destination.lower() == "bank":
            for user in role.members:
                try:
                    await bank.deposit_credits(user, amount)
                except (ValueError, TypeError):
                    pass
                except BalanceTooHigh as e:
                    await bank.set_balance(ctx.author, e.max_balance)
                    failedmsg += f"{user}'s bank is full. I gave them {amount} in cash.\n"
        else:
            for user in role.members:
                try:
                    await self.briefcasedeposit(ctx, user, amount)
                except ValueError:
                    failedmsg += f"{user} is holding the max amount of cash. I couldn't give them {amount}.\n"
        if failedmsg:
            for page in pagify(failedmsg):
                await ctx.send(page)
        await ctx.tick()

    @checks.admin_or_permissions(manage_guild=True)
    @check_global_setting_admin()
    @commands.guild_only()
    @commands.command(aliases=["removecashrole"])
    async def removemoneyrole(
        self, ctx, amount: int, role: discord.Role, destination: Optional[str] = "briefcase"
    ):
        """Remove money from the bank balance of all users within a role.

        Valid options are 'bank' or 'briefcase'.
        """
        if destination.lower() not in ["bank", "briefcase"]:
            return await ctx.send(
                "Do you **want** people to get robbed?? Choose their bank or their briefcase.\nOr choose nothing, and I'll give it in cash."
            )
        if destination.lower() == "bank":
            for user in role.members:
                try:
                    await bank.withdraw_credits(user, amount)
                except ValueError:
                    await bank.set_balance(user, 0)
        else:
            for user in role.members:
                await self.briefcaseremove(user, amount)
        await ctx.tick()

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def work(self, ctx):
        """Work for some cash."""
        if ctx.assume_yes:
            return await ctx.send("This command can't be scheduled.")
        cdcheck = await self.cdcheck(ctx, "workcd")
        if isinstance(cdcheck, tuple):
            embed = await self.cdnotice(ctx.author, cdcheck[1], "work")
            return await ctx.send(embed=embed)
        conf = await self.configglobalcheck(ctx)
        payouts = await conf.payouts()
        wage = random.randint(payouts["work"]["min"], payouts["work"]["max"])
        wagesentence = "$" + str(humanize_number(wage)) + " " + await bank.get_currency_name(ctx.guild)
        if await conf.defaultreplies():
            job = random.choice(work)
            line = job.format(amount=wagesentence)
            linenum = work.index(job)
        else:
            replies = await conf.replies()
            if not replies["workreplies"]:
                return await ctx.send(
                    "You have custom replies enabled yet haven't added any replies yet."
                )
            job = random.choice(replies["workreplies"])
            linenum = replies["workreplies"].index(job)
            line = job.format(amount=wagesentence)
        embed = discord.Embed(
            colour=discord.Color.from_rgb(165,205,65), description=line, timestamp=ctx.message.created_at
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Reply #{}".format(linenum))
        if not await self.briefcasedisabledcheck(ctx):
            try:
                await self.briefcasedeposit(ctx, ctx.author, wage)
            except ValueError:
                embed.description += f"\nYou can't carry anymore {await bank.get_currency_name(ctx.guild)}. Baller!"
        else:
            try:
                await bank.deposit_credits(ctx.author, wage)
            except BalanceTooHigh as e:
                await bank.set_balance(ctx.author, e.max_balance)
                embed.description += f"\nYou've got so much {await bank.get_currency_name(ctx.guild)} in your bank, they've refused to deposit more. Wow!"

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def crime(self, ctx):
        """Commit a crime, more risk but higher payout."""
        if ctx.assume_yes:
            return await ctx.send("This command can't be scheduled.")
        cdcheck = await self.cdcheck(ctx, "crimecd")
        if isinstance(cdcheck, tuple):
            embed = await self.cdnotice(ctx.author, cdcheck[1], "crime")
            return await ctx.send(embed=embed)
        conf = await self.configglobalcheck(ctx)
        failrates = await conf.failrates()
        failurechance = float(failrates["crime"] / 100)
        fail = float(random.randint(1, 100) / 100)
        if fail <= failurechance:
            return await self.bail(ctx, "crime")
        payouts = await conf.payouts()
        wage = random.randint(payouts["crime"]["min"], payouts["crime"]["max"])
        wagesentence = "$" + str(humanize_number(wage)) + " " + await bank.get_currency_name(ctx.guild)
        if await conf.defaultreplies():
            job = random.choice(crimes)
            line = job.format(amount=wagesentence)
            linenum = crimes.index(job)
        else:
            replies = await conf.replies()
            if not replies["crimereplies"]:
                return await ctx.send(
                    "You have custom replies enabled yet haven't added any replies yet."
                )
            job = random.choice(replies["crimereplies"])
            line = job.format(amount=wagesentence)
            linenum = replies["crimereplies"].index(job)
        embed = discord.Embed(
            colour=discord.Color.from_rgb(165,205,65), description=line, timestamp=ctx.message.created_at
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Reply #{}".format(linenum))
        if not await self.briefcasedisabledcheck(ctx):
            try:
                await self.briefcasedeposit(ctx, ctx.author, wage)
            except ValueError:
                embed.description += f"\nYou can't carry anymore {await bank.get_currency_name(ctx.guild)}. Baller!"
        else:
            try:
                await bank.deposit_credits(ctx.author, wage)
            except BalanceTooHigh as e:
                await bank.set_balance(ctx.author, e.max_balance)
                embed.description += f"\nYou've got so much {await bank.get_currency_name(ctx.guild)} in your bank, they've refused to deposit more. Wow!"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def slut(self, ctx):
        """Slut for money, it's easy and fast."""
        if ctx.assume_yes:
            return await ctx.send("This command can't be scheduled.")
        cdcheck = await self.cdcheck(ctx, "slutcd")
        if isinstance(cdcheck, tuple):
            embed = await self.cdnotice(ctx.author, cdcheck[1], "slut")
            return await ctx.send(embed=embed)
        conf = await self.configglobalcheck(ctx)
        failrates = await conf.failrates()
        failurechance = float(failrates["slut"] / 100)
        fail = float(random.randint(1, 100) / 100)
        if fail <= failurechance:
            return await self.bail(ctx, "slut")
        payouts = await conf.payouts()
        wage = random.randint(payouts["slut"]["min"], payouts["slut"]["max"])
        wagesentence = "$" + str(humanize_number(wage)) + " " + await bank.get_currency_name(ctx.guild)
        if await conf.defaultreplies():
            job = random.choice(slut)
            line = job.format(amount=wagesentence)
            linenum = slut.index(job)
        else:
            replies = await conf.replies()
            if not replies["slutreplies"]:
                return await ctx.send(
                    "You have custom replies enabled yet haven't added any replies yet."
                )
            job = random.choice(replies["slutreplies"])
            line = job.format(amount=wagesentence)
            linenum = replies["slutreplies"].index(job)
        embed = discord.Embed(
            colour=discord.Color.from_rgb(165,205,65), description=line, timestamp=ctx.message.created_at
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Reply #{}".format(linenum))
        if not await self.briefcasedisabledcheck(ctx):
            try:
                await self.briefcasedeposit(ctx, ctx.author, wage)
            except ValueError:
                embed.description += f"\nYou can't carry anymore {await bank.get_currency_name(ctx.guild)}. Baller!"
        else:
            try:
                await bank.deposit_credits(ctx.author, wage)
            except BalanceTooHigh as e:
                await bank.set_balance(ctx.author, e.max_balance)
                embed.description += f"\nYou've got so much {await bank.get_currency_name(ctx.guild)} in your bank, they've refused to deposit more. Wow!"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @briefcase_disabled_check()
    @commands.bot_has_permissions(embed_links=True)
    async def rob(self, ctx, user: discord.Member):
        """Rob another user."""
        if ctx.assume_yes:
            return await ctx.send("This command can't be scheduled.")
        if user == ctx.author:
            return await ctx.send("Robbing yourself doesn't make much sense.")
        cdcheck = await self.cdcheck(ctx, "robcd")
        if isinstance(cdcheck, tuple):
            embed = await self.cdnotice(ctx.author, cdcheck[1], "rob")
            return await ctx.send(embed=embed)
        conf = await self.configglobalcheck(ctx)
        failrates = await conf.failrates()
        failurechance = float(failrates["rob"] / 100)
        fail = float(random.randint(1, 100) / 100)
        if fail <= failurechance:
            return await self.bail(ctx, "rob")
        userbalance = await self.briefcasebalance(user)
        if userbalance <= 50:
            bailchance = random.randint(1, 10)
            if bailchance > 5:
                embed = discord.Embed(
                    colour=discord.Color.from_rgb(233,60,56),
                    description="You steal {}'s briefcase when they're not looking. Fortunately for them it's empty.".format(
                        user.name
                    ),
                    timestamp=ctx.message.created_at,
                )
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                return await ctx.send(embed=embed)
            else:
                return await self.bail(ctx, "rob")
        modifier = roll()
        stolen = random.randint(1, int(userbalance * modifier))
        embed = discord.Embed(
            colour=discord.Color.from_rgb(165,205,65),
            description="You slip {}'s briefcase from their room and find <:xohats_rent_money:803732707423158312> {} bucks inside. Nice!".format(
                user.name, humanize_number(stolen)
            ),
            timestamp=ctx.message.created_at,
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        try:
            await self.briefcasedeposit(ctx, ctx.author, stolen)
            await self.briefcaseremove(user, stolen)
        except ValueError:
            embed.description += f"\nOop. After stealing the cash, you notice your **own** briefcase is full. You were forced to return the cash since you can't make off with it."
        await ctx.send(embed=embed)
