import discord
from discord.ext import commands
import os

class ReglasAutomatizacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RULES_CHANNEL_ID = 1390152260578967556  # ID Directo del canal

    @commands.Cog.listener()
    async def on_ready(self):
        # Obtenemos el canal directamente por su ID
        channel = self.bot.get_channel(self.RULES_CHANNEL_ID)

        if channel:
            try:
                # --- LÓGICA DE LIMPIEZA SELECTIVA ---
                everyone_encontrado = False
                mensajes_a_borrar = []

                # Escaneamos los mensajes del bot en ese canal específico
                async for message in channel.history(limit=50):
                    if message.author == self.bot.user:
                        # Si detectamos que ya existe un @everyone, lo dejamos quieto
                        if "@everyone" in message.content:
                            everyone_encontrado = True
                        else:
                            # Los embeds anteriores se marcan para borrar
                            mensajes_a_borrar.append(message)

                # Borramos los mensajes viejos (excluyendo el everyone)
                if mensajes_a_borrar:
                    try:
                        await channel.delete_messages(mensajes_a_borrar)
                        print(f"🧹 Mensajes antiguos eliminados en {channel.name}")
                    except Exception:
                        # Si los mensajes son muy viejos para delete_messages, borramos de a uno
                        for m in mensajes_a_borrar:
                            await m.delete()

                # Si no existe el everyone (primera vez), lo enviamos
                if not everyone_encontrado:
                    await channel.send("@everyone")
                    print("📢 Primera mención @everyone enviada.")

                # --- PREPARACIÓN DE ARCHIVOS ---
                file_logo = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
                file_banner = discord.File("Imgs/Banner.png", filename="Banner.png")

                # --- EMBEDS DE LA NORMATIVA ---
                
                # Embed 1: General
                e1 = discord.Embed(
                    title="🚌 NORMATIVA GENERAL - LA NUEVA METROPOL S.A.",
                    description="Respeto y conducta obligatoria dentro de la comunidad.",
                    color=0x0055AA
                )
                e1.set_author(name="Control de Personal", icon_url="attachment://LogoPFP.png")
                e1.add_field(name="G1 - Respeto General", value="Prohibido el bardo e insultos. La toxicidad se corta de raíz.", inline=False)
                e1.add_field(name="G2 - Escritura", value="Mínimo de ortografía. Si no se entiende lo que escribís, el mensaje será borrado.", inline=True)
                e1.add_field(name="G3 - Multicuentas", value="Prohibido el uso de Alts. Una cuenta por persona.", inline=True)

                # Embed 2: Conducta Crítica
                e2 = discord.Embed(
                    title="⚠️ SECCIÓN CRÍTICA: FILTRADORES Y ANSIEDAD",
                    color=0xCC0000
                )
                e2.add_field(name="A1 - TOLERANCIA CERO A LA ANSIEDAD", value="Si venís a apurar a creadores por skins o mods, o molestás de forma pesada por privado, vas baneado inmediatamente.", inline=False)
                e2.add_field(name="A2 - FILTRADORES", value="Robar contenido o publicar modelos privados sin permiso te convierte en **filtrador**. Expulsión directa.", inline=False)

                # Embed 3: Simulación
                e3 = discord.Embed(
                    title="🎮 J - REGLAS DE JUEGO / MAPAS",
                    color=0x2ECC71
                )
                e3.add_field(name="J1 - Conducción", value="No choques ni interrumpas el recorrido de otros de forma intencional.", inline=False)
                e3.add_field(name="J2 - Zonas Restringidas", value="Respetá los depósitos y cabinas. No entres si no tenés el rol de personal.", inline=False)

                # Embed 4: Staff y Apelación
                e4 = discord.Embed(
                    title="🛡️ S - STAFF Y DERECHO A APELACIÓN",
                    description="Todo reclamo se canaliza con respeto.",
                    color=0x95A5A6
                )
                e4.add_field(name="S1 - Cuestionamiento", value="Las decisiones del Staff pueden ser cuestionadas. Si no estás de acuerdo, plantealo educadamente.", inline=False)
                e4.add_field(name="S2 - Verificación", value="Tenés 7 días para verificar tu cuenta o serás expulsado por seguridad.", inline=False)
                e4.set_image(url="attachment://Banner.png")
                e4.set_footer(text="Reaccioná con ✅ para aceptar e ingresar.")

                # --- ENVÍO ---
                await channel.send(file=file_logo, embed=e1)
                await channel.send(embed=e2)
                await channel.send(embed=e3)
                last_msg = await channel.send(file=file_banner, embed=e4)
                
                await last_msg.add_reaction("✅")
                print("🚀 Reglamento actualizado en el canal ID: 1390152260578967556")

            except Exception as e:
                print(f"❌ Error en la automatización de reglas: {e}")
        else:
            print(f"⚠️ No se pudo acceder al canal con ID: {self.RULES_CHANNEL_ID}")

async def setup(bot):
    await bot.add_cog(ReglasAutomatizacion(bot))
