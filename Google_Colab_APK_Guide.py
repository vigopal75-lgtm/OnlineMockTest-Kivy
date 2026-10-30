# Google Colab notebook cells for building the Android APK.
# 1) Upload the OnlineMockTest_Kivy.zip file in Colab, then run these cells.

from google.colab import files
uploaded = files.upload()  # Select OnlineMockTest_Kivy.zip

import zipfile, os
zip_name = next(name for name in uploaded if name.lower().endswith(".zip"))
with zipfile.ZipFile(zip_name) as z:
    z.extractall("/content")
os.chdir("/content/OnlineMockTest_Kivy")
print("Project ready:", os.listdir())

# Install Android build dependencies
!sudo apt-get update -y
!sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip python3-venv \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev

# Install Buildozer and Cython
!python3 -m pip install --user --upgrade pip setuptools wheel
!python3 -m pip install --user buildozer cython==0.29.36

# Make sure Buildozer is on PATH
import os
os.environ["PATH"] += os.pathsep + os.path.expanduser("~/.local/bin")
!buildozer --version

# Build the debug APK (first build can take 20–60 minutes)
!yes | buildozer -v android debug

# Download the generated APK
import glob
apk_files = glob.glob("bin/*.apk")
print(apk_files)
from google.colab import files
files.download(apk_files[0])
