"""
Discord Multipurpose Bot - Main Entry Point
Professional Discord.py bot with moderation, antinuke, fun, utility, and logging features.
Author: Professional Discord Bot Developer
Version: 1.0.0
"""

import discord
from discord.ext import commands
import asyncio
import logging
import json
import os
import sys
from typing import Optional, List
import aiohttp
import asyncpg
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('DiscordBot')


class DiscordBot(commands.AutoShardedBot):
    """Professional Discord Bot with advanced features."""
    
    def __init__(self) -> None:
        """Initialize the bot with necessary intents and configuration."""
        # Configure intents
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.presences = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            owner_ids=set(),
            strip_after_prefix=True,
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True)
        )
        
        self.config: dict = {}
        self.db_pool: Optional[asyncpg.Pool] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.start_time: datetime = datetime.utcnow()
        self.cogs_list: List[str] = [
            'cogs.moderation',
            'cogs.antinuke',
            'cogs.fun',
            'cogs.utility',
            'cogs.logging',
            'cogs.help'
        ]
        
    async def get_prefix(self, message: discord.Message) -> List[str]:
        """Get custom prefix for the guild or use default.
        
        Args:
            message: The message to get prefix for
            
        Returns:
            List of valid prefixes for the guild
        """
        default_prefix = self.config.get('default_prefix', '!')
        
        if not message.guild:
            return commands.when_mentioned_or(default_prefix)(self, message)
        
        try:
            if self.db_pool:
                guild_prefix = await self.db_pool.fetchval(
                    'SELECT prefix FROM guild_config WHERE guild_id = $1',
                    message.guild.id
                )
                if guild_prefix:
                    return commands.when_mentioned_or(guild_prefix)(self, message)
        except Exception as e:
            logger.error(f'Error fetching prefix for guild {message.guild.id}: {e}')
        
        return commands.when_mentioned_or(default_prefix)(self, message)
    
    async def load_config(self) -> None:
        """Load bot configuration from config.json file."""
        try:
            with open('config/config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info('Configuration loaded successfully')
        except FileNotFoundError:
            logger.error('config.json not found! Please create one from config.example.json')
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f'Invalid JSON in config.json: {e}')
            sys.exit(1)
    
    async def setup_database(self) -> None:
        """Setup PostgreSQL database connection pool."""
        try:
            database_url = self.config.get('database_url')
            if not database_url:
                logger.warning('No database URL configured, database features will be disabled')
                return
            
            self.db_pool = await asyncpg.create_pool(
                database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Initialize database tables
            async with self.db_pool.acquire() as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS guild_config (
                        guild_id BIGINT PRIMARY KEY,
                        prefix VARCHAR(10) DEFAULT '!',
                        log_channel BIGINT,
                        mod_role BIGINT,
                        mute_role BIGINT,
                        antinuke_enabled BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                ''')
                
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS warnings (
                        id SERIAL PRIMARY KEY,
                        guild_id BIGINT NOT NULL,
                        user_id BIGINT NOT NULL,
                        moderator_id BIGINT NOT NULL,
                        reason TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                ''')
                
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS antinuke_whitelist (
                        guild_id BIGINT NOT NULL,
                        user_id BIGINT NOT NULL,
                        added_by BIGINT NOT NULL,
                        added_at TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY (guild_id, user_id)
                    )
                ''')
                
            logger.info('Database connection established and tables initialized')
        except Exception as e:
            logger.error(f'Failed to setup database: {e}')
    
    async def load_cogs(self) -> None:
        """Load all bot cogs/extensions."""
        for cog in self.cogs_list:
            try:
                await self.load_extension(cog)
                logger.info(f'Loaded cog: {cog}')
            except Exception as e:
                logger.error(f'Failed to load cog {cog}: {e}', exc_info=True)
    
    async def setup_hook(self) -> None:
        """Setup hook called when the bot is starting up."""
        # Create aiohttp session
        self.session = aiohttp.ClientSession()
        
        # Load configuration
        await self.load_config()
        
        # Setup database
        await self.setup_database()
        
        # Load all cogs
        await self.load_cogs()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f'Synced {len(synced)} slash command(s)')
        except Exception as e:
            logger.error(f'Failed to sync slash commands: {e}')
    
    async def on_ready(self) -> None:
        """Event handler for when bot is ready."""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guild(s)')
        logger.info(f'Watching {len(self.users)} user(s)')
        logger.info('Bot is ready!')
        
        # Set bot presence
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f'{len(self.guilds)} servers | !help'
        )
        await self.change_presence(status=discord.Status.online, activity=activity)
    
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Event handler for when bot joins a guild.
        
        Args:
            guild: The guild that was joined
        """
        logger.info(f'Joined guild: {guild.name} (ID: {guild.id})')
        
        # Initialize guild config in database
        if self.db_pool:
            try:
                await self.db_pool.execute(
                    'INSERT INTO guild_config (guild_id) VALUES ($1) ON CONFLICT DO NOTHING',
                    guild.id
                )
            except Exception as e:
                logger.error(f'Failed to initialize guild config: {e}')
    
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Event handler for when bot leaves a guild.
        
        Args:
            guild: The guild that was left
        """
        logger.info(f'Left guild: {guild.name} (ID: {guild.id})')
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Global error handler for command errors.
        
        Args:
            ctx: The command context
            error: The error that occurred
        """
        # Ignore command not found errors
        if isinstance(error, commands.CommandNotFound):
            return
        
        # Handle cooldown errors
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f'⏰ This command is on cooldown. Try again in {error.retry_after:.2f}s',
                delete_after=5
            )
            return
        
        # Handle missing permissions
        if isinstance(error, commands.MissingPermissions):
            perms = ', '.join(error.missing_permissions)
            await ctx.send(f'❌ You need the following permissions: {perms}')
            return
        
        # Handle bot missing permissions
        if isinstance(error, commands.BotMissingPermissions):
            perms = ', '.join(error.missing_permissions)
            await ctx.send(f'❌ I need the following permissions: {perms}')
            return
        
        # Log unexpected errors
        logger.error(f'Unexpected error in command {ctx.command}: {error}', exc_info=error)
        await ctx.send('❌ An unexpected error occurred. Please try again later.')
    
    async def close(self) -> None:
        """Cleanup before bot shutdown."""
        logger.info('Shutting down bot...')
        
        # Close aiohttp session
        if self.session:
            await self.session.close()
        
        # Close database pool
        if self.db_pool:
            await self.db_pool.close()
        
        await super().close()
        logger.info('Bot shutdown complete')


async def main() -> None:
    """Main entry point for the bot."""
    bot = DiscordBot()
    
    try:
        # Get token from environment or config
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            # Load config first to get token
            with open('config/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            token = config.get('token')
        
        if not token:
            logger.error('No bot token found! Set DISCORD_BOT_TOKEN env var or add to config.json')
            sys.exit(1)
        
        async with bot:
            await bot.start(token)
    except KeyboardInterrupt:
        logger.info('Received keyboard interrupt')
    except Exception as e:
        logger.error(f'Fatal error: {e}', exc_info=True)
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped by user')
