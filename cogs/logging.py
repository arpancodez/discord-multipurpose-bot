import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class Logging(commands.Cog):
    """Server event logging cog.

    Demonstrates listener usage and structured logging with embeds.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("Logging cog initialized")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Log when a member joins the guild and post an embed to a log channel.
        
        Looks for a channel named 'mod-logs'. In production, make this configurable.
        """
        try:
            guild = member.guild
            log_ch = discord.utils.get(guild.text_channels, name="mod-logs")
            logger.info("Member joined: %s (%s)", member, member.id)
            if log_ch:
                embed = discord.Embed(
                    title="Member Joined",
                    description=f"{member.mention} joined",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(name="ID", value=str(member.id))
                await log_ch.send(embed=embed)
        except Exception:
            logger.exception("Error handling member join event")

async def setup(bot: commands.Bot):
    """Load the Logging cog."""
    await bot.add_cog(Logging(bot))
    logger.info("Logging cog loaded successfully")
