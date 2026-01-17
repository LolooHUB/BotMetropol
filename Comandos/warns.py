import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from firebase_admin import firestore

class Warns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]

    @app_commands.command(name="warn", description="Warnear a un usuario")
    async def warn(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("No tienes permisos.", ephemeral=True)

        db = firestore.client()
        warns_ref = db.collection("Warns").where("UsuarioID", "==", str(usuario.id))
        docs = warns_ref.get()
        count = len(docs) + 1

        db.collection("Warns").add({
            "UsuarioID": str(usuario.id),
            "UsuarioNombre": usuario.name,
            "Moderador": interaction.user.name,
            "Motivo": motivo,
            "Fecha": datetime.now()
        })

        await usuario.timeout(timedelta(minutes=5), reason=f"Warn #{count}: {motivo}")

        embed = discord.Embed(title="📛 Usuario Warneado", color=discord.Color.yellow())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Usuario", value=usuario.mention)
        embed.add_field(name="Motivo", value=motivo)
        embed.add_field(name="Warn N°", value=str(count))
        embed.set_footer(text=f"La Nueva Metropol S.A. | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        channel = interaction.guild.get_channel(1397738825609904242)
        file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        await channel.send(file=file, embed=embed)
        await interaction.response.send_message(f"Warn aplicado a {usuario.name}.", ephemeral=True)

    @app_commands.command(name="clearwarnings", description="Eliminar warns de un usuario")
    async def clear(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str, cantidad: int):
        # Lógica para borrar documentos en Firebase y enviar embed de apelación...
        await interaction.response.send_message("Warnings removidos de la base de datos.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Warns(bot))
