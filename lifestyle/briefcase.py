from typing import Union

import discord
from redbot.core import bank, commands
from redbot.core.errors import BalanceTooHigh
#from redbot.core.utils.chat_formatting import box, humanize_number
from redbot.core.utils.chat_formatting import box, humanize_number, humanize_timedelta, pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from .abc import MixinMeta
from .checks import check_global_setting_admin, roulette_disabled_check, briefcase_disabled_check


class Briefcase(MixinMeta):
    """Briefcase Commands."""

    async def briefcasedisabledcheck(self, ctx):
        if await bank.is_global():
            return not await self.config.disable_briefcase()
        return not await self.config.guild(ctx.guild).disable_briefcase()

    async def briefcasedeposit(self, ctx, user, amount):
        conf = await self.configglobalcheckuser(user)
        main_conf = await self.configglobalcheck(ctx)
        briefcase = await conf.briefcase()
        max_bal = await main_conf.briefcase_max()
        amount = abs(briefcase + amount)
        if amount <= max_bal:
            await conf.briefcase.set(amount)
        else:
            await conf.briefcase.set(max_bal)
            raise ValueError

    async def briefcaseremove(self, user, amount):
        conf = await self.configglobalcheckuser(user)
        briefcase = await conf.briefcase()
        if amount < briefcase:
            await conf.briefcase.set(briefcase - amount)
        else:
            await conf.briefcase.set(0)

    async def briefcasewithdraw(self, user, amount):
        conf = await self.configglobalcheckuser(user)
        briefcase = await conf.briefcase()
        if amount < briefcase:
            await conf.briefcase.set(briefcase - amount)
        else:
            raise ValueError

    async def briefcaseset(self, user, amount):
        conf = await self.configglobalcheckuser(user)
        await conf.briefcase.set(amount)

    async def bankdeposit(self, ctx, user, amount):
        conf = await self.configglobalcheckuser(user)
        briefcase = await conf.briefcase()
        deposit = int(amount)
        if deposit > briefcase:
            return await ctx.send("**INSUFFICIENT FUNDS!** LOL! I'm telling Hatsumi you're poor! <a:13lol_point:743118114019082241>")
        try:
            await bank.deposit_credits(user, deposit)
            msg = f"You succesfully deposited ${humanize_number(deposit)} {await bank.get_currency_name(ctx.guild)} into your bank account."
        except BalanceTooHigh as e:
            deposit = e.max_balance - await bank.get_balance(user)
            await bank.deposit_credits(user, deposit)
            msg = f"Damn. You could only deposit ${humanize_number(deposit)} {e.currency_name} into your account, because you've exceeded your deposit limits. Be careful out there, man."
        await self.briefcaseset(user, briefcase - deposit)
        return await ctx.send(msg)

    async def briefcasebalance(self, user):
        conf = await self.configglobalcheckuser(user)
        return await conf.briefcase()

    async def bankwithdraw(self, ctx, user, amount):
        conf = await self.configglobalcheckuser(user)
        mainconf = await self.configglobalcheck(ctx)
        max_bal = await mainconf.briefcase_max()
        briefcase = await conf.briefcase()
        try:
            if briefcase + amount > max_bal:
                return await ctx.send(
                    f"You tried to withdraw more cash than you can hold. Tf are you doing, dude? lol keep it under ${humanize_number(max_bal)} {await bank.get_currency_name(ctx.guild)}."
                )
            await bank.withdraw_credits(user, amount)
            await self.briefcaseset(user, briefcase + amount)
            return await ctx.send(
                f"You succesfully withdrew ${humanize_number(amount)} {await bank.get_currency_name(ctx.guild)} from your bank account."
            )
        except ValueError:
            return await ctx.send("**INSUFFICIENT FUNDS!** LOL! I'm telling Hatsumi you're poor! <a:13lol_point:743118114019082241>")

    @commands.group()
    @briefcase_disabled_check()
    @commands.guild_only()
    async def briefcase(self, ctx):
        """Briefcase commands."""

    @briefcase.command()
    @commands.guild_only()
    async def stash(self, ctx, user: discord.Member = None):
        """See how much money is in someone's briefcase.

        Defaults to yours.
        """
        if user is None:
            user = ctx.author
        balance = await self.briefcasebalance(user)
        currency = await bank.get_currency_name(ctx.guild)
        await ctx.send(
            f"{user.display_name} has ${humanize_number(int(balance))} {currency} in their briefcase."
        )

    @briefcase.command()
    @commands.guild_only()
    async def fattest(self, ctx, top: int = 10):
        """See who has the most stacked briefcase."""
        if top < 1:
            top = 10
        guild = ctx.guild
        if await bank.is_global():
            raw_accounts = await self.config.all_users()
            if guild is not None:
                tmp = raw_accounts.copy()
                for acc in tmp:
                    if not guild.get_member(acc):
                        del raw_accounts[acc]
        else:
            raw_accounts = await self.config.all_members(guild)
        briefcaselist = sorted(raw_accounts.items(), key=lambda x: x[1]["briefcase"], reverse=True)[:top]
        try:
            bal_len = len(str(briefcaselist[0][1]["briefcase"]))

        except IndexError:
            return await ctx.send("No one has any money in their briefcase.")
        pound_len = len(str(len(briefcaselist)))
        header = "{pound:{pound_len}}{score:{bal_len}}{name:2}\n".format(
            pound="#", name="Name", score="Rent Money", bal_len=str(humanize_number(int(bal_len + 6))), pound_len=pound_len + 3
        )
        highscores = []
        pos = 1
        temp_msg = header
        for acc in briefcaselist:
            try:
                name = guild.get_member(acc[0]).display_name
            except AttributeError:
                user_id = ""
                if await ctx.bot.is_owner(ctx.author):
                    user_id = f"({str(acc[0])})"
                name = f"{user_id}"
            balance = str(humanize_number(int(acc[1]["briefcase"])))

            if acc[0] != ctx.author.id:
                temp_msg += f"{f'{pos}.': <{pound_len+2}} {balance: <{str(humanize_number(int(bal_len + 5)))}} {name}\n"

            else:
                temp_msg += (
                    f"{f'{pos}.': <{pound_len+2}} "
                    f"{balance: <{str(humanize_number(int(bal_len + 5)))}} "
                    f"<<{ctx.author.display_name}>>\n"
                )
            if pos % 10 == 0:
                highscores.append(box(temp_msg, lang="md"))
                temp_msg = header
            pos += 1

        if temp_msg != header:
            highscores.append(box(temp_msg, lang="md"))

        if highscores:
            await menu(ctx, highscores, DEFAULT_CONTROLS)

    @briefcase_disabled_check()
    @check_global_setting_admin()
    @commands.guild_only()
    @briefcase.command(name="set")
    async def _briefcaseset(self, ctx, user: discord.Member, amount: int):
        """Set a users briefcase balance."""
        conf = await self.configglobalcheck(ctx)
        maxw = await conf.briefcase_max()
        if amount > maxw:
            return await ctx.send(
                f"{user.display_name}'s briefcase can't hold more than ${humanize_number(maxw)} {await bank.get_currency_name(ctx.guild)}."
            )
        await self.briefcaseset(user, amount)
        await ctx.send(
            f"{ctx.author.display_name} stashed ${humanize_number(amount)} {await bank.get_currency_name(ctx.guild)} in {user.display_name}'s briefcase."
        )

    @commands.command()
    @briefcase_disabled_check()
    @commands.guild_only()
    async def deposit(self, ctx, amount: Union[int, str]):
        """Deposit cash from your briefcase to your bank."""
        cdcheck = await self.cdcheck(ctx, "depositcd")
        if isinstance(cdcheck, tuple):
            embed = await self.cdnotice(ctx.author, cdcheck[1], "deposit")
            return await ctx.send(embed=embed)
        if isinstance(amount, str):
            if amount != "all":
                return await ctx.send("You must provide a number or type `all`.")
            amount = await self.briefcasebalance(ctx.author)
        await self.bankdeposit(ctx, ctx.author, amount)

    @commands.command()
    @briefcase_disabled_check()
    @commands.guild_only()
    async def withdraw(self, ctx, amount: int):
        """Withdraw cash from your bank to your briefcase."""
        cdcheck = await self.cdcheck(ctx, "withdrawcd")
        if isinstance(cdcheck, tuple):
            embed = await self.cdnotice(ctx.author, cdcheck[1], "withdraw")
            return await ctx.send(embed=embed)
        await self.bankwithdraw(ctx, ctx.author, amount)
