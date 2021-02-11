import asyncio
import discord
import random
import calendar

from typing import Any, Union
from discord.utils import get
from datetime import datetime

from redbot.core import Config, checks, commands, bank
from redbot.core.utils.chat_formatting import pagify, humanize_list, humanize_number, box
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

#from redbot.core.bot import Red

class CompositeMetaClass(type(commands.Cog), type(ABC)):
    """This allows the metaclass used for proper type detection to coexist with discord.py's
    metaclass."""

class MarshmallowShop(commands.Cog, metaclass=CompositeMetaClass):
    """
    Shop add-on for Marshmallows.
    """

    #__author__ = "NylaPop"
    __version__ = "1.0.0"

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}"

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=56198540690061319, force_registration=True, invoke_without_command=True
        )
        self.config.register_guild(
            enabled=False, items={}, roles={}, certificates={}, ping=None
        )
        self.config.register_member(lunchbox={})

    @commands.group(autohelp=True)
    @checks.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    async def shop(self, ctx):
        """Marshmallow shop"""
        pass

    @shop.command(name="open")
    async def shop_toggle(self, ctx: commands.Context, on_off: bool = None):
        """Open or close the server's Marshmallow shop.

        Type `[p]open yes` to open the shop. Leave `yes` off to close it."""
        target_state = (
            #on_off
            yes
            #if on_off
            if yes
            else not (await self.config.guild(ctx.guild).enabled())
        )
        await self.config.guild(ctx.guild).enabled.set(target_state)
        if target_state:
            await ctx.send("The Marshmallow shop is now open.")
        else:
            await ctx.send("The Marshmallow shop is now closed.")

    @shop.command(name="add")
    async def shop_add(self, ctx: commands.Context):
        """Add an item to the Marshmallow shop"""

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        types = ["item", "role", "certificate"]
        pred = MessagePredicate.lower_contained_in(types)
        pred_int = MessagePredicate.valid_int(ctx)
        pred_role = MessagePredicate.valid_role(ctx)
        pred_yn = MessagePredicate.yes_or_no(ctx)

        await ctx.send(
            "Do you want to add an item, role or certificate?\nCertificates can be gift card codes, game keys, etc."
        )
        try:
            await self.bot.wait_for("message", timeout=30, check=pred)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again.")
        if pred.result == 0:
            await ctx.send(
                "What is item's name? Don't include `@` in the name."
            )
            try:
                answer = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again.")
            item_name = answer.content
            item_name = item_name.strip("@")
            try:
                is_already_item = await self.config.guild(ctx.guild).items.get_raw(
                    item_name
                )
                if is_already_item:
                    return await ctx.send(
                        "This item already exists."
                    )
            except KeyError:
                ### START ADD CODE ###
                await ctx.send("Describe the item.")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                item_details = answer.content
                if item_details == "":
                    return await ctx.send("Please enter a description.")
                ### END ADD CODE ###
                await ctx.send("How many marshmallows should this cost?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                price = pred_int.result
                if price <= 0:
                    return await ctx.send("price has to be at least 1.")
                await ctx.send("How many are available?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                stock = pred_int.result
                if stock <= 0:
                    return await ctx.send("Amount in stock has to be at least 1.")
                await ctx.send("Is this redeemable?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_yn)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                redeemable = pred_yn.result
                ### START ADD CODE ###
                if not redeemable:
                    return await ctx.send("Please respond y or n.")
                await ctx.send("Is this returnable?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_yn)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                returnable = pred_yn.result
                ### END ADD CODE ###
                await self.config.guild(ctx.guild).items.set_raw(
                    item_name,
                    value={
                        ### START ADD CODE ###
                        "description": item_details,
                        ### END ADD CODE ###
                        "price": price,
                        "stock": stock,
                        "redeemable": redeemable,
                        ### START ADD CODE ###
                        "returnable": returnable,
                        ### END ADD CODE ###
                    },
                )
                await ctx.send(f"{item_name} added.")
        elif pred.result == 1:
            await ctx.send("What is the role?")
            try:
                await self.bot.wait_for("message", timeout=30, check=pred_role)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again.")
            role = pred_role.result
            try:
                is_already_role = await self.config.guild(ctx.guild).roles.get_raw(
                    role.name
                )
                if is_already_role:
                    return await ctx.send(
                        "This item already exists."
                    )
            except KeyError:
                ### START ADD CODE ###
                await ctx.send("Describe the role.")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                item_details = answer.content
                if item_details == "":
                    return await ctx.send("Please enter a description.")
                ### END ADD CODE ###
                await ctx.send("How many marshmallows should this cost?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                price = pred_int.result
                if price <= 0:
                    return await ctx.send("price has to be at least 1.")
                await ctx.send("How many are available?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                stock = pred_int.result
                if stock <= 0:
                    return await ctx.send("Amount in stock has to be at least 1.")
                await self.config.guild(ctx.guild).roles.set_raw(
                    role.name, value={"description": item_details, "price": price, "stock": stock}
                )
                await ctx.send(f"{role.name} added.")
        elif pred.result == 2:
            await ctx.send(
                "What is the certificate's name? Don't include `@` in the name."
            )
            try:
                answer = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again.")
            certificate_name = answer.content
            certificate_name = certificate_name.strip("@")
            try:
                is_already_certificate = await self.config.guild(ctx.guild).certificates.get_raw(
                    certificate_name
                )
                if is_already_certificate:
                    return await ctx.send(
                        "This certificate already exists."
                    )
            except KeyError:
                ### START ADD CODE ###
                await ctx.send("Describe the certificate.")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                item_details = answer.content
                if item_details == "":
                    return await ctx.send("Please enter a description.")
                ### END ADD CODE ###
                await ctx.send("How many marshmallows should this cost?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                price = pred_int.result
                if price <= 0:
                    return await ctx.send("price has to be at least 1.")
                await ctx.send("How many are available?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                stock = pred_int.result
                if stock <= 0:
                    return await ctx.send("Amount in stock has to be at least 1.")
                await ctx.send("Is the item redeemable?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_yn)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                redeemable = pred_yn.result
                ### START ADD CODE ###
                if not redeemable:
                    return await ctx.send("Please respond y or n.")
                await ctx.send("Is this returnable?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_yn)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again.")
                returnable = pred_yn.result
                ### END ADD CODE ###
                await self.config.guild(ctx.guild).certificates.set_raw(
                    certificate_name,
                    value={
                        ### START ADD CODE ###
                        "description": item_details,
                        ### END ADD CODE ###
                        "price": price,
                        "stock": stock,
                        "redeemable": redeemable,
                        ### START ADD CODE ###
                        "returnable": returnable,
                        ### END ADD CODE ###
                    },
                )
                await ctx.send(f"{certificate_name} added.")
        else:
            await ctx.send("Huh?")

    @shop.command(name="delete")
    async def shop_delete(self, ctx: commands.Context, *, item: str):
        """Delete an item from the Marshmallow shop"""
        item = item.strip("@")
        try:
            is_already_item = await self.config.guild(ctx.guild).items.get_raw(item)
            if is_already_item:
                await self.config.guild(ctx.guild).items.clear_raw(item)
                return await ctx.send(f"**{item}** deleted.")
        except KeyError:
            try:
                is_already_certificate = await self.config.guild(ctx.guild).certificates.get_raw(item)
                if is_already_certificate:
                    await self.config.guild(ctx.guild).certificates.clear_raw(item)
                    return await ctx.send(f"**{item}** deleted.")
            except KeyError:
                try:
                    is_already_role = await self.config.guild(ctx.guild).roles.get_raw(
                        item
                    )
                    if is_already_role:
                        await self.config.guild(ctx.guild).roles.clear_raw(item)
                        await ctx.send(f"**{item}** deleted.")
                except KeyError:
                    await ctx.send("That item doesn't exist.")

    @shop.command(name="view")
    async def shop_view(self, ctx: commands.Context, *, item: str):
        """View item info"""
        item = item.strip("@")
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        certificates = await self.config.guild(ctx.guild).certificates.get_raw()

        if item in items:
            info = await self.config.guild(ctx.guild).items.get_raw(item)
            item_type = "item"
        elif item in roles:
            info = await self.config.guild(ctx.guild).roles.get_raw(item)
            item_type = "role"
        elif item in certificates:
            info = await self.config.guild(ctx.guild).certificates.get_raw(item)
            item_type = "certificate"
        else:
            return await ctx.send("That item doesn't exist.")
        desc = info.get("description")
        price = info.get("price")
        cost = str(humanize_number(price))
        stock = info.get("stock")
        stock = str(humanize_number(stock))
        redeemable = info.get("redeemable")
        returnable = info.get("returnable")
        if not redeemable:
            redeemable = False
        if not returnable:
            returnable = False
        await ctx.send(
            f"**__{item}__**\n{desc}\n<:sh_space:755971083210981426>\n*Dept.:* {item_type}\n*Price:* {cost}\n*In Stock:* {stock}\n*Redeemable:* {redeemable}\n*Returnable:* {returnable}"
        )

    @shop.command(name="price")
    async def shop_price(self, ctx: commands.Context, price: int, *, item: str):
        """Change an item's price"""
        if price <= 0:
            return await ctx.send("price has to be at least 1.")
        item = item.strip("@")
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        certificates = await self.config.guild(ctx.guild).certificates.get_raw()

        if item in items:
            await self.config.guild(ctx.guild).items.set_raw(item, "price", value=price)
            await ctx.send(f"**{item}'s** price changed to {price}.")
        elif item in roles:
            await self.config.guild(ctx.guild).roles.set_raw(item, "price", value=price)
            await ctx.send(f"**{item}'s** price changed to {price}.")
        elif item in certificates:
            await self.config.guild(ctx.guild).certificates.set_raw(item, "price", value=price)
            await ctx.send(f"**{item}'s** price changed to {price}.")
        else:
            await ctx.send("This item isn't in the shop. Add it first.")

    @shop.command(name="stock")
    async def shop_stock(self, ctx: commands.Context, stock: int, *, item: str):
        """Change amount of an item the shop has in stock"""
        if stock <= 0:
            return await ctx.send("Amount in stock has to be at least 1.")
        item = item.strip("@")
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        certificates = await self.config.guild(ctx.guild).certificates.get_raw()

        if item in items:
            await self.config.guild(ctx.guild).items.set_raw(
                item, "stock", value=stock
            )
            await ctx.send(f"**{item}'s** stock changed to {stock}.")
        elif item in roles:
            await self.config.guild(ctx.guild).roles.set_raw(
                item, "stock", value=stock
            )
            await ctx.send(f"**{item}'s** stock changed to {stock}.")
        elif item in certificates:
            await self.config.guild(ctx.guild).certificates.set_raw(
                item, "stock", value=stock
            )
            await ctx.send(f"**{item}'s** stock changed to {stock}.")
        else:
            await ctx.send("This item isn't in the shop. Add it first.")

    @shop.command(name="redeemable")
    async def shop_redeemable(
        self, ctx: commands.Context, redeemable: bool, *, item: str
    ):
        """Change whether an item can be redeemed"""
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        certificates = await self.config.guild(ctx.guild).certificates.get_raw()

        item = item.strip("@")
        if item in items:
            await self.config.guild(ctx.guild).items.set_raw(
                item, "redeemable", value=redeemable
            )
            await ctx.send(f"**{item}'s** redeemability changed to {redeemable}.")
        elif item in roles:
            await self.config.guild(ctx.guild).roles.set_raw(
                item, "redeemable", value=redeemable
            )
            await ctx.send(f"**{item}'s** redeemability changed to {redeemable}.")
        elif item in certificates:
            await self.config.guild(ctx.guild).certificates.set_raw(
                item, "redeemable", value=redeemable
            )
            await ctx.send(f"**{item}'s** redeemability changed to {redeemable}.")
        else:
            await ctx.send("This item isn't in the shop. Add it first.")

    @shop.command(name="returnable")
    async def shop_returnable(
        self, ctx: commands.Context, returnable: bool, *, item: str
    ):
        """Change whether an item can be returned"""
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        certificates = await self.config.guild(ctx.guild).certificates.get_raw()

        item = item.strip("@")
        if item in items:
            await self.config.guild(ctx.guild).items.set_raw(
                item, "returnable", value=returnable
            )
            await ctx.send(f"**{item}'s** returnability changed to {returnable}.")
        elif item in roles:
            await self.config.guild(ctx.guild).roles.set_raw(
                item, "returnable", value=returnable
            )
            await ctx.send(f"**{item}'s** returnability changed to {returnable}.")
        elif item in certificates:
            await self.config.guild(ctx.guild).certificates.set_raw(
                item, "returnable", value=returnable
            )
            await ctx.send(f"**{item}'s** returnability changed to {returnable}.")
        else:
            await ctx.send("This item isn't in the shop. Add it first.")

    @shop.command(name="reset")
    async def shop_reset(self, ctx: commands.Context, confirmation: bool = False):
        """Delete all items from the shop"""
        if not confirmation:
            return await ctx.send(
                "This will delete **all** items. This action **cannot** be undone.\n"
                f"If you're sure, type `{ctx.clean_prefix}shop reset yes`."
            )
        for i in await self.config.guild(ctx.guild).items.get_raw():
            await self.config.guild(ctx.guild).items.clear_raw(i)
        for r in await self.config.guild(ctx.guild).roles.get_raw():
            await self.config.guild(ctx.guild).roles.clear_raw(r)
        for g in await self.config.guild(ctx.guild).certificates.get_raw():
            await self.config.guild(ctx.guild).certificates.clear_raw(i)
        await ctx.send("All items have been deleted from the shop.")

    @shop.command(name="ping")
    async def shop_ping(
        self, ctx: commands.Context, who: Union[discord.Member, discord.Role] = None
    ):
        """Set a role/member to be pinged when a member wants to redeem something.

        Leave blank to see current pings"""
        if not who:
            ping_id = await self.config.guild(ctx.guild).ping()
            if not ping_id:
                return await ctx.send("No pings set.")
            ping = get(ctx.guild.members, id=ping_id)
            if not ping:
                ping = get(ctx.guild.roles, id=ping_id)
                if not ping:
                    return await ctx.send(
                        "The role must have been deleted or user must have left."
                    )
            return await ctx.send(f"{ping.name} is set to be pinged.")
        await self.config.guild(ctx.guild).ping.set(who.id)
        await ctx.send(
            f"{who.name} will be pinged when a member wants to redeem something."
        )

    @shop.command(name="resetinventories")
    async def shop_resetinventories(
        self, ctx: commands.Context, confirmation: bool = False
    ):
        """Delete all items from all members' inventories"""
        if not confirmation:
            return await ctx.send(
                "This will delete **all** items from all members' inventories. This action **cannot** be undone.\n"
                f"If you're sure, type `{ctx.clean_prefix}shop resetinventories yes`."
            )
        for member in ctx.guild.members:
            lunchbox = await self.config.member(member).lunchbox.get_raw()
            for item in lunchbox:
                await self.config.member(member).lunchbox.clear_raw(item)
        await ctx.send("All items have been deleted from all members' inventories.")

    @commands.command()
    @commands.guild_only()
    async def shop(self, ctx: commands.Context):
        """See the marshmallow shop"""
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("The Marshmallow shop is closed.")
        page_list = await self._show_shop(ctx)
        if len(page_list) > 1:
            await menu(ctx, page_list, DEFAULT_CONTROLS)
        else:
            await ctx.send(embed=page_list[0])

    @commands.command()
    @commands.guild_only()
    async def buy(self, ctx: commands.Context, *, item: str = ""):
        """Buy an item from the marshmallow shop"""
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("The Marshmallow shop is closed.")
        marshmallows = int(
            await self.bot.get_cog("Marshmallows").config.member(ctx.author).marshmallows()
        )
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        certificates = await self.config.guild(ctx.guild).certificates.get_raw()

        if not item:
            page_list = await self._show_shop(ctx)
            if len(page_list) > 1:
                return await menu(ctx, page_list, DEFAULT_CONTROLS)
            return await ctx.send(embed=page_list[0])
        item = item.strip("@")
        lunchbox = await self.config.member(ctx.author).lunchbox.get_raw()
        if item in lunchbox:
            return await ctx.send("You already own this.")
        if item in roles:
            role_obj = get(ctx.guild.roles, name=item)
            if role_obj:
                role = await self.config.guild(ctx.guild).roles.get_raw(item)
                price = int(role.get("price"))
                stock = int(role.get("stock"))
                if stock == 0:
                    return await ctx.send("**OUT OF STOCK**")
                if price <= marshmallows:
                    pass
                else:
                    return await ctx.send("Maybe you could get this if you didn't already eat all your marshmallows lmao.")
                await ctx.author.add_roles(role_obj)
                marshmallows -= price
                stock -= 1
                await self.bot.get_cog("Marshmallows").config.member(ctx.author).marshmallows.set(
                    marshmallows
                )
                await self.config.member(ctx.author).lunchbox.set_raw(
                    item,
                    value={
                        "price": price,
                        "is_role": True,
                        "is_certificate": False,
                        "redeemable": False,
                        "redeemed": True,
                        "returnable": False,
                        "returned": True,
                    },
                )
                await self.config.guild(ctx.guild).roles.set_raw(
                    item, "stock", value=stock
                )
                await ctx.send(f"You bought **{item}**.")
            else:
                await ctx.send("I can't find that badge.")
        elif item in items:
            item_info = await self.config.guild(ctx.guild).items.get_raw(item)
            price = int(item_info.get("price"))
            stock = int(item_info.get("stock"))
            redeemable = item_info.get("redeemable")
            returnable = item_info.get("returnable")
            if not redeemable:
                redeemable = False
            if not returnable:
                returnable = False
            if stock == 0:
                return await ctx.send("**OUT OF STOCK**")
            if price <= marshmallows:
                pass
            else:
                return await ctx.send("Maybe you could get this if you didn't already eat all your marshmallows lmao.")
            marshmallows -= price
            stock -= 1
            await self.bot.get_cog("Marshmallows").config.member(ctx.author).marshmallows.set(
                marshmallows
            )
            await self.config.guild(ctx.guild).items.set_raw(
                item, "stock", value=stock
            )
            if not redeemable and not returnable:
                await self.config.member(ctx.author).lunchbox.set_raw(
                    item,
                    value={
                        "price": price,
                        "is_role": False,
                        "is_certificate": False,
                        "redeemable": False,
                        "redeemed": True,
                        "returnable": False,
                        "returned": True,
                    },
                )
                await ctx.send(f"You bought **{item}**. __This sale is final.__")
            if not redeemable and returnable:
                await self.config.member(ctx.author).lunchbox.set_raw(
                    item,
                    value={
                        "price": price,
                        "is_role": False,
                        "is_certificate": False,
                        "redeemable": False,
                        "redeemed": True,
                        "returnable": True,
                        "returned": False,
                    },
                )
                await ctx.send(f"You bought **{item}**. You may return it any time before using it.")
            else:
                await self.config.member(ctx.author).lunchbox.set_raw(
                    item,
                    value={
                        "price": price,
                        "is_role": False,
                        "is_certificate": False,
                        "redeemable": True,
                        "redeemed": False,
                        "returnable": True,
                        "returned": False,
                    },
                )
                await ctx.send(
                    f"You bought **{item}**. Type `{ctx.clean_prefix}redeem {item}` or `{ctx.clean_prefix}return {item}` to redeem or return it."
                )
        elif item in certificates:
            certificate_info = await self.config.guild(ctx.guild).certificates.get_raw(item)
            price = int(certificate_info.get("price"))
            stock = int(certificate_info.get("stock"))
            redeemable = certificate_info.get("redeemable")
            returnable = certificate_info.get("returnable")
            if not redeemable:
                redeemable = False
            if not returnable:
                returnable = False
            if stock == 0:
                return await ctx.send("**OUT OF STOCK**")
            if price <= marshmallows:
                pass
            else:
                return await ctx.send("Maybe you could get this if you didn't already eat all your marshmallows lmao.")
            marshmallows -= price
            stock -= 1
            await self.bot.get_cog("Marshmallows").config.member(ctx.author).marshmallows.set(
                marshmallows
            )
            await self.config.guild(ctx.guild).certificates.set_raw(
                item, "stock", value=stock
            )
            if not redeemable and not returnable:
                await self.config.member(ctx.author).lunchbox.set_raw(
                    item,
                    value={
                        "price": price,
                        "is_role": False,
                        "is_certificate": True,
                        "redeemable": False,
                        "redeemed": True,
                        "returnable": False,
                        "returned": True,
                    },
                )
                await ctx.send(f"You bought **{item}**. __This sale is final.__")
            if not redeemable and returnable:
                await self.config.member(ctx.author).lunchbox.set_raw(
                    item,
                    value={
                        "price": price,
                        "is_role": False,
                        "is_certificate": True,
                        "redeemable": False,
                        "redeemed": True,
                        "returnable": True,
                        "returned": False,
                    },
                )
                await ctx.send(f"You bought **{item}**. You may return it any time before using it.")
            else:
                await self.config.member(ctx.author).lunchbox.set_raw(
                    item,
                    value={
                        "price": price,
                        "is_role": False,
                        "is_certificate": True,
                        "redeemable": True,
                        "redeemed": False,
                        "returnable": True,
                        "returned": False,
                    },
                )
                await ctx.send(
                    f"You bought **{item}**. Type `{ctx.clean_prefix}redeem {item}` or `{ctx.clean_prefix}return {item}` to redeem or return it."
                )
        else:
            page_list = await self._show_shop(ctx)
            if len(page_list) > 1:
                return await menu(ctx, page_list, DEFAULT_CONTROLS)
            return await ctx.send(embed=page_list[0])

    @commands.command(name="return")
    @commands.guild_only()
    async def shop_return(self, ctx: commands.Context, *, item: str):
        """Return an item. You'll only get a 50% refund"""
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("The Marshmallow shop is closed.")
        marshmallows = int(
            await self.bot.get_cog("Marshmallows").config.member(ctx.author).marshmallows()
        )
        lunchbox = await self.config.member(ctx.author).lunchbox.get_raw()

        if item in lunchbox:
            pass
        else:
            return await ctx.send("Dude, I can't refund you for something you don't even own. smh")
        info = await self.config.member(ctx.author).lunchbox.get_raw(item)

        is_certificate = info.get("is_certificate")
        if is_certificate:
            return await ctx.send("lol nice try")
        is_role = info.get("is_role")
        if is_role:
            role_obj = get(ctx.guild.roles, name=item)
            if role_obj:
                await ctx.author.remove_roles(role_obj)
        redeemed = info.get("redeemed")
        if not redeemed:
            redeemed = False
        if redeemed:
            return await ctx.send("Did you really just try to finesse me? <a:blink:729474129409081394>")
        price = int(info.get("price"))
        return_price = price * 0.5
        marshmallows += return_price
        refund_amount = str(humanize_number(return_price))
        await self.config.member(ctx.author).lunchbox.clear_raw(item)
        await self.bot.get_cog("Marshmallows").config.member(ctx.author).marshmallows.set(marshmallows)
        await ctx.send(
            f"All done. **{item}** has been returned. I refunded {refund_amount} <:so_love:754613619836321892> back to your account."
        )

    @commands.command()
    @commands.guild_only()
    async def lunchbox(self, ctx: commands.Context):
        """Look inside your lunchbox"""
        lunchbox = await self.config.member(ctx.author).lunchbox.get_raw()

        lst = []
        for i in lunchbox:
            info = await self.config.member(ctx.author).lunchbox.get_raw(i)
            if not info.get("is_role"):
                lst.append(i)
            else:
                role_obj = get(ctx.guild.roles, name=i)
                lst.append(role_obj.mention)
        if lst == []:
            desc = "<a:where:804616694176940032> ...there's nothing here."
        else:
            desc = humanize_list(lst)
        embed = discord.Embed(
            description=desc, colour=ctx.author.colour, timestamp=datetime.now()
        )
        embed.set_author(
            name=f"{ctx.author.display_name}'s lunchbox",
            icon_url=ctx.author.avatar_url,
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["clb"])
    @commands.guild_only()
    async def cleanlunchbox(self, ctx: commands.Context, *, item: str):
        """Remove an item from your lunchbox"""
        lunchbox = await self.config.member(ctx.author).lunchbox.get_raw()
        if item not in lunchbox:
            return await ctx.send("...you don't own that.")
        await self.config.member(ctx.author).lunchbox.clear_raw(item)
        await ctx.send(f"**{item}** tossed in the trash.")

    @commands.command()
    @commands.guild_only()
    async def redeem(self, ctx: commands.Context, *, item: str):
        """Redeem an item"""
        lunchbox = await self.config.member(ctx.author).lunchbox.get_raw()
        if item not in lunchbox:
            return await ctx.send("...you don't own that.")
        info = await self.config.member(ctx.author).lunchbox.get_raw(item)
        is_role = info.get("is_role")
        if is_role:
            return await ctx.send("Roles aren't redeemable.")
        redeemable = info.get("redeemable")
        if not redeemable:
            return await ctx.send("This isn't redeemable.")
        redeemed = info.get("redeemed")
        if redeemed:
            return await ctx.send("lol yeah ok")
        ping_id = await self.config.guild(ctx.guild).ping()
        if not ping_id:
            return await ctx.send("This hasn't been set up, yet. Ask a staff member to help you.")
        ping = get(ctx.guild.members, id=ping_id)
        if not ping:
            ping = get(ctx.guild.roles, id=ping_id)
            if not ping:
                return await ctx.send("This hasn't been set up, yet. Ask a staff member to help you.")
            if not ping.mentionable:
                await ping.edit(mentionable=True)
                await ctx.send(
                    f"{ping.mention}, {ctx.author.mention} would like to redeem **{item}**."
                )
                await ping.edit(mentionable=False)
            else:
                await ctx.send(
                    f"{ping.mention}, {ctx.author.mention} would like to redeem **{item}**."
                )
            await self.config.member(ctx.author).lunchbox.set_raw(
                item, "redeemed", value=True
            )
        else:
            await ctx.send(
                f"{ping.mention}, {ctx.author.mention} would like to redeem **{item}**."
            )
            await self.config.member(ctx.author).lunchbox.set_raw(
                item, "redeemed", value=True
            )

    async def _show_shop(self, ctx):
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        certificates = await self.config.guild(ctx.guild).certificates.get_raw()
        stuff = []
        for i in items:
            item = await self.config.guild(ctx.guild).items.get_raw(i)
            price = humanize_number(int(item.get("price")))
            stock = humanize_number(int(item.get("stock")))
            item_text = f"__Item__ **{i}** | __Price__ {price} <:so_love:754613619836321892> | __In Stock__ {stock}"
            stuff.append(item_text)
        for g in certificates:
            certificate = await self.config.guild(ctx.guild).certificates.get_raw(g)
            price = humanize_number(int(certificate.get("price")))
            stock = humanize_number(int(certificate.get("stock")))
            certificate_text = f"__Item__ **{g}** | __Price__ {price} <:so_love:754613619836321892> | __In Stock__ {stock}"
            stuff.append(certificate_text)
        for r in roles:
            role_obj = get(ctx.guild.roles, name=r)
            if not role_obj:
                continue
            role = await self.config.guild(ctx.guild).roles.get_raw(r)
            price = humanize_number(int(role.get("price")))
            stock = humanize_number(int(role.get("stock")))
            role_text = f"__Badge__ {role_obj.mention} | __Price__ {price} <:so_love:754613619836321892> | __In Stock__ {stock}"
            stuff.append(role_text)
        if stuff == []:
            desc = "The shop is empty. Ask a staff member to restock it!"
        else:
            desc = "\n".join(stuff)
        page_list = []
        for page in pagify(desc, delims=["\n"], page_length=1000):
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                description=page,
                timestamp=datetime.now(),
            )
            embed.set_author(
                name=f"{ctx.guild.name}'s Marshmallow Shop", icon_url=ctx.guild.icon_url,
            )
            page_list.append(embed)
        return page_list
