import shutil
import os
import tarfile
import subprocess
def copy_to_root_fs(file_path, fs_path, dst):
    print("e2cp '{}' {}:{}".format(file_path,fs_path, dst))
    os.system("e2cp '{}' {}:{}".format(file_path,fs_path, dst))

def create_folder_root_fs(fs_path, dst):
    print("e2mkdir {}:{}".format(fs_path, dst))
    os.system("e2mkdir {}:{}".format(fs_path, dst))

def extract_from_root_file(fs_path, file_path, dst_local_path):
    print("e2cp {}:{} '{}'".format(fs_path, file_path, dst_local_path))
    os.system("e2cp {}:{} '{}'".format(fs_path, file_path, dst_local_path))

def list_rootfs_files(fs_path, dst):
    output = subprocess.check_output("e2ls -l {}:{}".format(fs_path, dst), shell=True).decode().split("\n")
    print(output)
    list_files = []
    for i in output:
        name = i.split(" ")[-1]
        if name != '':
            list_files.append(name)
    return list_files
