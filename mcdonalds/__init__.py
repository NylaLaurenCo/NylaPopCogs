from redbot.core import data_manager

from .mcdonalds import McDonalds


def setup(bot):
    plant = McDonalds(bot)
    data_manager.bundled_data_path(plant)
    bot.add_cog(plant)
