import random
import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class Fun(commands.Cog):
    """Fun commands to entertain your server.
    
    Includes simple, safe interactions demonstrating slash commands and context menus.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("Fun cog initialized")

    @app_commands.command(name="coinflip", description="Flip a coin and get heads or tails.")
    async def coinflip(self, interaction: discord.Interaction):
        """Flip a fair coin.
        
        Args:
            interaction: The interaction context provided by Discord
        """
        try:
            result = random.choice(["Heads", "Tails"])
            embed = discord.Embed(
                title="🪙 Coin Flip",
                description=f"The coin landed on **{result}**!",
                color=discord.Color.blurple()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logger.exception("Error in coinflip command")
            await interaction.response.send_message("An unexpected error occurred while flipping the coin.", ephemeral=True)

    @app_commands.command(name="roll", description="Roll an n-sided die (default 6).")
    @app_commands.describe(sides="Number of sides on the die (2-1000)")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        """Roll a die with a given number of sides.
        
        Validates input and returns a random integer.
        """
        try:
            if not 2 <= sides <= 1000:
                return await interaction.response.send_message("Please choose between 2 and 1000 sides.", ephemeral=True)
            value = random.randint(1, sides)
            await interaction.response.send_message(f"🎲 You rolled **{value}** (1-{sides}).")
        except Exception:
            logger.exception("Error in roll command")
            await interaction.response.send_message("An error occurred while rolling the die.", ephemeral=True)

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Generic error handler for app commands in this cog.
        
        Logs the error and provides a friendly ephemeral message.
        """
        logger.error("App command error in Fun cog: %s", error)
        if interaction.response.is_done():
            await interaction.followup.send("Something went wrong executing that command.", ephemeral=True)
        else:
            await interaction.response.send_message("Something went wrong executing that command.", ephemeral=True)

async def setup(bot: commands.Bot):
    """Load the Fun cog."""
    await bot.add_cog(Fun(bot))
    logger.info("Fun cog loaded successfully")
