import discord
from discord.ext import commands
import os
import asyncio

class ReglasAutomatizacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RULES_CHANNEL_ID = 1390152260578967556

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.RULES_CHANNEL_ID)

        if channel:
            try:
                # --- LIMPIEZA ---
                everyone_encontrado = False
                mensajes_a_borrar = []

                async for message in channel.history(limit=50):
                    if message.author == self.bot.user:
                        if "@everyone" in message.content:
                            everyone_encontrado = True
                        else:
                            mensajes_a_borrar.append(message)

                if mensajes_a_borrar:
                    for m in mensajes_a_borrar:
                        await m.delete()
                        await asyncio.sleep(0.5) # Pausa para evitar Rate Limit

                if not everyone_encontrado:
                    await channel.send("@everyone")

                # --- ENVÍO DE EMBEDS UNO POR UNO ---
                
                # 1. Embed Inicial con Logo
                file_logo1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
                e1 = discord.Embed(
                    title="🚌 NORMATIVA GENERAL - LA NUEVA METROPOL S.A.",
                    description="Respeto y conducta obligatoria dentro de la comunidad.",
                    color=0x0055AA
                )
                e1.set_author(name="Control de Personal", icon_url="attachment://LogoPFP.png")
                e1.add_field(name="G1 - Respeto General", value="Prohibido el bardo e insultos. La toxicidad se corta de raíz.", inline=False)
                e1.add_field(name="G2 - Escritura", value="Mínimo de ortografía. Si no se entiende lo que escribís, el mensaje será borrado.", inline=True)
                e1.add_field(name="G3 - Multicuentas", value="Prohibido el uso de Alts. Una cuenta por persona.", inline=True)
                await channel.send(file=file_logo1, embed=e1)

                # 2. Embed Crítico
                e2 = discord.Embed(
                    title="⚠️ SECCIÓN CRÍTICA: FILTRADORES Y ANSIEDAD",
                    color=0xCC0000
                )
                e2.add_field(name="A1 - TOLERANCIA CERO A LA ANSIEDAD", value="Si venís a apurar a creadores por skins o mods, o molestás de forma pesada por privado, vas baneado inmediatamente.", inline=False)
                e2.add_field(name="A2 - FILTRADORES", value="Robar contenido o publicar modelos privados sin permiso te convierte en **filtrador**. Expulsión directa.", inline=False)
                await channel.send(embed=e2)

                # 3. Embed Simulación
                e3 = discord.Embed(
                    title="🎮 J - REGLAS DE JUEGO / MAPAS",
                    color=0x2ECC71
                )
                e3.add_field(name="J1 - Conducción", value="No choques ni interrumpas el recorrido de otros de forma intencional.", inline=False)
                e3.add_field(name="J2 - Zonas Restringidas", value="Respetá los depósitos y cabinas. No entres si no tenés el rol de personal.", inline=False)
                await channel.send(embed=e3)

                # 4. Embed Final con Banner
                file_banner = discord.File("Imgs/Banner.png", filename="Banner.png")
                e4 = discord.Embed(
                    title="🛡️ S - STAFF Y DERECHO A APELACIÓN",
                    description="Todo reclamo se canaliza con respeto.",
                    color=0x95A5A6
                )
                e4.add_field(name="S1 - Cuestionamiento", value="Las decisiones del Staff pueden ser cuestionadas. Si no estás de acuerdo, plantealo educadamente.", inline=False)
                e4.add_field(name="S2 - Verificación", value="Tenés 7 días para verificar tu cuenta o serás expulsado por seguridad.", inline=False)
                e4.set_image(url="attachment://Banner.png")
                e4.set_footer(text="Reaccioná con ✅ para aceptar e ingresar.")
                
                last_msg = await channel.send(file=file_banner, embed=e4)
                await last_msg.add_reaction("✅")

                print("🚀 Reglamento completo enviado correctamente.")

            except Exception as e:
                print(f"❌ Error enviando el reglamento: {e}")

async def setup(bot):
    await bot.add_cog(ReglasAutomatizacion(bot))
