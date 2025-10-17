import discord
from discord.ext import commands
from discord import app_commands
import logging

# Configure logging for this cog
logger = logging.getLogger(__name__)


class YuesCog(commands.Cog):
    """
    YuesCog - A professional Discord.py cog template.
    
    This cog serves as a foundation for building custom Discord bot commands.
    It includes sample commands demonstrating both prefix and slash command functionality.
    
    Attributes:
        bot (commands.Bot): The Discord bot instance.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the YuesCog.
        
        Args:
            bot (commands.Bot): The bot instance to attach this cog to.
        """
        self.bot = bot
        logger.info("YuesCog has been initialized.")
    
    # Event listener example - Called when the cog is loaded
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Event listener that triggers when the bot is ready.
        Useful for initialization tasks specific to this cog.
        """
        logger.info(f"YuesCog is ready and operational.")
    
    # Prefix command example
    @commands.command(name="hello", help="Sends a friendly greeting message.")
    async def hello_command(self, ctx: commands.Context, *, name: str = None):
        """
        A simple greeting command that responds to the user.
        
        Usage:
            !hello [name]
        
        Args:
            ctx (commands.Context): The context of the command invocation.
            name (str, optional): The name to greet. Defaults to the user's display name.
        """
        # If no name is provided, use the author's display name
        target_name = name if name else ctx.author.display_name
        
        # Create an embed for a more professional look
        embed = discord.Embed(
            title="👋 Hello!",
            description=f"Hello, {target_name}! Welcome to the server!",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        
        await ctx.send(embed=embed)
        logger.info(f"Hello command used by {ctx.author} (ID: {ctx.author.id})")
    
    # Slash command example
    @app_commands.command(name="info", description="Displays information about the bot or server.")
    async def info_command(self, interaction: discord.Interaction):
        """
        A slash command that provides bot and server information.
        
        Usage:
            /info
        
        Args:
            interaction (discord.Interaction): The interaction object from the slash command.
        """
        # Gather server information
        guild = interaction.guild
        
        # Create an informative embed
        embed = discord.Embed(
            title="📊 Server Information",
            description=f"Information about **{guild.name}**",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        
        # Add fields with server details
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Member Count", value=guild.member_count, inline=True)
        embed.add_field(name="Created At", value=discord.utils.format_dt(guild.created_at, style='F'), inline=False)
        
        # Set server icon if available
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        # Respond to the interaction
        await interaction.response.send_message(embed=embed)
        logger.info(f"Info command used by {interaction.user} (ID: {interaction.user.id})")
    
    # Hybrid command example (works as both prefix and slash command)
    @commands.hybrid_command(name="ping", description="Check the bot's latency.")
    async def ping_command(self, ctx: commands.Context):
        """
        A hybrid command that displays the bot's latency.
        
        Usage:
            !ping  OR  /ping
        
        Args:
            ctx (commands.Context): The context of the command invocation.
        """
        # Calculate the bot's latency in milliseconds
        latency_ms = round(self.bot.latency * 1000, 2)
        
        # Create a simple embed with latency information
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency_ms}ms**",
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed)
        logger.info(f"Ping command used by {ctx.author} (ID: {ctx.author.id}) - Latency: {latency_ms}ms")
    
    # Error handler example for this cog
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """
        Local error handler for commands in this cog.
        
        Args:
            ctx (commands.Context): The context where the error occurred.
            error (commands.CommandError): The error that was raised.
        """
        # Handle specific error types
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
        elif isinstance(error, commands.CommandNotFound):
            # Silently ignore command not found errors
            pass
        else:
            # Log unexpected errors
            logger.error(f"Error in command {ctx.command}: {error}", exc_info=error)
            await ctx.send("❌ An error occurred while processing the command.")


# Setup function - Required for loading the cog
async def setup(bot: commands.Bot):
    """
    Setup function to add the YuesCog to the bot.
    
    This function is called when the cog is loaded via bot.load_extension().
    
    Args:
        bot (commands.Bot): The bot instance to add the cog to.
    """
    await bot.add_cog(YuesCog(bot))
    logger.info("YuesCog has been loaded successfully.")
