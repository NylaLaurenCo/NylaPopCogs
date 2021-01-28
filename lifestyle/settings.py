import datetime

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_number, humanize_timedelta
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from .abc import MixinMeta
from .checks import check_global_setting_admin
from .functions import chunks


class SettingsMixin(MixinMeta):
    """Settings."""

    @commands.group(name="lstyleset", aliases=["lstyle-set"])
    @check_global_setting_admin()
    @commands.guild_only()
    async def lstyle_set(self, ctx):
        """Manage various settings for Lifestyle."""

    @commands.guild_only()
    @lstyle_set.command(name="cooldown")
    async def cooldown_set(
        self,
        ctx,
        job,
        *,
        time: commands.TimedeltaConverter(
            minimum=datetime.timedelta(seconds=0),
            maximum=datetime.timedelta(days=2),
            default_unit="minutes",
        ),
    ):
        """Set the cooldown for the work, crime, slut, rob, and bank commands. Minimum cooldown is 30 seconds.

        The time can be formatted as so `1h30m` etc. Valid times are hours, minutes and seconds.
        """
        job = job.lower()
        if job not in ["slut", "work", "crime", "rob", "deposit", "withdraw"]:
            return await ctx.send("Invalid job.")
        seconds = time.total_seconds()
        if seconds < 30:
            return await ctx.send("The miniumum interval is 30 seconds.")
        jobcd = {
            "work": "workcd",
            "crime": "crimecd",
            "rob": "robcd",
            "slut": "slutcd",
            "deposit": "depositcd",
            "withdraw": "withdrawcd",
        }
        conf = await self.configglobalcheck(ctx)
        async with conf.cooldowns() as cooldowns:
            cooldowns[jobcd[job]] = int(seconds)
        await ctx.tick()

    @check_global_setting_admin()
    @commands.guild_only()
    @lstyle_set.command(name="payout", usage="<work | crime | slut> <min | max> <amount>")
    async def payout_set(self, ctx, job: str, min_or_max: str, amount: int):
        """Set the min or max payout for working, slutting or crimes."""
        if job not in ["work", "crime", "slut"]:
            return await ctx.send("Invalid job.")
        if min_or_max not in ["max", "min"]:
            return await ctx.send("You must choose between min or max.")
        conf = await self.configglobalcheck(ctx)
        async with conf.payouts() as payouts:
            payouts[job][min_or_max] = amount
        await ctx.tick()

    @check_global_setting_admin()
    @commands.guild_only()
    @lstyle_set.command(name="betting", usage="<min | max> <amount>")
    async def betting_set(self, ctx, min_or_max: str, amount: int):
        """Set the min or max betting amounts."""
        if min_or_max not in ["max", "min"]:
            return await ctx.send("You must choose between min or max.")
        conf = await self.configglobalcheck(ctx)
        async with conf.betting() as betting:
            betting[min_or_max] = amount
        await ctx.tick()

    @check_global_setting_admin()
    @commands.guild_only()
    @lstyle_set.group(name="briefcase")
    async def briefcase_set(self, ctx):
        """Briefcase Settings."""

    @check_global_setting_admin()
    @commands.guild_only()
    @briefcase_set.command(name="toggle", usage="<on_or_off>")
    async def briefcase_toggle(self, ctx, on_or_off: bool):
        """Toggle the briefcase system."""
        conf = await self.configglobalcheck(ctx)
        if on_or_off:
            await ctx.send("The briefcase and rob system has been enabled.")
        else:
            await ctx.send("The briefcase and rob system has been disabled.")
        await conf.disable_briefcase.set(on_or_off)
        await ctx.tick()

    @check_global_setting_admin()
    @commands.guild_only()
    @briefcase_set.command(name="max")
    async def briefcase_max(self, ctx, amount: int):
        """Set the max a briefcase can have."""
        conf = await self.configglobalcheck(ctx)
        await conf.briefcase_max.set(amount)
        await ctx.tick()

    @check_global_setting_admin()
    @commands.guild_only()
    @lstyle_set.command(name="failure-rate", usage="<rob | crime | slut> <amount>", aliases=["failurerate"])
    async def failure_set(self, ctx, job: str, amount: int):
        """Set the failure rate for crimes, slutting and robbing."""
        if job not in ["rob", "crime", "slut"]:
            return await ctx.send("Invalid job.")
        if amount < 0 or amount > 100:
            return await ctx.send("Amount must be between 0-100.")
        conf = await self.configglobalcheck(ctx)
        async with conf.failrates() as failrates:
            failrates[job] = amount
        await ctx.tick()

    @check_global_setting_admin()
    @commands.guild_only()
    @lstyle_set.command(name="bail-amount", usage="<min | max> <amount>", aliases=["bail"])
    async def bail_set(self, ctx, min_or_max: str, amount: int):
        """Set the min or max bail amount for crimes and slutting. **This is a percentage.** Do not include symbols."""
        if min_or_max not in ["max", "min"]:
            return await ctx.send("You must choose between min or max.")
        conf = await self.configglobalcheck(ctx)
        async with conf.bailamounts() as bailamounts:
            bailamounts[min_or_max] = amount
        await ctx.tick()

    @check_global_setting_admin()
    @commands.guild_only()
    @lstyle_set.command(name="fine-percent", usage="<amount>", aliases=["bailtax"])
    async def fine_set(self, ctx, amount: int):
        """Set the fine if unable to pay bail in cash."""
        if amount < 0 or amount > 100:
            return await ctx.send("Amount must be between 0-100.")
        conf = await self.configglobalcheck(ctx)
        await conf.fine.set(amount)
        await ctx.tick()

    @commands.guild_only()
    @check_global_setting_admin()
    @lstyle_set.command(name="add-reply")
    async def add_reply(self, ctx, job, *, reply: str):
        """Add a custom reply for working, slutting or crime.

        Put {amount} in place of where you want the amount earned to be.
        """
        if job not in ["work", "crime", "slut"]:
            return await ctx.send("Invalid job.")
        if "{amount}" not in reply:
            return await ctx.send("{amount} must be present in the reply.")
        conf = await self.configglobalcheck(ctx)
        jobreplies = {"work": "workreplies", "crime": "crimereplies", "slut": "slutreplies"}
        async with conf.replies() as replies:
            if reply in replies[jobreplies[job]]:
                return await ctx.send("That is already a response.")
            replies[jobreplies[job]].append(reply)
            ind = replies[jobreplies[job]].index(reply)
        await ctx.send("Your reply has been added and is reply ID #{}".format(ind))

    @commands.guild_only()
    @check_global_setting_admin()
    @lstyle_set.command(name="del-reply")
    async def del_reply(self, ctx, job, *, id: int):
        """Delete a custom reply."""
        if job not in ["work", "crime", "slut"]:
            return await ctx.send("Invalid job.")
        jobreplies = {"work": "workreplies", "crime": "crimereplies", "slut": "slutreplies"}
        conf = await self.configglobalcheck(ctx)
        async with conf.replies() as replies:
            if not replies[jobreplies[job]]:
                return await ctx.send("This job has no custom replies.")
            if id > len(replies[jobreplies[job]]):
                return await ctx.send("Invalid ID.")
            replies[jobreplies[job]].pop(id)
        await ctx.send("Your reply has been removed")

    @check_global_setting_admin()
    @commands.guild_only()
    @lstyle_set.command(name="list-replies")
    async def list_reply(self, ctx, job):
        """List custom replies."""
        if job not in ["work", "crime", "slut"]:
            return await ctx.send("Invalid job.")
        jobreplies = {"work": "workreplies", "crime": "crimereplies", "slut": "slutreplies"}
        conf = await self.configglobalcheck(ctx)
        async with conf.replies() as replies:
            if not replies[jobreplies[job]]:
                return await ctx.send("This job has no custom replies.")
            a = chunks(replies[jobreplies[job]], 10)
            embeds = []
            for item in a:
                items = []
                for i, strings in enumerate(item):
                    items.append(f"Reply {i}: {strings}")
                embed = discord.Embed(colour=discord.Color.from_rgb(233,60,56), description="\n".join(items))
                embeds.append(embed)
            if len(embeds) == 1:
                await ctx.send(embed=embeds[0])
            else:
                await menu(ctx, embeds, DEFAULT_CONTROLS)

    @check_global_setting_admin()
    @commands.guild_only()
    @lstyle_set.command(name="default-replies", usage="<enable | disable>")
    async def default_replies(self, ctx, enable: bool):
        """Whether to use the default replies to work and crime."""
        conf = await self.configglobalcheck(ctx)
        if enable:
            await ctx.send("Default replies are enabled.")
            await conf.defaultreplies.set(enable)
        else:
            await ctx.send("Default replies are now disabled.")
            await conf.defaultreplies.set(enable)

    @commands.command()
    @commands.guild_only()
    async def cooldowns(self, ctx):
        """List your remaining cooldowns.."""
        conf = await self.configglobalcheck(ctx)
        userconf = await self.configglobalcheckuser(ctx.author)
        cd = await userconf.cooldowns()
        jobcd = await conf.cooldowns()
        if cd["workcd"] is None:
            workcd = "None"
        else:
            time = int(datetime.datetime.utcnow().timestamp()) - cd["workcd"]
            if time < jobcd["workcd"]:
                workcd = humanize_timedelta(seconds=jobcd["workcd"] - time)
            else:
                workcd = "Ready to use."
        if cd["crimecd"] is None:
            crimecd = "Ready to use."
        else:
            time = int(datetime.datetime.utcnow().timestamp()) - cd["crimecd"]
            if time < jobcd["crimecd"]:
                crimecd = humanize_timedelta(seconds=jobcd["crimecd"] - time)
            else:
                crimecd = "Ready to use."
        if cd["slutcd"] is None:
            slutcd = "Ready to use."
        else:
            time = int(datetime.datetime.utcnow().timestamp()) - cd["slutcd"]
            if time < jobcd["slutcd"]:
                slutcd = humanize_timedelta(seconds=jobcd["slutcd"] - time)
            else:
                slutcd = "Ready to use."
        if not await self.briefcasedisabledcheck(ctx):
            if cd["robcd"] is None:
                robcd = "Ready to use."
            else:
                time = int(datetime.datetime.utcnow().timestamp()) - cd["robcd"]
                if time < jobcd["robcd"]:
                    robcd = humanize_timedelta(seconds=jobcd["robcd"] - time)
                else:
                    robcd = "Ready to use."
        else:
            robcd = "Disabled."
        msg = "Work Cooldown: `{}`\nCrime Cooldown: `{}`\nSlut Cooldown: `{}`\nRob Cooldown: `{}`".format(
            workcd, crimecd, slutcd, robcd
        )
        await ctx.maybe_send_embed(msg)

    @lstyle_set.command()
    @check_global_setting_admin()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def settings(self, ctx):
        """Current lifestyle settings."""
        conf = await self.configglobalcheck(ctx)
        data = await conf.all()
        cooldowns = data["cooldowns"]
        workcd = humanize_timedelta(seconds=cooldowns["workcd"])
        robcd = humanize_timedelta(seconds=cooldowns["robcd"])
        crimecd = humanize_timedelta(seconds=cooldowns["crimecd"])
        slutcd = humanize_timedelta(seconds=cooldowns["slutcd"])
        cooldownmsg = "Work Cooldown: `{}`\nCrime Cooldown: `{}`\nSlut Cooldown: `{}`\nRob Cooldown: `{}`".format(
            workcd, crimecd, slutcd, robcd
        )
        embed = discord.Embed(colour=ctx.author.colour, title="Lifestyle Settings")
        embed.add_field(
            name="Using Default Replies?",
            value="Yes" if data["defaultreplies"] else "No",
            inline=True,
        )
        payouts = data["payouts"]
        slutpayout = f"**Max**: {humanize_number(payouts['slut']['max'])}\n**Min**: {humanize_number(payouts['slut']['min'])}"
        crimepayout = f"**Max**: {humanize_number(payouts['crime']['max'])}\n**Min**: {humanize_number(payouts['crime']['min'])}"
        workpayout = f"**Max**: {humanize_number(payouts['work']['max'])}\n**Min**: {humanize_number(payouts['work']['min'])}"
        embed.add_field(name="Work Payouts", value=workpayout, inline=True)
        embed.add_field(name="Crime Payouts", value=crimepayout, inline=True)
        embed.add_field(name="Slut Payouts", value=slutpayout, inline=True)
        failrates = data["failrates"]
        embed.add_field(
            name="Fail Rates",
            value=f"**Crime**: {failrates['crime']}%\n**Slut**: {failrates['slut']}%\n**Rob**: {failrates['rob']}%\n**Fine**: {data['fine']}%",
            inline=True,
        )
        bailamounts = data["bailamounts"]
        embed.add_field(
            name="Bail Amounts",
            value=f"**Max**: {humanize_number(bailamounts['max'])}%\n**Min**: {humanize_number(bailamounts['min'])}%",
            inline=True,
        )
        embed.add_field(name="Cooldown Settings", value=cooldownmsg, inline=True)
        briefcasesettings = data["disable_briefcase"]
        embed.add_field(
            name="Briefcase Settings",
            value="Disabled."
            if not briefcasesettings
            else f"**Max Balance**: {humanize_number(data['briefcase_max'])}\n**Withdraw Cooldown**: {humanize_timedelta(seconds=cooldowns['withdrawcd'])}\n**Deposit Cooldown**: {humanize_timedelta(seconds=cooldowns['depositcd'])}",
            inline=True,
        )
        minbet = humanize_number(data["betting"]["min"])
        maxbet = humanize_number(data["betting"]["max"])
        betstats = f"**Max**: {maxbet}\n**Min**: {minbet}"
        embed.add_field(name="Betting Info", value=betstats)
        roulette = data["roulette_toggle"]
        game_stats = f"**Roulette**: {'Enabled' if roulette else 'Disabled'}"
        embed.add_field(name="Games", value=game_stats)
        await ctx.send(embed=embed)
