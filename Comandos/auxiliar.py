import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

# --- VISTA DE BOTONES CON GUARDADO EN FIREBASE ---
class AuxilioButtons(discord.ui.View):
    def __init__(self, chofer_id, chofer_nombre, lugar, motivo):
        super().__init__(timeout=None)
        self.chofer_id = chofer_id
        self.chofer_nombre = chofer_nombre
        self.lugar = lugar
        self.motivo = motivo

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.primary, emoji="🚛")
    async def en_camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✅ **{interaction.user.display_name}** está en camino al auxilio.", ephemeral=False)

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.success, emoji="✅")
    async def finalizado(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Accedemos a la DB definida en el main.py
        db = interaction.client.db
        
        if db:
            try:
                # Guardamos el reporte en la colección "Auxilios"
                db.collection("Auxilios").add({
                    "chofer_id": str(self.chofer_id),
                    "chofer_nombre": self.chofer_nombre,
                    "mecanico": interaction.user.name,
                    "lugar": self.lugar,
                    "motivo": self.motivo,
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "estado": "Completado"
                })
                await interaction.response.send_message("📥 Auxilio finalizado y guardado en la base de datos.", ephemeral=True)
            except Exception as e:
                print(f"Error en Firebase: {e}")
                await interaction.response.send_message("⚠️ Error al guardar en la nube, pero el auxilio se cerró.", ephemeral=True)
        else:
            await interaction.response.send_message("✅ Finalizado (Base de datos no conectada).", ephemeral=True)
            
        await interaction.message.delete()

# --- CLASE DEL COMANDO ---
class Auxiliar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auxilio", description="Solicitar asistencia mecánica - Metropol")
    @app_commands.describe(chofer="Chofer que necesita ayuda", lugar="Ubicación actual", motivo="Falla de la unidad", foto="Foto de la falla")
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        
        # ID CANAL SOLICITUD: 1390464495725576304
        if interaction.channel_id != 1390464495725576304:
            return await interaction.response.send_message("❌ Este comando solo funciona en el canal de Auxilios.", ephemeral=True)

        # Crear el Embed para los mecánicos
        embed = discord.Embed(title="📛 SOLICITUD DE ASISTENCIA", color=discord.Color.orange(), timestamp=datetime.now())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        embed.add_field(name="👤 Chofer", value=chofer.mention, inline=True)
        embed.add_field(name="📍 Lugar", value=lugar, inline=True)
        embed.add_field(name="🛠️ Motivo/Falla", value=motivo, inline=False)
        
        if foto:
            embed.set_image(url=foto.url)
            
        embed.set_footer(text=f"Solicitado por: {interaction.user.name}")

        # ID CANAL DESTINO (Mecánicos): 1461926580078252054
        canal_destino = interaction.guild.get_channel(1461926580078252054)
        
        if canal_destino:
            # Pasamos los datos a los botones para el guardado final
            view = AuxilioButtons(chofer.id, chofer.name, lugar, motivo)
            
            # Rol Auxiliar (Ping): 1390152252143964268
            await canal_destino.send(content="<@&1390152252143964268> ⚠️ **NUEVA ASISTENCIA REQUERIDA**", embed=embed, view=view)
            await interaction.response.send_message("✅ Tu solicitud ha sido enviada a los mecánicos.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Error crítico: No se pudo contactar con el canal de mecánica.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Auxiliar(bot))
