import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import random
import asyncio

# --- CONFIGURACIÓN HORA ARGENTINA ---
tz_arg = timezone(timedelta(hours=-3))

class LicenciaModal(discord.ui.Modal, title='Registro de Licencia Habilitante'):
    usuario_discord = discord.ui.TextInput(label='Usuario de Discord', placeholder='Ej: @el_chofer', min_length=3)
    usuario_roblox = discord.ui.TextInput(label='Usuario de Roblox', placeholder='Ej: ChoferBus2026', min_length=3)
    exp_previa = discord.ui.TextInput(label='¿Has estado en alguna empresa antes?', placeholder='Ej: Línea 60 o Ninguna', required=True)
    edad_irl = discord.ui.TextInput(label='¿Cuántos años tienes? IRL', placeholder='Ingresa tu edad real', min_length=1, max_length=2)

    def __init__(self, bot, db):
        super().__init__()
        self.bot = bot
        self.db = db
        self.CANAL_STAFF_ID = 1390152261937922070 # Canal de alertas

    async def on_submit(self, interaction: discord.Interaction):
        # Validar si es un número
        if not self.edad_irl.value.isdigit():
            return await interaction.response.send_message("❌ La edad debe ser un número.", ephemeral=True)
        
        edad = int(self.edad_irl.value)
        lic_id = f"LNM-{random.randint(1000, 9999)}"
        fecha_emision = datetime.now(tz_arg).strftime('%d/%m/%Y')

        data = {
            "Discord_User": self.usuario_discord.value,
            "Edad_IRL": self.edad_irl.value,
            "Experiencia": self.exp_previa.value,
            "FechaEmision": fecha_emision,
            "LicenciaID": lic_id,
            "Roblox_User": self.usuario_roblox.value,
            "UsuarioID": str(interaction.user.id)
        }

        # 1. Guardar en Firestore
        self.db.collection("Licencias").document(str(interaction.user.id)).set(data)

        # 2. Alerta a Staff si es menor a 13 años
        if edad < 13:
            canal_staff = self.bot.get_channel(self.CANAL_STAFF_ID)
            if canal_staff:
                # Formato de texto plano con ping a everyone
                reporte = (
                    f"@everyone\n"
                    f"⚠️ **EL USUARIO {interaction.user.mention} ES MENOR DE 13 AÑOS**\n"
                    "```yaml\n"
                    f"Discord_User\n\"{data['Discord_User']}\"\n(string)\n"
                    f"Edad_IRL\n\"{data['Edad_IRL']}\"\n(string)\n"
                    f"Experiencia\n\"{data['Experiencia']}\"\n(string)\n"
                    f"FechaEmision\n\"{data['FechaEmision']}\"\n(string)\n"
                    f"LicenciaID\n\"{data['LicenciaID']}\"\n(string)\n"
                    f"Roblox_User\n\"{data['Roblox_User']}\"\n(string)\n"
                    f"UsuarioID\n\"{data['UsuarioID']}\"\n(string)\n"
                    "```"
                )
                await canal_staff.send(reporte)

        # 3. Vincular con Legajo
        legajo_ref = self.db.collection("Legajos").document(str(interaction.user.id))
        if legajo_ref.get().exists:
            legajo_ref.update({"LicenciaID": lic_id})

        await interaction.response.send_message(f"✅ ¡Licencia tramitada! Tu ID es: **{lic_id}**.", ephemeral=True)

class Licencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="licencia", description="Crea o muestra tu licencia de conducir profesional")
    async def licencia(self, interaction: discord.Interaction):
        db = self.bot.db
        if not db:
            return await interaction.response.send_message("❌ Error de DB.", ephemeral=True)

        doc_ref = db.collection("Licencias").document(str(interaction.user.id))
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.response.send_modal(LicenciaModal(self.bot, db))

        data = doc.to_dict()
        
        embed = discord.Embed(title="🪪 LICENCIA DE CONDUCIR PROFESIONAL", color=0x00FF00, timestamp=datetime.now(tz_arg))
        embed.set_author(name="La Nueva Metropol S.A. | CNRT Virtual", icon_url="attachment://LogoPFP.png")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_image(url="attachment://Banner.png")

        embed.add_field(name="🏷️ Titular", value=interaction.user.mention, inline=True)
        embed.add_field(name="🆔 ID Licencia", value=f"**{data.get('LicenciaID')}**", inline=True)
        embed.add_field(name="🎮 Roblox", value=f"**{data.get('Roblox_User')}**", inline=False)
        embed.add_field(name="🎂 Edad IRL", value=f"**{data.get('Edad_IRL')} años**", inline=True)
        embed.add_field(name="📅 Fecha", value=data.get('FechaEmision'), inline=True)

        f1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        f2 = discord.File("Imgs/Banner.png", filename="Banner.png")
        await interaction.response.send_message(files=[f1, f2], embed=embed)

async def setup(bot):
    await bot.add_cog(Licencia(bot))
