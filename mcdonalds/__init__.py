from redbot.core import data_manager

from .mcdonalds import McDonalds


def setup(bot):
    mcdonalds = McDonalds(bot)
    data_manager.bundled_data_path(mcdonalds)
    bot.add_cog(mcdonalds)
