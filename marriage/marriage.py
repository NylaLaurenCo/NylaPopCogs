import discord
import asyncio
import random

from redbot.core import Config, checks, commands, bank
from redbot.core.utils.chat_formatting import humanize_list
from redbot.core.utils.predicates import MessagePredicate

from redbot.core.bot import Red

__author__ = "NylaPop"


class Marriage(commands.Cog):
    """
    Marriage with some extra stuff :eyes:
    """

    __author__ = "NylaPop"
    __version__ = "1.0.0"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=5465461324979524, force_registration=True
        )

        self.config.register_member(
            married=False,
            current=[],
            divorced=False,
            exes=[],
            about="Who's asking? <:13look_shrek:717577462292283482>",
            crush=None,
            marcount=0,
            happiness=100,
            gifts={
                "loveletter": 0,
                "flowers": 0,
                "sweets": 0,
                "coffee": 0,
                "snack": 0,
                "shopping": 0,
                "makeup": 0,
                "nudes": 0,
                "car": 0,
                "house": 0,
                "yacht": 0,
                "money": 0,
            },
        )
        self.config.register_guild(
            toggle=False,
            marprice=1500,
            divprice=2,
            currency=0,
            multi=False,
            stuff={
                "flirt": [5, 0],
                "glance": [1, 0],
                "stare": [3, 0],
                "wink": [5, 0],
                "kiss": [10, 0],
                "hold hands": [7, 0],
                "hug": [15, 0],
                "seks": [45, 0],
                "yell": [-20, 0],
                "push": [-60, 0],
                "slap": [-80, 0],
                "punch": [-95, 0],
                "kick": [-95, 0],
                "stomp": [-100, 0],
                "breakfast": [20, 30],
                "lunch": [20, 30],
                "dinner": [20, 100],
                "snack": [15, 10],
                "date": [10, 150],
                "flowers": [15, 60],
                "sweets": [20, 20],
                "coffee": [5, 5],
                "drinks": [10, 60],
                "shopping": [40, 1000],
                "pamper": [45, 500],
                "loveletter": [10, 0],
                "sext": [25, 0],
                "nudes": [30, 0],
                "makeup": [8, 100],
                "car": [50, 35000],
                "house": [90, 500000],
                "yacht": [100, 1000000],
                "vacation": [60, 5000],
                "money": [45, 5000],
            },
        )

    #"stuff": [happiness, price]
    #"gift": [owned pcs]

    @commands.group(autohelp=True)
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def marriage(self, ctx):
        """Various Marriage settings."""
        pass

    @marriage.command(name="toggle")
    async def marriage_toggle(self, ctx: commands.Context, on_off: bool = None):
        """Toggle Marriage for current server.

        If `on_off` is not provided, the state will be flipped."""
        target_state = (
            on_off
            if on_off
            else not (await self.config.guild(ctx.guild).toggle())
        )
        await self.config.guild(ctx.guild).toggle.set(target_state)
        if target_state:
            await ctx.send("Marriage is now enabled.")
        else:
            await ctx.send("Marriage is now disabled.")

    @checks.is_owner()
    @marriage.command(name="currency")
    async def marriage_currency(self, ctx: commands.Context, currency: int):
        """Set the currency. 0 for global currency, 1 for marshmallows"""
        if currency != 0:
            if currency != 1:
                return await ctx.send("Um currency can only be 0 or 1.")
            loaded = self.bot.get_cog("Marshmallows")
            if not loaded:
                return await ctx.send(
                    f"Um Marshmallows isn't loaded. Load it using `{ctx.clean_prefix}load marshmallows`"
                )
        await self.config.guild(ctx.guild).currency.set(currency)
        await ctx.tick()

    @marriage.command(name="multiple")
    async def marriage_multiple(self, ctx: commands.Context, state: bool):
        """Enable/disable whether members can be married to multiple people at once."""
        if not state:
            text = "Members cannot marry multiple people."
        else:
            text = "Members can marry multiple people."
        await self.config.guild(ctx.guild).multi.set(state)
        await ctx.send(text)

    @marriage.command(name="marprice")
    async def marriage_marprice(self, ctx: commands.Context, price: int):
        """Set the price for getting married.

        With each past marriage, the cost of getting married is 50% more"""
        if price <= 0:
            return await ctx.send("Um price cannot be 0 or less.")
        await self.config.guild(ctx.guild).marprice.set(price)
        await ctx.tick()

    @marriage.command(name="divprice")
    async def marriage_divprice(self, ctx: commands.Context, multiplier: int):
        """Set the MULTIPLIER for getting divorced.

        This is a multiplier, not the price! Default is 2."""
        if multiplier <= 1:
            return await ctx.send("Um that ain't a valia multiplier.")
        await self.config.guild(ctx.guild).divprice.set(multiplier)
        await ctx.tick()

    @marriage.command(name="changehappiness")
    async def marriage_changehappiness(
        self, ctx: commands.Context, action: str, happiness: int
    ):
        """Set the action's/gift's happiness

        Happiness has to be in range 1 to 100. Negative actions (f.e. flirting with someone other than one's spouse) should have negative happiness.
        !!! Remember that starting point for everyone is 100 == happy and satisfied, 0 == leave their spouse"""
        available = [
          "flirt",
          "glance",
          "stare",
          "wink",
          "kiss",
          "hold hands",
          "hug",
          "seks",
          "yell",
          "push",
          "slap",
          "punch",
          "kick",
          "stomp",
          "breakfast",
          "lunch",
          "dinner",
          "snack",
          "date",
          "flowers",
          "sweets",
          "coffee",
          "drinks",
          "shopping",
          "pamper",
          "loveletter",
          "sext",
          "nudes",
          "makeup",
          "car",
          "house",
          "yacht",
          "vacation",
          "money",
        ]
        if action not in available:
            return await ctx.send(f"Available actions/gifts are: {available}")
        #if happiness < 0:
        #    return await ctx.send("Um happiness has to be 0 or more.")
        if happiness > 100:
            return await ctx.send("Um happiness has to be 100 or less.")
        #action = await self.config.guild(ctx.guild).stuff.get_raw(action)
        #action[0] = happiness
        #happiness = action[0]
        #await self.config.guild(ctx.guild).stuff.set_raw(action, value=[action[0], happiness])
        #await ctx.tick()
        action_data = await self.config.guild(ctx.guild).stuff.get_raw(action)
        await self.config.guild(ctx.guild).stuff.set_raw(action, value=[action_data[0], happiness])
        await ctx.tick()

    @marriage.command(name="changeprice")
    async def marriage_changeprice(
        self, ctx: commands.Context, action: str, price: int
    ):
        """Set the action's/gift's price"""
        available = [
          "flirt",
          "glance",
          "stare",
          "wink",
          "kiss",
          "hold hands",
          "hug",
          "seks",
          "yell",
          "push",
          "slap",
          "punch",
          "kick",
          "stomp",
          "breakfast",
          "lunch",
          "dinner",
          "snack",
          "date",
          "flowers",
          "sweets",
          "coffee",
          "drinks",
          "shopping",
          "pamper",
          "loveletter",
          "sext",
          "nudes",
          "makeup",
          "car",
          "house",
          "yacht",
          "vacation",
          "money",
        ]
        if action not in available:
            return await ctx.send(f"Available actions/gifts are: {available}")
        if price < 0:
            return await ctx.send("Um price has to be 0 or more.")
        action_data = await self.config.guild(ctx.guild).stuff.get_raw(action)
        await self.config.guild(ctx.guild).stuff.set_raw(action, value=[action_data[1], price])
        await ctx.tick()

    @commands.guild_only()
    @commands.command()
    async def lovelife(self, ctx: commands.Context, *, about: str):
        """Describe your love life."""
        if not await self.config.guild(ctx.guild).toggle():
            return await ctx.send("Marriage is off for this server. Ask staff to turn it on.")
        if len(about) > 1000:
            return await ctx.send("WTF are you writing a research paper??! <:dog_wtf:802959590408323133>")
        await self.config.member(ctx.author).about.set(about)
        await ctx.tick()

    @commands.guild_only()
    @commands.command()
    async def relationship(self, ctx: commands.Context, member: discord.Member = None):
        """See your or someone else's relationship status"""
        if not await self.config.guild(ctx.guild).toggle():
            return await ctx.send("Marriage is off for this server. Ask staff to turn it on.")
        if not member:
            member = ctx.author
        conf = self.config.member(member)

        is_married = await conf.married()
        if not is_married:
            is_divorced = await conf.married()
            if not is_divorced:
                rs_status = "Single"
            else:
                rs_status = "Divorced"
        else:
            rs_status = "Married"
            spouse_ids = await conf.current()
            spouses = []
            for spouse_id in spouse_ids:
                spouse = ctx.guild.get_member(spouse_id)
                if not spouse:
                    continue
                spouse = spouse.name
                spouses.append(spouse)
            if spouses == []:
                spouse_header = "Spouse:"
                spouse_text = "None"
            else:
                spouse_text = humanize_list(spouses)
                if len(spouses) == 1:
                    spouse_header = "Spouse:"
                else:
                    spouse_header = "Spouses:"
        marcount = await conf.marcount()
        if marcount == 1:
            been_married = f"{marcount} time"
        else:
            been_married = f"{marcount} times"
        if marcount != 0:
            exes_ids = await conf.exes()
            if exes_ids == []:
                ex_text = "None"
            else:
                exes = []
                for ex_id in exes_ids:
                    ex = ctx.guild.get_member(ex_id)
                    if not ex:
                        continue
                    ex = ex.name
                    exes.append(ex)
                if exes == []:
                    ex_text = "None"
                else:
                    ex_text = humanize_list(exes)
        crush = ctx.guild.get_member(await conf.crush())
        if not crush:
            crush = "None"
        else:
            crush = crush.name
        if await self.config.guild(ctx.guild).currency() == 0:
            currency = await bank.get_currency_name(ctx.guild)
            bal = await bank.get_balance(member)
        else:
            bal = int(await self.bot.get_cog("Marshmallows").config.member(member).marshmallows())
            currency = "<:so_love:754613619836321892>"
        gifts = await conf.gifts.get_raw()
        giftos = []
        for gift in gifts:
            amount = gifts.get(gift)
            if amount > 0:
                if amount == 1:
                    textos = f"{gift} - {amount} pc"
                else:
                    textos = f"{gift} - {amount} pcs"
                giftos.append(textos)
            else:
                continue
        if giftos == []:
            gift_text = "None"
        else:
            gift_text = humanize_list(giftos)
        e = discord.Embed(colour=member.color, description="*This is just for roleplay/pretend and is not real.*\n<:sh_space:755971083210981426>")
        e.set_author(name=f"{member.name}'s Lovelife", icon_url=member.avatar_url)
        e.set_footer(text=f"{member.name}#{member.discriminator} ({member.id})")
        e.set_thumbnail(url=member.avatar_url)
        e.add_field(name="Overheard:", value=await conf.about(), inline=False)
        e.add_field(name="Status:", value=rs_status)
        if is_married:
            e.add_field(name=spouse_header, value=spouse_text)
        e.add_field(name="Crush:", value=crush)
        e.add_field(name="Happiness:", value=await conf.happiness())
        e.add_field(name="x Married:", value=been_married)
        if await conf.marcount() != 0:
            e.add_field(name="Exes:", value=ex_text)
        e.add_field(name="Assets:", value=f"{bal} {currency}")
        e.add_field(name="Owned Gifts:", value=gift_text)

        await ctx.send(embed=e)

    @commands.guild_only()
    @commands.command()
    async def exes(self, ctx: commands.Context, member: discord.Member = None):
        """Display your or someone else's exes"""
        if not await self.config.guild(ctx.guild).toggle():
            return await ctx.send("Marriage is off for this server. Ask staff to turn it on.")
        if not member:
            member = ctx.author
        exes_ids = await self.config.member(member).exes()
        exes = []
        for ex_id in exes_ids:
            ex = ctx.guild.get_member(ex_id)
            if not ex:
                continue
            ex = ex.name
            exes.append(ex)
        if exes == []:
            ex_text = "unknown"
        else:
            ex_text = humanize_list(exes)
        await ctx.send(f"{member.mention}'s exes are: {ex_text}")

    @commands.guild_only()
    @commands.command()
    async def crush(self, ctx: commands.Context, member: discord.Member = None):
        """Tell us who you have a crush on"""
        if not await self.config.guild(ctx.guild).toggle():
            return await ctx.send("Marriage is off for this server. Ask staff to turn it on.")
        if not member:
            await self.config.member(ctx.author).crush.set(None)
        else:
            if member.id == ctx.author.id:
                return await ctx.send("You cannot have a crush on yourself.")
            await self.config.member(ctx.author).crush.set(member.id)
        await ctx.tick()

    @commands.guild_only()
    @commands.command()
    async def marry(self, ctx: commands.Context, member: discord.Member):
        """Marry the love of your life."""
        if not await self.config.guild(ctx.guild).toggle():
            return await ctx.send("Marriage is off for this server. Ask staff to turn it on.")
        if member.id == ctx.author.id:
            return await ctx.send("You cannot marry yourself.")
        if member.id in await self.config.member(ctx.author).current():
            return await ctx.send("You two are already married.")
        if not await self.config.guild(ctx.guild).multi():
            if await self.config.member(ctx.author).married():
                return await ctx.send("You're already married.")
            if await self.config.member(member).married():
                return await ctx.send("They're already married.")
        await ctx.send(
            f"{ctx.author.mention} has asked {member.mention} to marry them!\n"
            f"{member.mention}, what do you say?"
        )
        pred = MessagePredicate.yes_or_no(ctx, ctx.channel, member)
        await self.bot.wait_for("message", check=pred)
        if not pred.result:
            return await ctx.send("Damn... I was looking forward to the ceremony...")
        default_amount = await self.config.guild(ctx.guild).marprice()
        author_marcount = await self.config.member(ctx.author).marcount()
        target_marcount = await self.config.member(member).marcount()

        author_multiplier = author_marcount / 2 + 1
        target_multiplier = target_marcount / 2 + 1

        if author_multiplier <= target_multiplier:
            multiplier = target_multiplier
        else:
            multiplier = author_multiplier
        if multiplier != 0:
            amount = default_amount * multiplier
        else:
            amount = default_amount
        amount = int(round(amount))
        if await self.config.guild(ctx.guild).currency() == 0:
            currency = await bank.get_currency_name(ctx.guild)
            end_amount = f"{amount} {currency}"
            if await bank.can_spend(ctx.author, amount):
                if await bank.can_spend(member, amount):
                    await bank.withdraw_credits(ctx.author, amount)
                    await bank.withdraw_credits(member, amount)
                else:
                    return await ctx.send(f"imagine being this poor")
            else:
                return await ctx.send(f"imagine being this poor")
        else:
            author_marshmallows = int(
                await self.bot.get_cog("Marshmallows").config.member(ctx.author).marshmallows()
            )
            target_marshmallows = int(
                await self.bot.get_cog("Marshmallows").config.member(member).marshmallows()
            )
            end_amount = f"{amount} <:so_love:754613619836321892>"
            if amount <= author_marshmallows:
                if amount <= target_marshmallows:
                    await self.bot.get_cog("Marshmallows").config.member(
                        ctx.author
                    ).marshmallows.set(author_marshmallows - amount)
                    await self.bot.get_cog("Marshmallows").config.member(member).marshmallows.set(
                        target_marshmallows - amount
                    )
                else:
                    return await ctx.send(f"imagine being this poor")
            else:
                return await ctx.send(f"imagine being this poor")
        await self.config.member(ctx.author).marcount.set(author_marcount + 1)
        await self.config.member(member).marcount.set(target_marcount + 1)

        await self.config.member(ctx.author).married.set(True)
        await self.config.member(member).married.set(True)

        await self.config.member(ctx.author).divorced.set(False)
        await self.config.member(member).divorced.set(False)

        async with self.config.member(ctx.author).current() as acurrent:
            acurrent.append(member.id)
        async with self.config.member(member).current() as tcurrent:
            tcurrent.append(ctx.author.id)
        await self.config.member(ctx.author).happiness.set(100)
        await self.config.member(member).happiness.set(100)

        await ctx.send(
            f":church: {ctx.author.mention} and {member.mention} are now a happy married couple! "
            f"Congrats! :tada:\n*You both paid {end_amount}.*"
        )

    @commands.guild_only()
    @commands.command()
    async def divorce(
        self, ctx: commands.Context, member: discord.Member, court: bool = False
    ):
        """Divorce your current spouse"""
        if not await self.config.guild(ctx.guild).toggle():
            return await ctx.send("Marriage is off for this server. Ask staff to turn it on.")
        if member.id == ctx.author.id:
            return await ctx.send("You cannot divorce yourself.")
        if member.id not in await self.config.member(ctx.author).current():
            return await ctx.send("You two aren't married.")
        if not court:
            await ctx.send(
                f"{ctx.author.mention} wants to divorce you, {member.mention}, do you accept?\n"
                "If you say no, you will go to the court."
            )
            pred = MessagePredicate.yes_or_no(ctx, ctx.channel, member)
            await self.bot.wait_for("message", check=pred)
            if pred.result:
                default_amount = await self.config.guild(ctx.guild).marprice()
                default_multiplier = await self.config.guild(ctx.guild).divprice()
                author_marcount = await self.config.member(ctx.author).marcount()
                target_marcount = await self.config.member(member).marcount()

                author_multiplier = author_marcount / 2 + 1
                target_multiplier = target_marcount / 2 + 1

                if author_multiplier <= target_multiplier:
                    multiplier = target_multiplier
                else:
                    multiplier = author_multiplier
                if multiplier != 0:
                    amount = default_amount * multiplier * default_multiplier
                else:
                    amount = default_amount * default_multiplier
                amount = int(round(amount))
                if await self.config.guild(ctx.guild).currency() == 0:
                    currency = await bank.get_currency_name(ctx.guild)
                    end_amount = f"You both paid {amount} {currency}"
                    if await bank.can_spend(ctx.author, amount):
                        if await bank.can_spend(member, amount):
                            await bank.withdraw_credits(ctx.author, amount)
                            await bank.withdraw_credits(member, amount)
                        else:
                            return await ctx.send(
                                f"lmaoooo you're too broke to divorce! <:pepe_lol_point:802951769096585276> You can petition the courts like a poor to do it for free.  "
                                "Type `{ctx.clean_prefix}divorce {member.mention} yes`"
                            )
                    else:
                        return await ctx.send(
                            f"lmaoooo you're too broke to divorce! <:pepe_lol_point:802951769096585276> You can petition the courts like a poor to do it for free.  "
                            "Type `{ctx.clean_prefix}divorce {member.mention} yes`"
                        )
                else:
                    author_marshmallows = int(
                        await self.bot.get_cog("Marshmallows")
                        .config.member(ctx.author)
                        .marshmallows()
                    )
                    target_marshmallows = int(
                        await self.bot.get_cog("Marshmallows")
                        .config.member(member)
                        .marshmallows()
                    )
                    end_amount = f"You both paid {amount} <:so_love:754613619836321892>"
                    if amount <= author_marshmallows:
                        if amount <= target_marshmallows:
                            await self.bot.get_cog("Marshmallows").config.member(
                                ctx.author
                            ).marshmallows.set(author_marshmallows - amount)
                            await self.bot.get_cog("Marshmallows").config.member(
                                member
                            ).marshmallows.set(target_marshmallows - amount)
                        else:
                            return await ctx.send(
                                f"lmaoooo you're too broke to divorce! <:pepe_lol_point:802951769096585276> You can petition the courts like a poor to do it for free.  "
                                "Type `{ctx.clean_prefix}divorce {member.mention} yes`"
                            )
                    else:
                        return await ctx.send(
                            f"lmaoooo you're too broke to divorce! <:pepe_lol_point:802951769096585276> You can petition the courts like a poor to do it for free.  "
                            "Type `{ctx.clean_prefix}divorce {member.mention} yes`"
                        )
            else:
                court = True
        if court:
            court = random.randint(1, 100)
            court_multiplier = court / 100
            if await self.config.guild(ctx.guild).currency() == 0:
                currency = await bank.get_currency_name(ctx.guild)
                abal = await bank.get_balance(ctx.author)
                tbal = await bank.get_balance(member)
                aamount = int(round(abal * court_multiplier))
                tamount = int(round(tbal * court_multiplier))
                end_amount = f"{ctx.author.name} paid {aamount} {currency}, {member.name} paid {tamount} {currency}"
                await bank.withdraw_credits(ctx.author, aamount)
                await bank.withdraw_credits(member, tamount)
            else:
                author_marshmallows = int(
                    await self.bot.get_cog("Marshmallows")
                    .config.member(ctx.author)
                    .marshmallows()
                )
                target_marshmallows = int(
                    await self.bot.get_cog("Marshmallows").config.member(member).marshmallows()
                )
                aamount = int(round(author_marshmallows * court_multiplier))
                tamount = int(round(target_marshmallows * court_multiplier))
                end_amount = f"{ctx.author.name} paid {aamount} <:so_love:754613619836321892>, {member.name} paid {tamount} <:so_love:754613619836321892>"
                await self.bot.get_cog("Marshmallows").config.member(ctx.author).marshmallows.set(
                    author_marshmallows - aamount
                )
                await self.bot.get_cog("Marshmallows").config.member(member).marshmallows.set(
                    target_marshmallows - tamount
                )
        async with self.config.member(ctx.author).current() as acurrent:
            acurrent.remove(member.id)
        async with self.config.member(member).current() as tcurrent:
            tcurrent.remove(ctx.author.id)
        async with self.config.member(ctx.author).exes() as aexes:
            aexes.append(member.id)
        async with self.config.member(member).exes() as texes:
            texes.append(ctx.author.id)
        if len(await self.config.member(ctx.author).current()) == 0:
            await self.config.member(ctx.author).married.set(False)
            await self.config.member(ctx.author).divorced.set(True)
        if len(await self.config.member(member).current()) == 0:
            await self.config.member(member).married.set(False)
            await self.config.member(member).divorced.set(True)
        await ctx.send(
            f":broken_heart: {ctx.author.mention} and {member.mention} got divorced...\n*{end_amount}.*"
        )

    @commands.guild_only()
    @commands.command()
    async def rp(
        self,
        ctx: commands.Context,
        action: str,
        member: discord.Member,
        item: str = None,
    ):
        """Do something with someone"""
        gc = self.config.guild
        mc = self.config.member
        if not await gc(ctx.guild).toggle():
            return await ctx.send("Marriage is off for this server. Ask staff to turn it on.")
        consent = 1
        if action == "flirt":
            endtext = (
                f"<a:pepe_flirt:802960898641231883> {ctx.author.mention} is flirting with {member.mention}"
            )
        elif action == "seks":
            consent = 0
        elif action == "breakfast":
            endtext = (
                f":pancakes: :bacon: {ctx.author.mention} made {member.mention} a delicious breakfast."
            )
        elif action == "lunch":
            endtext = (
                f":bento: {ctx.author.mention} took {member.mention} out for lunch. It was tasty!"
            )
        elif action == "dinner":
            endtext = (
                f":lobster: {ctx.author.mention} took {member.mention} on a fancy dinner."
            )
        elif action == "date":
            endtext = (
                f":people_holding_hands: {ctx.author.mention} spent time with {member.mention} on a nice, relaxing date."
            )
        elif action == "drinks":
            endtext = (
                f":cocktail: {ctx.author.mention} took {member.mention} out for drinks and got a lil' tipsy!"
            )
        elif action == "pamper":
            endtext = (
                f"<:pepe_adore:802951856846405652> {ctx.author.mention} pampered {member.mention} with love, affection and gift cards to self-care."
            )
        elif action == "sext":
            endtext = (
                f"<:xo_love_u_aod:611242952882389042> {ctx.author.mention} sent {member.mention} some naughty text messages. <a:hatsu_love:802963021127352320>"
            )
        elif action == "vacation":
            endtext = (
                f":airplane: {ctx.author.mention} treated {member.mention} to a much needed 5-star vacation."
            )
        elif action == "glance":
            endtext = (
                f"<:13look:717577461046444053> {ctx.author.mention} snuck a quick glance at {member.mention}! What if they looked back? :flushed:"
            )
        elif action == "stare":
            endtext = (
                f"<:13look_shrek:717577462292283482> {ctx.author.mention} is staring seductively at {member.mention}! <a:a_w_lick:743119153312956517>"
            )
        elif action == "wink":
            endtext = (
                f"<a:13lewd_wink:749841311883985019> {ctx.author.mention} just winked at {member.mention}. It's clear they want one thing. :flushed:"
            )
        elif action == "kiss":
            endtext = (
                f":kiss: {ctx.author.mention} gave {member.mention} a romantic kiss."
            )
        elif action == "hold hands":
            endtext = (
                f"<a:stars_aod:612360693932621844> {ctx.author.mention} took {member.mention}'s hands in theirs and felt sparks. Aww."
            )
        elif action == "hug":
            endtext = (
                f"<a:hatsu_love:802963021127352320> {ctx.author.mention} gently grabs {member.mention} and hugs them close."
            )
        elif action == "yell":
            endtext = (
                f"<:13eyes:754285875453624330> {ctx.author.mention} yelled so loudly at {member.mention} that all the neighbors could hear! <:13sb_look:736425355417485362>"
            )
        elif action == "push":
            endtext = (
                f"<:13eyes2:754285875416006706> {ctx.author.mention} pushed {member.mention} and made them fall into a cabinet. Oh sh-!"
            )
        elif action == "slap":
            endtext = (
                f"<a:k_k_slap:733372281639665688> {ctx.author.mention} reached back and slapped {member.mention} **HARD** across the face!"
            )
        elif action == "punch":
            endtext = (
                f"<a:square_up:796218591866912799> WTF!! {ctx.author.mention} punched {member.mention} in the face and knocked out a tooth!"
            )
        elif action == "kick":
            endtext = (
                f":scream: OMGSH! {ctx.author.mention} JUST KICKED {member.mention}! I hope they're okay!"
            )
        elif action == "stomp":
            endtext = (
                f"**WTF!!!** {ctx.author.mention} **CURB STOMPED {member.mention}!** THEIR EARS ARE BLEEDING!!!"
            )
        elif action == "gift":
            gifts = [
                "loveletter",
                "flowers",
                "sweets",
                "coffee",
                "snack",
                "shopping",
                "makeup",
                "nudes",
                "car",
                "house",
                "yacht",
                "money",
            ]
            if item not in gifts:
                return await ctx.send(f"Available gifts are: {gifts}")
            endtext = (
                f":gift: {ctx.author.mention} has gifted one {item} to {member.mention}"
            )
        else:
            return await ctx.send(
                "Available actions are: `flirt`, `glance`, `stare`, `wink`, `kiss`, `hold hands`, `hug`, `seks`, `yell`, `push`, `slap`, `punch`, `kick`, `stomp`, `breakfast`, `lunch`, `dinner`, `date`, `drinks`, `pamper`, `sext`, `vacation`, `gift`"
            )
        if action == "gift":
            author_gift = await mc(ctx.author).gifts.get_raw(item)
            member_gift = await mc(member).gifts.get_raw(item)
            action = await gc(ctx.guild).stuff.get_raw(item)
            happiness = action[0]
            price = action[1]
        else:
            action = await gc(ctx.guild).stuff.get_raw(action)
            happiness = action[0]
            price = action[1]
            author_gift = 0
            member_gift = -1
        if author_gift == 0:
            price = int(round(price))
            if await self.config.guild(ctx.guild).currency() == 0:
                if await bank.can_spend(ctx.author, price):
                    await bank.withdraw_credits(ctx.author, price)
                    member_gift += 1
                    author_gift -= 1
                else:
                    return await ctx.send("You don't even have enough money. Stop wasting my time.")
            else:
                author_marshmallows = int(
                    await self.bot.get_cog("Marshmallows")
                    .config.member(ctx.author)
                    .marshmallows()
                )
                if price <= author_marshmallows:
                    await self.bot.get_cog("Marshmallows").config.member(
                        ctx.author
                    ).marshmallows.set(author_marshmallows - price)
                    member_gift += 1
                    author_gift -= 1
                else:
                    return await ctx.send("You don't even have enough money. Stop wasting my time.")
        else:
            author_gift -= 1
            member_gift += 1
        if author_gift >= 0:
            await mc(ctx.author).gifts.set_raw(item, value=author_gift)
        if member_gift > 0:
            await mc(member).gifts.set_raw(item, value=member_gift)
        if consent == 0:
            await ctx.send(
                f"<a:cheeks:802995703123017728> {ctx.author.mention} wants to bang you, {member.mention}. Give consent? <a:4dance_peen:735923702394519674>"
            )
            pred = MessagePredicate.yes_or_no(ctx, ctx.channel, member)
            try:
                await self.bot.wait_for("message", timeout=60, check=pred)
            except asyncio.TimeoutError:
                return await ctx.send(
                    "lol if you have to think that hard, it's a no."
                )
            if pred.result:
                t_temp = await mc(member).happiness()
                t_missing = 100 - t_temp
                if t_missing != 0:
                    if happiness <= t_missing:
                        await mc(member).happiness.set(t_temp + happiness)
                    else:
                        await mc(member).happiness.set(100)
                a_temp = await mc(ctx.author).happiness()
                a_missing = 100 - a_temp
                if a_missing != 0:
                    if happiness <= a_missing:
                        await mc(ctx.author).happiness.set(a_temp + happiness)
                    else:
                        await mc(ctx.author).happiness.set(100)
                endtext = f"<:okay_daddy:802980074268786706> {ctx.author.mention} banged {member.mention}. It was **amazing**. <a:13shake:729474123578998834>"
            else:
                a_temp = await mc(ctx.author).happiness()
                if happiness < a_temp:
                    await mc(ctx.author).happiness.set(a_temp - happiness)
                else:
                    await mc(ctx.author).happiness.set(0)
                endtext = "<:simp_hand:802963169576222770> lol they refused to bang you and you were forced to use your hand. <:simp_pills:802995365838192692>"
        else:
            t_temp = await mc(member).happiness()
            t_missing = 100 - t_temp
            if t_missing != 0:
                if happiness <= t_missing:
                    await mc(member).happiness.set(t_temp + happiness)
                else:
                    await mc(member).happiness.set(100)
            a_temp = await mc(ctx.author).happiness()
            a_missing = 100 - a_temp
            if a_missing != 0:
                if happiness <= a_missing:
                    await mc(ctx.author).happiness.set(a_temp + happiness)
                else:
                    await mc(ctx.author).happiness.set(100)
        spouses = await mc(ctx.author).current()
        if member.id in spouses:
            pass
        else:
            if await mc(ctx.author).married():
                for sid in spouses:
                    spouse = ctx.guild.get_member(sid)
                    s_temp = await mc(spouse).happiness()
                    if s_temp < happiness:
                        new_s_temp = 0
                    else:
                        new_s_temp = s_temp - happiness
                    await mc(spouse).happiness.set(new_s_temp)
                    if new_s_temp <= 0:
                        async with self.config.member(ctx.author).current() as acurrent:
                            acurrent.remove(spouse.id)
                        async with self.config.member(spouse).current() as tcurrent:
                            tcurrent.remove(ctx.author.id)
                        async with self.config.member(ctx.author).exes() as aexes:
                            aexes.append(spouse.id)
                        async with self.config.member(spouse).exes() as texes:
                            texes.append(ctx.author.id)
                        if len(await self.config.member(ctx.author).current()) == 0:
                            await self.config.member(ctx.author).married.set(False)
                            await self.config.member(ctx.author).divorced.set(True)
                        if len(await self.config.member(spouse).current()) == 0:
                            await self.config.member(spouse).married.set(False)
                            await self.config.member(spouse).divorced.set(True)
                        if await self.config.guild(ctx.guild).currency() == 0:
                            abal = await bank.get_balance(ctx.author)
                            tamount = int(round(tbal * court_multiplier))
                            await bank.withdraw_credits(ctx.author, abal)
                            await bank.deposit_credits(spouse, abal)
                        else:
                            author_marshmallows = int(
                                await self.bot.get_cog("Marshmallows").config.member(ctx.author).marshmallows()
                            )
                            spouse_marshmallows = int(
                                await self.bot.get_cog("Marshmallows").config.member(spouse).marshmallows()
                            )
                            await self.bot.get_cog("Marshmallows").config.member(
                                ctx.author
                            ).marshmallows.set(0)
                            await self.bot.get_cog("Marshmallows").config.member(
                                spouse
                            ).marshmallows.set(spouse_marshmallows + author_marshmallows)
                        endtext = f"{endtext}\nLOL! {ctx.author.mention} was a **horrible** partner to {spouse.mention} "
                        "so {spouse.mention} left them and took all their money! What a loser <:lol_dicaprio:802981845645787186> "
        await ctx.send(endtext)
