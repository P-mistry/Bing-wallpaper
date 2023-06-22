#! /usr/bin/python3
# Author: Maximilian Muth <mail@maxi-muth.de>
# https://github.com/mammuth/bing-wallpaper
# Version: 1.0
# License: GPL-2.0
# Description: Downloads the Bing picture of the Day and sets it as wallpaper (Linux / Windows).

import argparse
import datetime
from urllib.request import urlopen, urlretrieve
from xml.dom import minidom
import os
import sys
import ctypes
import subprocess


dir_path = os.path.dirname(os.path.realpath(__file__))
save_dir = os.path.join(dir_path, "images")
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


def set_windows_wallpaper(pic_path):
    """
    WinAPI wallpaper set
    Documentation is here
    https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-systemparametersinfow
    """
    print("Setting {} as a wallpaper".format(pic_path))
    uiAction = 20  # SPI_SETDESKWALLPAPER = 0x0014 or 20 in decimal
    uiParam = 0
    pvParam = pic_path
    fWinIni = 0
    success = ctypes.windll.user32.SystemParametersInfoW(
        uiAction, uiParam, pvParam, fWinIni
    )
    if success:
        print("Wallpaper is set.")
    else:
        print("Something went wrong. Wallpaper wasn't set")


def set_linux_wallpaper(pic_path):
    os.system(
        "".join(
            ["gsettings set org.gnome.desktop.background picture-uri file://", pic_path]
        )
    )
    print("Wallpaper is set.")


def set_macos_wallpaper(pic_path):
    script = f'''tell application "System Events" to set picture of every desktop to "{pic_path}"'''
    subprocess.run(["osascript", "-e", script])
    print("Wallpaper is set.")


def set_wallpaper(pic_path):
    if sys.platform.startswith("win32"):
        set_windows_wallpaper(pic_path)
    elif sys.platform.startswith("linux"):
        set_linux_wallpaper(pic_path)
    elif sys.platform.startswith("darwin"):
        set_macos_wallpaper(pic_path)
    else:
        print("OS not supported.")


# def download_old_wallpapers(minus_days=False):
#     """Uses download_wallpaper(set_wallpaper=False) to download the last 20 wallpapers.
#     If minus_days is given an integer a specific day in the past will be downloaded.
#     """
#     if minus_days:
#         download_wallpaper(idx=minus_days, use_wallpaper=False)
#         return
#     for i in range(0, 20):  # max 20
#         download_wallpaper(idx=i, use_wallpaper=False)


def download_wallpaper(idx=0, number_of_days=1, use_wallpaper=True):
    # Getting the XML File
    try:
        usock = urlopen(
            "".join(
                [
                    "http://cn.bing.com/HPImageArchive.aspx?format=xml&idx=",
                    str(idx),
                    "&n="+str(number_of_days),
                ]
            )
        )  # ru-RU, because they always have 1920x1200 resolution
    except Exception as e:
        print("Error while downloading #", idx, e)
        return
    try:
        xmldoc = minidom.parse(usock)
    # This is raised when there is trouble finding the image url.
    except Exception as e:
        print("Error while processing XML index #", idx, e)
        return
    # Parsing the XML File
    for element in xmldoc.getElementsByTagName("image"):

        #get date
        startDate=element.getElementsByTagName("startdate")[0].firstChild.nodeValue

        url = "http://www.bing.com" + element.getElementsByTagName("url")[0].firstChild.nodeValue

        # Get Current Date as fileName for the downloaded Picture
        # now = datetime.datetime.now()
        # date = now - datetime.timedelta(days=int(idx))
        #date= datetime.datetime.strptime(startDate,'%Y%m%d')
        pic_path = os.path.join(
            save_dir, "".join([startDate, ".jpg"])
        )

        if os.path.isfile(pic_path):
            print("Image of", startDate, "already downloaded.")
            if use_wallpaper:
                set_wallpaper(pic_path)
        else:
            print("Downloading: ", startDate, "index #", idx)
            # Download and Save the Picture
            # Get a higher resolution by replacing the file name
            urlretrieve(url.replace("_1920x1080", "_UHD"), pic_path)
            # Set Wallpaper if wanted by user
            if use_wallpaper:
                set_wallpaper(pic_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download bing wallpapers')
    parser.add_argument('--index', type=int,default=0,required=False,help="days back")
    parser.add_argument('--numberOfDays', type=int,default=1,required=False,help="Number of days to download")
    parser.add_argument('--setWallpaper',type=bool,default=False,action=argparse.BooleanOptionalAction,required=False,help="Set wallpaper")
    args = parser.parse_args()
    download_wallpaper(args.index,args.numberOfDays,args.setWallpaper)