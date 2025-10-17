import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Union
import asyncio
from datetime import timedelta

class Moderation(commands.Cog):
    """Advanced moderation commands for server management.
    
    This cog provides comprehensive moderation tools including:
    - Member management (kick, ban, timeout)
    - Message management (purge, clear)
    - Role management
    - Moderation logging
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        """Event listener that fires when the cog is loaded."""
        print(f"✅ {self.__class__.__name__} cog loaded successfully")
    
    # ==================== KICK COMMAND ====================
    @commands.hybrid_command(
        name="kick",
        description="Kick a member from the server"
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """Kick a member from the server.
        
        Args:
            ctx: The command context
            member: The member to kick
            reason: The reason for the kick
        """
        # Permission hierarchy check
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot kick someone with a higher or equal role!", ephemeral=True)
            return
            
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("❌ I cannot kick someone with a higher or equal role than me!", ephemeral=True)
            return
        
        # Send DM to the member before kicking
        try:
            embed = discord.Embed(
                title="🚪 You have been kicked",
                description=f"You were kicked from **{ctx.guild.name}**",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await member.send(embed=embed)
        except:
            pass  # User has DMs disabled
        
        # Kick the member
        await member.kick(reason=f"{ctx.author} - {reason}")
        
        # Send confirmation
        embed = discord.Embed(
            title="✅ Member Kicked",
            description=f"**{member}** has been kicked from the server",
            color=discord.Color.green()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        await ctx.send(embed=embed)
    
    # ==================== BAN COMMAND ====================
    @commands.hybrid_command(
        name="ban",
        description="Ban a member from the server"
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: Union[discord.Member, discord.User], *, reason: Optional[str] = "No reason provided"):
        """Ban a member from the server.
        
        Args:
            ctx: The command context
            member: The member/user to ban
            reason: The reason for the ban
        """
        # If member is in the server, check hierarchy
        if isinstance(member, discord.Member):
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                await ctx.send("❌ You cannot ban someone with a higher or equal role!", ephemeral=True)
                return
                
            if member.top_role >= ctx.guild.me.top_role:
                await ctx.send("❌ I cannot ban someone with a higher or equal role than me!", ephemeral=True)
                return
            
            # Send DM before banning
            try:
                embed = discord.Embed(
                    title="🔨 You have been banned",
                    description=f"You were banned from **{ctx.guild.name}**",
                    color=discord.Color.red()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
                await member.send(embed=embed)
            except:
                pass
        
        # Ban the user
        await ctx.guild.ban(member, reason=f"{ctx.author} - {reason}", delete_message_days=1)
        
        # Send confirmation
        embed = discord.Embed(
            title="✅ Member Banned",
            description=f"**{member}** has been banned from the server",
            color=discord.Color.green()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        await ctx.send(embed=embed)
    
    # ==================== UNBAN COMMAND ====================
    @commands.hybrid_command(
        name="unban",
        description="Unban a user from the server"
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: str, *, reason: Optional[str] = "No reason provided"):
        """Unban a user from the server.
        
        Args:
            ctx: The command context
            user_id: The ID of the user to unban
            reason: The reason for the unban
        """
        try:
            user = await self.bot.fetch_user(int(user_id))
        except:
            await ctx.send("❌ Invalid user ID!", ephemeral=True)
            return
        
        try:
            await ctx.guild.unban(user, reason=f"{ctx.author} - {reason}")
            
            embed = discord.Embed(
                title="✅ Member Unbanned",
                description=f"**{user}** has been unbanned",
                color=discord.Color.green()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await ctx.send(embed=embed)
        except discord.NotFound:
            await ctx.send("❌ This user is not banned!", ephemeral=True)
    
    # ==================== TIMEOUT COMMAND ====================
    @commands.hybrid_command(
        name="timeout",
        description="Timeout a member"
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, member: discord.Member, duration: str, *, reason: Optional[str] = "No reason provided"):
        """Timeout a member for a specified duration.
        
        Args:
            ctx: The command context
            member: The member to timeout
            duration: Duration (e.g., 10m, 1h, 1d)
            reason: The reason for the timeout
        """
        # Parse duration
        try:
            time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            unit = duration[-1].lower()
            amount = int(duration[:-1])
            seconds = amount * time_dict.get(unit, 60)
            
            if seconds > 2419200:  # Max 28 days
                await ctx.send("❌ Timeout duration cannot exceed 28 days!", ephemeral=True)
                return
        except:
            await ctx.send("❌ Invalid duration format! Use: 10m, 1h, 1d, etc.", ephemeral=True)
            return
        
        # Hierarchy check
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot timeout someone with a higher or equal role!", ephemeral=True)
            return
        
        # Timeout the member
        await member.timeout(timedelta(seconds=seconds), reason=f"{ctx.author} - {reason}")
        
        embed = discord.Embed(
            title="⏰ Member Timed Out",
            description=f"**{member}** has been timed out for **{duration}**",
            color=discord.Color.orange()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        await ctx.send(embed=embed)
    
    # ==================== UNTIMEOUT COMMAND ====================
    @commands.hybrid_command(
        name="untimeout",
        description="Remove timeout from a member"
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def untimeout(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """Remove timeout from a member."""
        if not member.is_timed_out():
            await ctx.send("❌ This member is not timed out!", ephemeral=True)
            return
        
        await member.timeout(None, reason=f"{ctx.author} - {reason}")
        
        embed = discord.Embed(
            title="✅ Timeout Removed",
            description=f"**{member}**'s timeout has been removed",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    # ==================== PURGE COMMAND ====================
    @commands.hybrid_command(
        name="purge",
        description="Delete multiple messages"
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int):
        """Delete a specified number of messages.
        
        Args:
            ctx: The command context
            amount: Number of messages to delete (1-100)
        """
        if amount < 1 or amount > 100:
            await ctx.send("❌ Amount must be between 1 and 100!", ephemeral=True)
            return
        
        # Delete messages
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 for command message
        
        # Send confirmation that auto-deletes
        msg = await ctx.send(f"✅ Deleted **{len(deleted) - 1}** messages!", ephemeral=True)
    
    # ==================== SLOWMODE COMMAND ====================
    @commands.hybrid_command(
        name="slowmode",
        description="Set channel slowmode"
    )
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, seconds: int):
        """Set slowmode delay for the channel.
        
        Args:
            ctx: The command context
            seconds: Slowmode delay in seconds (0-21600)
        """
        if seconds < 0 or seconds > 21600:
            await ctx.send("❌ Slowmode must be between 0 and 21600 seconds (6 hours)!", ephemeral=True)
            return
        
        await ctx.channel.edit(slowmode_delay=seconds)
        
        if seconds == 0:
            await ctx.send("✅ Slowmode has been disabled!")
        else:
            await ctx.send(f"✅ Slowmode set to **{seconds}** seconds!")
    
    # ==================== ERROR HANDLER ====================
    @kick.error
    @ban.error
    @unban.error
    @timeout.error
    @untimeout.error
    @purge.error
    @slowmode.error
    async def moderation_error(self, ctx: commands.Context, error):
        """Error handler for moderation commands."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!", ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to execute this command!", ephemeral=True)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found!", ephemeral=True)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided!", ephemeral=True)
        else:
            await ctx.send(f"❌ An error occurred: {str(error)}", ephemeral=True)
            print(f"Error in moderation command: {error}")

# Required function for loading the cog
async def setup(bot: commands.Bot):
    """Load the Moderation cog."""
    await bot.add_cog(Moderation(bot))
