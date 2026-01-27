import discord
from discord.ext import commands
import asyncio
import datetime
import pytz
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

class ReglasAutomatizacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # ───────── CONFIGURACIÓN ─────────
        self.RULES_CHANNEL_ID = 1390152260578967556
        self.BLOXLINK_CHANNEL_ID = 1465472097949192315

        self.AUTO_ROLE_ID = 1465472198759284868  # Rol al ingresar
        self.UNVERIFIED_ROLE_ID = 1465472529974952281  # No verificado
        self.BLOXLINK_ROLE_ID = 1465474060313165995
        self.REGLAS_ROLE_IDS = [
            1465472529974952281,
            1390152252143964262
        ]

        self.EMOJI = "✅"
        self.reglas_message_id = None

        # ───────── FIREBASE ─────────
        self.db = None
        firebase_config = os.getenv("FIREBASE_CONFIG")
        if firebase_config:
            try:
                cred_dict = json.loads(firebase_config)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                print("Firebase conectado correctamente.")
            except Exception as e:
                print(f"Error al conectar Firebase: {e}")

    # ───────── ROL AUTOMÁTICO AL ENTRAR ─────────
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        auto_role = member.guild.get_role(self.AUTO_ROLE_ID)
        unverified_role = member.guild.get_role(self.UNVERIFIED_ROLE_ID)
        if auto_role and unverified_role:
            try:
                await member.add_roles(auto_role, reason="Ingreso al servidor")
                await member.add_roles(unverified_role, reason="Rol de acceso restringido")

                # Limitar visibilidad de canales
                for ch in member.guild.channels:
                    if ch.id not in [self.RULES_CHANNEL_ID, self.BLOXLINK_CHANNEL_ID]:
                        await ch.set_permissions(unverified_role, view_channel=False)

                # Registrar en DB
                if self.db:
                    doc_ref = self.db.collection("UsuariosVerificados").document(str(member.id))
                    doc_ref.set({
                        "username": str(member),
                        "status": "No Verificado",
                        "fecha": datetime.datetime.now(pytz.timezone("America/Argentina/Buenos_Aires"))
                    })
            except Exception as e:
                print(f"Error al asignar roles a {member}: {e}")

    # ───────── EMBEDS DE REGLAS ─────────
    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.RULES_CHANNEL_ID)
        if not channel:
            print("Canal de reglas no encontrado")
            return

        try:
            mensajes_viejos = []
            async for msg in channel.history(limit=30, oldest_first=True):
                if msg.author == self.bot.user and msg.embeds:
                    mensajes_viejos.append(msg)

            now_arg = datetime.datetime.now(pytz.timezone("America/Argentina/Buenos_Aires"))
            fecha_footer = now_arg.strftime("%d/%m/%Y %H:%M")

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
            e2.add_field(name="A1 - Ansiedad", value="No presiones a creadores por skins o mods. El contenido sale cuando está listo.", inline=False)
            e2.add_field(name="A2 - Filtradores", value="Robar o publicar modelos privados sin permiso = Expulsión directa.", inline=False)
            e2.add_field(name="A3 - Mensajes Privados", value="No satures los MD de los desarrolladores por soporte o primicias.", inline=False)
            e2.add_field(name="A4 - Difamación", value="Cualquier intento de dañar la imagen de la empresa será sancionado.", inline=False)
            e2.add_field(name="A5 - Comercio", value="Prohibida la venta de archivos o modelos que no sean de tu autoría.", inline=False)
            e2.add_field(name="A6 - Controversias", value="Cualquier tipo de polémica generada, acusación infundada o afirmar que alguien filtró contenido a la empresa será penalizado y desmentido.", inline=False)
            e2.set_footer(text="⚖️ Sanción: PBAN o Warn, dependiendo de la gravedad.")

            # ================= E3 =================
            e3 = discord.Embed(title="🎮 J - REGLAS DE JUEGO / SERVICIOS", color=0x2ECC71)
            e3.add_field(name="J1 - Prioridad de Servicio", value="Nuestras unidades tienen prioridad en recorrido. No obstruyas su paso.", inline=False)
            e3.add_field(name="J2 - Interferencia Externa", value="Usuarios de depósito free no deben interferir con nuestras maniobras o paradas.", inline=False)
            e3.add_field(name="J3 - Obstrucción de Salidas", value="Prohibido bloquear accesos o salidas de depósitos exclusivos de la Metropol.", inline=False)
            e3.add_field(name="J4 - Sincronización (Lag)", value="Si tu lag afecta el desempeño de nuestros servicios, deberás retirar la unidad.", inline=False)
            e3.add_field(name="J5 - Comportamiento", value="Actitudes antideportivas que afecten la simulación serán reportadas.", inline=False)
            e3.set_footer(text="⚖️ Sanción: Kick o Warn.")

            # ================= E4 =================
            e4 = discord.Embed(title="📋 P - REGLAS PARA EL PERSONAL", color=0xF1C40F)
            e4.add_field(name="P1 - Cuidado", value="Mantené tu unidad asignada en buen estado; evitá maniobras bruscas.", inline=False)
            e4.add_field(name="P2 - Unidades", value="No utilices internos ajenos o que no correspondan a tu rango sin permiso.", inline=False)
            e4.add_field(name="P3 - Armados", value="No pidas ni insistas por armados fuera de la lista oficial de la empresa.", inline=False)
            e4.add_field(name="P4 - Planillas", value="Registros de recorrido obligatorios, con datos reales y puntuales.", inline=False)
            e4.add_field(name="P5 - Rol", value="Mantené la simulación profesional y el respeto con tus compañeros.", inline=False)
            e4.set_footer(text="⚖️ Sanción: Warn o Expulsión (requiere rehacer formulario).")

            # ================= E5 =================
            e5 = discord.Embed(title="🛡️ S - STAFF Y DERECHO A APELACIÓN", color=0x95A5A6)
            e5.add_field(name="S1 - Integridad", value="Prohibido el abuso de poder. El Staff actúa con total imparcialidad.", inline=False)
            e5.add_field(name="S2 - Apelación", value="Plantealo educadamente en <#1464064701410447411>.", inline=False)
            e5.add_field(name="S3 - Privacidad", value="Los tickets son 100% confidenciales. No se divulga información.", inline=False)
            e5.add_field(name="S4 - Jerarquía", value="Ante problemas con un Staff, escalalo con un Superior vía ticket.", inline=False)
            e5.add_field(name="S5 - Soporte", value="Para reportes o ayuda, abrí un ticket en: <#1390152260578967559>.", inline=False)
            e5.set_footer(text="⚖️ Sanciones posibles: PBAN, Kick o Warn")

            # ================= E6 (VERIFICACIÓN) =================
            file_banner = discord.File("Imgs/Banner.png", filename="Banner.png")
            e6 = discord.Embed(
                title="Verificación de Ingreso",
                description=(
                    "Para ingresar al servidor se deben cumplir los siguientes pasos:\n\n"
                    "1. Leer todas las reglas anteriores.\n"
                    "2. Verificarse mediante Bloxlink (Roblox).\n"
                    "3. Reaccionar a este mensaje para confirmar la verificación.\n\n"
                    "Si el usuario no tiene Roblox verificado, no se otorgarán permisos adicionales."
                ),
                color=0x2ECC71
            )
            e6.set_footer(text=f"Sistema automático de verificación | {datetime.datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime('%d/%m/%Y %H:%M')}")
            e6.set_image(url="attachment://Banner.png")

            # ───────── ENVIAR O EDITAR MENSAJES ─────────
            embeds = [e1, e2, e3, e4, e5, e6]
            for i, embed in enumerate(embeds):
                if i < len(mensajes_viejos):
                    if i == 5:
                        await mensajes_viejos[i].edit(embed=embed, attachments=[file_banner])
                        self.reglas_message_id = mensajes_viejos[i].id
                    else:
                        await mensajes_viejos[i].edit(embed=embed)
                else:
                    if i == 5:
                        msg = await channel.send(file=file_banner, embed=embed)
                        await msg.add_reaction(self.EMOJI)
                        self.reglas_message_id = msg.id
                    else:
                        await channel.send(embed=embed)
                await asyncio.sleep(0.4)

            print("Reglas y verificación sincronizadas correctamente.")

        except Exception as e:
            print(f"Error ReglasAutomatizacion: {e}")

    # ───────── VERIFICACIÓN POR REACCIÓN ─────────
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) != self.EMOJI or payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if not member:
            return

        # Validar mensaje de verificación
        if self.reglas_message_id is None:
            channel = guild.get_channel(self.RULES_CHANNEL_ID)
            async for msg in channel.history(limit=20, oldest_first=False):
                if msg.author == self.bot.user and "Verificación de Ingreso" in msg.embeds[0].title:
                    self.reglas_message_id = msg.id
                    break

        if payload.message_id != self.reglas_message_id:
            return

        # Verificar que tenga Roblox
        blox_role = guild.get_role(self.BLOXLINK_ROLE_ID)
        if blox_role not in member.roles:
            return

        # Quitar rol No Verificado
        unverified_role = guild.get_role(self.UNVERIFIED_ROLE_ID)
        if unverified_role in member.roles:
            await member.remove_roles(unverified_role)

        # Dar roles de reglas
        reglas_roles = [guild.get_role(r) for r in self.REGLAS_ROLE_IDS]
        await member.add_roles(*reglas_roles, reason="Aceptó reglas y verificó Roblox")

        # Actualizar DB
        if self.db:
            doc_ref = self.db.collection("UsuariosVerificados").document(str(member.id))
            doc_ref.set({
                "username": str(member),
                "status": "Verificado",
                "fecha": datetime.datetime.now(pytz.timezone("America/Argentina/Buenos_Aires"))
            })

        # Restaurar permisos de canales
        for ch in guild.channels:
            if unverified_role in ch.overwrites:
                await ch.set_permissions(unverified_role, view_channel=None)

async def setup(bot):
    await bot.add_cog(ReglasAutomatizacion(bot))
