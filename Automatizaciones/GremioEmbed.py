import os
import json
import discord
from discord.ext import commands
import datetime
from zoneinfo import ZoneInfo

import firebase_admin
from firebase_admin import credentials, firestore

# ================== CONFIG ==================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FIREBASE_CONFIG = os.getenv("FIREBASE_CONFIG")

CANAL_ANUNCIOS_ID = 1465462294824882258
CANAL_COMUNICACION_ID = 1464064701410447411

ROL_DIRECTIVOS_ID = 1397020690435149824
ROL_GREMIO_ID = 1445835728285208769

BANNER_PATH = "Imgs/BannerGremio.png"

# ================= FIREBASE =================
if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(FIREBASE_CONFIG))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ================= DISCORD ==================
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= MODAL ====================
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
        now = datetime.datetime.now(
            ZoneInfo("America/Argentina/Buenos_Aires")
        )

        if role in self.member.roles:
            await self.member.remove_roles(role)

        db.collection("MiembrosGremio").document(str(self.member.id)).delete()

        db.collection("SalidasGremio").add({
            "user_id": self.member.id,
            "username": str(self.member),
            "fecha": now.strftime("%d/%m/%Y"),
            "hora": now.strftime("%H:%M"),
            "motivo": self.motivo.value
        })

        await interaction.response.send_message(
            "🚪 Saliste del gremio correctamente.",
            ephemeral=True
        )

# ================= VIEW =====================
class GremioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Unirme / Salir del gremio",
        style=discord.ButtonStyle.success,
        custom_id="toggle_gremio"
    )
    async def toggle(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        role = interaction.guild.get_role(ROL_GREMIO_ID)
        now = datetime.datetime.now(
            ZoneInfo("America/Argentina/Buenos_Aires")
        )

        if role in member.roles:
            await interaction.response.send_modal(MotivoSalidaModal(member))
            return

        await member.add_roles(role)

        db.collection("MiembrosGremio").document(str(member.id)).set({
            "user_id": member.id,
            "username": str(member),
            "fecha": now.strftime("%d/%m/%Y"),
            "hora": now.strftime("%H:%M")
        })

        await interaction.response.send_message(
            "✅ Te uniste al gremio.",
            ephemeral=True
        )

# ================= EVENTOS ==================
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

    # 🔥 botones persistentes
    bot.add_view(GremioView())

    canal = bot.get_channel(CANAL_ANUNCIOS_ID)
    if canal is None:
        print("❌ No se encontró el canal de anuncios")
        return

    hora_arg = datetime.datetime.now(
        ZoneInfo("America/Argentina/Buenos_Aires")
    ).strftime("%H:%M")

    embed = discord.Embed(
        title="🚌 Gremio de Colectiveros",
        description=(
            "### 📌 ¿Qué es el gremio?\n"
            "Organización de colectiveros donde se pueden presentar reclamos,\n"
            "coordinar acciones y organizar movilizaciones.\n\n"
            "### 🏛️ Estructura\n"
            f"• **Dirección:** <@&{ROL_DIRECTIVOS_ID}>\n"
            f"• **Miembros:** <@&{ROL_GREMIO_ID}>\n\n"
            "### 💬 Comunicación\n"
            f"Canal oficial: <#{CANAL_COMUNICACION_ID}>"
        ),
        color=discord.Color.dark_green()
    )

    embed.set_footer(text=f"La Nueva Metropol S.A. | {hora_arg}")

    file = discord.File(BANNER_PATH, filename="BannerGremio.png")
    embed.set_image(url="attachment://BannerGremio.png")

    await canal.send(embed=embed, view=GremioView(), file=file)

@bot.event
async def on_member_remove(member: discord.Member):
    role = member.guild.get_role(ROL_GREMIO_ID)

    if role and role in member.roles:
        now = datetime.datetime.now(
            ZoneInfo("America/Argentina/Buenos_Aires")
        )

        db.collection("MiembrosGremio").document(str(member.id)).delete()

        db.collection("SalidasGremio").add({
            "user_id": member.id,
            "username": str(member),
            "fecha": now.strftime("%d/%m/%Y"),
            "hora": now.strftime("%H:%M"),
            "motivo": "Salida del servidor"
        })

# ================= RUN =====================
bot.run(DISCORD_TOKEN)
