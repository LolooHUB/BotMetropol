import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from firebase_admin import firestore
import os

# --- CONFIGURACIÓN HORA ARGENTINA ---
tz_arg = timezone(timedelta(hours=-3))

class Warns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]
        self.log_channel_id = 1397738825609904242

    @app_commands.command(name="warn", description="Warnear a un usuario con ID único")
    @app_commands.describe(usuario="Usuario a sancionar", motivo="Razón de la sanción")
    async def warn(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)

        db = firestore.client()
        
        # Obtener fecha y generar ID único
        fecha_ahora = datetime.now(tz_arg)
        fecha_str = fecha_ahora.strftime('%d/%m/%Y %H:%M')
        
        # Crear referencia para obtener ID automático de Firestore
        nuevo_warn_ref = db.collection("Warns").document()
        warn_id = nuevo_warn_ref.id

        # Contar cuántos warns tiene el usuario (para el número correlativo)
        docs = db.collection("Warns").where("UsuarioID", "==", str(usuario.id)).get()
        count = len(docs) + 1

        # Guardar en la DB
        nuevo_warn_ref.set({
            "WarnID": warn_id,
            "UsuarioID": str(usuario.id),
            "UsuarioNombre": usuario.name,
            "Moderador": interaction.user.name,
            "Motivo": motivo,
            "Fecha": fecha_str
        })

        # Aplicar Timeout automático
        try:
            await usuario.timeout(timedelta(minutes=5), reason=f"Warn #{count} [ID:{warn_id}]: {motivo}")
        except:
            pass

        # --- DISEÑO DEL EMBED ---
        embed = discord.Embed(title="📛 Usuario Warneado", color=discord.Color.yellow(), timestamp=fecha_ahora)
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.set_thumbnail(url=usuario.display_avatar.url)
        embed.set_image(url="attachment://Banner.png")

        embed.add_field(name="Usuario", value=usuario.mention, inline=True)
        embed.add_field(name="Warn ID", value=f"`{warn_id}`", inline=True)
        embed.add_field(name="Moderador", value=interaction.user.mention, inline=False)
        embed.add_field(name="Motivo", value=f"```\n{motivo}\n```", inline=False)
        embed.add_field(name="Warn N°", value=str(count), inline=False)
        embed.set_footer(text=f"La Nueva Metropol S.A. | {fecha_str}")

        channel = interaction.guild.get_channel(self.log_channel_id)
        f1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        f2 = discord.File("Imgs/Banner.png", filename="Banner.png")

        if channel:
            await channel.send(files=[f1, f2], embed=embed)
            await interaction.response.send_message(f"✅ Warn aplicado a {usuario.name}. ID: `{warn_id}`", ephemeral=True)
        else:
            await interaction.response.send_message(files=[f1, f2], embed=embed, ephemeral=True)

    @app_commands.command(name="clearwarning", description="Eliminar un warn específico por su ID y archivarlo")
    @app_commands.describe(id_warn="El ID alfanumérico del warn", motivo="Razón de la eliminación")
    async def clear(self, interaction: discord.Interaction, id_warn: str, motivo: str):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        
        db = firestore.client()
        warn_doc_ref = db.collection("Warns").document(id_warn)
        doc = warn_doc_ref.get()

        if not doc.exists:
            return await interaction.response.send_message(f"❌ No existe un warn con el ID `{id_warn}`.", ephemeral=True)

        # Preparar datos para el archivo (DeletedWarns)
        data = doc.to_dict()
        fecha_ahora = datetime.now(tz_arg)
        fecha_str = fecha_ahora.strftime('%d/%m/%Y %H:%M')

        data["FechaEliminacion"] = fecha_str
        data["AdminQueElimino"] = interaction.user.name
        data["MotivoEliminacion"] = motivo

        # 1. Mover a colección de eliminados
        db.collection("DeletedWarns").document(id_warn).set(data)
        
        # 2. Borrar de la colección activa
        warn_doc_ref.delete()

        # --- EMBED DE LOG ---
        embed = discord.Embed(title="🗑️ Warning Eliminado", color=discord.Color.red(), timestamp=fecha_ahora)
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.set_image(url="attachment://Banner.png")

        embed.add_field(name="Usuario", value=f"**{data.get('UsuarioNombre')}**", inline=True)
        embed.add_field(name="ID del Warn", value=f"`{id_warn}`", inline=True)
        embed.add_field(name="Motivo de Eliminación", value=f"```\n{motivo}\n```", inline=False)
        embed.add_field(name="Administrador", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"La Nueva Metropol S.A. | {fecha_str}")

        channel = interaction.guild.get_channel(self.log_channel_id)
        if channel:
            f1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
            f2 = discord.File("Imgs/Banner.png", filename="Banner.png")
            await channel.send(files=[f1, f2], embed=embed)
        
        await interaction.response.send_message(f"✅ El warn `{id_warn}` ha sido movido a historial de eliminados.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Warns(bot))
