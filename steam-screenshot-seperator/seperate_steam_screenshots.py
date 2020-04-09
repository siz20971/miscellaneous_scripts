#
# Steam Screenshot Seperator
# requires Python 3.6.2
# Script by siz20971
# 

# 압축하지 않은 사본 분류기
# 압축하지 않은 사본 스크린샷이 저장된 폴더에서 실행

import sys
import os
import requests
import json
import errno
import shutil
import re

def get_steamapps_dict():
    print ("Start SteamApps list...")
    res = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
    ret_dict = dict()

    if (res.status_code == 200):
        ret = json.loads(res.text)

        if (ret["applist"] and ret["applist"]["apps"]):
            for kv in ret["applist"]["apps"]:
                ret_dict[str(kv["appid"])] = kv["name"]
        
        len_loaded = len(ret_dict)

        if len_loaded == 0:
            print ("get SteamApps List Failed.")
        else:
            print ("Finish SteamApps list. Total SteamApps:", len_loaded)
    else:
        print ("RequestError. retStatusCode:" , res.status_code)

    return ret_dict

def parse_app_id(file_name):
    splited = file_name.split("_")
    if (len(splited) > 0):
        appid = splited[0]
    return appid

def seperate_files(src_path, dst_path):
    steamapps_dict = get_steamapps_dict()

    # Load files.
    cnt_moved = 0
    files = os.listdir(src_path)
    for f in files:
        src_full_path = os.path.join(src_path, f)
        dst_full_path = ""

        if (os.path.isdir(src_full_path)):
            continue

        appid = parse_app_id(f)
        if (appid in steamapps_dict):
            game_name = steamapps_dict[appid]
            dst_dir_path = os.path.join(dst_path, game_name)
            
            try:
                os.mkdir(dst_dir_path)
            except  OSError as oserr:
                if oserr.errno == errno.EINVAL:
                    print (" !!! create Directory Failed. (Invalid Name) Name:", game_name, " ErrNo:", oserr.errno)
                    continue
                elif oserr.errno == errno.ENOTDIR:
                    new_dir_name = game_name
                    illegal = ['NUL','\',''//',':','*','"','<','>','|']
                    for i in illegal:
                        new_dir_name = new_dir_name.replace(i, '')
                    print (" !!! Iillegal Directory Name. Replace... ", game_name, " -> ", new_dir_name)
                    dst_dir_path = os.path.join(dst_path, new_dir_name)
                    os.mkdir(os.path.join(dst_path, new_dir_name))
                elif oserr.errno != errno.EEXIST:
                    print (" !!! create Directory Failed. (Unknown) Name:", game_name, " ErrNo:", oserr.errno)
                    continue

            if (os.path.isdir(dst_dir_path)):
                print ("[Move] File:", f, " GameName:", steamapps_dict[appid])
                shutil.move(src_full_path, os.path.join(dst_dir_path, f))
            else:
                print ("[Fail] File:", f, " GameName:", steamapps_dict[appid])

            cnt_moved += 1
        else:
            print ("[Skip] File:", f , " NOT STEAM IMG")

# main.
src_path = os.getcwd()
dst_path = os.getcwd()

print (os.name ,  " , " , src_path)

seperate_files(src_path, dst_path)