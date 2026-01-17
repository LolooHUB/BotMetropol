import discord
from discord.ext import commands, tasks
import os
import sys
import logging
import random
from datetime import datetime

# Configuración de Logs para ver errores en GitHub Actions
logging.basicConfig(level=logging.INFO)

class MetropolBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!", 
            intents=intents, 
            help_command=None,
            chunk_guilds_at_startup=True
        )
        # Extensiones a cargar
        self.inicial_extensions = ['Comandos.moderacion', 'Comandos.servicios']
        
        # IDs de Configuración
        self.canal_logs_id = 1390152261937922070
        self.GUILD_ID = discord.Object(id=1390152252143964260) 

    async def setup_hook(self):
        # 1. Limpieza de comandos antiguos para evitar duplicados
        print("--- 🧹 Limpiando Caché de Comandos ---")
        try:
            self.tree.clear(guild=None)
            await self.tree.sync(guild=None)
            print("✅ Caché global limpia.")
        except Exception as e:
            print(f"⚠️ Nota en limpieza global: {e}")

        # 2. Carga de Cogs (servicios.py y moderacion.py)
        print("--- 📥 Cargando Extensiones ---")
        for extension in self.inicial_extensions:
            try:
                await self.load_extension(extension)
                print(f"✅ Extensión cargada: {extension}")
            except Exception as e:
                print(f"❌ ERROR cargando {extension}: {e}")

        # 3. Sincronización Forzada al Servidor (Instantánea)
        print("--- 🔄 Sincronizando Servidor Metropol ---")
        try:
            self.tree.copy_global_to(guild=self.GUILD_ID)
            comandos = await self.tree.sync(guild=self.GUILD_ID)
            print(f"✨ ÉXITO: {len(comandos)} comandos de barra activos en el servidor.")
        except Exception as e:
            print(f"❌ Error crítico en sync: {e}")

    @tasks.loop(minutes=20)
    async def presencia_loop(self):
        await self.wait_until_ready()
        estados = [
            "¿Cuándo pasa la 65?", 
            "La Nueva Metropol S.A.", 
            "Control de Unidades", 
            "¡Qué lindos los ints!"
        ]
        await self.change_presence(activity=discord.Game(name=random.choice(estados)))

    async def on_ready(self):
        if not self.presencia_loop.is_running():
            self.presencia_loop.start()
        print(f"--- 🤖 BOT ONLINE COMO: {self.user.name} ---")

# Instancia del bot
bot = MetropolBot()

# --- EVENTO DE BIENVENIDA ---
@bot.event
async def on_member_join(member):
    canal = bot.get_channel(bot.canal_logs_id)
    if canal:
        embed = discord.Embed(
            title="📥 Nuevo Miembro", 
            description=f"{member.mention} se unió al servidor de la Metropol.", 
            color=discord.Color.green(), 
            timestamp=datetime.now()
        )
        await canal.send(embed=embed)

# --- COMANDOS CLÁSICOS (!) Y MENCIONES ---
@bot.event
async def on_message(message):
    if message.author.bot: return

    # 1. Respuesta a menciones del bot
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        respuestas = ["¿Necesitás ayuda? Usá !ayuda", "¿Ya te inscribiste a Metropol?", "¡QUÉ QUERÉEEEEES!"]
        await message.reply(random.choice(respuestas))

    # 2. Comandos de texto clásicos
    contenido = message.content.lower()
    
    if contenido == "!ayuda":
        await message.reply("📖 **Comandos Metropol:**\n`/auxilio` - Pedir mecánica.\n`!formularios` - Enlaces.\n`!ayuda` - Este mensaje.")
    
    elif contenido == "!formularios":
        await message.reply("📋 Encontrá los formularios en <#1390152260578967558>")

    # 3. COMANDO DE EMERGENCIA (Para forzar la carga si nada funciona)
    elif contenido == "!fuerza" and message.author.guild_permissions.administrator:
        try:
            bot.tree.copy_global_to(guild=bot.GUILD_ID)
            await bot.tree.sync(guild=bot.GUILD_ID)
            await message.reply("🚀 Sincronización forzada enviada a Discord. Reiniciá tu app (Ctrl+R).")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")

    await bot.process_commands(message)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ ERROR: No se encontró el DISCORD_TOKEN.")
