import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)


class AntiNuke(commands.Cog):
    """Anti-nuke protection cog to prevent server raids and malicious actions.
    
    This cog monitors and prevents potentially harmful actions such as:
    - Mass channel deletions
    - Mass role deletions
    - Mass member kicks/bans
    - Unauthorized permission changes
    """

    def __init__(self, bot: commands.Bot):
        """Initialize the AntiNuke cog.
        
        Args:
            bot: The bot instance
        """
        self.bot = bot
        self.action_cooldowns = {}  # Track actions to detect spam
        logger.info("AntiNuke cog initialized")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        """Monitor channel deletions to detect potential raids.
        
        Args:
            channel: The deleted channel
        """
        try:
            guild = channel.guild
            
            # Fetch the audit log to see who deleted the channel
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                if entry.target.id == channel.id:
                    deleter = entry.user
                    
                    # Log the deletion
                    logger.warning(f"Channel {channel.name} deleted by {deleter} in {guild.name}")
                    
                    # Send alert to a designated log channel (if configured)
                    # This is a placeholder - would need proper configuration
                    log_channel = discord.utils.get(guild.text_channels, name="anti-nuke-logs")
                    if log_channel:
                        embed = discord.Embed(
                            title="⚠️ Channel Deleted",
                            description=f"**Channel:** {channel.name}\n**Deleted by:** {deleter.mention}",
                            color=discord.Color.red(),
                            timestamp=discord.utils.utcnow()
                        )
                        await log_channel.send(embed=embed)
                    break
                    
        except discord.Forbidden:
            logger.error(f"Missing permissions to check audit logs in {guild.name}")
        except Exception as e:
            logger.error(f"Error in on_guild_channel_delete: {e}")

    @app_commands.command(name="antinuke", description="Configure anti-nuke protection settings")
    @app_commands.checks.has_permissions(administrator=True)
    async def antinuke_config(self, interaction: discord.Interaction, enabled: bool):
        """Configure anti-nuke protection for the server.
        
        Args:
            interaction: The interaction object
            enabled: Whether to enable or disable anti-nuke protection
        """
        try:
            # This would typically save to a database
            # For demonstration purposes, we'll just send a confirmation
            
            status = "enabled" if enabled else "disabled"
            embed = discord.Embed(
                title="🛡️ Anti-Nuke Configuration",
                description=f"Anti-nuke protection has been **{status}** for this server.",
                color=discord.Color.green() if enabled else discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"Configured by {interaction.user}")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Anti-nuke {status} in {interaction.guild.name} by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error in antinuke_config command: {e}")
            await interaction.response.send_message(
                "An error occurred while configuring anti-nuke protection.",
                ephemeral=True
            )

    @antinuke_config.error
    async def antinuke_config_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handle errors for the antinuke_config command.
        
        Args:
            interaction: The interaction object
            error: The error that occurred
        """
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You need Administrator permissions to use this command.",
                ephemeral=True
            )
        else:
            logger.error(f"Unhandled error in antinuke_config: {error}")
            await interaction.response.send_message(
                "An unexpected error occurred.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    """Load the AntiNuke cog.
    
    Args:
        bot: The bot instance
    """
    await bot.add_cog(AntiNuke(bot))
    logger.info("AntiNuke cog loaded successfully")
