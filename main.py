import discord
from discord.ext import commands
import os
import random

# Configuración de Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.typing = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    # Actividad permanente
    activity = discord.Activity(type=discord.ActivityType.watching, name="La Nueva Metropol S.A.")
    await bot.change_presence(activity=activity)
    print(f'Bot iniciado como {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Respuesta al mencionar al bot
    if bot.user.mentioned_in(message):
        respuestas = [
            "¿Necesitas ayuda?, hace !ayuda para más.",
            f"¿Ya te inscribiste a Metropol en <#1390152260578967558>?",
            "¡Hola! Los inspectores están atentos a las rutas hoy.",
            "Recuerda respetar las señales de tránsito en el simulador.",
            "Si tienes una emergencia, usa el comando /auxilio."
        ]
        await message.channel.send(random.choice(respuestas))
    
    await bot.process_commands(message)

# Aquí se cargarían los cogs (comandos en carpetas)
# bot.load_extension('Comandos.ban') ... etc
