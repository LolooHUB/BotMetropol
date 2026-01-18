import discord
from discord.ext import commands
import os

# --- CONFIGURACIÓN ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    # Sincronizamos al prender para que aparezcan los /
    try:
        await bot.tree.sync()
        print(f"✅ Bot conectado como {bot.user}")
        print("🌐 Comandos de barra sincronizados.")
    except Exception as e:
        print(f"❌ Error al sincronizar: {e}")

# Comando de emergencia por chat
@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("🔄 Sincronización manual solicitada.")

# Función para cargar el auxiliar.py específicamente
async def load_extensions():
    try:
        # Cargamos el archivo directamente
        await bot.load_extension('Comandos.auxiliar')
        print("✅ Extensión Auxiliar cargada.")
    except Exception as e:
        print(f"❌ No se pudo cargar auxiliar.py: {e}")

async def setup():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv("DISCORD_TOKEN"))

import asyncio
if __name__ == "__main__":
    asyncio.run(setup())
