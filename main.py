import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio

# --- CONFIGURACIÓN DE RUTAS ---
# Usamos el nombre exacto que me pasaste
RUTA_LOGO = "./IMGS/LogoPFP.png" 

class MetropolBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.GUILD_ID = discord.Object(id=1390152252143964260)

    async def setup_hook(self):
        print("--- 📂 Cargando Comandos ---")
        for filename in os.listdir('./Comandos'):
            if filename.endswith('.py') and not filename.startswith('__'):
                extension = f'Comandos.{filename[:-3]}'
                try:
                    await self.load_extension(extension)
                    print(f"✅ Cargado: {extension}")
                except Exception as e:
                    print(f"❌ Error en {extension}: {e}")

    async def on_ready(self):
        print(f"--- 🤖 {self.user.name} ONLINE ---")
        try:
            self.tree.copy_global_to(guild=self.GUILD_ID)
            await self.tree.sync(guild=self.GUILD_ID)
            print("🚀 Comandos sincronizados con el logo local.")
        except Exception as e:
            print(f"❌ Error de Sync: {e}")

bot = MetropolBot()

# --- COMANDO DE PRUEBA DEL LOGO ---
@bot.tree.command(name="test_logo", description="Verifica si el logo de IMGS carga bien")
async def test_logo(interaction: discord.Interaction):
    if os.path.exists(RUTA_LOGO):
        # 1. Creamos el objeto del archivo
        file = discord.File(RUTA_LOGO, filename="LogoPFP.png")
        
        embed = discord.Embed(
            title="Soporte Metropol",
            description="Si ves el logo a la derecha, la carpeta IMGS está bien vinculada.",
            color=discord.Color.blue()
        )
        # 2. Referenciamos el archivo adjunto en el thumbnail
        embed.set_thumbnail(url="attachment://LogoPFP.png")
        embed.set_footer(text="Metropol Sistema", icon_url="attachment://LogoPFP.png")
        
        # 3. Se envía el archivo y el embed juntos
        await interaction.response.send_message(file=file, embed=embed)
    else:
        await interaction.response.send_message(f"❌ No se encontró el archivo en: `{RUTA_LOGO}`", ephemeral=True)

# --- COMANDO PARA RECARGAR TODO ---
@bot.command()
async def recargar(ctx):
    if ctx.author.guild_permissions.administrator:
        try:
            await bot.tree.sync(guild=discord.Object(id=1390152252143964260))
            await ctx.send("⚡ Sistema resincronizado.")
        except Exception as e:
            await ctx.send(f"Error: {e}")

# --- INICIO DEL BOT ---
async def main():
    token = os.getenv('DISCORD_TOKEN')
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
