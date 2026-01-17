import discord
from discord.ext import commands
import os

class MetropolBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        # ID de tu servidor Metropol
        self.GUILD_ID = discord.Object(id=1390152252143964260)

    async def setup_hook(self):
        # 1. Carga de extensiones
        for ext in ['Comandos.moderacion', 'Comandos.servicios']:
            try:
                await self.load_extension(ext)
                print(f"✅ {ext} cargado.")
            except Exception as e:
                print(f"❌ Error cargando {ext}: {e}")

    async def on_ready(self):
        print(f"--- 🤖 {self.user.name} ONLINE ---")
        # 2. Sincronización automática al encender
        try:
            self.tree.copy_global_to(guild=self.GUILD_ID)
            await self.tree.sync(guild=self.GUILD_ID)
            print("🚀 COMANDOS / SINCRONIZADOS EXITOSAMENTE")
        except discord.errors.Forbidden:
            print("🛑 ERROR 403: Seguís sin el permiso de comandos. Usá el link que te pasé.")

bot = MetropolBot()

@bot.event
async def on_message(message):
    if message.author.bot: return

    # Comando de texto para probar si el bot "ve" el chat
    if message.content.lower() == "!test":
        await message.reply("✅ El bot te lee. Si no ves el '/' es por el permiso de comandos.")

    # Comando de emergencia para forzar carga
    if message.content.lower() == "!fuerza":
        if message.author.guild_permissions.administrator:
            try:
                await bot.tree.sync(guild=discord.Object(id=1390152252143964260))
                await message.channel.send("⚡ Sincronización completada. Reiniciá Discord (Ctrl+R).")
            except Exception as e:
                await message.channel.send(f"❌ Error: {e}")

    await bot.process_commands(message)

# Comandos clásicos que pediste
@bot.command()
async def ayuda(ctx):
    await ctx.send("📖 **Ayuda Metropol:**\nUsa `/auxilio` para mecánica o `!formularios`.")

@bot.command()
async def formularios(ctx):
    await ctx.send("📋 Encontrá los formularios en <#1390152260578967558>")

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
