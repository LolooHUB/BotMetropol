import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from firebase_admin import firestore

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Roles Administrativos
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]

    @app_commands.command(name="ban", description="Banear a un usuario de La Nueva Metropol S.A.")
    @app_commands.describe(usuario="El chofer o cliente a banear", motivo="Razón de la sanción", duracion="Tiempo del baneo", evidencia="Foto o video de la falta")
    async def ban(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str, duracion: str, evidencia: discord.Attachment = None):
        # Verificar permisos
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ No tienes rango administrativo para ejecutar baneos.", ephemeral=True)

        db = firestore.client()
        
        try:
            # Guardar en Firebase
            db.collection("Baneos").add({
                "Usuario": usuario.name,
                "Moderador": interaction.user.name,
                "Hora": datetime.now(),
                "Motivo": motivo
            })

            # Ejecutar Ban en Discord
            await usuario.ban(reason=motivo)

            # Crear Embed
            embed = discord.Embed(title="⛔ Usuario Baneado", color=discord.Color.red())
            embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
            embed.add_field(name="Usuario", value=usuario.mention, inline=False)
            embed.add_field(name="Motivo", value=motivo, inline=False)
            embed.add_field(name="Evidencia", value=evidencia.url if evidencia else "No proporcionada", inline=False)
            embed.add_field(name="Duración", value=duracion, inline=False)
            embed.add_field(name="Administrador", value=interaction.user.mention, inline=False)
            embed.set_footer(text=f"La Nueva Metropol S.A. | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

            # Enviar a canal de sanciones
            channel = interaction.guild.get_channel(1397738825609904242)
            file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
            await channel.send(file=file, embed=embed)
            
            await interaction.response.send_message(f"✅ Se ha baneado a {usuario.name} correctamente.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error al ejecutar el baneo: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ban(bot))
