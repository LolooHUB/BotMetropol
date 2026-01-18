import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- FIREBASE ---
cred_json = os.getenv("FIREBASE_CONFIG")
if cred_json:
    try:
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Error Firebase: {e}")

# --- BOT CONFIG ---
intents = discord.Intents.all() # Activamos todos para evitar problemas de permisos
bot = commands.Bot(command_prefix="!", intents=intents)

# --- CARGA DE COMANDOS ---
async def load_extensions():
    for folder in ['Comandos', 'Interacciones']:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith('.py'):
                    try:
                        # Evitamos recargar si ya está cargado
                        if f"{folder}.{filename[:-3]}" not in bot.extensions:
                            await bot.load_extension(f'{folder}.{filename[:-3]}')
                    except Exception as e:
                        print(f'Error cargando {filename}: {e}')

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="La Nueva Metropol S.A."
    ))
    print(f'✅ Bot conectado: {bot.user}')

# --- COMANDO SECRETO PARA ACTIVAR LOS "/" ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    """Escribe !sync en el chat para que aparezcan los comandos /"""
    await ctx.send("🔄 Intentando sincronizar comandos de barra...")
    try:
        # Esto sincroniza los comandos con el servidor actual
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"✅ ¡Éxito! Se sincronizaron {len(synced)} comandos. Reinicia tu Discord (Ctrl+R) para verlos.")
    except Exception as e:
        await ctx.send(f"❌ Error al sincronizar: {e}")

# --- RESPUESTA A PINGS ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    if bot.user.mentioned_in(message):
        await message.channel.send("¿Necesitas ayuda?, hace !ayuda para mas.")
    await bot.process_commands(message)

# --- INICIO ---
async def setup():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv("DISCORD_TOKEN"))

import asyncio
if __name__ == "__main__":
    asyncio.run(setup())
