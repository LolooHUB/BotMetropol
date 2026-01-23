import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import random
import asyncio

# --- CONFIGURACIÓN HORA ARGENTINA ---
tz_arg = timezone(timedelta(hours=-3))

class LicenciaModal(discord.ui.Modal, title='Registro de Licencia Habilitante'):
    # --- NUEVOS CAMPOS ---
    # El usuario de Discord se obtiene automáticamente, pero lo pedimos para confirmar
    usuario_discord = discord.ui.TextInput(label='Usuario de Discord', placeholder='Ej: @el_chofer', min_length=3)
    usuario_roblox = discord.ui.TextInput(label='Usuario de Roblox', placeholder='Ej: ChoferBus2026', min_length=3)
    exp_previa = discord.ui.TextInput(
        label='¿Has estado en alguna empresa antes?', 
        placeholder='Ej: Línea 60, Empresa del Oeste, o Ninguna', 
        required=True
    )
    edad_irl = discord.ui.TextInput(
        label='¿Cuántos años tienes? IRL', 
        placeholder='Ingresa tu edad real', 
        min_length=1, 
        max_length=2
    )

    def __init__(self, db):
        super().__init__()
        self.db = db

    async def on_submit(self, interaction: discord.Interaction):
        # Generar un ID de Licencia único
        lic_id = f"LNM-{random.randint(1000, 9999)}"
        fecha_emision = datetime.now(tz_arg).strftime('%d/%m/%Y')

        # Guardamos los nuevos datos en el diccionario
        data = {
            "UsuarioID": str(interaction.user.id),
            "LicenciaID": lic_id,
            "Discord_User": self.usuario_discord.value,
            "Roblox_User": self.usuario_roblox.value,
            "Experiencia": self.exp_previa.value,
            "Edad_IRL": self.edad_irl.value,
            "FechaEmision": fecha_emision
        }

        # 1. Guardar en la colección Licencias (Firestore)
        self.db.collection("Licencias").document(str(interaction.user.id)).set(data)

        # 2. Vincular con el Legajo automáticamente si ya existe
        legajo_ref = self.db.collection("Legajos").document(str(interaction.user.id))
        if legajo_ref.get().exists:
            legajo_ref.update({"LicenciaID": lic_id})

        await interaction.response.send_message(
            f"✅ ¡Licencia tramitada satisfactoriamente! Tu ID de conductor es: **{lic_id}**.\nYa puedes consultar tu ficha profesional con `/licencia`.", 
            ephemeral=True
        )

class Licencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="licencia", description="Crea o muestra tu licencia de conducir profesional")
    async def licencia(self, interaction: discord.Interaction):
        # Usamos la DB compartida en el bot (configurada en Main.py)
        db = self.bot.db
        if not db:
            return await interaction.response.send_message("❌ Error: No se pudo conectar con la base de datos.", ephemeral=True)

        doc_ref = db.collection("Licencias").document(str(interaction.user.id))
        doc = doc_ref.get()

        # Si NO tiene licencia, abrir Modal con los nuevos campos
        if not doc.exists:
            return await interaction.response.send_modal(LicenciaModal(db))

        # Si TIENE licencia, mostrarla con el formato de la empresa
        data = doc.to_dict()
        
        embed = discord.Embed(
            title="🪪 LICENCIA DE CONDUCIR PROFESIONAL", 
            color=0x00FF00, # Verde Metropol
            timestamp=datetime.now(tz_arg)
        )
        embed.set_author(name="La Nueva Metropol S.A. | CNRT Virtual", icon_url="attachment://LogoPFP.png")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_image(url="attachment://Banner.png")

        embed.add_field(name="🏷️ Titular (Discord)", value=interaction.user.mention, inline=True)
        embed.add_field(name="🆔 ID Licencia", value=f"**{data.get('LicenciaID', 'N/A')}**", inline=True)
        embed.add_field(name="🎮 Usuario Roblox", value=f"**{data.get('Roblox_User', 'No registrado')}**", inline=False)
        embed.add_field(name="🎂 Edad IRL", value=f"**{data.get('Edad_IRL', 'N/A')} años**", inline=True)
        embed.add_field(name="📅 Fecha de Emisión", value=data.get('FechaEmision', 'N/A'), inline=True)
        embed.add_field(name="🚛 Antecedentes", value=data.get('Experiencia', 'Sin información'), inline=False)

        embed.set_footer(text="Documento oficial intransferible - Metropol")

        # Carga de archivos para el Embed
        try:
            f1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
            f2 = discord.File("Imgs/Banner.png", filename="Banner.png")
            await interaction.response.send_message(files=[f1, f2], embed=embed)
        except:
            # Fallback por si las imágenes fallan
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Licencia(bot))
