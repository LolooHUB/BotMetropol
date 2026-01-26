import discord
from discord.ext import commands
import asyncio
import time

class ReglasAutomatizacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.RULES_CHANNEL_ID = 1390152260578967556

        # Roles
        self.AUTO_ROLE_ID = 1465472198759284868
        self.BLOXLINK_ROLE_ID = 1465474060313165995
        self.REGLAS_ROLE_IDS = [
            1465472529974952281,
            1390152252143964262
        ]

        self.EMOJI = "✅"

    # ─────────────────────────────────────────────
    # DB HELPERS
    # ─────────────────────────────────────────────
    def now(self):
        return {
            "fecha": time.strftime("%Y-%m-%d"),
            "hora": time.strftime("%H:%M:%S")
        }

    def db_set(self, collection, data):
        if not hasattr(self.bot, "db") or self.bot.db is None:
            return
        try:
            self.bot.db.collection(collection).document(str(data["user_id"])).set(data)
        except Exception as e:
            print(f"❌ Error DB: {e}")

    # ─────────────────────────────────────────────
    # 1️⃣ ROL AUTOMÁTICO AL ENTRAR
    # ─────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        role = member.guild.get_role(self.AUTO_ROLE_ID)
        if role:
            try:
                await member.add_roles(role, reason="Ingreso al servidor")
            except Exception as e:
                print(f"❌ Error rol automático: {e}")

        self.db_set("NoVerificados", {
            "user_id": member.id,
            "username": member.name,
            "motivo": "Ingreso al servidor",
            **self.now()
        })

    # ─────────────────────────────────────────────
    # 2️⃣ REGLAS + EMBEDS (NO SE BORRA NADA)
    # ─────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.RULES_CHANNEL_ID)
        if not channel:
            print("❌ Canal de reglas no encontrado")
            return

        try:
            mensajes_viejos = []
            async for msg in channel.history(limit=30, oldest_first=True):
                if msg.author == self.bot.user and msg.embeds:
                    mensajes_viejos.append(msg)

            # ================= E1 =================
            e1 = discord.Embed(title="🚌 NORMATIVA GENERAL - LA NUEVA METROPOL S.A.", color=0x0055AA)
            e1.add_field(name="G1 - Respeto General", value="Prohibido el bardo e insultos. La toxicidad se corta de raíz.", inline=False)
            e1.add_field(name="G2 - Escritura y Claridad", value="Mínimo de ortografía. Si no se entiende, el mensaje será borrado.", inline=False)
            e1.add_field(name="G3 - Multicuentas", value="Prohibido el uso de Alts. Solo una cuenta por persona física.", inline=False)
            e1.add_field(name="G4 - Contenido Prohibido", value="No se permite contenido NSFW, Gore o violencia gráfica en ningún canal.", inline=False)
            e1.add_field(name="G5 - Spam", value="Prohibido el spam de otros servidores o publicidad no autorizada.", inline=False)
            e1.set_footer(text="⚖️ Sanción: 1 Warn por infracción.")

            # ================= E2 =================
            e2 = discord.Embed(title="⚠️ SECCIÓN CRÍTICA: FILTRADORES Y ANSIEDAD", color=0xCC0000)
            e2.add_field(name="A1 - Ansiedad", value="No presiones a creadores por skins o mods.", inline=False)
            e2.add_field(name="A2 - Filtradores", value="Robar o publicar modelos privados sin permiso = Expulsión directa.", inline=False)
            e2.add_field(name="A3 - Mensajes Privados", value="No satures los MD de los desarrolladores.", inline=False)
            e2.add_field(name="A4 - Difamación", value="Cualquier intento de dañar la imagen será sancionado.", inline=False)
            e2.add_field(name="A5 - Comercio", value="Prohibida la venta de archivos ajenos.", inline=False)
            e2.set_footer(text="⚖️ Sanción: PBAN o Warn.")

            # ================= E3 =================
            e3 = discord.Embed(title="🎮 J - REGLAS DE JUEGO / SERVICIOS", color=0x2ECC71)
            e3.add_field(name="J1 - Prioridad de Servicio", value="Nuestras unidades tienen prioridad en recorrido.", inline=False)
            e3.add_field(name="J2 - Interferencia Externa", value="No interfieras con maniobras.", inline=False)
            e3.add_field(name="J3 - Obstrucción", value="Prohibido bloquear accesos.", inline=False)
            e3.add_field(name="J4 - Lag", value="Lag que afecte el servicio será sancionado.", inline=False)
            e3.add_field(name="J5 - Comportamiento", value="Actitudes antideportivas serán reportadas.", inline=False)
            e3.set_footer(text="⚖️ Sanción: Kick o Warn.")

            # ================= E4 =================
            e4 = discord.Embed(title="📋 P - REGLAS PARA EL PERSONAL", color=0xF1C40F)
            e4.add_field(name="P1 - Cuidado", value="Mantené tu unidad en buen estado.", inline=False)
            e4.add_field(name="P2 - Unidades", value="No uses internos ajenos.", inline=False)
            e4.add_field(name="P3 - Armados", value="No pidas armados fuera de lista.", inline=False)
            e4.add_field(name="P4 - Planillas", value="Registros obligatorios.", inline=False)
            e4.add_field(name="P5 - Rol", value="Respeto y profesionalismo.", inline=False)
            e4.set_footer(text="⚖️ Sanción: Warn o Expulsión.")

            # ================= E5 (BANNER) =================
            file_banner = discord.File("Imgs/Banner.png", filename="Banner.png")
            e5 = discord.Embed(title="🛡️ S - STAFF Y DERECHO A APELACIÓN", color=0x95A5A6)
            e5.add_field(name="S1 - Integridad", value="Prohibido el abuso de poder.", inline=False)
            e5.add_field(name="S2 - Apelación", value="Plantealo en <#1464064701410447411>.", inline=False)
            e5.add_field(name="S3 - Privacidad", value="Tickets confidenciales.", inline=False)
            e5.add_field(name="S4 - Jerarquía", value="Escalá con un superior.", inline=False)
            e5.add_field(name="S5 - Soporte", value="Abrí ticket si necesitás ayuda.", inline=False)
            e5.set_image(url="attachment://Banner.png")
            e5.set_footer(text="✅ Reaccioná para ingresar | Sanción Staff: PBAN, Kick o Warn.")

            # ================= E6 (NUEVO) =================
            file_banner = discord.File("Imgs/Banner.png", filename="Banner.png")
            e6 = discord.Embed(
                title="✅ VERIFICACIÓN DE INGRESO",
                description=(
                    "Para acceder al servidor:\n\n"
                    "1️⃣ Leé todas las reglas\n"
                    "2️⃣ Verificate con **Bloxlink**\n"
                    "3️⃣ Reaccioná con ✅\n\n"
                    "⚠️ Sin Bloxlink no podés ingresar."
                ),
                color=0x2ECC71
            )
            e6.set_footer(text="Sistema automático de verificación")
            e6.set_image(url="attachment://Banner.png")

            embeds = [e1, e2, e3, e4, e5, e6]

            for i, embed in enumerate(embeds):
                if i < len(mensajes_viejos):
                    if i == 4:
                        await mensajes_viejos[i].edit(embed=embed, attachments=[file_banner])
                    else:
                        await mensajes_viejos[i].edit(embed=embed)
                else:
                    if i == 4:
                        msg = await channel.send(file=file_banner, embed=embed)
                        await msg.add_reaction(self.EMOJI)
                    elif i == 5:
                        msg = await channel.send(embed=embed)
                        await msg.add_reaction(self.EMOJI)
                    else:
                        await channel.send(embed=embed)

                await asyncio.sleep(0.4)

            print("✅ Reglas + verificación sincronizadas")

        except Exception as e:
            print(f"❌ Error ReglasAutomatizacion: {e}")

    # ─────────────────────────────────────────────
    # 3️⃣ VERIFICACIÓN POR REACCIÓN
    # ─────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) != self.EMOJI:
            return
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if not member:
            return

        if guild.get_role(self.BLOXLINK_ROLE_ID) not in member.roles:
            self.db_set("NoVerificados", {
                "user_id": member.id,
                "username": member.name,
                "motivo": "Intentó verificar sin Bloxlink",
                **self.now()
            })
            return

        auto_role = guild.get_role(self.AUTO_ROLE_ID)
        if auto_role in member.roles:
            await member.remove_roles(auto_role)

        roles = [guild.get_role(r) for r in self.REGLAS_ROLE_IDS if guild.get_role(r)]
        await member.add_roles(*roles, reason="Aceptó reglas")

        self.db_set("Verificados", {
            "user_id": member.id,
            "username": member.name,
            "estado": "verificado",
            **self.now()
        })

async def setup(bot):
    await bot.add_cog(ReglasAutomatizacion(bot))
