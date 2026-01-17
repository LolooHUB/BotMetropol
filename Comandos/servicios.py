import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import random
from firebase_admin import firestore

# --- VISTA DE BOTONES (Persistent View) ---
class AuxilioButtons(discord.ui.View):
    def __init__(self, caso_id):
        super().__init__(timeout=None) # Importante para que no mueran los botones
        self.caso_id = caso_id

    async def actualizar_db(self, interaction: discord.Interaction, estado, color, emoji):
        db = firestore.client()
        # Actualizamos la base de datos
        db.collection("SolicitudesAuxilio").document(self.caso_id).update({
            "estado": estado, 
            "auxiliar": interaction.user.name,
            "ultima_actualizacion": datetime.now()
        })
        
        # Editamos el Embed actual
        embed = interaction.message.embeds[0]
        embed.title = f"{emoji} Caso #{self.caso_id}: {estado}"
        embed.color = color
        embed.set_footer(text=f"Atendido por {interaction.user.name} | Metropol")
        
        # Si el caso termina, sacamos los botones
        view_actualizada = None if estado in ["Finalizado", "Rechazado"] else self
        await interaction.response.edit_message(embed=embed, view=view_actualizada)

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.orange, emoji="🚨")
    async def camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.actualizar_db(interaction, "En Camino", discord.Color.orange(), "🚑")

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.green, emoji="✅")
    async def fin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.actualizar_db(interaction, "Finalizado", discord.Color.green(), "🏁")

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red, emoji="✖️")
    async def rechazo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.actualizar_db(interaction, "Rechazado", discord.Color.red(), "❌")

# --- CLASE PRINCIPAL ---
class Servicios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # IDs fijos para evitar errores
        self.canal_envio = 1390464495725576304
        self.canal_mecanicos = 1461926580078252054
        self.rol_mecanicos = 1390152252143964268

    @app_commands.command(name="auxilio", description="Solicitar auxilio mecánico a la empresa")
    @app_commands.describe(chofer="El chofer afectado", lugar="Ubicación de la unidad", motivo="Falla técnica", foto="Imagen de la unidad/falla")
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        
        # Verificación de canal
        if interaction.channel_id != self.canal_envio:
            return await interaction.response.send_message(f"❌ Este comando solo funciona en <#{self.canal_envio}>", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        
        try:
            db = firestore.client()
            caso_id = str(random.randint(100000, 999999))
            
            # Guardar en Firestore
            db.collection("SolicitudesAuxilio").document(caso_id).set({
                "chofer": chofer.name,
                "lugar": lugar,
                "motivo": motivo,
                "estado": "Pendiente",
                "fecha": datetime.now()
            })

            # Obtener el canal de mecánicos
            canal_dest = self.bot.get_channel(self.canal_mecanicos)
            if not canal_dest:
                return await interaction.followup.send("❌ Error: No se encontró el canal de recepción.", ephemeral=True)

            # Crear Embed
            embed = discord.Embed(
                title=f"🚨 NUEVA SOLICITUD DE AUXILIO #{caso_id}",
                description=f"Se requiere asistencia técnica inmediata.",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.set_author(name="La Nueva Metropol S.A.", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            embed.add_field(name="👷 Chofer", value=chofer.mention, inline=True)
            embed.add_field(name="📍 Lugar", value=lugar, inline=True)
            embed.add_field(name="🔧 Motivo", value=motivo, inline=False)
            embed.set_image(url=foto.url)
            embed.set_footer(text="Sistema de Emergencias - Metropol")

            # Enviar mensaje con botones
            await canal_dest.send(
                content=f"<@&{self.rol_mecanicos}>", 
                embed=embed, 
                view=AuxilioButtons(caso_id)
            )
            
            await interaction.followup.send(f"✅ Tu solicitud ha sido enviada con el **ID #{caso_id}**.", ephemeral=True)

        except Exception as e:
            print(f"Error en comando auxilio: {e}")
            await interaction.followup.send(f"❌ Ocurrió un error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Servicios(bot))
