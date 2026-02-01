import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from firebase_admin import firestore
import os

tz_arg = timezone(timedelta(hours=-3))

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]

    @app_commands.command(name="ban", description="Banear a un usuario de La Nueva Metropol S.A.")
    @app_commands.describe(usuario="Usuario a banear", motivo="Razón", duracion="Tiempo o 'pban' para Permanente", evidencia="Prueba")
    async def ban(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str, duracion: str, evidencia: discord.Attachment = None):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)

        # --- LÓGICA DE DURACIÓN (PBAN) ---
        duracion_display = "Permanente (P-BAN)" if duracion.lower() == "pban" else duracion
        
        fecha_ahora = datetime.now(tz_arg)
        fecha_str = fecha_ahora.strftime('%d/%m/%Y %H:%M')
        db = firestore.client()
        
        try:
            # Guardar en Firebase con el formato de duración solicitado
            db.collection("Baneos").add({
                "Usuario": usuario.name, "UsuarioID": str(usuario.id),
                "Moderador": interaction.user.name, "Fecha": fecha_str,
                "Motivo": motivo, "Duracion": duracion_display
            })

            # Ejecutar baneo en el servidor
            await usuario.ban(reason=f"{motivo} | Duración: {duracion_display}")

            # --- PREPARACIÓN DE ARCHIVOS ---
            f1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
            f2 = discord.File("Imgs/Banner.png", filename="Banner.png")
            evidencia_url = evidencia.url if evidencia else "No proporcionada"

            # --- EMBED PARA CANAL PÚBLICO (SANCIONES) ---
            embed_pub = discord.Embed(title="⛔ Usuario Baneado", color=discord.Color.red(), timestamp=fecha_ahora)
            embed_pub.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
            embed_pub.set_image(url="attachment://Banner.png")
            embed_pub.add_field(name="Usuario", value=usuario.mention, inline=False)
            embed_pub.add_field(name="Motivo", value=f"```\n{motivo}\n```", inline=False)
            embed_pub.add_field(name="Duración", value=duracion_display, inline=False)
            # Evidencia en formato texto para no ocupar espacio visual de imagen
            embed_pub.add_field(name="Evidencia", value=evidencia_url, inline=False)
            embed_pub.set_footer(text=f"La Nueva Metropol S.A. | {fecha_str}")

            # --- ENVÍO A CANALES ---
            canal_sanciones = interaction.guild.get_channel(1397738825609904242)
            canal_logs_evidencia = interaction.guild.get_channel(1467601585029910668)

            # 1. Envío a Sanciones (Público)
            if canal_sanciones:
                await canal_sanciones.send(files=[f1, f2], embed=embed_pub)

            # 2. Envío a Logs (Evidencia Detallada)
            if canal_logs_evidencia:
                embed_log = embed_pub.copy()
                embed_log.set_image(url=evidencia.url if evidencia else None) # Aquí sí se ve la imagen
                embed_log.add_field(name="Moderador Responsable", value=interaction.user.mention)
                
                # Re-adjuntar archivos para el nuevo mensaje
                f_log1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
                await canal_logs_evidencia.send(file=f_log1, embed=embed_log)

            await interaction.response.send_message(f"✅ Se ha baneado a **{usuario.name}** correctamente ({duracion_display}).", ephemeral=True)

        except discord.Forbidden:
            await interaction.response.send_message("❌ No tengo permisos suficientes (jerarquía de roles) para banear a este usuario.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error crítico: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ban(bot))
