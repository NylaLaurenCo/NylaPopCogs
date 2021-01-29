import logging
import math

from discord.ext import tasks
from redbot.core import Config, bank, commands
from redbot.core.bot import Red
from tabulate import tabulate

log = logging.getLogger("red.nylapopcogs.activitycredits")

# taken from Red-Discordbot bank.py
def is_owner_if_bank_global():
    """
    Command decorator. If the bank is global, it checks if the author is
    bot owner, otherwise it only checks
    if command was used in guild - it DOES NOT check any permissions.
    When used on the command, this should be combined
    with permissions check like `guildowner_or_permissions()`.
    """

    async def pred(ctx: commands.Context):
        author = ctx.author
        if not await bank.is_global():
            if not ctx.guild:
                return False
            return True
        else:
            return await ctx.bot.is_owner(author)

    return commands.check(pred)


class ActivityCredits(commands.Cog):
    """
    Award currency credits to active members.
    """

    __version__ = "1.1"

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=582650109, force_registration=True
        )

        default_config = {"credits": 0, "messages": 0}

        self.config.register_global(**default_config)
        self.config.register_guild(**default_config)

        self.bot.loop.create_task(self.initialize())
        self.msg = {}
        self.actcredits.start()

    async def initialize(self):
        await self.bot.wait_until_red_ready()

        if await bank.is_global():
            self.cache = await self.config.all()
        else:
            self.cache = await self.config.all_guilds()
        self.bank = await bank.is_global()

    def cog_unload(self):
        self.actcredits.cancel()

    @commands.Cog.listener()
    async def on_message_without_command(self, message):

        if message.author.bot:
            return
        if message.guild == None:
            return
        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return

        if await bank.is_global():
            try:
                self.msg[message.author.id].append(message.id)
            except KeyError:
                self.msg[message.author.id] = [message.id]
        else:
            try:
                self.msg[message.guild.id]
                try:
                    self.msg[message.guild.id][message.author.id].append(message.id)
                except KeyError:
                    self.msg[message.guild.id][message.author.id] = [message.id]
            except KeyError:
                self.msg[message.guild.id] = {message.author.id: [message.id]}

    @tasks.loop(minutes=1)
    async def actcredits(self):
        if self.bank is not await bank.is_global():
            if await bank.is_global():
                self.cache = await self.config.all()
            else:
                self.cache = await self.config.all_guilds()
            self.bank = await bank.is_global()

        if await bank.is_global():
            msgs = self.msg
            for user, msg in msgs.items():
                if len(msg) >= self.cache["messages"]:
                    num = math.floor(len(msg) / self.cache["messages"])
                    del (self.msg[user])[0 : (num * self.cache["messages"])]
                    val = await bank.deposit_credits(
                        (await self.bot.get_or_fetch_user(user)),
                        num * self.cache["credits"],
                    )
        else:
            msgs = self.msg
            for guild, users in msgs.items():
                if not self.bot.cog_disabled_in_guild(self, self.bot.get_guild(guild)):
                    for user, msg in users.items():
                        if len(msg) >= self.cache[guild]["messages"]:
                            num = math.floor(len(msg) / self.cache[guild]["messages"])
                            del (self.msg[guild][user])[
                                0 : (num * self.cache[guild]["messages"])
                            ]
                            val = await bank.deposit_credits(
                                (
                                    await self.bot.get_or_fetch_member(
                                        self.bot.get_guild(guild), user
                                    )
                                ),
                                num * self.cache[guild]["credits"],
                            )

    @actcredits.before_loop
    async def before_actcredits(self):
        await self.bot.wait_until_red_ready()

    @is_owner_if_bank_global()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.group(aliases=["actcreditsset"])
    async def activitycredits(self, ctx):
        """ Set up activity credits. """

    @is_owner_if_bank_global()
    @commands.admin_or_permissions(manage_guild=True)
    @activitycredits.command(name="info", aliases=["settings"])
    async def ts_info(self, ctx):
        """ Show current settings """

        if await bank.is_global():
            await ctx.send(
                f"Credits: {self.cache['credits']}\nMessages: {self.cache['messages']}"
            )
        else:
            await ctx.send(
                f"Credits: {self.cache[ctx.guild.id]['credits']}\nMessages: {self.cache[ctx.guild.id]['messages']}"
            )

    @is_owner_if_bank_global()
    @commands.admin_or_permissions(manage_guild=True)
    @activitycredits.command(name="credits")
    async def ts_credits(self, ctx, number: int):
        """
        Set the number of credits to grant

        Set the number to 0 to disable
        Max value is 1000
        """

        if await bank.is_global():
            if 0 <= number <= 1000:
                await self.config.credits.set(number)
                self.cache["credits"] = number
                if not await ctx.tick():
                    await ctx.send("Setting saved")
            else:
                await ctx.send(
                    f"Enter a value between 0-1000"
                )
        else:
            if 0 <= number <= 1000:
                await self.config.guild(ctx.guild).credits.set(number)
                self.cache[ctx.guild.id] = await self.config.guild(ctx.guild).all()
                if not await ctx.tick():
                    await ctx.send("Setting saved")
            else:
                await ctx.send(
                    f"Enter a value between 0-1000"
                )

    @is_owner_if_bank_global()
    @commands.admin_or_permissions(manage_guild=True)
    @activitycredits.command(name="messages")
    async def ts_messages(self, ctx, number: int):
        """
        Set the number of messages required to gain credits

        Set the number to 0 to disable
        Max value is 100
        """

        if await bank.is_global():
            if 0 <= number <= 100:
                await self.config.messages.set(number)
                self.cache["messages"] = number
                if not await ctx.tick():
                    await ctx.send("Setting saved")
            else:
                await ctx.send(
                    f"Enter a value between 0-100"
                )
        else:
            if 0 <= number <= 100:
                await self.config.guild(ctx.guild).messages.set(number)
                self.cache[ctx.guild.id] = await self.config.guild(ctx.guild).all()
                if not await ctx.tick():
                    await ctx.send("Setting saved")
            else:
                await ctx.send(
                    f"Enter a value between 0-100"
                )

    async def red_get_data_for_user(self, *, user_id: int):
        # this cog does not store any data
        return {}

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        # this cog does not store any data
        pass
