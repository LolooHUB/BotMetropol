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

    @app_commands.command(name="warn", description="Warnear a un usuario")
    async def warn(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)

        db = firestore.client()
        warns_ref = db.collection("Warns").where("UsuarioID", "==", str(usuario.id))
        docs = warns_ref.get()
        count = len(docs) + 1

        # Hora Argentina
        fecha_ahora = datetime.now(tz_arg)
        fecha_str = fecha_ahora.strftime('%d/%m/%Y %H:%M')

        db.collection("Warns").add({
            "UsuarioID": str(usuario.id),
            "UsuarioNombre": usuario.name,
            "Moderador": interaction.user.name,
            "Motivo": motivo,
            "Fecha": fecha_str
        })

        try:
            await usuario.timeout(timedelta(minutes=5), reason=f"Warn #{count}: {motivo}")
        except:
            pass

        path_imagen = "Imgs/LogoPFP.png"
        file = discord.File(path_imagen, filename="LogoPFP.png") if os.path.exists(path_imagen) else None

        embed = discord.Embed(title="📛 Usuario Warneado", color=discord.Color.yellow(), timestamp=fecha_ahora)
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.set_thumbnail(url=usuario.display_avatar.url)
        embed.add_field(name="Usuario", value=usuario.mention, inline=False)
        embed.add_field(name="Moderador", value=interaction.user.mention, inline=False)
        embed.add_field(name="Motivo", value=f"```\n{motivo}\n```", inline=False)
        embed.add_field(name="Warn N°", value=str(count), inline=False)
        embed.set_footer(text=f"La Nueva Metropol S.A. | {fecha_str}")

        channel = interaction.guild.get_channel(1397738825609904242)
        if channel and file:
            await channel.send(file=file, embed=embed)
            await interaction.response.send_message(f"✅ Warn aplicado a {usuario.name}.", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clearwarnings", description="Eliminar todos los warns de un usuario")
    @app_commands.describe(usuario="Usuario al que limpiar los warns", motivo="Razón de la limpieza")
    async def clear(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ No tienes permisos para limpiar warns.", ephemeral=True)
        
        db = firestore.client()
        # Buscamos todos los documentos de ese usuario
        warns_ref = db.collection("Warns").where("UsuarioID", "==", str(usuario.id))
        docs = warns_ref.get()

        if len(docs) == 0:
            return await interaction.response.send_message(f"El usuario {usuario.name} no tiene advertencias activas.", ephemeral=True)

        # Borramos cada documento encontrado
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1

        # Embed de confirmación para los logs
        fecha_ahora = datetime.now(tz_arg)
        fecha_str = fecha_ahora.strftime('%d/%m/%Y %H:%M')
        
        embed = discord.Embed(title="✨ Advertencias Limpiadas", color=discord.Color.green(), timestamp=fecha_ahora)
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Usuario", value=usuario.mention, inline=False)
        embed.add_field(name="Cantidad Borrada", value=str(deleted_count), inline=False)
        embed.add_field(name="Motivo", value=f"```\n{motivo}\n```", inline=False)
        embed.add_field(name="Administrador", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"La Nueva Metropol S.A. | {fecha_str}")

        channel = interaction.guild.get_channel(1397738825609904242)
        path_imagen = "Imgs/LogoPFP.png"
        
        if channel and os.path.exists(path_imagen):
            file = discord.File(path_imagen, filename="LogoPFP.png")
            await channel.send(file=file, embed=embed)
        
        await interaction.response.send_message(f"✅ Se han eliminado {deleted_count} advertencias de **{usuario.name}**.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Warns(bot))
    
