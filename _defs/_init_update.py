import os
import shutil
from pathlib import Path
import numpy as np

current_path = os.getcwd()
cpkeys = current_path.split('/')

## run updating: 
# defs version
# defs_vers = 'v20260116'

defs_vers = list(Path('./_defs').glob('_defs_*'))[0].name[-13:-4]

defs_source = '/'.join(cpkeys[:3])+'/_samplecodes/defs/'+defs_vers
# print('defs version = '+ defs_vers )
print('defs version: '+defs_source)

defs_destination = current_path+'/_defs'

def getfilemtime(folder_path):
    file_modified_time=[]
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):  # Check if it's a file
            file_modified_time.append(os.path.getmtime(file_path))
    file_modified_time=np.array(file_modified_time)
    return file_modified_time.max()

if os.path.exists(defs_destination):
    # Get the last modification times of both folders
    # source_mod_time = os.path.getmtime(defs_source)
    # destination_mod_time = os.path.getmtime(defs_destination)
    source_mod_time = getfilemtime(defs_source)
    destination_mod_time = getfilemtime(defs_destination)
    # Compare the modification times
    if source_mod_time > destination_mod_time:
        # Source is newer; update the destination folder
        # Remove the existing destination folder
        shutil.rmtree(defs_destination)
        # Copy the source folder to the destination
        shutil.copytree(defs_source, defs_destination)
        print(f"defs updated from {defs_source}.")
        logfile = os.path.join(defs_destination,"_defs_"+defs_vers+'.txt')
        with open(logfile, "w", encoding="utf-8") as f:
            f.write(defs_vers)
    else:
        # Destination is up-to-date; no action needed
        print("defs is up-to-date.")
else:
    # Destination folder does not exist; create it by copying the source folder
    shutil.copytree(defs_source, defs_destination)
    print(f"defs created from {defs_source}.")




