import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class DesvioModal(discord.ui.Modal, title='Informe Desvío'):
    lugar = discord.ui.TextInput(label='Lugar', placeholder='Ej: Av. General Paz y Constituyentes')
    descripcion = discord.ui.TextInput(label='Describí lo sucedido', style=discord.TextStyle.paragraph)

    def __init__(self, tipo_alerta):
        super().__init__()
        self.tipo_alerta = tipo_alerta

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🚨 Informe Alertas", color=discord.Color.yellow())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Informante", value=interaction.user.mention)
        embed.add_field(name="Tipo de Alerta", value=self.tipo_alerta)
        embed.add_field(name="Descripción", value=self.descripcion.value)
        embed.add_field(name="Lugar", value=self.lugar.value)
        embed.set_footer(text=f"La Nueva Metropol S.A. | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        canal_cortes = interaction.guild.get_channel(1392951234796978298)
        file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        await canal_cortes.send(file=file, embed=embed)
        await interaction.response.send_message("Informe enviado correctamente.", ephemeral=True)

class Desvio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_permitidos = [1390152252169125992, 1390152252143964267, 1390152252143964266]

    @app_commands.command(name="desvio", description="Reportar un desvío o corte")
    @app_commands.choices(tipo=[
        app_commands.Choice(name="Desvio", value="Desvio"),
        app_commands.Choice(name="Corte de Calle", value="Corte de Calle"),
        app_commands.Choice(name="Otro", value="Otro")
    ])
    async def desvio(self, interaction: discord.Interaction, tipo: app_commands.Choice[str]):
        if not any(r.id in self.roles_permitidos for r in interaction.user.roles):
            return await interaction.response.send_message("No tienes permiso para reportar alertas.", ephemeral=True)
        
        await interaction.response.send_modal(DesvioModal(tipo.value))

async def setup(bot):
    await bot.add_cog(Desvio(bot))
