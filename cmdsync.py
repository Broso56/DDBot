from http import client
from multiprocessing.connection import Client
import discord
from discord.ext import commands

class UserSync(commands.Cog):
    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx, arg1): # Command to manually sync slash commands (Honestly no idea how this works, especially across files. Main issue with bot ATM.)
        if arg1 == 'guild':
            await ctx.bot.tree.sync(guild=ctx.guild)
            await ctx.send('Synced to current guild.')
        if arg1 == 'global':
            await ctx.bot.tree.sync()
            await ctx.send('Synced globally.')

async def setup(client):
    await client.add_cog(UserSync(client))
