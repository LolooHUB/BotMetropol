import discord
from discord.ext import commands
import os
import asyncio
import json

async def sincronizar():
    # Solo necesitamos los intents básicos para sincronizar
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    # ID de tu servidor (Asegurate que sea este)
    GUILD_ID = discord.Object(id=1390152252143964260) 

    async with bot:
        print("--- 🛠️ Iniciando Registro Forzado ---")
        
        # Intentamos cargar las extensiones pero ignoramos errores de Firebase
        extensions = ['Comandos.moderacion', 'Comandos.servicios']
        for ext in extensions:
            try:
                await bot.load_extension(ext)
                print(f"✅ Extensión preparada: {ext}")
            except Exception as e:
                print(f"⚠️ Error cargando {ext} (pero seguiremos): {e}")
        
        print("Conectando a Discord...")
        await bot.login(os.getenv('DISCORD_TOKEN'))
        
        # LIMPIEZA TOTAL Y REGISTRO EN EL SERVIDOR
        print("Limpiando comandos antiguos...")
        bot.tree.clear(guild=GUILD_ID)
        
        print(f"Sincronizando en servidor: {GUILD_ID.id}")
        bot.tree.copy_global_to(guild=GUILD_ID)
        comandos = await bot.tree.sync(guild=GUILD_ID)
        
        print(f"--- ✅ SINCRONIZACIÓN COMPLETADA ---")
        print(f"Se registraron {len(comandos)} comandos en el servidor.")
        
        await bot.close()

if __name__ == "__main__":
    asyncio.run(sincronizar())
