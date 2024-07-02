import requests
import json
import os
from requests.adapters import HTTPAdapter, Retry

servers = "https://bwsecondary.ddns.net:8080"
auth_token = ""
print("Input your authentication token. This can be found whenever you launch the game.")
choice = input(">")
auth_token = choice

s = requests.Session()
retries = Retry(total=5,backoff_factor=0.1,status_forcelist=[ 500, 502, 503, 504 ])
s.mount("http://", HTTPAdapter(max_retries=retries))
s.mount("https://", HTTPAdapter(max_retries=retries))

'''print("Logging in...")
authenticated = s.post(servers + "/api/v2/account/login/auth_token", json={"auth_token": auth_token})
print("Loading worlds...")
worlds = s.get(servers + "/api/v1/current_user/worlds", headers={"BW-Auth-Token": auth_token})
print("Fetching remote configuration...")
s.get(servers + "/api/v1/steam-app-remote-configuration", headers={"BW-Auth-Token": auth_token})
print("Downloading categories...")
categories = s.get(servers + "/api/v1/content-categories-no-ip", headers={"BW-Auth-Token": auth_token})
print("Downloading block data...")
block_item_prices = s.get(servers + "/api/v1/block_items/pricing", headers={"BW-Auth-Token": auth_token})'''

def get_world_data(worldId):
     url = servers + "/api/v1/worlds/" + str(worldId)
     
     return s.get(url).json()["world"]

def publish_world(worldId,copyFolder):
     url = servers + "/api/v1/worlds/" + str(worldId)
     
     multipart_form_data = {
          "source_json_str": (None, json.loads(open(copyFolder + "/worldData.json", "r").read())["source_json_str"]),
          "has_win_condition": (None, False),
          "required_mods_json_str": (None, "[]"),
          "screenshot_image": ("screenshot.jpg", open(copyFolder + "/screenshot.jpg", "rb"))
     }

     return s.put(url, files=multipart_form_data, headers={"BW-Auth-Token": auth_token, "User-Agent": "UnityPlayer/5.5.5f1 (UnityWebRequest/1.0, libcurl/7.51.0-DEV)", "BW-App-Version": "1.47.0", "BW-Client-Type": "Windows", "X-Unity-Version": "5.5.5f1"})

def delete_world(worldId):
     url = servers + "/api/v1/worlds/" + str(worldId)
     
     return s.delete(url,  headers={"BW-Auth-Token": auth_token})

def publish_model(modelId):
     return

def make_options_from_list(list,prompt):
     prompt = "\n" + prompt + "\n" or "\nSelect an option\n"
     i = 0
     for v in list:
          i += 1
          prompt = prompt + "["+str(i)+"]. "+v+" - "+json.loads(open("exported_worlds/" + v + "/worldData.json", "r").read())["title"]+"\n"
     prompt = prompt[:-1]
     return prompt

print("""
Select an option
[1]. Copy to your world
[2]. Download any world
[3]. Delete your world""")
choice = int(input(">"))
if choice == 1:
     exportedWorlds = os.listdir("exported_worlds")
     if len(exportedWorlds) >= 1:
          print(make_options_from_list(exportedWorlds,"Select a world to copy"))
          picked = exportedWorlds[int(input(">"))-1]
          print("\nInput your world id")
          worldId = int(input(">"))
          worldName = get_world_data(worldId)["title"]
          print("\nPublishing to " + worldName + "...")
          publish_world(worldId,"exported_worlds/"+picked)
          print("Finished.\n\nRestart blocksworld, then go to the build tab.\nIf you see a screen that says \"Your world has been modified on another device\", click the option that says \"Version on other device\"")
     else: print("You don't have any worlds to copy, download some worlds by choosing option 2")
elif choice == 2:
     print("Input world id\n")
     worldId = int(input(">"))
     print("\nDownloading world...")
     worldData = get_world_data(worldId)
     
     imageUrl = worldData["image_urls_for_sizes"]["1024x768"]
     imageData = requests.get(imageUrl, allow_redirects=True)
     
     worldExport = "exported_worlds/"+ str(worldId)
     if not os.path.exists(worldExport):
          os.makedirs(worldExport)

     open("exported_worlds/"+ str(worldId) +"/screenshot.jpg", "wb").write(imageData.content)
     
     print("\nSaving " + worldData["title"] + "...")
     worldFile = open("exported_worlds/"+ str(worldId) +"/worldData.json", "w")
     worldFile.seek(0)
     worldFile.write(json.dumps(worldData))
     worldFile.truncate()
     worldFile.close()
     print("Finished.")
elif choice == 3:
     print("Input world id\n")
     worldId = int(input(">"))
     worldName = get_world_data(worldId)["title"]
     print("\nDeleting " + worldName + "...")
     print(delete_world(worldId).text)
     print("Finished.")
