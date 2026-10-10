
import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


class TicketButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Abrir ticket",
        emoji="🎫",
        style=discord.ButtonStyle.primary,
        custom_id="relgold:open_ticket"
    )
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild is None:
            return

        existing = discord.utils.get(
            guild.text_channels,
            topic=f"ticket_owner:{interaction.user.id}"
        )
        if existing:
            await interaction.response.send_message(
                f"Tu já tens um ticket aberto: {existing.mention}",
                ephemeral=True
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )
        }

        category = discord.utils.get(guild.categories, name="Tickets")
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}".lower()[:90],
            category=category,
            overwrites=overwrites,
            topic=f"ticket_owner:{interaction.user.id}"
        )

        await channel.send(
            f"{interaction.user.mention}, conta-nos como podemos ajudar.",
            view=CloseTicket()
        )
        await interaction.response.send_message(
            f"Teu ticket foi criado: {channel.mention}",
            ephemeral=True
        )


class CloseTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Fechar ticket",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="relgold:close_ticket"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.channel or not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message(
                "Este botão só pode ser usado dentro de um ticket.",
                ephemeral=True
            )
            return

        await interaction.response.send_message("Ticket fechado. O canal será removido em breve.")
        await interaction.channel.delete(reason=f"Ticket fechado por {interaction.user}")


@bot.event
async def on_ready():
    bot.add_view(TicketButtons())
    bot.add_view(CloseTicket())
    print(f"RelGold Bot online: {bot.user}")


@bot.command()
@commands.has_permissions(administrator=True)
async def painel(ctx):
    await ctx.send(
        "**RelGold | Atendimento**\nClica abaixo para abrir um atendimento privado.",
        view=TicketButtons()
    )


@bot.command()
@commands.has_permissions(administrator=True)
async def configurar(ctx):
    category = discord.utils.get(ctx.guild.categories, name="Tickets")
    if category is None:
        await ctx.guild.create_category("Tickets")
    await ctx.send("Categoria de tickets configurada.")


bot.run(TOKEN)
      
