from .eviction import Eviction

def setup(bot):
    n = Eviction(bot)
    bot.add_cog(n)
