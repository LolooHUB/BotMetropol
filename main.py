import discord
from discord.ext import commands
import os

class MetropolBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        # ID de tu servidor
        self.GUILD_ID = discord.Object(id=1390152252143964260)

    async def setup_hook(self):
        # Carga de archivos
        for ext in ['Comandos.moderacion', 'Comandos.servicios']:
            try:
                await self.load_extension(ext)
                print(f"✅ {ext} cargado.")
            except Exception as e:
                print(f"❌ Error cargando {ext}: {e}")

    async def on_ready(self):
        print(f"--- 🤖 BOT ONLINE: {self.user.name} ---")
        # FORZAR SINCRONIZACIÓN AL CONECTARSE
        try:
            self.tree.copy_global_to(guild=self.GUILD_ID)
            await self.tree.sync(guild=self.GUILD_ID)
            print("🚀 COMANDOS SINCRONIZADOS EXITOSAMENTE")
        except Exception as e:
            print(f"❌ Error en sincronización: {e}")

bot = MetropolBot()

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # Si nada funciona, escribí !sincronizar en Discord
    if message.content.lower() == "!sincronizar":
        if message.author.guild_permissions.administrator:
            try:
                await bot.tree.sync(guild=discord.Object(id=1390152252143964260))
                await message.reply("⚡ Comandos sincronizados a la fuerza.")
            except Exception as e:
                await message.reply(f"❌ Error: {e}")
        else:
            await message.reply("Solo admins.")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
