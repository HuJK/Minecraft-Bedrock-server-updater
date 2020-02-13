#!/usr/bin/python3
from bs4 import BeautifulSoup
import os
import sys
import time
import atexit
import shutil
import requests
import subprocess

serverFolder = 'serverZip'
serverFolderExe = 'serverFolder'


difficulty = 'hard'
if len(sys.argv) >1:
    if sys.argv[1] == 'easy':
        difficulty = 'easy'
    elif sys.argv[1] == 'normal':
        difficulty = 'normal'
    elif sys.argv[1] == 'hard':
        difficulty = 'hard'

def initialize():
    #Check serverFolder has only 1 file
    if len(oslistdir(serverFolder)) > 1:
        raise AssertionError("This folder can only have 1 file:" + serverFolder)
    #Setup folders
    fristRun = False
    if not os.path.isdir(serverFolder):
        print("First run. Creating serverFolder")
        os.makedirs(serverFolder)
        fristRun = True
    if not os.path.isdir(serverFolderExe):
        os.makedirs(serverFolderExe)
        fristRun = True
    if(fristRun==True):
        setProperties("difficulty",difficulty)#I think in miltiplayer mode, we can cooperate eachother, so difficulty=hard make this game more challengeable.
        setProperties("max-players",str(20))  #Java edition default setting.
        setProperties("content-log-file-enabled","true") #Enable log
    
def getDWurl():
    #get minecraft bedrock server dounload URL
    MCurl = requests.get('https://www.minecraft.net/en-us/download/server/bedrock').text
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

        
def srartServer():
    print("Starting server...")
    subprocess.call(["tmux", "new", "-d", "-s", "MC_BDRK" , "bash"] , cwd=serverFolderExe)
    time.sleep(1)
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
srartServer()
while(True):
    dwurl = getDWurl()
    newVersion = dwurl.split("/")[-1]
    oldVersion = oslistdir(serverFolder)[0] if len(oslistdir(serverFolder)) != 0 else "(No old version found)"
    if oldVersion != newVersion:
        print("New Minecraft version found: " + newVersion)
        print("Start downloading: " + newVersion)
        myfile = requests.get(dwurl)
        open(serverFolder + "/" + newVersion, 'wb').write(myfile.content)
        print("Remove old version: " + oldVersion)
        try:
            os.remove(serverFolder + "/" + oldVersion)
        except:
            pass
        stopServer()
        #Backup old server.properties to server.properties.bak
        shutil.move(serverFolderExe + "/server.properties", serverFolderExe + "/server.properties.bak")
        print("Extracting new server from zip")
        subprocess.call(["unzip", "-o", "-q", serverFolder + "/" + newVersion , "-d" ,  serverFolderExe])
        #Restore server.properties from server.properties.bak
        shutil.move(serverFolderExe + "/server.properties.bak", serverFolderExe + "/server.properties")
        srartServer()
        
    time.sleep(86400)
