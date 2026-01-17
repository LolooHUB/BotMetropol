import discord
from discord.ext import commands
import os
import asyncio

async def sincronizar():
    # Configuramos el bot solo para sincronización
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    # Lista de extensiones a cargar para registrar sus comandos
    extensions = [
        'Comandos.moderacion',
        'Comandos.servicios'
    ]
    
    async with bot:
        print("--- Iniciando Proceso de Sincronización ---")
        
        # Cargamos las extensiones
        for ext in extensions:
            try:
                await bot.load_extension(ext)
                print(f"✅ Extensión preparada: {ext}")
            except Exception as e:
                print(f"❌ Error al preparar {ext}: {e}")
        
        # Nos conectamos brevemente para sincronizar
        print("Conectando con la API de Discord...")
        await bot.login(os.getenv('DISCORD_TOKEN'))
        
        # Sincronización global
        comandos_sincronizados = await bot.tree.sync()
        
        print(f"--- Sincronización Exitosa ---")
        print(f"Se han registrado {len(comandos_sincronizados)} comandos de barra.")
        print("Ya puedes cerrar este proceso o dejar que termine.")
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(sincronizar())
    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN DEPLOY: {e}")