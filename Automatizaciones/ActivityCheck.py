import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone

# --- CONFIGURACIÓN HORA ARGENTINA ---
tz_arg = timezone(timedelta(hours=-3))

class ActivityCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]
        self.log_channel_id = 1390152261937922070
        self.preguntas_id = 1390152261367369788
        self.tickets_id = 1390152260578967559
        self.check_loop.start()

    def cog_unload(self):
        self.check_loop.cancel()

    @commands.command(name="ac")
    async def activity_check(self, ctx):
        # 1. Validación de Roles
        if not any(role.id in self.admin_roles for role in ctx.author.roles):
            return await ctx.send("❌ No tienes permisos para iniciar un Activity Check.", delete_after=5)

        # 2. Mensaje con formato solicitado
        message_content = (
            "## :white_check_mark: Activity Check\n\n"
            ":point_right: Con el fin de mantener una comunidad mas activa, se realiza cada tanto un **ACTIVITY CHECK**.\n\n"
            "`¿En que consiste?` \n"
            "El equipo de moderacion, con fines de revisar que usuarios permanecen activos, que cuentas quedan inactivas y etc, realizaran **cada un tiempo indeterminado** estas revisiones.\n\n"
            "*Aquellos usuarios que no reaccionen pasados los 3 dias, podran sufrir las siguientes consecuencias :*\n"
            "> Se agregara a una lista de Inactivos, compartida con otros servidores (Afecta reputacion en general).\n"
            "> `Podra sufrir sanciones como :` \n"
            "> Warn \n"
            "> Kick \n\n"
            f"`¿Y donde mando mis dudas? :` \n"
            f"Las podes mandar en <#{self.preguntas_id}> (Si no son relevantes al staff.)\n"
            f"O en caso que pueda implicar moderacion : <#{self.tickets_id}>\n\n"
            "`Reacciona con \"`*:white_check_mark:*`\" para indicar que leiste este mensaje y que te encontras activo.`\n"
            "|| Ping : @everyone ||"
        )

        msg = await ctx.send(content=message_content)
        await msg.add_reaction("✅")

        # 3. Guardado en Firebase (Usa la instancia de tu cliente)
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

            inactivos = [f"• {m.name} ({m.id})" for m in guild.members if not m.bot and m.id not in reaccionaron]

            # Envío de reporte
            header = f"📋 **REPORTE DE INACTIVIDAD FINALIZADO**\nID Mensaje: `{msg_id}`\n"
            if inactivos:
                lista_str = "\n".join(inactivos)
                if len(lista_str) > 1800:
                    with open("inactivos.txt", "w", encoding="utf-8") as f: f.write(lista_str)
                    await log_channel.send(content=header, file=discord.File("inactivos.txt"))
                else:
                    await log_channel.send(f"{header}```\n{lista_str}\n```")
            else:
                await log_channel.send(f"{header} No hubo usuarios inactivos.")

            self.bot.db.collection("ActivityChecks").document(msg_id).update({"procesado": True})

        except Exception as e:
            print(f"Error procesando AC {msg_id}: {e}")

async def setup(bot):
    await bot.add_cog(ActivityCheck(bot))
