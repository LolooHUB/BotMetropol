import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
import asyncio

# --- CONFIGURACIÓN HORA ARGENTINA ---
tz_arg = timezone(timedelta(hours=-3))

class ActivityCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]
        self.log_channel_id = 1390152261937922070
        self.check_loop.start() # Iniciar el rastreador automático

    def cog_unload(self):
        self.check_loop.cancel()

    @commands.command(name="ac")
    async def activity_check(self, ctx):
        # 1. Verificar Permisos (Roles de Admin)
        if not any(role.id in self.admin_roles for role in ctx.author.roles):
            return await ctx.send("❌ No tienes permisos para iniciar un Activity Check.", delete_after=5)

        # 2. Formato del Mensaje
        embed_content = (
            "## :white_check_mark: Activity Check\n\n"
            ":point_right: Con el fin de mantener una comunidad mas activa, se realiza cada tanto un **ACTIVITY CHECK**.\n\n"
            "`¿En que consiste?` \n"
            "El equipo de moderacion, con fines de revisar que usuarios permanecen activos, realizaran **cada un tiempo indeterminado** estas revisiones.\n\n"
            "*Aquellos usuarios que no reaccionen pasados los 3 dias, podran sufrir las siguientes consecuencias :*\n"
            "> Se agregara a una lista de Inactivos, compartida con otros servidores.\n"
            "> `Sanciones:` Warn / Kick\n\n"
            "`¿Dudas? :` #〔❓〕preguntas o #〔📨〕ᴛɪᴄᴋᴇᴛꜱ\n\n"
            "**Reacciona con \"✅\" para indicar que estás activo.**\n"
            "|| Ping : @everyone ||"
        )

        msg = await ctx.send(embed_content)
        await msg.add_reaction("✅")

        # 3. Guardar en Firebase (usando la DB de tu cliente)
        db = self.bot.db
        if db:
            try:
                fecha_limite = datetime.now(tz_arg) + timedelta(days=3)
                db.collection("ActivityChecks").document(str(msg.id)).set({
                    "guild_id": ctx.guild.id,
                    "channel_id": ctx.channel.id,
                    "creado_el": datetime.now(tz_arg).strftime("%d/%m/%Y %H:%M:%S"),
                    "expira_el": fecha_limite.isoformat(),
                    "procesado": False
                })
            except Exception as e:
                print(f"Error Firebase AC: {e}")

    @tasks.loop(hours=1)
    async def check_loop(self):
        db = self.bot.db
        if not db: return

        # Buscar checks no procesados
        docs = db.collection("ActivityChecks").where("procesado", "==", False).stream()
        ahora = datetime.now(tz_arg)

        for doc in docs:
            data = doc.to_dict()
            expira_el = datetime.fromisoformat(data['expira_el'])

            if ahora >= expira_el:
                await self.procesar_inactivos(doc.id, data)

    async def procesar_inactivos(self, msg_id, data):
        guild = self.bot.get_guild(data['guild_id'])
        channel = guild.get_channel(data['channel_id'])
        log_channel = guild.get_channel(self.log_channel_id)

        try:
            message = await channel.fetch_message(int(msg_id))
            reaction = discord.utils.get(message.reactions, emoji="✅")
            
            reaccionaron = []
            if reaction:
                async for user in reaction.users():
                    reaccionaron.append(user.id)

            inactivos = []
            for member in guild.members:
                if not member.bot and member.id not in reaccionaron:
                    inactivos.append(f"• {member.name} ({member.id})")

            # Enviar el reporte al canal de logs
            header = f"📋 **REPORTE DE INACTIVIDAD**\nID Mensaje: `{msg_id}`\n"
            if inactivos:
                lista_str = "\n".join(inactivos)
                if len(lista_str) > 1800:
                    # Si es muy larga, enviar archivo
                    with open("inactivos.txt", "w", encoding="utf-8") as f:
                        f.write(lista_str)
                    await log_channel.send(content=header, file=discord.File("inactivos.txt"))
                else:
                    await log_channel.send(f"{header}```\n{lista_str}\n```")
            else:
                await log_channel.send(f"{header} No se encontraron usuarios inactivos.")

            # Marcar como procesado
            self.bot.db.collection("ActivityChecks").document(msg_id).update({"procesado": True})

        except Exception as e:
            print(f"Error al procesar AC {msg_id}: {e}")

async def setup(bot):
    await bot.add_cog(ActivityCheck(bot))
