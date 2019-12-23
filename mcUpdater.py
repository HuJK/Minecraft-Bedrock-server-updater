#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import os
import time
import subprocess
import sys
import atexit

serverFolder = 'serverZip'
serverFolderExe = 'serverFolder'
fristRun = False

difficulty = 'hard'
if len(sys.argv) >1:
    if sys.argv[1] == 'easy':
        difficulty = 'easy'
    elif sys.argv[1] == 'normal':
        difficulty = 'normal'
    elif sys.argv[1] == 'hard':
        difficulty = 'hard'

if not os.path.isdir(serverFolder):
    print("First run. Creating serverFolder")
    os.makedirs(serverFolder)
    fristRun = True
if not os.path.isdir(serverFolderExe):
    print("First run. Creating serverFolder")
    os.makedirs(serverFolderExe)
    fristRun = True
    
def getDWurl():
    MCurl = requests.get('https://www.minecraft.net/en-us/download/server/bedrock').text
    MCSoup =  BeautifulSoup(MCurl, 'html.parser')
    for dwbtn in MCSoup.findAll("a",{"class":"btn btn-disabled-outline mt-4 downloadlink"}):
        if  dwbtn['data-platform'] == 'serverBedrockLinux':
            return dwbtn['href']


def oslistdir(path):
    return list(filter((lambda x:x[0] != "."),os.listdir(serverFolder)))

print("Starting server...")
subprocess.call(["tmux", "new", "-d", "-s", "MC_BDRK" , "./bedrock_server"] , cwd=serverFolderExe)

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

        
        
def stopServer():
    print("Stopping server...")
    subprocess.call(["tmux", "send-keys", "-t", "MC_BDRK","stop"])
    time.sleep(1)
    subprocess.call(["tmux", "send-keys", "-t", "MC_BDRK","Enter"])
    time.sleep(5)
    subprocess.call(["tmux", "kill-session", "-t", "MC_BDRK"])


atexit.register(stopServer)

while(True):
    dwurl = getDWurl()
    fname = dwurl.split("/")[-1]
    currentVersion = oslistdir(serverFolder)[0] if len(oslistdir(serverFolder)) != 0 else "(No old version found)"
    if currentVersion != fname:
        print("New Minecraft version found: " + fname)
        print("Start downloading: " + fname)
        myfile = requests.get(dwurl)
        open(serverFolder + "/" + fname, 'wb').write(myfile.content)
        print("Remove old version: " + currentVersion)
        try:
            os.remove(serverFolder + "/" + currentVersion)
        except:
            pass
        stopServer()
        print("Extracting new server from zip")
        subprocess.call(["unzip", "-o", "-q", serverFolder + "/" + fname , "-d" ,  serverFolderExe])
        if(fristRun==True):
            setProperties("difficulty",difficulty)
            setProperties("max-players",str(20))
        print("Running new server")
        subprocess.call(["tmux", "new", "-d", "-s", "MC_BDRK" , "./bedrock_server"] , cwd=serverFolderExe)
    time.sleep(86400)
