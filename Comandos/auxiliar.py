import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from firebase_admin import firestore

# --- VISTA DE BOTONES PARA AUXILIARES ---
class AuxilioButtons(discord.ui.View):
    def __init__(self, chofer, lugar):
        super().__init__(timeout=None) # Los botones no expiran
        self.chofer = chofer
        self.lugar = lugar

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.orange, emoji="🚛")
    async def en_camino(self, interaction: discord.Interaction, button: discord.ui.button):
        # Intentar avisar al chofer
        try:
            await self.chofer.send(f"✅ ¡Atención! Un Auxiliar de **La Nueva Metropol** va en camino a tu ubicación en: **{self.lugar}**.")
            await interaction.response.send_message(f"Has marcado que vas en camino a asistir a {self.chofer.name}.", ephemeral=True)
        except:
            await interaction.response.send_message(f"Vas en camino, pero el chofer tiene los MD cerrados.", ephemeral=True)

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.green, emoji="✅")
    async def finalizado(self, interaction: discord.Interaction, button: discord.ui.button):
        db = firestore.client()
        db.collection("Auxilios").add({
            "Chofer": self.chofer.name,
            "Auxiliar": interaction.user.name,
            "Lugar": self.lugar,
            "Fecha": datetime.now()
        })
        await interaction.response.send_message(f"Auxilio en {self.lugar} finalizado y registrado.", ephemeral=True)
        # Desactivar botones para que no se vuelvan a usar
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red, emoji="🛑")
    async def rechazar(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message("Solicitud rechazada.", ephemeral=True)
        await interaction.message.delete()

# --- CLASE DEL COMANDO ---
class Auxiliar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auxilio", description="Solicitar auxilio mecánico (Solo personal autorizado)")
    @app_commands.describe(chofer="El chofer que necesita ayuda", lugar="Ubicación exacta", motivo="¿Qué pasó?", foto="Evidencia del problema")
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        # 1. Verificar Canal (Solo en Solicitud de Auxilio)
        if interaction.channel_id != 1390464495725576304:
            return await interaction.response.send_message("❌ Este comando solo puede usarse en <#1390464495725576304>.", ephemeral=True)
        
        # 2. Verificar Rol Prohibido (Cliente: 1390152252143964262)
        if any(r.id == 1390152252143964262 for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Los Clientes no pueden solicitar auxilio mecánico.", ephemeral=True)

        # 3. Crear el Embed
        embed = discord.Embed(title="📛 Solicitud de Auxilio", color=discord.Color.orange())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        
        embed.add_field(name="📋 Chofer Solicitante", value=chofer.mention, inline=True)
        embed.add_field(name="📍 Lugar", value=lugar, inline=True)
        embed.add_field(name="🛠️ Motivo", value=motivo, inline=False)
        
        if foto.content_type.startswith('image'):
            embed.set_image(url=foto.url)

        embed.set_footer(text=f"La Nueva Metropol S.A. | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # 4. Enviar al canal "EMBED AUXILIO" (1461926580078252054)
        canal_destino = interaction.guild.get_channel(1461926580078252054)
        file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        
        # Ping al rol Auxiliar: 1390152252143964268
        view = AuxilioButtons(chofer, lugar)
        await canal_destino.send(content="<@&1390152252143964268> ⚠️ **NUEVA SOLICITUD DE ASISTENCIA**", file=file, embed=embed, view=view)
        
        await interaction.response.send_message("✅ Tu solicitud ha sido enviada a los mecánicos de guardia.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Auxiliar(bot))
