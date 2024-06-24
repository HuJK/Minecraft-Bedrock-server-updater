#!/usr/bin/python3
from bs4 import BeautifulSoup
import os
import sys
import time
import atexit
import shutil
import requests
import subprocess


serverFolder = 'downloadbedrock'
serverFolderExe = 'bedrock'

httpheaders = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}


difficulty = 'hard'
if len(sys.argv) >1:
    if sys.argv[1] == 'easy':
        difficulty = 'easy'
    elif sys.argv[1] == 'normal':
        difficulty = 'normal'
    elif sys.argv[1] == 'hard':
        difficulty = 'hard'
    elif sys.argv[1] == 'peaceful':
        difficulty = 'peaceful'

firstRun = False
def initialize():
    #Setup folders
    global firstRun
    if not os.path.isdir(serverFolder):
        print("First run. Creating serverFolder")
        os.makedirs(serverFolder)
        firstRun = True
    if not os.path.isdir(serverFolderExe):
        os.makedirs(serverFolderExe)
        firstRun = True
    #Check serverFolder has only 1 file
    if len(oslistdir(serverFolder)) > 1:
        raise AssertionError("This folder can only have 1 file:" + serverFolder)

def initializeiProperties():
    if(firstRun==True):
        setProperties("difficulty",difficulty)#I think in multiplayer mode, we can cooperate with each other, so difficulty=hard make this game more challenging.
        setProperties("max-players",str(20))  #Java edition default setting.
        setProperties("content-log-file-enabled","true") #Enable log
    
def getDWurl():
    #get minecraft bedrock server dounload URL
    MCurl = requests.get('https://www.minecraft.net/en-us/download/server/bedrock',headers=httpheaders).text
    MCSoup =  BeautifulSoup(MCurl, 'html.parser')
    for dwbtn in MCSoup.findAll("a",{"class":"btn btn-disabled-outline mt-4 downloadlink"}):
        if  dwbtn['data-platform'] == 'serverBedrockLinux':
            return dwbtn['href']


def oslistdir(path):
    return list(filter((lambda x:x[0] != "."),os.listdir(serverFolder)))


def setProperties(P,V):
    print("Set " + P + " to " + V)
    with open(serverFolderExe + "/server.properties") as spfp:
        sp = spfp.read()
    sp = sp.split("\n")
    for i,setting in enumerate(sp):
        if setting.startswith(P + "="):
            sp[i] = P + "=" + V
    with open(serverFolderExe + "/server.properties","w") as spfp:
        spfp.write("\n".join(sp))

        
def startServer():
    print("Starting server...")
    if not os.path.isfile(serverFolderExe + "/bedrock_server"):
        print("Server file not found, wait download.")
        for root, dirs, files in os.walk(serverFolder):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
    subprocess.call(["tmux", "new", "-d", "-s", "MC_BDRK" , "bash"] , cwd=serverFolderExe)
    time.sleep(1)
    subprocess.call(["tmux", "send-keys", "-t", "MC_BDRK","set +e", "Enter"])#don't bail out of bash script
    subprocess.call(["tmux", "send-keys", "-t", "MC_BDRK","while true; do ./bedrock_server; echo Server stopped. Restarting in 10 seconds...; sleep 10; done", "Enter"])

def stopServer():
    print("Stopping server...")
    subprocess.call(["tmux", "send-keys", "-t", "MC_BDRK","stop"])
    time.sleep(1)
    subprocess.call(["tmux", "send-keys", "-t", "MC_BDRK","Enter"])
    time.sleep(5)
    subprocess.call(["tmux", "send-keys", "-t", "MC_BDRK","C-c"])
    time.sleep(1)
    subprocess.call(["tmux", "kill-session", "-t", "MC_BDRK"])


atexit.register(stopServer)

initialize()
startServer()

while(True):
    try:
        dwurl = getDWurl()
        newVersion = dwurl.split("/")[-1]
        oldVersion = oslistdir(serverFolder)[0] if len(oslistdir(serverFolder)) != 0 else "(No old version found)"
        if oldVersion != newVersion:
            print("New Minecraft version found: " + newVersion)
            print("Start downloading: " + newVersion)
            myfile = requests.get(dwurl,headers=httpheaders)
            open(serverFolder + "/" + newVersion, 'wb').write(myfile.content)
            stopServer()
            if firstRun == False:
                print("Remove old version: " + oldVersion)
                try:
                    os.remove(serverFolder + "/" + oldVersion)
                except:
                    pass
                #Backup old server.properties to server.properties.bak
                print("Backing up server properties, whitelist and permissions")
                try:
                    shutil.move(serverFolderExe + "/server.properties", serverFolderExe + "/server.properties.bak")
                except FileNotFoundError as e:
                    print(e)
                try:
                    shutil.move(serverFolderExe + "/whitelist.json", serverFolderExe + "/whitelist.json.bak")
                except FileNotFoundError as e:
                    print(e)
                try:
                    shutil.move(serverFolderExe + "/permissions.json", serverFolderExe + "/permissions.json.bak")
                except FileNotFoundError as e:
                    print(e)
            print("Extracting new server from zip")
            subprocess.call(["unzip", "-o", "-q", serverFolder + "/" + newVersion , "-d" ,  serverFolderExe])
            if firstRun == True:
                initializeiProperties()
            else:
                #Restore server.properties from server.properties.bak
                print("Restoring original server properties, whitelist and permissions")
                shutil.move(serverFolderExe + "/server.properties.bak", serverFolderExe + "/server.properties")
                shutil.move(serverFolderExe + "/whitelist.json.bak", serverFolderExe + "/whitelist.json")
                shutil.move(serverFolderExe + "/permissions.json.bak", serverFolderExe + "/permissions.json")
            startServer()
            firstRun = False
    except Exception as e:
        print(e)
    time.sleep(86400)
