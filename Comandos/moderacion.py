import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns_locales = {} # Se reinicia al apagar el bot
        self.roles_admin = [1390152252169125992, 1445570965852520650, 1397020690435149824]
        self.canal_sanciones_id = 1397738825609904242
        self.path_logo = "./Imgs/LogoPFP.png"

    def es_admin(self, interaction: discord.Interaction):
        return any(role.id in self.roles_admin for role in interaction.user.roles)

    # --- COMANDO BAN ---
    @app_commands.command(name="ban", description="Baneo administrativo de usuarios")
    async def ban(self, interaction: discord.Interaction, usuario: discord.User, motivo: str, duracion: str, evidencia: discord.Attachment = None):
        if not self.es_admin(interaction):
            return await interaction.response.send_message("❌ No tienes rango administrativo.", ephemeral=True)
        
        file = discord.File(self.path_logo, filename="LogoPFP.png")
        embed = discord.Embed(title="⛔ Usuario Baneado", color=discord.Color.red(), timestamp=datetime.now())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Usuario", value=usuario.mention, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=True)
        embed.add_field(name="Duración", value=duracion, inline=True)
        embed.add_field(name="Evidencia", value=evidencia.url if evidencia else "No proporcionada", inline=False)
        embed.add_field(name="Administrador", value=interaction.user.mention, inline=False)
        embed.set_footer(text="La Nueva Metropol S.A.")

        await interaction.guild.get_channel(self.canal_sanciones_id).send(file=file, embed=embed)
        await interaction.response.send_message(f"✅ {usuario.name} ha sido baneado.", ephemeral=True)

    # --- COMANDO KICK ---
    @app_commands.command(name="kick", description="Expulsión administrativa de usuarios")
    async def kick(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str, evidencia: discord.Attachment = None):
        if not self.es_admin(interaction):
            return await interaction.response.send_message("❌ No tienes rango administrativo.", ephemeral=True)
        
        file = discord.File(self.path_logo, filename="LogoPFP.png")
        embed = discord.Embed(title="⛔ Usuario Kickeado", color=discord.Color.from_rgb(255, 69, 0), timestamp=datetime.now())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Usuario", value=usuario.mention, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=True)
        embed.add_field(name="Evidencia", value=evidencia.url if evidencia else "No proporcionada", inline=False)
        embed.add_field(name="Administrador", value=interaction.user.mention, inline=False)
        embed.set_footer(text="La Nueva Metropol S.A.")

        await interaction.guild.get_channel(self.canal_sanciones_id).send(file=file, embed=embed)
        await usuario.kick(reason=motivo)
        await interaction.response.send_message(f"✅ {usuario.name} ha sido kickeado.", ephemeral=True)

    # --- COMANDO WARN ---
    @app_commands.command(name="warn", description="Advertencia administrativa")
    async def warn(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str):
        if not self.es_admin(interaction):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        
        uid = str(usuario.id)
        self.warns_locales[uid] = self.warns_locales.get(uid, 0) + 1
        
        file = discord.File(self.path_logo, filename="LogoPFP.png")
        embed = discord.Embed(title="📛 Usuario Warneado", color=discord.Color.yellow(), timestamp=datetime.now())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Usuario", value=usuario.mention, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=True)
        embed.add_field(name="Warn N°", value=f"{self.warns_locales[uid]}", inline=True)
        embed.add_field(name="Administrador", value=interaction.user.mention, inline=False)
        embed.set_footer(text="La Nueva Metropol S.A.")

        await interaction.guild.get_channel(self.canal_sanciones_id).send(file=file, embed=embed)
        await interaction.response.send_message(f"✅ Warn #{self.warns_locales[uid]} enviado a {usuario.name}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderacion(bot))