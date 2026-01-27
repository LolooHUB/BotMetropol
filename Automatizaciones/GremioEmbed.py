import discord
from discord.ext import commands
import datetime
from zoneinfo import ZoneInfo
import asyncio

class GremioEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        
        # IDs de Configuración
        self.CANAL_ANUNCIOS_ID = 1465462294824882258
        self.CANAL_COMUNICACION_ID = 1464064701410447411
        self.ROL_DIRECTIVOS_ID = 1397020690435149824
        self.ROL_GREMIO_ID = 1445835728285208769
        self.BANNER_PATH = "Imgs/BannerGremio.png"

        self.bot.add_view(self.GremioView(self))

    # ================= MODAL DE SALIDA =================
    class MotivoSalidaModal(discord.ui.Modal, title="Declaración de Baja Gremial"):
        motivo = discord.ui.TextInput(
            label="Motivo de la desvinculación",
            style=discord.TextStyle.paragraph,
            placeholder="Ej: Disconformidad, retiro de la empresa, cambio de funciones...",
            required=True, max_length=400
        )

        def __init__(self, cog, member):
            super().__init__(); self.cog = cog; self.member = member

        async def on_submit(self, interaction: discord.Interaction):
            role = interaction.guild.get_role(self.cog.ROL_GREMIO_ID)
            now = datetime.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
            
            if role in self.member.roles: await self.member.remove_roles(role)

            self.cog.db.collection("SalidasGremio").add({
                "user_id": self.member.id,
                "username": str(self.member),
                "fecha": now.strftime("%d/%m/%Y"),
                "hora": now.strftime("%H:%M"),
                "motivo": self.motivo.value
            })
            self.cog.db.collection("MiembrosGremio").document(str(self.member.id)).delete()

            await interaction.response.send_message("🚪 Se ha procesado tu baja del cuerpo gremial.", ephemeral=True)

    # ================= VIEW (BOTÓN) =================
    class GremioView(discord.ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog

        @discord.ui.button(label="Gestionar Afiliación", style=discord.ButtonStyle.success, custom_id="btn_gremio_v3")
        async def toggle(self, interaction: discord.Interaction, button: discord.ui.Button):
            member = interaction.user
            role = interaction.guild.get_role(self.cog.ROL_GREMIO_ID)
            now = datetime.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))

            if role in member.roles:
                await interaction.response.send_modal(self.cog.MotivoSalidaModal(self.cog, member))
                return

            await member.add_roles(role)
            self.cog.db.collection("MiembrosGremio").document(str(member.id)).set({
                "fecha": now.strftime("%d/%m/%Y"),
                "hora": now.strftime("%H:%M"),
                "user_id": member.id,
                "username": str(member)
            })
            await interaction.response.send_message("✅ Te has afiliado al Gremio de La Nueva Metropol S.A.", ephemeral=True)

    # ================= ON_READY (EMBED ACTUALIZADO) =================
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.CANAL_ANUNCIOS_ID)
        if not channel or not self.db: return

        config_ref = self.db.collection("Configuracion").document("gremio_msg")
        if config_ref.get().exists: return

        hora_arg = datetime.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).strftime("%H:%M")

        embed = discord.Embed(
            title="⚖️ CUERPO GREMIAL | LA NUEVA METROPOL S.A.",
            description=(
                "Este es el espacio de **unidad y defensa** de los conductores. El gremio no es un canal de soporte, "
                "es la herramienta colectiva para garantizar el respeto a nuestros derechos laborales.\n\n"
                
                "### ✊ ¿POR QUÉ AFILIARSE?\n"
                "* **🛡️ Defensa ante Sanciones:** Representación y mediación frente a medidas disciplinarias injustas o arbitrarias.\n"
                "* **📢 Voz en la Empresa:** Elevamos reclamos colectivos sobre condiciones de trabajo y normativas internas.\n"
                "* **⚖️ Justicia Laboral:** Velamos por un entorno de trabajo digno, respetando descansos y asignaciones equitativas.\n"
                "* **🤝 Unidad de Conductores:** Organización de asambleas y deliberación sobre el futuro de nuestra labor.\n\n"
                
                "### 🏛️ AUTORIDADES\n"
                f"• **Delegados / Directivos:** <@&{self.ROL_DIRECTIVOS_ID}>\n"
                f"• **Personal Afiliado:** <@&{self.ROL_GREMIO_ID}>\n\n"
                
                "### ⚠️ ACLARACIÓN IMPORTANTE\n"
                "Para problemas técnicos con el juego, reportes de lag o auxilio mecánico en ruta, "
                "dirigirse a los canales de **Soporte o Ticket**. Este canal es **exclusivamente gremial**.\n\n"
                
                "--- \n"
                "**¿Deseás afiliarte?** Al unirte, aceptás participar activamente en la defensa del cuerpo de conductores."
            ),
            color=0x1F8B4C
        )
        embed.set_footer(text=f"Unidad y Lucha | La Nueva Metropol S.A. | {hora_arg}")

        try:
            file = discord.File(self.BANNER_PATH, filename="BannerGremio.png")
            embed.set_image(url="attachment://BannerGremio.png")
            msg = await channel.send(embed=embed, view=self.GremioView(self), file=file)
            config_ref.set({"message_id": msg.id})
        except Exception as e:
            print(f"Error Gremio: {e}")

async def setup(bot):
    await bot.add_cog(GremioEmbed(bot))
