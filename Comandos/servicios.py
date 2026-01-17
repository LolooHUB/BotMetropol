import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import random
import firebase_admin
from firebase_admin import firestore

# --- VISTA INTERACTIVA (BOTONES) ---
class AuxilioView(discord.ui.View):
    def __init__(self, caso_id):
        super().__init__(timeout=None) # Los botones no expiran nunca
        self.caso_id = caso_id

    async def actualizar_estado(self, interaction: discord.Interaction, estado, color, emoji):
        # Conexión a Firestore
        db = firestore.client()
        
        # Actualizamos el documento en la base de datos
        db.collection("SolicitudesAuxilio").document(self.caso_id).update({
            "estado": estado,
            "auxiliar_cargo": interaction.user.name,
            "ultima_actualizacion": datetime.now()
        })

        # Editamos el Embed para mostrar el progreso
        embed = interaction.message.embeds[0] # Tomamos el embed original
        embed.title = f"{emoji} Caso #{self.caso_id} - {estado}"
        embed.color = color
        
        # Limpiamos campos de estado anteriores si existen y añadimos el nuevo
        embed.clear_fields()
        # Intentamos mantener la info original (chofer, lugar, motivo) si es posible o re-crearla
        # Para hacerlo simple y efectivo:
        embed.add_field(name="Estado Actual", value=f"**{estado}**", inline=True)
        embed.add_field(name="Auxiliar a cargo", value=interaction.user.mention, inline=True)
        embed.set_footer(text=f"Actualizado por {interaction.user.name} | La Nueva Metropol S.A.")

        # Si el caso terminó, quitamos los botones para que nadie más los use
        if estado in ["Finalizado", "Rechazado"]:
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.orange, emoji="🚨")
    async def camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.actualizar_estado(interaction, "En Camino", discord.Color.orange(), "🚑")

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.green, emoji="✅")
    async def fin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.actualizar_estado(interaction, "Finalizado", discord.Color.green(), "✅")

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red, emoji="✖️")
    async def rechazo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.actualizar_estado(interaction, "Rechazado", discord.Color.red(), "❌")

# --- COG PRINCIPAL ---
class Servicios(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.canal_envio = 1390464495725576304
        self.canal_recepcion = 1461926580078252054
        self.rol_aux_id = 1390152252143964268

    @app_commands.command(name="auxilio", description="Solicitar asistencia mecánica en ruta")
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        # Validación de canal
        if interaction.channel_id != self.canal_envio:
            return await interaction.response.send_message(f"❌ Comando solo disponible en <#{self.canal_envio}>", ephemeral=True)

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

            # Canal donde los auxiliares ven el pedido
            canal_destino = self.bot.get_channel(self.canal_recepcion)
            
            embed = discord.Embed(
                title=f"🚨 Solicitud de Auxilio #{caso_id}",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.set_author(name="La Nueva Metropol S.A.", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            embed.add_field(name="Chofer", value=chofer.mention, inline=True)
            embed.add_field(name="Lugar", value=lugar, inline=True)
            embed.add_field(name="Motivo", value=motivo, inline=False)
            embed.set_image(url=foto.url)
            embed.set_footer(text="Estado: Pendiente de Atención")

            # Enviamos el mensaje con los BOTONES
            view = AuxilioView(caso_id)
            await canal_destino.send(content=f"<@&{self.rol_aux_id}>", embed=embed, view=view)
            
            await interaction.followup.send(f"✅ Caso #{caso_id} enviado a los auxiliares.", ephemeral=True)

        except Exception as e:
            print(f"Error: {e}")
            await interaction.followup.send(f"❌ Error al procesar: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Servicios(bot))
