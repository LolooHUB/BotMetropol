import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from datetime import datetime

# --- CONFIGURACIÓN ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- VISTA DE BOTONES (CORREGIDA) ---
class AuxilioButtons(discord.ui.View):
    def __init__(self, chofer_id, lugar):
        super().__init__(timeout=None)
        self.chofer_id = chofer_id
        self.lugar = lugar

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.warning, emoji="🚛") # 'warning' es el naranja
    async def en_camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Asistencia marcada en camino.", ephemeral=True)

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.success, emoji="✅") # 'success' es verde
    async def finalizado(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Auxilio finalizado.", ephemeral=True)
        await interaction.message.delete()

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.danger, emoji="🛑") # 'danger' es rojo
    async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Solicitud rechazada.", ephemeral=True)
        await interaction.message.delete()

# --- COMANDO AUXILIO ---
@bot.tree.command(name="auxilio", description="Pedir asistencia mecanica Metropol")
@app_commands.describe(chofer="Chofer que necesita ayuda", lugar="Ubicación", motivo="Falla", foto="Imagen")
async def auxilio(interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
    if interaction.channel_id != 1390464495725576304:
        return await interaction.response.send_message("Usa el canal de auxilio.", ephemeral=True)
    
    embed = discord.Embed(title="📛 Solicitud de Auxilio", color=discord.Color.orange())
    embed.add_field(name="Chofer", value=chofer.mention)
    embed.add_field(name="Lugar", value=lugar)
    embed.add_field(name="Motivo", value=motivo)
    embed.set_image(url=foto.url)
    
    canal_destino = interaction.guild.get_channel(1461926580078252054)
    if canal_destino:
        view = AuxilioButtons(chofer.id, lugar)
        await canal_destino.send(content="<@&1390152252143964268> NUEVA SOLICITUD", embed=embed, view=view)
        await interaction.response.send_message("✅ Solicitud enviada.", ephemeral=True)
    else:
        await interaction.response.send_message("Error: Canal de destino no encontrado.", ephemeral=True)

# --- CARGA Y SINCRONIZACIÓN ---
@bot.event
async def setup_hook():
    # Cargar otros archivos de las carpetas
    for folder in ['Comandos', 'Interacciones']:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith('.py') and filename != 'auxiliar.py':
                    try:
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                    except Exception as e:
                        print(f'No se pudo cargar {filename}: {e}')
    
    # Sincronizar comandos de barra
    await bot.tree.sync()
    print("✅ Comandos sincronizados correctamente.")

@bot.event
async def on_ready():
    print(f'✅ Bot online como {bot.user}')

# --- INICIO ---
token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("❌ Falta el DISCORD_TOKEN en los Secrets de GitHub")
