import discord
from discord import app_commands
from discord.ext import commands
import datetime

class PermisosAutor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CANAL_PERMISOS_ID = 1463699359391547515

    # Definimos el comando de Slash
    @app_commands.command(
        name="agregarpermiso", 
        description="Registra permisos de exportación de modelos OMSI a Roblox."
    )
    @app_commands.describe(
        modelo="Nombre del colectivo/modelo",
        descripcion="Detalles adicionales sobre el permiso",
        link_autor="Link al perfil del autor original",
        imagen_modelo="Foto del colectivo",
        imagen_permiso="Captura de pantalla de la autorización"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def agregar_permiso(
        self,
        interaction: discord.Interaction,
        modelo: str,
        descripcion: str,
        link_autor: str,
        imagen_modelo: discord.Attachment,
        imagen_permiso: discord.Attachment
    ):
        # Defer para que no expire la interacción mientras subimos a Firebase
        await interaction.response.defer(thinking=True)

        try:
            # --- GUARDAR EN FIRESTORE ---
            # Usamos la db que definiste en el Main.py
            if self.bot.db:
                doc_ref = self.bot.db.collection("Permisos").document()
                doc_ref.set({
                    "modelo": modelo,
                    "descripcion": descripcion,
                    "link_autor": link_autor,
                    "img_modelo_url": imagen_modelo.url,
                    "img_permiso_url": imagen_permiso.url,
                    "registrado_por": interaction.user.display_name,
                    "fecha": datetime.datetime.now()
                })
                print(f"✅ Documento guardado en Firestore para {modelo}")

            # --- ENVÍO AL CANAL ---
            canal = self.bot.get_channel(self.CANAL_PERMISOS_ID)
            if not canal:
                return await interaction.followup.send("❌ Error: No se encontró el canal de permisos.")

            # Embed principal con la foto del modelo
            embed1 = discord.Embed(
                title=f"📁 NUEVO PERMISO REGISTRADO: {modelo}",
                description=f"**Descripción:**\n{descripcion}\n\n**Autor Original:**\n[Link al Autor]({link_autor})",
                color=0x00FF7F, # Verde primavera
                timestamp=datetime.datetime.now()
            )
            embed1.set_image(url=imagen_modelo.url)
            embed1.set_footer(text=f"Subido por: {interaction.user.display_name}")

            # Embed secundario para mostrar la prueba del permiso
            embed2 = discord.Embed(
                title="📑 EVIDENCIA DE AUTORIZACIÓN",
                color=0x00FF7F
            )
            embed2.set_image(url=imagen_permiso.url)

            # Enviamos ambos juntos
            await canal.send(embeds=[embed1, embed2])

            await interaction.followup.send(f"✅ Permiso de **{modelo}** subido correctamente a {canal.mention}")

        except Exception as e:
            print(f"❌ Error en agregar_permiso: {e}")
            await interaction.followup.send(f"❌ Ocurrió un error al procesar el permiso: {e}")

async def setup(bot):
    await bot.add_cog(PermisosAutor(bot))
