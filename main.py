import discord
from discord.ext import commands
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import asyncio

# --- CONFIGURACIÓN DE FIREBASE ---
firebase_config = os.getenv("FIREBASE_CONFIG")
db = None

if firebase_config:
    try:
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase Conectado correctamente.")
    except Exception as e:
        print(f"❌ Error al conectar Firebase: {e}")

# --- CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.db = db  # Compartimos la DB para que los Cogs la usen

# --- CARGA DE EXTENSIONES RECURSIVA ---
# Esto permite leer Comandos/Staff, Comandos/Personal, etc.
async def load_extensions():
    # Carpetas principales a escanear
    folders = ['Comandos', 'Interacciones', 'Automatizaciones']
    
    for base_folder in folders:
        if os.path.exists(base_folder):
            # os.walk recorre todas las subcarpetas de forma profunda
            for root, dirs, files in os.walk(base_folder):
                for filename in files:
                    if filename.endswith('.py') and not filename.startswith('__'):
                        # Construye la ruta del módulo para Discord.py
                        # Ejemplo: Comandos/Staff/ban.py -> Comandos.Staff.ban
                        path = os.path.join(root, filename)
                        extension_name = os.path.splitext(path)[0].replace(os.sep, '.')
                        
                        try:
                            await bot.load_extension(extension_name)
                            print(f'✅ Extensión cargada: {extension_name}')
                        except Exception as e:
                            print(f'❌ Error cargando {extension_name}: {e}')

@bot.event
async def on_ready():
    # Establecer Status
    activity = discord.Activity(type=discord.ActivityType.watching, name="La Nueva Metropol S.A.")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    # Sincronización inicial rápida
    try:
        await bot.tree.sync()
        print(f"🚀 Bot Online: {bot.user} | Comandos Sincronizados")
    except Exception as e:
        print(f"❌ Error en Sync inicial: {e}")

# --- COMANDO PARA LIMPIAR DUPLICADOS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    """Limpia la caché de comandos y resincroniza todo"""
    await ctx.send("♻️ **Limpiando comandos duplicados...** esto puede tardar unos segundos.")
    try:
        # 1. Limpia los comandos del árbol interno
        bot.tree.clear_commands(guild=ctx.guild)
        
        # 2. Sincroniza (esto pisa cualquier comando viejo en el servidor)
        await bot.tree.sync(guild=ctx.guild)
        await bot.tree.sync() # Sincronización global
        
        await ctx.send("✅ **Limpieza completada.**\n⚠️ **IMPORTANTE:** Si seguís viendo duplicados, presioná `Ctrl + R` en PC o reiniciá la app.")
    except Exception as e:
        await ctx.send(f"❌ Error durante la sincronización: {e}")

# --- ARRANQUE DEL BOT ---
async def main():
    async with bot:
        await load_extensions()
        token = os.getenv("DISCORD_TOKEN")
        if token:
            await bot.start(token)
        else:
            print("❌ ERROR: No se encontró el DISCORD_TOKEN en los Secrets.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
