import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

# --- MODAL PARA BANEO ---
class BanModal(discord.ui.Modal, title='Sistema de Baneo - Metropol'):
    usuario = discord.ui.TextInput(label='Usuario (ID o mención)', placeholder='Ej: 123456789', required=True)
    motivo = discord.ui.TextInput(label='Motivo de la sanción', style=discord.TextStyle.paragraph, required=True)
    duracion = discord.ui.TextInput(label='Duración', placeholder='Ej: 7 días / Permanente', required=True)
    evidencia = discord.ui.TextInput(label='Link de Evidencia (Opcional)', required=False)

    async def on_submit(self, interaction: discord.Interaction):
        canal_logs = interaction.guild.get_channel(1390152261937922070)
        canal_sanciones = interaction.guild.get_channel(1397738825609904242)
        
        embed = discord.Embed(title="⛔ Usuario Baneado", color=discord.Color.red(), timestamp=datetime.now())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="https://tu-link.com/LogoPFP.png") # Cambiar por path real
        embed.add_field(name="Usuario", value=self.usuario.value, inline=False)
        embed.add_field(name="Motivo", value=self.motivo.value, inline=False)
        embed.add_field(name="Duración", value=self.duracion.value, inline=True)
        embed.add_field(name="Evidencia", value=self.evidencia.value or "No provista", inline=True)
        embed.add_field(name="Administrador", value=interaction.user.mention, inline=False)
        embed.set_footer(text="La Nueva Metropol S.A.")

        await canal_sanciones.send(embed=embed)
        if canal_logs: await canal_logs.send(embed=embed)
        await interaction.response.send_message(f"✅ Sanción aplicada a {self.usuario.value}", ephemeral=True)

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_admin = [1390152252169125992, 1445570965852520650, 1397020690435149824]

    def es_admin(self, interaction):
        return any(role.id in self.roles_admin for role in interaction.user.roles)

    @app_commands.command(name="ban", description="Banear a un usuario de la empresa")
    async def ban(self, interaction: discord.Interaction):
        if self.es_admin(interaction):
            await interaction.response.send_modal(BanModal())
        else:
            await interaction.response.send_message("❌ No tienes rango jerárquico para esto.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderacion(bot))
