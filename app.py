import logging
import os, io, base64

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

        embed = discord.Embed(title='Minecraft', description=os.getenv('SERVER_IP'), type='rich')
        embed.set_thumbnail(url='attachment://server.png')
        embed.add_field(name='Status:  :green_circle:', value='')
        embed.add_field(name=f'Players:  {status.players.online}', value='')
        embed.add_field(name='Players Online: ', value=query.players.names, inline=False)
        embed.color = discord.Color.from_str('#5b8731')

        await interaction.response.send_message(file=get_server_icon(status), embed=embed)
    except ConnectionRefusedError:
        await interaction.response.send_message('MCServer is down!')


def get_server_icon(status):
    icon = status.icon.split(',')[1]
    file = discord.File(io.BytesIO(base64.b64decode(icon)), filename='server.png')
    return file


if __name__ == '__main__':
    handler = logging.FileHandler(filename='logs/debug.log', encoding='utf-8', mode='w')
    client.run(os.getenv('BOT_TOKEN'), log_handler=handler, log_level=logging.DEBUG)
