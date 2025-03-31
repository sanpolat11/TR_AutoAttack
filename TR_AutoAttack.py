from phBot import *
import QtBind
from threading import Timer
import struct
import json
import os

pName = 'TR_AutoAttack'
pVersion = '1.0'
pUrl = 'https://raw.githubusercontent.com/sanpolat11/TR_AutoAttack/refs/heads/main/TR_AutoAttack.py'

# Globals
character_data = None

# GUI
gui = QtBind.init(__name__,pName)

# GUI Elements
lblRadius = QtBind.createLabel(gui,'Saldırı Mesafesi',70,10)
txtRadius = QtBind.createLineEdit(gui,"100",70,30,50,20)
cbxEnabled = QtBind.createCheckBox(gui,'cbxEnabled_clicked',' Otomatik Saldırı ',70,60)

def getPath():
    return get_config_dir()+pName+"\\"

def getConfig():
    return getPath()+character_data["server"]+"_"+character_data["name"]+".json"

def loadConfig():
    if isJoined():
        if os.path.exists(getConfig()):
            data = {}
            with open(getConfig(),"r") as f:
                data = json.load(f)
            if "Enabled" in data:
                QtBind.setChecked(gui,cbxEnabled,data["Enabled"])
            if "Radius" in data:
                QtBind.setText(gui,txtRadius,data["Radius"])

def saveConfig():
    if isJoined():
        data = {}
        data["Enabled"] = QtBind.isChecked(gui,cbxEnabled)
        data["Radius"] = QtBind.text(gui,txtRadius)
        with open(getConfig(),"w") as f:
            f.write(json.dumps(data, indent=4))

def isJoined():
    global character_data
    character_data = get_character_data()
    return character_data and "name" in character_data and character_data["name"]

def cbxEnabled_clicked(checked):
    saveConfig()
    if checked:
        log("Plugin: Otomatik saldırı başlatıldı")
    else:
        log("Plugin: Otomatik saldırı durduruldu")

def handle_event(t, data):
    if t == 0:  # PLUGIN_EVENT_NOTIFICATION
        if data == "GAME_READY":
            loadConfig()
    return True

def handle_chat(t,p,msg):
    return True

def event_loop():
    if isJoined() and QtBind.isChecked(gui,cbxEnabled):
        radius = float(QtBind.text(gui,txtRadius))
        monsters = get_monsters()
        if monsters:
            playerX = get_position()['x']
            playerY = get_position()['y']
            nearestMob = None
            shortestDistance = 999999
            
            for key, mob in monsters.items():
                if mob['type'] == 0:  # Normal mob
                    distance = ((mob['x'] - playerX)**2 + (mob['y'] - playerY)**2)**0.5
                    if distance < shortestDistance and distance <= radius:
                        shortestDistance = distance
                        nearestMob = key
            
            if nearestMob:
                p = struct.pack('<I', nearestMob)
                inject_joymax(0x7074, p, False)
    return 500

# Plugin loaded
log('Plugin: '+pName+' v'+pVersion+' successfully loaded')

if os.path.exists(getPath()):
    loadConfig()
else:
    os.makedirs(getPath())
    log('Plugin: '+pName+' folder has been created')
