import discord
from discord.ext import commands
import asyncio

class ReglasAutomatizacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RULES_CHANNEL_ID = 1390152260578967556

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.RULES_CHANNEL_ID)
        if not channel:
            print(f"❌ No se encontró el canal con ID {self.RULES_CHANNEL_ID}")
            return

        try:
            # --- 1. OBTENER MENSAJES PREVIOS DEL BOT PARA EDITAR ---
            mensajes_viejos = []
            async for message in channel.history(limit=20, oldest_first=True):
                if message.author == self.bot.user and message.embeds:
                    mensajes_viejos.append(message)

            # --- 2. DEFINICIÓN DE LOS EMBEDS ---

            # Embed 1: Normativa General
            e1 = discord.Embed(title="🚌 NORMATIVA GENERAL - LA NUEVA METROPOL S.A.", color=0x0055AA)
            e1.add_field(name="G1 - Respeto General", value="Prohibido el bardo e insultos. La toxicidad se corta de raíz.", inline=False)
            e1.add_field(name="G2 - Escritura y Claridad", value="Mínimo de ortografía. Si no se entiende, el mensaje será borrado.", inline=False)
            e1.add_field(name="G3 - Multicuentas", value="Prohibido el uso de Alts. Solo una cuenta por persona física.", inline=False)
            e1.add_field(name="G4 - Contenido Prohibido", value="No se permite contenido NSFW, Gore o violencia gráfica en ningún canal.", inline=False)
            e1.add_field(name="G5 - Spam", value="Prohibido el spam de otros servidores o publicidad no autorizada.", inline=False)
            e1.set_footer(text="⚖️ Sanción: 1 Warn por infracción.")

            # Embed 2: Sección Crítica
            e2 = discord.Embed(title="⚠️ SECCIÓN CRÍTICA:", color=0xCC0000)
            e2.add_field(name="A1 - Ansiedad", value="No presiones a creadores por skins o mods. El contenido sale cuando está listo.", inline=False)
            e2.add_field(name="A2 - Filtradores", value="Robar o publicar modelos privados sin permiso = Expulsión directa.", inline=False)
            e2.add_field(name="A3 - Mensajes Privados", value="No satures los MD de los desarrolladores por soporte o primicias.", inline=False)
            e2.add_field(name="A4 - Difamación", value="Cualquier intento de dañar la imagen de la empresa será sancionado.", inline=False)
            e2.add_field(name="A5 - Comercio", value="Prohibida la venta de archivos o modelos que no sean de tu autoría.", inline=False)
            e2.add_field(name="A6 - Polémicas y acusaciones", value="Cualquier tipo de polémica generada, acusaciones sin pruebas o afirmar que la empresa filtra contenido será PENALIZADO. Toda información falsa será DESMENTIDA oficialmente.", inline=False)
            e2.set_footer(text="⚖️ Sanción: PBAN o Warn, dependiendo de la gravedad.")

            # Embed 3: Reglas de Juego (Interferencia)
            e3 = discord.Embed(title="🎮 J - REGLAS DE JUEGO / SERVICIOS", color=0x2ECC71)
            e3.add_field(name="J1 - Prioridad de Servicio", value="Nuestras unidades tienen prioridad en recorrido. No obstruyas su paso.", inline=False)
            e3.add_field(name="J2 - Interferencia Externa", value="Usuarios de depósito free no deben interferir con nuestras maniobras o paradas.", inline=False)
            e3.add_field(name="J3 - Obstrucción de Salidas", value="Prohibido bloquear accesos o salidas de depósitos exclusivos de la Metropol.", inline=False)
            e3.add_field(name="J4 - Sincronización (Lag)", value="Si tu lag afecta el desempeño de nuestros servicios, deberás retirar la unidad.", inline=False)
            e3.add_field(name="J5 - Comportamiento", value="Actitudes antideportivas que afecten la simulación serán reportadas.", inline=False)
            e3.set_footer(text="⚖️ Sanción: Kick o Warn.")

            # Embed 4: Reglas para el Personal
            e4 = discord.Embed(title="📋 P - REGLAS PARA EL PERSONAL", color=0xF1C40F)
            e4.add_field(name="P1 - Cuidado", value="Mantené tu unidad asignada en buen estado; evitá maniobras bruscas.", inline=False)
            e4.add_field(name="P2 - Unidades", value="No utilices internos ajenos o que no correspondan a tu rango sin permiso.", inline=False)
            e4.add_field(name="P3 - Armados", value="No pidas ni insistas por armados fuera de la lista oficial de la empresa.", inline=False)
            e4.add_field(name="P4 - Planillas", value="Registros de recorrido obligatorios, con datos reales y puntuales.", inline=False)
            e4.add_field(name="P5 - Rol", value="Mantené la simulación profesional y el respeto con tus compañeros.", inline=False)
            e4.set_footer(text="⚖️ Sanción: Warn o Expulsión (requiere rehacer formulario).")

            # Embed 5: Staff y Apelación (Con Banner)
            file_banner = discord.File("Imgs/Banner.png", filename="Banner.png")
            e5 = discord.Embed(title="🛡️ S - STAFF Y DERECHO A APELACIÓN", color=0x95A5A6)
            e5.add_field(name="S1 - Integridad", value="Prohibido el abuso de poder. El Staff actúa con total imparcialidad.", inline=False)
            e5.add_field(name="S2 - Apelación", value="Plantealo educadamente en <#1464064701410447411>.", inline=False)
            e5.add_field(name="S3 - Privacidad", value="Los tickets son 100% confidenciales. No se divulga información.", inline=False)
            e5.add_field(name="S4 - Jerarquía", value="Ante problemas con un Staff, escalalo con un Superior vía ticket.", inline=False)
            e5.add_field(name="S5 - Soporte", value="Para reportes o ayuda, abrí un ticket en: <#1390152260578967559>.", inline=False)
            e5.set_image(url="attachment://Banner.png")
            e5.set_footer(text="✅ Reaccioná para ingresar | Sanción Staff: PBAN, Kick o Warn.")

            lista_embeds = [e1, e2, e3, e4, e5]

            # --- 3. LÓGICA DE ACTUALIZACIÓN ---
            for i in range(len(lista_embeds)):
                if i < len(mensajes_viejos):
                    # EDITAR MENSAJES EXISTENTES
                    if i == 4: # El último lleva el banner
                        await mensajes_viejos[i].edit(embed=lista_embeds[i], attachments=[file_banner])
                    else:
                        await mensajes_viejos[i].edit(embed=lista_embeds[i])
                else:
                    # ENVIAR MENSAJES NUEVOS
                    if i == 4:
                        msg = await channel.send(file=file_banner, embed=lista_embeds[i])
                        await msg.add_reaction("✅")
                    else:
                        await channel.send(embed=lista_embeds[i])
                
                await asyncio.sleep(0.5)

            print("✅ Reglamento de La Nueva Metropol S.A. sincronizado correctamente.")

        except Exception as e:
            print(f"❌ Error en ReglasAutomatizacion: {e}")

async def setup(bot):
    await bot.add_cog(ReglasAutomatizacion(bot))
