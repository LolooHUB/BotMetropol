import discord
from discord.ext import commands
import os
import random
import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- CONFIGURACIÓN DE FIREBASE ---
cred_json = os.getenv("FIREBASE_CONFIG")
if cred_json:
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
else:
    print("⚠️ Error: No se encontró la variable FIREBASE_CONFIG")

# --- CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.typing = True

class MetropolBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Carga automática de carpetas
        for folder in ['Comandos', 'Interacciones']:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    if filename.endswith('.py'):
                        try:
                            await self.load_extension(f'{folder}.{filename[:-3]}')
                            print(f'✅ Cargado: {folder}/{filename}')
                        except Exception as e:
                            print(f'❌ Error al cargar {filename}: {e}')

bot = MetropolBot()

@bot.event
async def on_ready():
    # Actividad permanente
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="La Nueva Metropol S.A."
    ))
    print(f'--- BOT ONLINE ---')
    print(f'Usuario: {bot.user}')
    print(f'ID: {bot.user.id}')
    print(f'------------------')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Interacción por Ping (Mención)
    if bot.user.mentioned_in(message):
        respuestas = [
            "¿Necesitas ayuda?, hace !ayuda para mas.",
            "Ya te inscribiste a Metropol en <#1390152260578967558>?",
            "¡Hola! Los servicios están operando con normalidad.",
            "Recordá que para reportar cortes tenés el comando /desvio.",
            "Si sos chofer y necesitás asistencia, usá /auxilio."
        ]
        await message.channel.send(random.choice(respuestas))

    await bot.process_commands(message)

# Ejecución
token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("⚠️ Error: No se encontró la variable DISCORD_TOKEN")
