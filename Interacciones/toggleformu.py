import discord
from discord.ext import commands
from datetime import datetime

class ToggleFormu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Roles Administrativos: Director Metropol y Direccion Personal
        self.admin_roles = [1390152252169125992, 1445570965852520650]
        self.formu_status = False # Falso por defecto (Cerrado)

    @commands.command(name="ToggleFormularios")
    async def toggle_formu(self, ctx):
        # Verificar permisos
        if not any(role.id in self.admin_roles for role in ctx.author.roles):
            return await ctx.send("No tienes rango administrativo para usar esto.", delete_after=5)

        # Cambiar estado
        self.formu_status = not self.formu_status
        canal_formus = ctx.guild.get_channel(1390152260578967558)
        file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")

        if self.formu_status:
            # Embed ABIERTO
            embed = discord.Embed(
                title="FORMULARIO INGRESO LA NUEVA METROPOL S.A.",
                description=(
                    "**Estado del Formulario :** ABIERTO ✅\n\n"
                    "**Requisitos :**\n"
                    "> Tener 13 Años.\n"
                    "> Tener mínima experiencia previa.\n"
                    "> Estar dispuesto a hacer 3 planillas por semana.\n\n"
                    "**Link :** https://forms.gle/C88AeE5g1eBHJZL68"
                ),
                color=65290
            )
            msg_confirmacion = "Formulario ABIERTO CORRECTAMENTE"
        else:
            # Embed CERRADO
            embed = discord.Embed(
                title="FORMULARIO INGRESO LA NUEVA METROPOL S.A.",
                description=(
                    "**Estado del Formulario :** CERRADO ❌\n"
                    "¡Pero ya podés ir preparándote para cuando abramos!\n \n"
                    "**Requisitos:**\n"
                    "> Tener 13 Años.\n"
                    "> Tener mínima experiencia previa.\n"
                    "> Estar dispuesto a hacer 3 planillas por semana.\n\n"
                    "Sugerencia : Leer acerca de señaleticas y practicar manejo."
                ),
                color=16711680
            )
            msg_confirmacion = "Formulario CERRADO CORRECTAMENTE"

        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        
        # Enviar al canal de formularios
        await canal_formus.send(file=file, embed=embed)
        
        # Confirmación al admin (simulando ephemeral con delete_after)
        await ctx.send(f"✅ {msg_confirmacion}", delete_after=10)

async def setup(bot):
    await bot.add_cog(ToggleFormu(bot))
