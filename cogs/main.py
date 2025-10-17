import discord
import asyncio
import logging
import os
import traceback
import aiohttp
from discord.ext import commands
from discord.ext.commands import Bot, Context
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DiscordBot')

# Bot configuration
class BotConfig:
    TOKEN = os.getenv('BOT_TOKEN')
    PREFIX = os.getenv('BOT_PREFIX', '!')
    OWNER_ID = int(os.getenv('OWNER_ID', '0'))
    DATABASE_URL = os.getenv('DATABASE_URL')
    
class MultipurposeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            owner_id=BotConfig.OWNER_ID,
            case_insensitive=True,
            strip_after_prefix=True,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for commands | !help"
            ),
            status=discord.Status.online
        )
        
        # Bot attributes
        self.config = BotConfig
        self.uptime = datetime.now()
        self.session = None
        self.db = None
        
        # Cog extensions
        self.initial_extensions = [
            'cogs.moderation',
            'cogs.fun',
            'cogs.games',
            'cogs.utility',
            'cogs.antinuke',
            'cogs.help',
            'cogs.logging',
            'cogs.economy',
            'cogs.music',
            'cogs.automod'
        ]
    
    async def get_prefix(self, bot, message):
        """Dynamic prefix handler"""
        if not message.guild:
            return commands.when_mentioned_or(BotConfig.PREFIX)(bot, message)
        
        # Add custom guild prefix logic here if needed
        return commands.when_mentioned_or(BotConfig.PREFIX)(bot, message)
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Bot is starting up...")
        
        # Create aiohttp session
        self.session = aiohttp.ClientSession()
        
        # Load extensions
        await self.load_extensions()
        
        logger.info(f"Loaded {len(self.extensions)} extensions")
    
    async def load_extensions(self):
        """Load all cog extensions"""
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Successfully loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
                traceback.print_exc()
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info(f"Serving {len(set(self.get_all_members()))} users")
        logger.info("Bot is ready!")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_guild_join(self, guild):
        """Called when the bot joins a guild"""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        # Send welcome message to the first available text channel
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="Thanks for adding me!",
                    description=f"Hello! I'm a multipurpose Discord bot.\n\n"
                               f"🔧 **Prefix:** `{BotConfig.PREFIX}`\n"
                               f"📚 **Help:** `{BotConfig.PREFIX}help`\n"
                               f"🌟 **Features:** Moderation, Fun, Games, Utility, Music & More!",
                    color=0x00ff00
                )
                embed.set_thumbnail(url=self.user.display_avatar.url)
                embed.add_field(
                    name="Getting Started",
                    value=f"Type `{BotConfig.PREFIX}help` to see all available commands!",
                    inline=False
                )
                try:
                    await channel.send(embed=embed)
                except:
                    pass
                break
    
    async def on_guild_remove(self, guild):
        """Called when the bot is removed from a guild"""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
    
    async def on_command_error(self, ctx: Context, error: Exception):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing Required Argument",
                description=f"You're missing the `{error.param.name}` argument.\n"
                           f"**Usage:** `{ctx.command.signature}`",
                color=0xff0000
            )
            await ctx.send(embed=embed, delete_after=10)
            return
        
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description=f"You need the following permissions: {', '.join(error.missing_permissions)}",
                color=0xff0000
            )
            await ctx.send(embed=embed, delete_after=10)
            return
        
        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="❌ Bot Missing Permissions",
                description=f"I need the following permissions: {', '.join(error.missing_permissions)}",
                color=0xff0000
            )
            await ctx.send(embed=embed, delete_after=10)
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏰ Command on Cooldown",
                description=f"Try again in {error.retry_after:.2f} seconds.",
                color=0xffaa00
            )
            await ctx.send(embed=embed, delete_after=10)
            return
        
        # Log unexpected errors
        logger.error(f"Unexpected error in command {ctx.command}: {error}")
        traceback.print_exception(type(error), error, error.__traceback__)
        
        embed = discord.Embed(
            title="❌ An Error Occurred",
            description="An unexpected error occurred while processing your command.",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=10)
    
    async def close(self):
        """Clean shutdown"""
        logger.info("Bot is shutting down...")
        
        if self.session:
            await self.session.close()
        
        await super().close()

# Bot instance
bot = MultipurposeBot()

@bot.command(name='reload', hidden=True)
@commands.is_owner()
async def reload_cog(ctx: Context, cog: str = None):
    """Reload a cog (Owner only)"""
    if cog is None:
        embed = discord.Embed(
            title="🔄 Reload Cog",
            description="Please specify a cog to reload.",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        return
    
    try:
        await bot.reload_extension(f'cogs.{cog}')
        embed = discord.Embed(
            title="✅ Cog Reloaded",
            description=f"Successfully reloaded `{cog}` cog.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        logger.info(f"Reloaded cog: {cog}")
    except Exception as e:
        embed = discord.Embed(
            title="❌ Reload Failed",
            description=f"Failed to reload `{cog}` cog.\nError: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        logger.error(f"Failed to reload cog {cog}: {e}")

@bot.command(name='load', hidden=True)
@commands.is_owner()
async def load_cog(ctx: Context, cog: str):
    """Load a cog (Owner only)"""
    try:
        await bot.load_extension(f'cogs.{cog}')
        embed = discord.Embed(
            title="✅ Cog Loaded",
            description=f"Successfully loaded `{cog}` cog.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        logger.info(f"Loaded cog: {cog}")
    except Exception as e:
        embed = discord.Embed(
            title="❌ Load Failed",
            description=f"Failed to load `{cog}` cog.\nError: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        logger.error(f"Failed to load cog {cog}: {e}")

@bot.command(name='unload', hidden=True)
@commands.is_owner()
async def unload_cog(ctx: Context, cog: str):
    """Unload a cog (Owner only)"""
    try:
        await bot.unload_extension(f'cogs.{cog}')
        embed = discord.Embed(
            title="✅ Cog Unloaded",
            description=f"Successfully unloaded `{cog}` cog.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        logger.info(f"Unloaded cog: {cog}")
    except Exception as e:
        embed = discord.Embed(
            title="❌ Unload Failed",
            description=f"Failed to unload `{cog}` cog.\nError: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        logger.error(f"Failed to unload cog {cog}: {e}")

@bot.command(name='shutdown', hidden=True)
@commands.is_owner()
async def shutdown(ctx: Context):
    """Shutdown the bot (Owner only)"""
    embed = discord.Embed(
        title="🔄 Shutting Down",
        description="Bot is shutting down...",
        color=0xffaa00
    )
    await ctx.send(embed=embed)
    logger.info("Bot shutdown initiated by owner")
    await bot.close()

if __name__ == '__main__':
    if not BotConfig.TOKEN:
        logger.error("Bot token not found! Please set BOT_TOKEN in your .env file.")
        exit(1)
    
    try:
        bot.run(BotConfig.TOKEN, log_handler=None)
    except discord.LoginFailure:
        logger.error("Invalid bot token provided.")
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}")
        traceback.print_exc()
