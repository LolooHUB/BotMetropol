import os
import json
import discord
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo

import firebase_admin
from firebase_admin import credentials, firestore

# ================= SECRETS =================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FIREBASE_CONFIG = os.getenv("FIREBASE_CONFIG")

# ================= CONFIG ==================
CANAL_ANUNCIOS_ID = 1465462294824882258
CANAL_COMUNICACION_ID = 1464064701410447411

ROL_DIRECTIVOS_ID = 1397020690435149824
ROL_GREMIO_ID = 1445835728285208769

BANNER_PATH = "Imgs/BannerGremio.png"

# =============== FIREBASE ==================
cred = credentials.Certificate(json.loads(FIREBASE_CONFIG))
firebase_admin.initialize_app(cred)
db = firestore.client()

# =============== DISCORD ===================
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =============== MODAL =====================
class MotivoSalidaModal(discord.ui.Modal, title="Salida del gremio"):
    motivo = discord.ui.TextInput(
        label="Motivo de la salida",
        placeholder="Explicá brevemente el motivo...",
        max_length=300,
        required=True
    )

    def __init__(self, member: discord.Member):
        super().__init__()
        self.member = member

    async def on_submit(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(ROL_GREMIO_ID)

        if role in self.member.roles:
            await self.member.remove_roles(role)

        # 🔴 BORRA DE MIEMBROS
        db.collection("MiembrosGremio").document(str(self.member.id)).delete()

        now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))

        # 🟢 REGISTRA SALIDA
        db.collection("SalidasGremio").add({
            "user_id": self.member.id,
            "username": str(self.member),
            "motivo": self.motivo.value,
            "fecha": now.strftime("%d/%m/%Y"),
            "hora": now.strftime("%H:%M")
        })

        await interaction.response.send_message(
            "🚪 Saliste del gremio. El motivo fue registrado.",
            ephemeral=True
        )

# =============== VIEW ======================
class GremioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Unirme al gremio",
        style=discord.ButtonStyle.success,
        custom_id="toggle_gremio"
    )
    async def toggle_gremio(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        role = interaction.guild.get_role(ROL_GREMIO_ID)

        now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))

        # 🔁 SI YA ES MIEMBRO → MODAL
        if role in member.roles:
            await interaction.response.send_modal(MotivoSalidaModal(member))
            return

        # 🟢 ALTA
        await member.add_roles(role)

        # 🟢 CREA / ACTUALIZA MIEMBROS
        db.collection("MiembrosGremio").document(str(member.id)).set({
            "user_id": member.id,
            "username": str(member),
            "fecha": now.strftime("%d/%m/%Y"),
            "hora": now.strftime("%H:%M")
        })

        await interaction.response.send_message(
            "✅ Te uniste al gremio correctamente.",
            ephemeral=True
        )

# =============== EVENTOS ===================
@bot.event
async def on_member_remove(member: discord.Member):
    role = member.guild.get_role(ROL_GREMIO_ID)

    if role and role in member.roles:
        now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))

        # 🔴 LIMPIA MIEMBROS
        db.collection("MiembrosGremio").document(str(member.id)).delete()

        # 🟠 REGISTRA SALIDA AUTOMÁTICA
        db.collection("SalidasGremio").add({
            "user_id": member.id,
            "username": str(member),
            "motivo": "Salida del servidor",
            "fecha": now.strftime("%d/%m/%Y"),
            "hora": now.strftime("%H:%M")
        })

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

    canal = bot.get_channel(CANAL_ANUNCIOS_ID)
    if not canal:
        print("❌ Canal de anuncios no encontrado")
        return

    hora_arg = datetime.now(
        ZoneInfo("America/Argentina/Buenos_Aires")
    ).strftime("%H:%M")

    embed = discord.Embed(
        title="🚌 Gremio de Colectiveros",
        description=(
            "### 📌 ¿Qué es el gremio?\n"
            "Organización destinada a representar y defender a los colectiveros,\n"
            "permitiendo **reclamos, propuestas y organización de acciones**.\n\n"
            "### 🏛️ Estructura\n"
            f"• **Dirección:** <@&{ROL_DIRECTIVOS_ID}>\n"
            f"• **Miembros:** <@&{ROL_GREMIO_ID}>\n\n"
            "### 💬 Comunicación\n"
            f"Los miembros pueden comunicarse libremente en <#{CANAL_COMUNICACION_ID}>."
        ),
        color=discord.Color.dark_green()
    )

    embed.set_footer(
        text=f"La Nueva Metropol S.A. | {hora_arg}"
    )

    file = discord.File(BANNER_PATH, filename="BannerGremio.png")
    embed.set_image(url="attachment://BannerGremio.png")

    await canal.send(embed=embed, view=GremioView(), file=file)

bot.run(DISCORD_TOKEN)
