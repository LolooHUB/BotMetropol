import discord
from discord.ext import commands
import datetime
from zoneinfo import ZoneInfo
import asyncio

class GremioEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db  # Firestore inicializada en main.py
        
        # --- CONFIGURACIÓN DE IDs ---
        self.CANAL_ANUNCIOS_ID = 1465462294824882258
        self.CANAL_COMUNICACION_ID = 1464064701410447411
        self.ROL_DIRECTIVOS_ID = 1397020690435149824
        self.ROL_GREMIO_ID = 1445835728285208769
        self.BANNER_PATH = "Imgs/BannerGremio.png"

        # Registro de la View para que los botones funcionen siempre
        self.bot.add_view(self.GremioView(self))

    # =================================================_
    # MODAL DE SALIDA (SE DISPARA SI YA TIENE EL ROL)
    # =================================================_
    class MotivoSalidaModal(discord.ui.Modal, title="Declaración de Salida Gremial"):
        motivo = discord.ui.TextInput(
            label="Motivo de la baja",
            style=discord.TextStyle.paragraph,
            placeholder="Por favor, indicá el motivo de tu salida (ej: retiro, cambio de empresa, etc.)",
            required=True,
            max_length=400
        )

        def __init__(self, cog, member):
            super().__init__()
            self.cog = cog
            self.member = member

        async def on_submit(self, interaction: discord.Interaction):
            role = interaction.guild.get_role(self.cog.ROL_GREMIO_ID)
            now = datetime.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
            fecha_str = now.strftime("%d/%m/%Y")
            hora_str = now.strftime("%H:%M")

            # 1. Quitar el rol en Discord
            if role in self.member.roles:
                await self.member.remove_roles(role)

            # 2. Registrar la salida en Firestore
            self.cog.db.collection("SalidasGremio").add({
                "user_id": self.member.id,
                "username": str(self.member),
                "fecha": fecha_str,
                "hora": hora_str,
                "motivo": self.motivo.value
            })

            # 3. Eliminar de la lista de miembros activos
            self.cog.db.collection("MiembrosGremio").document(str(self.member.id)).delete()

            await interaction.response.send_message(
                f"🚪 **Baja procesada.** Hemos registrado tu salida del gremio el día {fecha_str} a las {hora_str}.",
                ephemeral=True
            )

    # =================================================_
    # VIEW CON BOTÓN INTERACTIVO (TOGGLE)
    # =================================================_
    class GremioView(discord.ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog

        @discord.ui.button(
            label="Gestionar Afiliación (Unirme/Salir)",
            style=discord.ButtonStyle.success,
            custom_id="btn_gremio_metropol_v2"
        )
        async def toggle_gremio(self, interaction: discord.Interaction, button: discord.ui.Button):
            member = interaction.user
            role = interaction.guild.get_role(self.cog.ROL_GREMIO_ID)
            now = datetime.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))

            # SI YA ES MIEMBRO -> ABRIR MODAL
            if role in member.roles:
                await interaction.response.send_modal(self.cog.MotivoSalidaModal(self.cog, member))
                return

            # SI NO ES MIEMBRO -> DAR ALTA
            await member.add_roles(role)
            
            # Formato de datos coincidente con tus registros actuales
            data = {
                "fecha": now.strftime("%d/%m/%Y"),
                "hora": now.strftime("%H:%M"),
                "user_id": member.id,
                "username": str(member)
            }
            
            self.cog.db.collection("MiembrosGremio").document(str(member.id)).set(data)

            await interaction.response.send_message(
                "✅ **Afiliación Exitosa.** Bienvenido al Gremio de La Nueva Metropol S.A. Se te han otorgado los permisos correspondientes.",
                ephemeral=True
            )

    # =================================================_
    # EVENTO READY: ENVÍO DEL EMBED INSTITUCIONAL
    # =================================================_
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(3) # Delay para asegurar carga de caché

        channel = self.bot.get_channel(self.CANAL_ANUNCIOS_ID)
        if not channel or not self.db:
            return

        # Verificar si el mensaje ya existe en Firestore para evitar spam
        config_ref = self.db.collection("Configuracion").document("gremio_msg")
        if config_ref.get().exists:
            return

        now = datetime.datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
        hora_arg = now.strftime("%H:%M")

        # --- CONSTRUCCIÓN DEL EMBED EXTENDIDO ---
        embed = discord.Embed(
            title="🚌 GREMIO DE COLECTIVEROS | LA NUEVA METROPOL S.A.",
            description=(
                "Bienvenido al espacio de representación oficial de los conductores. "
                "Este gremio ha sido constituido bajo los principios de **unidad, respeto y profesionalismo**.\n\n"
                
                "### 📑 NUESTRA MISIÓN\n"
                "Garantizar que cada jornada en ruta se desarrolle en un entorno justo, seguro y coordinado, "
                "profesionalizando nuestro servicio a través de la unión colectiva.\n\n"
                
                "### 🛠️ BENEFICIOS Y ASISTENCIA\n"
                "* **🛡️ Defensa Laboral:** Representación activa ante sanciones o conflictos operativos.\n"
                "* **🔧 Estado de Flota:** Canal directo para reportar fallas mecánicas o necesidades de mantenimiento.\n"
                "* **🆘 Apoyo en Ruta:** Red de contacto inmediata para asistencia ante incidentes viales o emergencias.\n\n"
                
                "### 🏛️ ESTRUCTURA ORGÁNICA\n"
                f"• **Cuerpo Directivo:** <@&{self.ROL_DIRECTIVOS_ID}>\n"
                f"• **Personal Afiliado:** <@&{self.ROL_GREMIO_ID}>\n\n"
                
                "### 📜 COMPROMISO DEL AFILIADO\n"
                "1. Mantener un comportamiento ejemplar con los colegas.\n"
                "2. Respetar las jerarquías y los reglamentos internos.\n"
                "3. Colaborar activamente en la mejora del servicio común.\n\n"
                
                "### 💬 CANALES OFICIALES\n"
                f"Consultas y reportes: <#{self.CANAL_COMUNICACION_ID}>\n\n"
                "--- \n"
                "**¿Deseás afiliarte o gestionar tu baja?**\n"
                "Utilizá el botón interactivo de abajo. Para bajas, el sistema solicitará una declaración de motivos."
            ),
            color=0x1F8B4C
        )
        embed.set_footer(text=f"Asuntos Gremiales | La Nueva Metropol S.A. | {hora_arg}")

        try:
            file = discord.File(self.BANNER_PATH, filename="BannerGremio.png")
            embed.set_image(url="attachment://BannerGremio.png")
            
            msg = await channel.send(embed=embed, view=self.GremioView(self), file=file)
            
            # Registrar éxito en Firestore
            config_ref.set({
                "message_id": msg.id,
                "channel_id": channel.id,
                "ultima_actualizacion": now.strftime("%d/%m/%Y %H:%M")
            })
            print("✅ Mensaje institucional del Gremio publicado con éxito.")
        except Exception as e:
            print(f"❌ Error al publicar Gremio: {e}")

async def setup(bot):
    await bot.add_cog(GremioEmbed(bot))
