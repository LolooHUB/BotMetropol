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
            return

        try:
            # --- 1. OBTENER MENSAJES PREVIOS DEL BOT ---
            mensajes_viejos = []
            async for message in channel.history(limit=20, oldest_first=True):
                if message.author == self.bot.user and message.embeds:
                    mensajes_viejos.append(message)
                elif message.author == self.bot.user and "@everyone" in message.content:
                    # Guardamos el mensaje de everyone si existe
                    pass 

            # --- 2. DEFINICIÓN DE LOS 5 EMBEDS ---
            # Preparamos los datos para iterar y editar/enviar
            
            # Embed 1: General
            e1 = discord.Embed(title="🚌 NORMATIVA GENERAL - LA NUEVA METROPOL S.A.", color=0x0055AA)
            e1.add_field(name="G1 - Respeto General", value="Prohibido el bardo e insultos. La toxicidad se corta de raíz.", inline=False)
            e1.add_field(name="G2 - Escritura y Claridad", value="Mínimo de ortografía. Si no se entiende, se borra.", inline=False)
            e1.add_field(name="G3 - Multicuentas", value="Prohibido el uso de Alts. Una cuenta por persona.", inline=False)
            e1.add_field(name="G4 - Contenido Prohibido", value="No NSFW, Gore o violencia gráfica.", inline=False)
            e1.add_field(name="G5 - Spam", value="Prohibido el spam de otros servidores.", inline=False)

            # Embed 2: Crítica
            e2 = discord.Embed(title="⚠️ SECCIÓN CRÍTICA: FILTRADORES Y ANSIEDAD", color=0xCC0000)
            e2.add_field(name="A1 - Ansiedad", value="No presiones a creadores. El contenido sale cuando está listo.", inline=False)
            e2.add_field(name="A2 - Filtradores", value="Robar modelos privados = Expulsión directa.", inline=False)
            e2.add_field(name="A3 - Mensajes Privados", value="No satures los MD de los desarrolladores.", inline=False)
            e2.add_field(name="A4 - Difamación", value="No dañar la imagen de la empresa.", inline=False)
            e2.add_field(name="A5 - Comercio", value="Prohibida la venta de archivos ajenos.", inline=False)

            # Embed 3: Juego
            e3 = discord.Embed(title="🎮 J - REGLAS DE JUEGO / MAPAS", color=0x2ECC71)
            e3.add_field(name="J1 - Conducción", value="No choques ni interrumpas a otros adrede.", inline=False)
            e3.add_field(name="J2 - Zonas", value="Respetá depósitos y cabinas personalizadas.", inline=False)
            e3.add_field(name="J3 - Unidades", value="Utilizá las unidades de tu rango.", inline=False)
            e3.add_field(name="J4 - Sincro", value="Si tenés lag excesivo, retirá la unidad.", inline=False)
            e3.add_field(name="J5 - Trampas", value="Hacks o glitches prohibidos.", inline=False)

            # Embed 4: Personal
            e4 = discord.Embed(title="📋 P - REGLAS PARA EL PERSONAL", color=0xF1C40F)
            e4.add_field(name="P1 - Cuidado", value="Mantené tu unidad en buen estado.", inline=False)
            e4.add_field(name="P2 - Unidades", value="No uses internos ajenos.", inline=False)
            e4.add_field(name="P3 - Armados", value="No modifiques skins sin permiso.", inline=False)
            e4.add_field(name="P4 - Planillas", value="Registros reales y puntuales obligatorios.", inline=False)
            e4.add_field(name="P5 - Rol", value="Mantené la simulación profesional.", inline=False)

            # Embed 5: Staff (El que tiene la reacción)
            e5 = discord.Embed(title="🛡️ S - STAFF Y DERECHO A APELACIÓN", color=0x95A5A6)
            e5.add_field(name="S1 - Integridad", value="Prohibido el abuso de poder.", inline=False)
            e5.add_field(name="S2 - Apelación", value="Plantealo educadamente en <#1464064701410447411>.", inline=False)
            e5.add_field(name="S3 - Privacidad", value="Tickets 100% confidenciales.", inline=False)
            e5.add_field(name="S4 - Jerarquía", value="Problemas con Staff se escalan con Superiores.", inline=False)
            e5.add_field(name="S5 - Soporte", value="Tickets en: <#1390152260578967559>.", inline=False)
            e5.set_footer(text="Reaccioná con ✅ para aceptar e ingresar.")

            lista_embeds = [e1, e2, e3, e4, e5]

            # --- 3. LÓGICA DE ACTUALIZACIÓN (EDITAR O ENVIAR) ---
            for i in range(len(lista_embeds)):
                if i < len(mensajes_viejos):
                    # Si el mensaje existe, lo editamos (MANTIENE REACCIONES)
                    await mensajes_viejos[i].edit(embed=lista_embeds[i])
                else:
                    # Si no existe, lo enviamos de cero
                    msg = await channel.send(embed=lista_embeds[i])
                    if i == 4: # Si es el último, agregamos la reacción
                        await msg.add_reaction("✅")
                
                await asyncio.sleep(0.5)

            print("✅ Reglamento sincronizado (editado si ya existía).")

        except Exception as e:
            print(f"❌ Error: {e}")

async def setup(bot):
    await bot.add_cog(ReglasAutomatizacion(bot))
