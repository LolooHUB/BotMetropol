import discord
from discord.ext import commands
import datetime
from zoneinfo import ZoneInfo

class GremioEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

        self.CANAL_ANUNCIOS_ID = 1465462294824882258
        self.CANAL_COMUNICACION_ID = 1464064701410447411

        self.ROL_DIRECTIVOS_ID = 1397020690435149824
        self.ROL_GREMIO_ID = 1445835728285208769

        self.BANNER_PATH = "Imgs/BannerGremio.png"

        # View persistente
        bot.add_view(self.GremioView(self))

    # ================= VIEW =================
    class GremioView(discord.ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog

        @discord.ui.button(
            label="Unirme / Salir del gremio",
            style=discord.ButtonStyle.success,
            custom_id="toggle_gremio"
        )
        async def toggle(self, interaction: discord.Interaction, button: discord.ui.Button):
            member = interaction.user
            role = interaction.guild.get_role(self.cog.ROL_GREMIO_ID)
            now = datetime.datetime.now(
                ZoneInfo("America/Argentina/Buenos_Aires")
            )

            if role in member.roles:
                await interaction.response.send_modal(
                    self.cog.MotivoSalidaModal(self.cog, member)
                )
                return

            await member.add_roles(role)

            self.cog.db.collection("MiembrosGremio").document(str(member.id)).set({
                "user_id": member.id,
                "username": str(member),
                "fecha": now.strftime("%d/%m/%Y"),
                "hora": now.strftime("%H:%M")
            })

            await interaction.response.send_message(
                "✅ Te uniste al gremio.",
                ephemeral=True
            )

    # ================= MODAL =================
    class MotivoSalidaModal(discord.ui.Modal, title="Salida del gremio"):
        motivo = discord.ui.TextInput(
            label="Motivo",
            placeholder="Explicá brevemente el motivo...",
            max_length=300,
            required=True
        )

        def __init__(self, cog, member):
            super().__init__()
            self.cog = cog
            self.member = member

        async def on_submit(self, interaction: discord.Interaction):
            role = interaction.guild.get_role(self.cog.ROL_GREMIO_ID)
            now = datetime.datetime.now(
                ZoneInfo("America/Argentina/Buenos_Aires")
            )

            if role in self.member.roles:
                await self.member.remove_roles(role)

            self.cog.db.collection("MiembrosGremio").document(
                str(self.member.id)
            ).delete()

            self.cog.db.collection("SalidasGremio").add({
                "user_id": self.member.id,
                "username": str(self.member),
                "fecha": now.strftime("%d/%m/%Y"),
                "hora": now.strftime("%H:%M"),
                "motivo": self.motivo.value
            })

            await interaction.response.send_message(
                "🚪 Saliste del gremio.",
                ephemeral=True
            )

    # ================= READY =================
    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.CANAL_ANUNCIOS_ID)
        if not channel:
            return

        hora_arg = datetime.datetime.now(
            ZoneInfo("America/Argentina/Buenos_Aires")
        ).strftime("%H:%M")

        embed = discord.Embed(
            title="🚌 Gremio de Colectiveros",
            description=(
                "### 📌 ¿Qué es el gremio?\n"
                "Espacio donde los colectiveros pueden presentar reclamos,\n"
                "organizarse y coordinar acciones.\n\n"
                "### 🏛️ Estructura\n"
                f"• **Dirección:** <@&{self.ROL_DIRECTIVOS_ID}>\n"
                f"• **Miembros:** <@&{self.ROL_GREMIO_ID}>\n\n"
                "### 💬 Comunicación\n"
                f"Canal oficial: <#{self.CANAL_COMUNICACION_ID}>"
            ),
            color=0x1F8B4C
        )

        embed.set_footer(
            text=f"La Nueva Metropol S.A. | {hora_arg}"
        )

        file = discord.File(self.BANNER_PATH, filename="BannerGremio.png")
        embed.set_image(url="attachment://BannerGremio.png")

        await channel.send(
            embed=embed,
            view=self.GremioView(self),
            file=file
        )

    # ============== LEAVE SERVER ==============
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        role = member.guild.get_role(self.ROL_GREMIO_ID)
        if role and role in member.roles:
            now = datetime.datetime.now(
                ZoneInfo("America/Argentina/Buenos_Aires")
            )

            self.db.collection("MiembrosGremio").document(
                str(member.id)
            ).delete()

            self.db.collection("SalidasGremio").add({
                "user_id": member.id,
                "username": str(member),
                "fecha": now.strftime("%d/%m/%Y"),
                "hora": now.strftime("%H:%M"),
                "motivo": "Salida del servidor"
            })

async def setup(bot):
    await bot.add_cog(GremioEmbed(bot))
