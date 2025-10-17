import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class Help(commands.Cog):
    """Custom help command using slash commands and app command tree introspection.

    Presents a simple, navigable overview of available slash commands.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("Help cog initialized")

    @app_commands.command(name="help", description="Show available commands and categories.")
    async def help(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(title="Help", color=discord.Color.blurple())
            # Group commands by cog for readability
            by_cog: dict[str, list[str]] = {}
            for cmd in self.bot.tree.get_commands():
                if isinstance(cmd, app_commands.Command):
                    cog_name = getattr(cmd.binding, "__class__", type("_", (), {})) .__name__ if getattr(cmd, "binding", None) else "Misc"
                    by_cog.setdefault(cog_name, []).append(f"/{cmd.name} – {cmd.description or 'No description'}")
            for cog_name, lines in sorted(by_cog.items()):
                value = "\n".join(sorted(lines))[:1024] or "No commands."
                embed.add_field(name=cog_name, value=value, inline=False)
            embed.set_footer(text=f"Requested by {interaction.user}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            logger.exception("Error generating help")
            await interaction.response.send_message("Unable to render help right now.", ephemeral=True)

async def setup(bot: commands.Bot):
    """Load the Help cog."""
    await bot.add_cog(Help(bot))
    logger.info("Help cog loaded successfully")
