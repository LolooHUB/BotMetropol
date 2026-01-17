import discord
from discord.ext import commands
import os

class MetropolBot(commands.Bot):
    def __init__(self):
        # Los intents permiten que el bot vea los mensajes y miembros
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        # ID de tu servidor Metropol
        self.GUILD_ID = discord.Object(id=1390152252143964260)

    async def setup_hook(self):
        print("--- 🛠️ Iniciando Limpieza y Carga ---")
        # Cargamos los archivos de la carpeta Comandos
        for ext in ['Comandos.moderacion', 'Comandos.servicios']:
            try:
                await self.load_extension(ext)
                print(f"✅ Extensión cargada: {ext}")
            except Exception as e:
                print(f"❌ Error cargando {ext}: {e}")

    async def on_ready(self):
        print(f"--- 🤖 BOT ONLINE: {self.user.name} ---")
        try:
            # Borramos comandos viejos y cargamos los nuevos solo en tu servidor
            self.tree.clear(guild=self.GUILD_ID)
            self.tree.copy_global_to(guild=self.GUILD_ID)
            await self.tree.sync(guild=self.GUILD_ID)
            print("🚀 ÉXITO TOTAL: Comandos sincronizados en Metropol.")
        except Exception as e:
            print(f"❌ Error crítico en on_ready: {e}")

bot = MetropolBot()

# Evento para verificar que el bot lee el chat
@bot.event
async def on_message(message):
    if message.author.bot: return

    # Si escribís !test y el bot NO responde, es un problema de INTENTS en el panel
    if message.content.lower() == "!test":
        await message.reply("👋 ¡Hola! El bot está funcionando. Si no ves los '/', reiniciá Discord (Ctrl+R).")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
