import discord
from discord.ext import commands
import datetime
from zoneinfo import ZoneInfo
import asyncio

class GremioEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.CANAL_ANUNCIOS_ID = 1465462294824882258
        self.ROL_GREMIO_ID = 1445835728285208769
        self.ROL_DIRECTIVOS_ID = 1397020690435149824
        self.BANNER_PATH = "Imgs/BannerGremio.png"
        
        self.bot.add_view(self.GremioView(self))

    # ================= VIEW & MODAL (IGUALES) =================
    class MotivoSalidaModal(discord.ui.Modal, title="Declaración de Baja Gremial"):
        motivo = discord.ui.TextInput(label="Motivo", style=discord.TextStyle.paragraph, required=True)
        def __init__(self, cog, member): super().__init__(); self.cog = cog; self.member = member
        async def on_submit(self, interaction: discord.Interaction):
            now = datetime.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
            role = interaction.guild.get_role(self.cog.ROL_GREMIO_ID)
            if role in self.member.roles: await self.member.remove_roles(role)
            self.cog.db.collection("SalidasGremio").add({
                "user_id": self.member.id, "username": str(self.member),
                "fecha": now.strftime("%d/%m/%Y"), "hora": now.strftime("%H:%M"), "motivo": self.motivo.value
            })
            self.cog.db.collection("MiembrosGremio").document(str(self.member.id)).delete()
            await interaction.response.send_message("🚪 Baja procesada.", ephemeral=True)

    class GremioView(discord.ui.View):
        def __init__(self, cog): super().__init__(timeout=None); self.cog = cog
        @discord.ui.button(label="Gestionar Afiliación", style=discord.ButtonStyle.success, custom_id="btn_gremio_v4")
        async def toggle(self, interaction: discord.Interaction, button: discord.ui.Button):
            role = interaction.guild.get_role(self.cog.ROL_GREMIO_ID)
            if role in interaction.user.roles:
                await interaction.response.send_modal(self.cog.MotivoSalidaModal(self.cog, interaction.user))
            else:
                now = datetime.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
                await interaction.user.add_roles(role)
                self.cog.db.collection("MiembrosGremio").document(str(interaction.user.id)).set({
                    "fecha": now.strftime("%d/%m/%Y"), "hora": now.strftime("%H:%M"),
                    "user_id": interaction.user.id, "username": str(interaction.user)
                })
                await interaction.response.send_message("✅ Afiliado correctamente.", ephemeral=True)

    # ================= ON_READY (LOGICA DE ENVÍO FORZADO) =================
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.CANAL_ANUNCIOS_ID)
        if not channel: return

        print("🚌 Sincronizando mensaje de Gremio...")
        hora_arg = datetime.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).strftime("%H:%M")

        embed = discord.Embed(
            title="⚖️ CUERPO GREMIAL | LA NUEVA METROPOL S.A.",
            description=(
                "Este es el espacio de **unidad y defensa** de los conductores.\n\n"
                "### ✊ ¿POR QUÉ AFILIARSE?\n"
                "* **🛡️ Defensa ante Sanciones:** Mediación frente a medidas disciplinarias injustas.\n"
                "* **📢 Voz en la Empresa:** Reclamos colectivos sobre condiciones de trabajo.\n"
                "* **⚖️ Justicia Laboral:** Velamos por descansos y asignaciones equitativas.\n"
                "* **🤝 Unidad:** Organización de asambleas para el futuro de nuestra labor.\n\n"
                "### 🏛️ AUTORIDADES\n"
                f"• **Delegados:** <@&{self.ROL_DIRECTIVOS_ID}>\n"
                f"• **Afiliados:** <@&{self.ROL_GREMIO_ID}>\n\n"
                "### ⚠️ ACLARACIÓN\n"
                "Temas técnicos o auxilio mecánico van por **Soporte**. Esto es **exclusivamente gremial**."
            ),
            color=0x1F8B4C
        )
        embed.set_footer(text=f"Unidad y Lucha | La Nueva Metropol S.A. | {hora_arg}")

        try:
            file = discord.File(self.BANNER_PATH, filename="BannerGremio.png")
            embed.set_image(url="attachment://BannerGremio.png")

            # BUSCAR SI YA EXISTE EL MENSAJE EN FIRESTORE
            config_ref = self.db.collection("Configuracion").document("gremio_msg")
            doc = config_ref.get()

            if doc.exists:
                msg_id = doc.to_dict().get("message_id")
                try:
                    old_msg = await channel.fetch_message(msg_id)
                    await old_msg.edit(embed=embed, view=self.GremioView(self), attachments=[file])
                    print("✅ Mensaje de Gremio EDITADO correctamente.")
                    return
                except:
                    print("⚠️ El mensaje guardado no existe en Discord. Enviando uno nuevo...")

            # SI NO EXISTE O FALLÓ LA EDICIÓN, ENVIAR NUEVO
            msg = await channel.send(embed=embed, view=self.GremioView(self), file=file)
            config_ref.set({"message_id": msg.id})
            print("✅ Mensaje de Gremio ENVIADO correctamente.")

        except Exception as e:
            print(f"❌ Error Gremio: {e}")

async def setup(bot):
    await bot.add_cog(GremioEmbed(bot))
