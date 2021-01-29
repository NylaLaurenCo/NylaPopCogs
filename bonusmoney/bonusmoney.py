import logging
from datetime import datetime, timedelta
from typing import Literal

from redbot.core import Config, bank, checks, commands
from redbot.core.bot import Red
from redbot.core.utils import AsyncIter
from redbot.core.utils.chat_formatting import box, humanize_timedelta
from tabulate import tabulate

from . import checks as lc

log = logging.getLogger("red.nylapopcogs.bonusmoney")


class BonusMoney(commands.Cog):
    """
    Customizable BonusMoney system
    """

    __version__ = "1.5"

    settings = {"day": 1, "week": 7, "month": 30, "quarter": 90, "year": 365}
    friendly = {
        "hour": "Hourly",
        "day": "Daily",
        "week": "Weekly",
        "month": "Monthly",
        "quarter": "Quarterly",
        "year": "Yearly",
    }

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=582650109, force_registration=True
        )

        default_config = {
            "hour": 0,
            "day": 0,
            "week": 0,
            "month": 0,
            "quarter": 0,
            "year": 0,
        }
        default_user = {
            "hour": "2016-01-02T04:25:00-04:00",
            "day": "2016-01-02T04:25:00-04:00",
            "week": "2016-01-02T04:25:00-04:00",
            "month": "2016-01-02T04:25:00-04:00",
            "quarter": "2016-01-02T04:25:00-04:00",
            "year": "2016-01-02T04:25:00-04:00",
        }

        self.config.register_global(**default_config)
        self.config.register_guild(**default_config)
        self.config.register_member(**default_user)
        self.config.register_user(**default_user)

    @lc.guild_only_check()
    @commands.group()
    async def bonusmoney(self, ctx):
        """Get bonus server money!"""

    @lc.all()
    @bonusmoney.command(name="cooldown")
    async def bonusmoney_times(self, ctx):
        """Find out when you can get more bonus money."""

        if await bank.is_global():
            amounts = await self.config.all()
            times = await self.config.user(ctx.author).all()
            now = datetime.now().astimezone().replace(microsecond=0)
            strings = ""

            if amounts["hour"]:
                td = now - datetime.fromisoformat(times["hour"])
                strings += (
                    self.friendly["hour"]
                    + ": "
                    + (
                        humanize_timedelta(timedelta=(timedelta(hours=1) - td))
                        if td.seconds < 3600
                        else "Available Now!"
                    )
                    + "\n"
                )

            for k, v in self.settings.items():
                if amounts[k]:
                    td = now - (datetime.fromisoformat(times[k]))
                    strings += (
                        self.friendly[k]
                        + ": "
                        + (
                            humanize_timedelta(timedelta=(timedelta(days=v) - td))
                            if td.days < v
                            else "Available Now!"
                        )
                        + "\n"
                    )
            if strings == "":
                await ctx.send("Bonus money hasn't been set up, yet. Ask a mod to help.")
            else:
                await ctx.send(strings)
        else:
            amounts = await self.config.guild(ctx.guild).all()
            times = await self.config.member(ctx.author).all()
            now = datetime.now().astimezone().replace(microsecond=0)
            strings = ""

            if amounts["hour"]:
                td = now - (datetime.fromisoformat(times["hour"]))
                strings += (
                    self.friendly["hour"]
                    + ": "
                    + (
                        humanize_timedelta(timedelta=(timedelta(hours=1) - td))
                        if td.seconds < 3600
                        else "Available Now!"
                    )
                    + "\n"
                )

            for k, v in self.settings.items():
                if amounts[k]:
                    td = now - (datetime.fromisoformat(times[k]))
                    strings += (
                        self.friendly[k]
                        + ": "
                        + (
                            humanize_timedelta(timedelta=(timedelta(days=v) - td))
                            if td.days < v
                            else "Available Now!"
                        )
                        + "\n"
                    )

            if strings == "":
                await ctx.send("Bonus money hasn't been set up, yet. Ask a mod to help.")
            else:
                await ctx.send(strings)

    @lc.all()
    @bonusmoney.command(name="all")
    async def bonusmoney_all(self, ctx):
        """Claim all available bonusmoney"""

        amount = 0
        if await bank.is_global():
            amounts = await self.config.all()
            times = await self.config.user(ctx.author).all()
            now = datetime.now().astimezone().replace(microsecond=0)

            if (
                amounts["hour"]
                and (now - (datetime.fromisoformat(times["hour"]))).seconds >= 3600
            ):
                amount += await self.config.hour()
                await self.config.user(ctx.author).hour.set(now.isoformat())

            for k, v in self.settings.items():
                if amounts[k] and (now - (datetime.fromisoformat(times[k]))).days >= v:
                    amount += amounts[k]
                    await self.config.user(ctx.author).set_raw(k, value=now.isoformat())

            if amount > 0:
                await bank.deposit_credits(ctx.author, amount)
                await ctx.send(
                    "Stop begging geez. You already got all your bonus money. +{} {}".format(
                        amount, (await bank.get_currency_name())
                    )
                )
            else:
                await ctx.send("no.")
        else:
            amounts = await self.config.guild(ctx.guild).all()
            times = await self.config.member(ctx.author).all()
            now = datetime.now().astimezone().replace(microsecond=0)

            if (
                amounts["hour"]
                and (now - (datetime.fromisoformat(times["hour"]))).seconds >= 3600
            ):
                amount += await self.config.guild(ctx.guild).hour()
                await self.config.member(ctx.author).hour.set(now.isoformat())

            for k, v in self.settings.items():
                if amounts[k] and (now - (datetime.fromisoformat(times[k]))).days >= v:
                    amount += int(amounts[k])
                    await self.config.member(ctx.author).set_raw(
                        k, value=now.isoformat()
                    )

            if amount > 0:
                await bank.deposit_credits(ctx.author, amount)
                await ctx.send(
                    "Stop begging geez. You already got all your bonus money. +{} {}".format(
                        amount, (await bank.get_currency_name(ctx.guild))
                    )
                )
            else:
                await ctx.send("Dude, I'm busy. Go be poor somewhere else.")

    @lc.hourly()
    @bonusmoney.command(name="hourly")
    async def bonusmoney_hourly(self, ctx):
        """Get bonus money every hour"""

        if await bank.is_global():
            free = await self.config.hour()
            if free > 0:
                last = datetime.fromisoformat(await self.config.user(ctx.author).hour())
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).seconds >= 3600:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.user(ctx.author).hour.set(now.isoformat())
                    await ctx.send(
                        "I deposited {} {} in your account. Nice!".format(
                            free, (await bank.get_currency_name())
                        )
                    )
                else:
                    await ctx.send(
                        "You have {} left. Nice try.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(hours=1) - (now - last))
                            )
                        )
                    )
        else:
            free = await self.config.guild(ctx.guild).hour()
            if free > 0:
                last = datetime.fromisoformat(
                    await self.config.member(ctx.author).hour()
                )
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).seconds >= 3600:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.member(ctx.author).hour.set(now.isoformat())
                    await ctx.send(
                        "A fat deposit of {} {} just hit your account.".format(
                            free, (await bank.get_currency_name(ctx.guild))
                        )
                    )
                else:
                    await ctx.send(
                        "You have {} left. Nice try.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(hours=1) - (now - last))
                            )
                        )
                    )

    @lc.daily()
    @bonusmoney.command(name="daily")
    async def bonusmoney_daily(self, ctx):
        """Get bonus money everyday"""

        if await bank.is_global():
            free = await self.config.day()
            if free > 0:
                last = datetime.fromisoformat(await self.config.user(ctx.author).day())
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).days >= 1:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.user(ctx.author).day.set(now.isoformat())
                    await ctx.send(
                        "A fat deposit of {} {} just hit your account.".format(
                            free, (await bank.get_currency_name())
                        )
                    )
                else:
                    await ctx.send(
                        "You have {} left. Nice try.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(days=1) - (now - last))
                            )
                        )
                    )
        else:
            free = await self.config.guild(ctx.guild).day()
            if free > 0:
                last = datetime.fromisoformat(
                    await self.config.member(ctx.author).day()
                )
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).days >= 1:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.member(ctx.author).day.set(now.isoformat())
                    await ctx.send(
                        "A fat deposit of {} {} just hit your account.".format(
                            free, (await bank.get_currency_name(ctx.guild))
                        )
                    )
                else:
                    await ctx.send(
                        "You have {} left. Nice try.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(days=1) - (now - last))
                            )
                        )
                    )

    @lc.weekly()
    @bonusmoney.command(name="weekly")
    async def bonusmoney_weekly(self, ctx):
        """Get bonus money every week"""

        if await bank.is_global():
            free = await self.config.week()
            if free > 0:
                last = datetime.fromisoformat(await self.config.user(ctx.author).week())
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).days >= 7:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.user(ctx.author).week.set(now.isoformat())
                    await ctx.send(
                        "Just take this {} {} and go.".format(
                            free, (await bank.get_currency_name())
                        )
                    )
                else:
                    await ctx.send(
                        "Fail. Try again in {}.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(days=7) - (now - last))
                            )
                        )
                    )
        else:
            free = await self.config.guild(ctx.guild).week()
            if free > 0:
                last = datetime.fromisoformat(
                    await self.config.member(ctx.author).week()
                )
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).days >= 7:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.member(ctx.author).week.set(now.isoformat())
                    await ctx.send(
                        "Just take this {} {} and go.".format(
                            free, (await bank.get_currency_name(ctx.guild))
                        )
                    )
                else:
                    await ctx.send(
                        "Fail. Try again in {}.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(days=7) - (now - last))
                            )
                        )
                    )

    @lc.monthly()
    @bonusmoney.command(name="monthly")
    async def bonusmoney_monthly(self, ctx):
        """Get bonus money every month"""

        if await bank.is_global():
            free = await self.config.month()
            if free > 0:
                last = datetime.fromisoformat(
                    await self.config.user(ctx.author).month()
                )
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).days >= 30:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.user(ctx.author).month.set(now.isoformat())
                    await ctx.send(
                        "Just take this {} {} and go.".format(
                            free, (await bank.get_currency_name())
                        )
                    )
                else:
                    await ctx.send(
                        "Fail. Try again in {}.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(days=30) - (now - last))
                            )
                        )
                    )
        else:
            free = await self.config.guild(ctx.guild).month()
            if free > 0:
                last = datetime.fromisoformat(
                    await self.config.member(ctx.author).month()
                )
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).days >= 30:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.member(ctx.author).month.set(now.isoformat())
                    await ctx.send(
                        "Just take this {} {} and go.".format(
                            free, (await bank.get_currency_name(ctx.guild))
                        )
                    )
                else:
                    await ctx.send(
                        "Fail. Try again in {}.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(days=30) - (now - last))
                            )
                        )
                    )

    @lc.quarterly()
    @bonusmoney.command(name="quarterly")
    async def bonusmoney_quarterly(self, ctx):
        """Get bonus money every 3 months"""

        if await bank.is_global():
            free = await self.config.quarter()
            if free > 0:
                last = datetime.fromisoformat(
                    await self.config.user(ctx.author).quarter()
                )
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).days >= 90:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.user(ctx.author).quarter.set(now.isoformat())
                    await ctx.send(
                        "+{} {}... can you please pay me for cleaning your room, now?".format(
                            free, (await bank.get_currency_name())
                        )
                    )
                else:
                    await ctx.send(
                        "Dude. That's not even close to being on time. Wait {} wtf.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(days=90) - (now - last))
                            )
                        )
                    )
        else:
            free = await self.config.guild(ctx.guild).quarter()
            if free > 0:
                last = datetime.fromisoformat(
                    await self.config.member(ctx.author).quarter()
                )
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).days >= 90:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.member(ctx.author).quarter.set(now.isoformat())
                    await ctx.send(
                        "+{} {}... can you please pay me for cleaning your room, now?".format(
                            free, (await bank.get_currency_name(ctx.guild))
                        )
                    )
                else:
                    await ctx.send(
                        "Dude. That's not even close to being on time. Wait {} wtf.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(days=90) - (now - last))
                            )
                        )
                    )

    @lc.yearly()
    @bonusmoney.command(name="yearly")
    async def bonusmoney_yearly(self, ctx):
        """Get bonus money every year"""

        if await bank.is_global():
            free = await self.config.year()
            if free > 0:
                last = datetime.fromisoformat(await self.config.user(ctx.author).year())
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).days >= 365:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.user(ctx.author).year.set(now.isoformat())
                    await ctx.send(
                        "Tax time at Sumi's House! My favorite season. Here's {} {}. Enjoy it, sis.".format(
                            free, (await bank.get_currency_name())
                        )
                    )
                else:
                    await ctx.send(
                        "Could've sworn this bonus was once a year. You've got {} left, bro.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(days=365) - (now - last))
                            )
                        )
                    )
        else:
            free = await self.config.guild(ctx.guild).year()
            if free > 0:
                last = datetime.fromisoformat(
                    await self.config.member(ctx.author).year()
                )
                now = datetime.now().astimezone().replace(microsecond=0)

                if (now - last).days >= 365:
                    await bank.deposit_credits(ctx.author, free)
                    await self.config.member(ctx.author).year.set(now.isoformat())
                    await ctx.send(
                        "Tax time at Sumi's House! My favorite season. Here's {} {}. Enjoy it, sis.".format(
                            free, (await bank.get_currency_name(ctx.guild))
                        )
                    )
                else:
                    await ctx.send(
                        "Could've sworn this bonus was once a year. You've got {} left, bro.".format(
                            humanize_timedelta(
                                timedelta=(timedelta(days=365) - (now - last))
                            )
                        )
                    )

    @lc.is_owner_if_bank_global()
    @checks.guildowner_or_permissions(administrator=True)
    @commands.group()
    async def setbonus(self, ctx):
        """
        Set up available bonuses.
        """

    @lc.is_owner_if_bank_global()
    @checks.guildowner_or_permissions(administrator=True)
    @setbonus.command(name="settings")
    async def setbonus_info(self, ctx):
        """See current bonus settings."""

        if await bank.is_global():
            conf = await self.config.all()
            await ctx.send(box(tabulate(conf.items())))
        else:
            conf = await self.config.guild(ctx.guild).all()
            await ctx.send(box(tabulate(conf.items())))

    @lc.is_owner_if_bank_global()
    @checks.guildowner_or_permissions(administrator=True)
    @setbonus.command(name="hourly", aliases=["hour"])
    async def setbonus_hourly(self, ctx, value: int):
        """
        Replace `<value>` with the amount of money you want to give.
        Entering `0` for the amount will disable this bonus.
        Times are calculated automatically.
        """

        if value < 0:
            return await ctx.send("Amount must be 0 or above.")
        if await bank.is_global():
            await self.config.hour.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")
        else:
            await self.config.guild(ctx.guild).hour.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")

    @lc.is_owner_if_bank_global()
    @checks.guildowner_or_permissions(administrator=True)
    @setbonus.command(name="daily", aliases=["day"])
    async def setbonus_daily(self, ctx, value: int):
        """
        Replace `<value>` with the amount of money you want to give.
        Entering `0` for the amount will disable this bonus.
        Times are calculated automatically.
        """

        if value < 0:
            return await ctx.send("Amount must be 0 or above.")
        if await bank.is_global():
            await self.config.day.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")
        else:
            await self.config.guild(ctx.guild).day.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")

    @lc.is_owner_if_bank_global()
    @checks.guildowner_or_permissions(administrator=True)
    @setbonus.command(name="weekly", aliases=["week"])
    async def setbonus_weekly(self, ctx, value: int):
        """
        Replace `<value>` with the amount of money you want to give.
        Entering `0` for the amount will disable this bonus.
        Times are calculated automatically.
        """

        if value < 0:
            return await ctx.send("Amount must be 0 or above.")
        if await bank.is_global():
            await self.config.week.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")
        else:
            await self.config.guild(ctx.guild).week.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")

    @lc.is_owner_if_bank_global()
    @checks.guildowner_or_permissions(administrator=True)
    @setbonus.command(name="monthly", aliases=["month"])
    async def setbonus_monthly(self, ctx, value: int):
        """
        Replace `<value>` with the amount of money you want to give.
        Entering `0` for the amount will disable this bonus.
        Times are calculated automatically.
        """

        if value < 0:
            return await ctx.send("Amount must be 0 or above.")
        if await bank.is_global():
            await self.config.month.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")
        else:
            await self.config.guild(ctx.guild).month.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")

    @lc.is_owner_if_bank_global()
    @checks.guildowner_or_permissions(administrator=True)
    @setbonus.command(name="quarterly", aliases=["quarter"])
    async def setbonus_quarterly(self, ctx, value: int):
        """
        Replace `<value>` with the amount of money you want to give.
        Entering `0` for the amount will disable this bonus.
        Times are calculated automatically.
        """

        if value < 0:
            return await ctx.send("Amount must be 0 or above.")
        if await bank.is_global():
            await self.config.quarter.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")
        else:
            await self.config.guild(ctx.guild).quarter.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")

    @lc.is_owner_if_bank_global()
    @checks.guildowner_or_permissions(administrator=True)
    @setbonus.command(name="yearly", aliases=["year"])
    async def setbonus_yearly(self, ctx, value: int):
        """
        Replace `<value>` with the amount of money you want to give.
        Entering `0` for the amount will disable this bonus.
        Times are calculated automatically.
        """

        if value < 0:
            return await ctx.send("Amount must be 0 or above.")
        if await bank.is_global():
            await self.config.year.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")
        else:
            await self.config.guild(ctx.guild).year.set(value)
            if not await ctx.tick():
                await ctx.send("Bonus saved!")

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        if requester == "discord_deleted_user":
            # user is deleted, just comply

            data = await self.config.all_members()
            async for guild_id, members in AsyncIter(data.items(), steps=100):
                if user_id in members:
                    await self.config.member_from_ids(guild_id, user_id).clear()

            data = await self.config.all_users()
            async for users in AsyncIter(data.items(), steps=100):
                if user_id in users:
                    await self.config.user_from_id(user_id).clear()
