import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import random
from firebase_admin import firestore

class AuxilioButtons(discord.ui.View):
    def __init__(self, caso_id):
        super().__init__(timeout=None)
        self.caso_id = caso_id

    async def actualizar_estado(self, interaction: discord.Interaction, estado, color, emoji):
        db = firestore.client()
        db.collection("SolicitudesAuxilio").document(self.caso_id).update({
            "estado": estado,
            "auxiliar": interaction.user.name,
            "actualizado": datetime.now()
        })
        
        embed = interaction.message.embeds[0]
        embed.title = f"{emoji} Caso #{self.caso_id}: {estado}"
        embed.color = color
        embed.set_footer(text=f"Atendido por {interaction.user.name}")
        
        # Si el caso termina, quitamos los botones
        nueva_view = None if estado in ["Finalizado", "Rechazado"] else self
        await interaction.response.edit_message(embed=embed, view=nueva_view)

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.orange, emoji="🚨")
    async def camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.actualizar_estado(interaction, "En Camino", discord.Color.orange(), "🚑")

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.green, emoji="✅")
    async def fin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.actualizar_estado(interaction, "Finalizado", discord.Color.green(), "🏁")

class Servicios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auxilio", description="Solicitar auxilio mecánico a la Metropol")
    @app_commands.describe(chofer="Chofer afectado", lugar="Ubicación", motivo="Falla unidad", foto="Foto del problema")
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        # Canal de pedido: 1390464495725576304
        if interaction.channel_id != 1390464495725576304:
            return await interaction.response.send_message("❌ Usá este comando en el canal de pedidos.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        
        try:
            db = firestore.client()
            caso_id = str(random.randint(100000, 999999))
            
            db.collection("SolicitudesAuxilio").document(caso_id).set({
                "chofer": chofer.name,
                "lugar": lugar,
                "motivo": motivo,
                "estado": "Pendiente",
                "fecha": datetime.now()
            })

            # Canal de recepción (Mecánicos): 1461926580078252054
            canal_mecanicos = self.bot.get_channel(1461926580078252054)
            
            embed = discord.Embed(title=f"🚨 NUEVA SOLICITUD #{caso_id}", color=discord.Color.red(), timestamp=datetime.now())
            embed.add_field(name="Chofer", value=chofer.mention, inline=True)
            embed.add_field(name="Lugar", value=lugar, inline=True)
            embed.add_field(name="Motivo", value=motivo, inline=False)
            embed.set_image(url=foto.url)
            
            # Rol mecánicos: 1390152252143964268
            await canal_mecanicos.send(content="<@&1390152252143964268>", embed=embed, view=AuxilioButtons(caso_id))
            await interaction.followup.send(f"✅ Enviado con éxito. Caso #{caso_id}", ephemeral=True)

        except Exception as e:
            print(f"Error en auxilio: {e}")
            await interaction.followup.send("❌ Error al procesar la solicitud.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Servicios(bot))
