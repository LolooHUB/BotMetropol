import discord
from discord.ext import commands
import asyncio

class ReglasAutomatizacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RULES_CHANNEL_ID = 1390152260578967556
        self.BANNER_PATH = "Imgs/Banner.png"

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.RULES_CHANNEL_ID)
        if not channel:
            print(f"❌ No se encontró el canal de reglas (ID: {self.RULES_CHANNEL_ID})")
            return

        try:
            # --- 1. OBTENER MENSAJES PREVIOS DEL BOT PARA EDITAR ---
            mensajes_viejos = []
            async for message in channel.history(limit=10, oldest_first=True):
                if message.author == self.bot.user:
                    mensajes_viejos.append(message)

            # --- 2. DEFINICIÓN DE LOS EMBEDS CON FORMATO AVANZADO ---

            # Embed 1: Normativa General
            e1 = discord.Embed(title="✨ __NORMATIVA GENERAL - LA NUEVA METROPOL S.A.__", color=0x0055AA)
            e1.description = "Constitución de convivencia básica para todos los integrantes del servidor."
            e1.add_field(name="` G1 ` ➤ **RESPETO GENERAL**", value="__Prohibido__ el bardo e insultos. La toxicidad se corta de raíz para mantener un ambiente profesional.", inline=False)
            e1.add_field(name="` G2 ` ➤ **ESCRITURA Y CLARIDAD**", value="Mínimo de ortografía requerido. Si un mensaje es __ilegible__, será borrado sin previo aviso.", inline=False)
            e1.add_field(name="` G3 ` ➤ **MULTICUENTAS (ALTS)**", value="**Estrictamente prohibido.** Solo se permite **una cuenta** por persona física.", inline=False)
            e1.add_field(name="` G4 ` ➤ **CONTENIDO RESTRINGIDO**", value="No se permite contenido **NSFW, Gore o violencia gráfica**. Mantengamos el servidor apto para todo público.", inline=False)
            e1.add_field(name="` G5 ` ➤ **POLÍTICA DE SPAM**", value="Prohibida la publicidad no autorizada o invitaciones a otros servidores vía canales o MD.", inline=False)
            e1.set_footer(text="⚖️ Sanción: 1 Warn por infracción.")

            # Embed 2: Sección Crítica
            e2 = discord.Embed(title="⚠️ __SECCIÓN CRÍTICA: TOLERANCIA CERO__", color=0xCC0000)
            e2.description = "**Estas infracciones son consideradas faltas graves contra el desarrollo y la empresa.**"
            e2.add_field(name="` A1 ` ➤ **CONTROL DE ANSIEDAD**", value="No presiones a los desarrolladores por *skins* o *mods*. El contenido sale cuando cumple los **estándares de calidad**.", inline=False)
            e2.add_field(name="` A2 ` ➤ **FILTRADORES (LEAKERS)**", value="Robar o publicar modelos privados sin permiso = **__EXPULSIÓN DIRECTA E IRREVOCABLE__**.", inline=False)
            e2.add_field(name="` A3 ` ➤ **HOSTIGAMIENTO POR MD**", value="No satures los mensajes privados del Staff. Para soporte, utilizá los canales oficiales.", inline=False)
            e2.add_field(name="` A4 ` ➤ **DIFAMACIÓN E IMAGEN**", value="Cualquier intento de dañar deliberadamente la imagen de la empresa será sancionado.", inline=False)
            e2.add_field(name="` A5 ` ➤ **COMERCIO ILEGAL**", value="Prohibida la venta de archivos o modelos que no sean de tu autoría.", inline=False)
            e2.add_field(name="` A6 ` ➤ **POLÉMICAS Y RUMORES**", value="Generar acusaciones sin pruebas o afirmar que la empresa filtra contenido será **__PENALIZADO__**.", inline=False)
            e2.set_footer(text="⚖️ Sanción: PBAN o Warn, dependiendo de la gravedad.")

            # Embed 3: Reglas de Juego
            e3 = discord.Embed(title="🎮 __J - REGLAS DE JUEGO / SERVICIOS__", color=0x2ECC71)
            e3.add_field(name="` J1 ` ➤ **PRIORIDAD DE PASO**", value="Nuestras unidades tienen **prioridad absoluta** en el recorrido. No obstruyas su paso.", inline=False)
            e3.add_field(name="` J2 ` ➤ **INTERFERENCIA EXTERNA**", value="Usuarios ajenos no deben interferir con nuestras maniobras o paradas en la simulación.", inline=False)
            e3.add_field(name="` J3 ` ➤ **OBSTRUCCIÓN DE SALIDAS**", value="Prohibido bloquear accesos o salidas de depósitos exclusivos de la Metropol.", inline=False)
            e3.add_field(name="` J4 ` ➤ **ESTABILIDAD (LAG)**", value="Si tu lag afecta el desempeño de los servicios, se te solicitará retirar la unidad.", inline=False)
            e3.set_footer(text="⚖️ Sanción: Kick o Warn.")

            # Embed 4: Reglas para el Personal
            e4 = discord.Embed(title="📋 __P - REGLAS PARA EL PERSONAL__", color=0xF1C40F)
            e4.add_field(name="` P1 ` ➤ **CUIDADO DE UNIDAD**", value="Mantené tu unidad asignada en buen estado; evitá maniobras bruscas o daños innecesarios.", inline=False)
            e4.add_field(name="` P2 ` ➤ **ASIGNACIÓN DE INTERNOS**", value="No utilices coches ajenos o que no correspondan a tu rango sin permiso previo.", inline=False)
            e4.add_field(name="` P3 ` ➤ **PEDIDOS DE ARMADOS**", value="No insistas por armados fuera de la lista oficial de la empresa.", inline=False)
            e4.add_field(name="` P4 ` ➤ **REGISTRO DE PLANILLAS**", value="Los datos de recorrido deben ser **reales, precisos y puntuales**. El fraude es motivo de baja.", inline=False)
            e4.set_footer(text="⚖️ Sanción: Warn o Expulsión de la empresa.")

            # Embed 5: Staff y Soporte (Con Banner)
            e5 = discord.Embed(title="🛡️ __S - STAFF Y DERECHO A APELACIÓN__", color=0x95A5A6)
            e5.add_field(name="` S1 ` ➤ **INTEGRIDAD**", value="Prohibido el abuso de poder. El Staff actúa con total imparcialidad.", inline=False)
            e5.add_field(name="` S2 ` ➤ **APELACIONES**", value="Si consideras una sanción injusta, plantealo con respeto en <#1464064701410447411>.", inline=False)
            e5.add_field(name="` S3 ` ➤ **CONFIDENCIALIDAD**", value="Los tickets son 100% privados. No se permite divulgar información de soporte.", inline=False)
            e5.add_field(name="` S4 ` ➤ **SOPORTE TÉCNICO**", value="Para reportes o ayuda, abrí un ticket en: <#1390152260578967559>.", inline=False)
            
            # Preparar imagen para el último embed
            file_banner = discord.File(self.BANNER_PATH, filename="Banner.png")
            e5.set_image(url="attachment://Banner.png")
            e5.set_footer(text="✅ Reaccioná para ingresar | La Nueva Metropol S.A.")

            lista_embeds = [e1, e2, e3, e4, e5]

            # --- 3. LÓGICA DE ACTUALIZACIÓN / SINCRONIZACIÓN ---
            for i in range(len(lista_embeds)):
                if i < len(mensajes_viejos):
                    # EDITAR EXISTENTE
                    if i == 4: # El último lleva el banner
                        await mensajes_viejos[i].edit(embed=lista_embeds[i], attachments=[file_banner])
                    else:
                        await mensajes_viejos[i].edit(embed=lista_embeds[i])
                else:
                    # ENVIAR NUEVO
                    if i == 4:
                        msg = await channel.send(file=file_banner, embed=lista_embeds[i])
                        await msg.add_reaction("✅")
                    else:
                        await channel.send(embed=lista_embeds[i])
                
                await asyncio.sleep(0.8) # Pausa para evitar Rate Limit de Discord

            print("✅ Reglamento de La Nueva Metropol S.A. sincronizado y formateado.")

        except Exception as e:
            print(f"❌ Error en ReglasAutomatizacion: {e}")

async def setup(bot):
    await bot.add_cog(ReglasAutomatizacion(bot))
