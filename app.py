import logging
import os
from typing import Optional
import uuid
import discord

from mcstatus import JavaServer 
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from mcconn import message_user, add_user_prefix
from mcdb import MinecraftDB
load_dotenv()


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)


    async def setup_hook(self) -> None:
        guild_id = discord.Object(os.getenv('GUILD_ID'))
        self.tree.copy_global_to(guild=guild_id)
        await self.tree.sync(guild=guild_id)


class ServerStartButton(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label='Button', style=discord.ButtonStyle.green)
    async def StartButton(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(f'Starting Minecraft Server @ {os.getenv("SERVER_IP")}')


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
MCDB = MinecraftDB()


@client.event
async def on_ready():
    print(f'App running. Logged on as {client.user.id}')
    MCDB.init_db()


@client.event
async def on_guild_join(guild: discord.guild.Guild):
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)


@client.event
async def on_message(message: discord.Message):
    rmsg = message.reference.cached_message
    if message.type != discord.MessageType.reply:
        return
    if rmsg.author == client.user.id:
        return
    
    user_key = message.content
    user_id = message.author.id

    await rmsg.delete()
    await message.delete()

    try:
        MCDB.link_account(user_key, user_id)
        mc_account = MCDB.get_mc_account(user_id)
        message_user(mc_account, f'Accounts, MC: "{mc_account}" and Discord: "{message.author.name}", have been linked!')
        await message.channel.send(f'Congratulations {message.author.mention}! Your accounts, MC: "{mc_account}" and Discord: "{message.author.name}", have been linked successfully.')
    except AssertionError:
        await message.channel.send(f'Sorry {message.author.mention}, but the key you\'e entered is incorrect. Please try again.')


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


@client.tree.command()
async def link(interaction: discord.Interaction, account_name: str):
    try:
        server = JavaServer.lookup(os.getenv('SERVER_IP'))
        query = server.query()
    
        if account_name not in query.players.names:
            await interaction.response.send_message(f'Sorry {interaction.user.mention}, we were unable to link your account!\nThe user {account_name} must be logged into the server in order to link accounts!')
            return
        
        key = MCDB.get_key(account_name)
        message_user(account_name, f'Your discord verification code is {key}.')

        await interaction.response.send_message(f'{interaction.user.mention}. A message has been sent to {account_name} with your verification key!\nRespond to this message with the key to complete linking accounts.')
    except AssertionError: # User does not exist.
        key = str(uuid.uuid4()).split('-', maxsplit=1)[0]
        MCDB.add_user(key, account_name)
        message_user(account_name, f'Your discord verification code is {key}.')

        await interaction.response.send_message(f'{interaction.user.mention}. A message has been to {account_name} with your verification key!\nRespond to this message with the key to complete linking accounts.')
    except ConnectionRefusedError:
        await interaction.response.send_message('The server must be up in order to link accounts!')


@client.tree.command()
async def mcprefix(interaction: discord.Interaction, prefix: str):
    try:
        mc_account = MCDB.get_mc_account(interaction.user.id)
        add_user_prefix(mc_account, prefix)
        await interaction.response.send_message(f'Minecraft user, {mc_account}, prefix has been changed to {prefix}.')
    except AssertionError:
        await interaction.response.send_message(f'Sorry {interaction.user.mention}, but you need to first link your minecraft and discord accounts in order to use this command.\nType /link to begin the linking process.')


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
