import platform
import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class Utility(commands.Cog):
    """General utility commands for server members and admins.
    
    Demonstrates basic slash commands and ephemeral replies.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("Utility cog initialized")

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        try:
            latency_ms = round(self.bot.latency * 1000)
            await interaction.response.send_message(f"🏓 Pong! {latency_ms}ms", ephemeral=True)
        except Exception:
            logger.exception("Error in ping command")
            await interaction.response.send_message("An error occurred while calculating latency.", ephemeral=True)

    @app_commands.command(name="about", description="Show basic information about the bot.")
    async def about(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(
                title="About this bot",
                color=discord.Color.green()
            )
            embed.add_field(name="Python", value=platform.python_version(), inline=True)
            embed.add_field(name="discord.py", value=discord.__version__, inline=True)
            embed.set_footer(text=f"Requested by {interaction.user}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            logger.exception("Error in about command")
            await interaction.response.send_message("Unable to fetch about info right now.", ephemeral=True)

async def setup(bot: commands.Bot):
    """Load the Utility cog."""
    await bot.add_cog(Utility(bot))
    logger.info("Utility cog loaded successfully")
