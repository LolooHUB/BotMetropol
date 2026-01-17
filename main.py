import discord
from discord.ext import commands, tasks
import os
import sys
import logging
import random
from datetime import datetime

# Configuración de Logs para ver todo en el panel de GitHub Actions
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')

class MetropolBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            chunk_guilds_at_startup=True
        )
        self.inicial_extensions = [
            'Comandos.moderacion',
            'Comandos.servicios'
        ]

    async def setup_hook(self):
        """Se ejecuta antes de que el bot se conecte a Discord"""
        print("--- Iniciando Carga de Extensiones ---")
        for extension in self.inicial_extensions:
            try:
                await self.load_extension(extension)
                print(f"✅ Extensión cargada: {extension}")
            except Exception as e:
                print(f"❌ Error cargando {extension}: {e}")

        # Sincronización automática al encender
        print("--- Sincronizando Comandos de Barra ---")
        await self.tree.sync()
        print("✅ Sincronización completada.")
        
        # Iniciar tareas en segundo plano
        self.presencia_loop.start()

    @tasks.loop(minutes=20)
    async def presencia_loop(self):
        """Ciclo de actividad permanente"""
        estados = [
            "Cuando pasa la 65?", 
            "Ya te anotaste para Metropol?", 
            "Que lindos los ints de Metropol!"
        ]
        nuevo_estado = random.choice(estados)
        await self.change_presence(activity=discord.Game(name=nuevo_estado))
        print(f"🎮 Estado cambiado a: {nuevo_estado}")

    async def on_ready(self):
        print(f"--- BOT ONLINE ---")
        print(f"Nombre: {self.user.name}")
        print(f"ID: {self.user.id}")
        print(f"Servidores: {len(self.guilds)}")
        print("------------------")

# --- EVENTOS DE INTERACCIÓN ---

bot = MetropolBot()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Escuchar Pings al Bot
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        respuestas = [
            "¿Necesitas ayuda?, hace !ayuda para mas.",
            "¿Ya te inscribiste a Metropol en <#1390152260578967558>?",
            "¡Hola! Los servicios operan con normalidad.",
            "¿Buscás formar parte? Mirá <#1390152260578967558>.",
            "¡Buenas! Recordá que el respeto al pasajero es lo primero."
        ]
        await message.reply(random.choice(respuestas))

    # Comandos de texto directo (Compatibilidad)
    if message.content.lower() == "!ayuda":
        msg = ("Si queres obtener informacion acerca de los formularios ejecuta !formularios 🔰\n"
               "¿Queres hablar con el staff?, podes abrir un ticket en <#1390152260578967559>")
        await message.reply(msg)
    
    if message.content.lower() == "!formularios":
        await message.reply("Fijate el estado de nuestros formularios de ingreso en <#1390152260578967558> 💯")

    await bot.process_commands(message)

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ CRITICAL ERROR: DISCORD_TOKEN no encontrado en Secrets.")
        sys.exit(1)
    
    bot.run(token)