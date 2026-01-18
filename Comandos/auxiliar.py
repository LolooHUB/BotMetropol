import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

# Definimos la vista de botones
class AuxilioButtons(discord.ui.View):
    def __init__(self, chofer_id, lugar):
        super().__init__(timeout=None)
        self.chofer_id = chofer_id
        self.lugar = lugar

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.orange, emoji="🚛")
    async def en_camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Asistencia marcada en camino.", ephemeral=True)

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.green, emoji="✅")
    async def finalizado(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Auxilio finalizado.", ephemeral=True)
        await interaction.message.delete()

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red, emoji="🛑")
    async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Solicitud rechazada.", ephemeral=True)
        await interaction.message.delete()

# Definimos la clase del comando
class Auxiliar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auxilio", description="Pedir asistencia mecanica")
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        """Comando de auxilio"""
        
        # Validamos el canal por ID
        if interaction.channel_id != 1390464495725576304:
            return await interaction.response.send_message("Usa este comando en el canal de auxilio.", ephemeral=True)

        embed = discord.Embed(title="📛 Solicitud de Auxilio", color=discord.Color.orange())
        embed.set_author(name="La Nueva Metropol S.A.")
        embed.add_field(name="Chofer", value=chofer.mention)
        embed.add_field(name="Lugar", value=lugar)
        embed.add_field(name="Motivo", value=motivo)
        
        if foto:
            embed.set_image(url=foto.url)
            
        embed.set_footer(text=f"Metropol S.A. | {datetime.now().strftime('%H:%M')}")

        # Canal de destino
        canal_destino = interaction.guild.get_channel(1461926580078252054)
        
        if canal_destino:
            view = AuxilioButtons(chofer.id, lugar)
            await canal_destino.send(content="<@&1390152252143964268> NUEVA SOLICITUD", embed=embed, view=view)
            await interaction.response.send_message("✅ Solicitud enviada.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Error: No se encontró el canal de destino.", ephemeral=True)

# Función de carga obligatoria
async def setup(bot):
    await bot.add_cog(Auxiliar(bot))
