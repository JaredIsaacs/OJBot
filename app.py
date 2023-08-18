import logging
import os
import io
import base64

import discord

from mcstatus import JavaServer 
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)


    async def setup_hook(self) -> None:
        GUILD_ID = discord.Object(os.getenv('GUILD_ID'))
        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync(guild=GUILD_ID)


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'App running. Logged on as {client.user.id}')


@client.event
async def on_guild_join(guild: discord.guild.Guild):
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)


@client.tree.command()
async def mcserver(interaction: discord.Interaction):
    try:
        server = JavaServer.lookup(os.getenv('SERVER_IP'))
        status = server.status()
        query = server.query()

        embed = mc_embed(status, query)

        await interaction.response.send_message(embed=embed)
    except ConnectionRefusedError:
        embed = mc_embed(online=False)
        await interaction.response.send_message(embed=embed)


def mc_embed(status=None, query=None, online: bool = True) -> discord.Embed:
    embed = discord.Embed(title='Minecraft', description=f'IP: {os.getenv("SERVER_IP")}', type='rich', color=discord.Color.from_str('#5b8731'))
    embed.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Userbox_creeper.svg/2048px-Userbox_creeper.svg.png')

    if online:
        embed.add_field(name='Status:  :green_circle:', value='')
        embed.add_field(name=f'Players:  {status.players.online}', value='')
    else:
        embed.add_field(name='Status:  :red_circle:', value='')
        embed.add_field(name='Players:  N/A', value='')

    if query is not None and query.players.names != []:
        embed.add_field(name='Players Online: ', value=query.players.names, inline=False)

    return embed


if __name__ == '__main__':
    handler = logging.FileHandler(filename='logs/debug.log', encoding='utf-8', mode='w')
    client.run(os.getenv('BOT_TOKEN'), log_handler=handler, log_level=logging.DEBUG)
