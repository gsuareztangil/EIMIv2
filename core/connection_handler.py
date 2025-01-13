
import socket
from termcolor import colored
import os
import time
from helper import load_env_file
import logging
import pexpect
import utils
import shutil
import subprocess


class DynamicAnalysis:

    def __init__(self, user, password, vm_guest, internet_access_mode, sample_path):
        self.user = user
        self.password = password
        self.vm_guest = vm_guest
        self.vm_handler = None
        self.internet_access_mode = internet_access_mode
        self.filename = ''
        self.sample_path = sample_path
    def get_filename(self):
        return self.filename

    def start_qemu_machine(self):
        if 'ppc_32_big_' in self.vm_guest:
            command = '/usr/bin/qemu-system-ppc -M g3beige -kernel ../machines/' + self.vm_guest + '/vmlinux -drive file=../machines/' + self.vm_guest + '/rootfs.ext2,format=raw -append "console=ttyS0 root=/dev/sda" -net nic,model=rtl8139 -net user,restrict=' + self.internet_access_mode + ' -nographic'
        elif 'arm_32_little_' in self.vm_guest:
            command = 'qemu-system-arm -M vexpress-a9 -kernel ../machines/' + self.vm_guest + '/zImage -drive file=../machines/' + self.vm_guest + '/rootfs.ext2,format=raw,if=sd -dtb ../machines/' + self.vm_guest + '/vexpress-v2p-ca9.dtb -append "rootwait root=/dev/mmcblk0" -net nic,model=lan9118 -net user,restrict=' + self.internet_access_mode + ' -nographic'
        #elif self.vm_guest == 'armo_32_little':
        #    command = 'qemu-system-arm -M vexpress-a9 -kernel ../machines/' + self.vm_guest + '/zImage -drive file=../machines/' + self.vm_guest + '/rootfs.ext2,format=raw,if=sd -append "rootwait root=/dev/mmcblk0" -net nic,model=lan9118 -net user,restrict=' + self.internet_access_mode + ' -nographic'
        elif self.vm_guest == 'arm_64_little':
            command = 'qemu-system-aarch64 -M virt -cpu cortex-a57 -smp 1 -drive file=../machines/' + self.vm_guest + '/rootfs.ext2,if=none,id=hd0 -device virtio-blk-device,drive=hd0 -kernel ../machines/' + self.vm_guest + '/Image -append "console=ttyAMA0 root=/dev/vda" -device virtio-net-device,netdev=eth0 -netdev user,id=eth0,restrict=' + self.internet_access_mode + ' -nographic'
        elif 'mips_32_big_' in self.vm_guest:
            command = 'qemu-system-mips -M malta -kernel ../machines/' + self.vm_guest + '/vmlinux -drive file=../machines/' + self.vm_guest + '/rootfs.ext2,format=raw -append "rootwait root=/dev/sda" -net nic,model=pcnet -net user,restrict=' + self.internet_access_mode + ' -nographic'
        elif 'mips_32_little_' in self.vm_guest:
            command = 'qemu-system-mipsel -M malta -kernel ../machines/' + self.vm_guest + '/vmlinux -drive file=../machines/' + self.vm_guest + '/rootfs.ext2,format=raw -append "rootwait root=/dev/sda" -net nic,model=pcnet -net user,restrict=' + self.internet_access_mode + ' -nographic'
        #elif self.vm_guest == 'mips_64_big':
        #    command = 'qemu-system-mips64 -M malta -kernel ../machines/' + self.vm_guest + '/vmlinux -hda ../machines/' + self.vm_guest + '/rootfs.ext2 -append "root=/dev/hda" -net nic,model=pcnet -net user,restrict=' + self.internet_access_mode + ' -nographic'
        elif 'x86_32_little_' in self.vm_guest:
            command = 'qemu-system-i386 -kernel ../machines/' + self.vm_guest + '/bzImage -drive file=../machines/' + self.vm_guest + '/rootfs.ext2,if=virtio,format=raw -append "root=/dev/vda console=ttyS0" -net nic,model=virtio -net user,restrict=' + self.internet_access_mode + ' -nographic'
        elif 'x86_64_little_' in self.vm_guest:
            command = 'qemu-system-x86_64 -kernel ../machines/' + self.vm_guest + '/bzImage -drive file=../machines/' + self.vm_guest + '/rootfs.ext2,if=virtio,format=raw -append "root=/dev/vda console=ttyS0" -net nic,model=virtio -net user,restrict=' + self.internet_access_mode + ' -nographic'

        elif 'sh_32_little_' in self.vm_guest:
            command = 'qemu-system-sh4 -M r2d -kernel ../machines/' + self.vm_guest + '/zImage -drive file=../machines/' + self.vm_guest + '/rootfs.ext2,if=ide,format=raw -append "rootwait root=/dev/sda console=ttySC1,115200 noiotrap" -serial null -net nic,model=rtl8139 -net user,restrict=' + self.internet_access_mode + ' -serial stdio -display none'

        elif 'sparc_32_big_' in self.vm_guest:
            command = 'qemu-system-sparc -M SS-10 -kernel ../machines/' + self.vm_guest + '/zImage -drive file=../machines/' + self.vm_guest + '/rootfs.ext2,format=raw -append "rootwait root=/dev/sda console=ttyS0,115200"  -net nic,model=lance -net user,restrict=' + self.internet_access_mode + ' -nographic'
        elif 'm68k_32_big' in self.vm_guest:
            command = 'qemu-system-m68k -M q800 -kernel ../machines/' + self.vm_guest + '/vmlinux -nographic -drive file=../machines/' + self.vm_guest + '/rootfs.ext2,format=raw -append "rootwait root=/dev/sda console=ttyS0" -net nic -net user,restrict=' + self.internet_access_mode + ' -nographic'
        else:
            print(colored("[X] Virtual machine not found", 'red'))
            return False
        print(command)
        self.vm_handler = pexpect.spawnu(command)
        time.sleep(5)
        return True

    def prepare_rootfs(self, localpath, remotepath):
        # Split dir and sample file
        dirname, self.filename = os.path.split(localpath)
        print(self.filename)
        # Create sample execution environment
        fs_path = '../machines/' + self.vm_guest + '/rootfs.ext2'
        print(fs_path)

        shutil.copy(os.path.join('../machines/' + self.vm_guest, "rootfs.ext2.bak"), fs_path)
        print(os.path.join(remotepath, self.filename))
        utils.create_folder_root_fs(fs_path, os.path.join(remotepath, self.filename))
        utils.copy_to_root_fs(localpath, fs_path, os.path.join(remotepath, self.filename))

    def send_command(self, command):
        self.vm_handler.sendline(command)

    def do_login(self):
        print("[X] Logging into the CLI")
        if self.vm_handler is not None:
            id = self.vm_handler.expect(["login: "])
            time.sleep(5)
            if id == 0:
                print("Sending {}".format(self.user))
                self.vm_handler.sendline(self.user)
                id = self.vm_handler .expect(["[pP]assword: ", "# ", "\$ "])
                if id == 0:
                    print("Sending {}".format(self.password))
                    self.vm_handler.sendline(self.password)
                    id = self.vm_handler.expect(["\$ ", "# "])
                    if id == 0 or id == 1:
                        return True
        return False

    def run_sample(self, remotepath):
        ok = False
        # Load .env file
        load_env_file()

        # Build commands to execute in VM
        command = "mkdir -p " + os.getenv('NETWORK_REMOTEPATH') + "; timeout -s SIGKILL " + os.getenv('NETWORK_TIMEOUT') + " tcpdump -i any -s 0 -U -w " + os.path.join(os.getenv('NETWORK_REMOTEPATH'), self.filename) + ".pcap & sleep 1; cd " + os.path.join(remotepath, self.filename) + "; chmod +x " + self.filename + ";" + "mkdir -p " + os.path.join(os.getenv('LOGSYSCALL_REMOTEPATH'), self.filename) + "; timeout -s SIGKILL " + os.getenv('EXECUTION_TIMEOUT') + " strace -s 4096 -qq -e 'signal=!all' -ff -o " \
                  + os.path.join(os.getenv('LOGSYSCALL_REMOTEPATH'), self.filename) + "/" + self.filename + " ./" + self.filename + ' & sleep ' + os.getenv('EXECUTION_TIMEOUT') + "; kill -9 $!;"
        print(command)
        if "sh_32_little_" in self.vm_guest:
            for i in command:
                self.vm_handler.send(i)
            self.send_command("")
        else:
            self.send_command(command)
        print(colored("[+] Executing sample (" + os.getenv('EXECUTION_TIMEOUT') + " secs)...", 'green'))
        time.sleep(int(os.getenv('NETWORK_TIMEOUT')) + 2)  # Timeout to execute malware

        self.send_command("sync")
        self.send_command("poweroff")
        time.sleep(10)
    def stop_machine(self):
        self.vm_handler.close()

    def download_results(self):
        # Download strace output files
        if not os.path.isdir('../tmp'):
            os.mkdir('../tmp')

        print(colored(
            "[+] Downloading sample execution results in " + os.path.dirname(
                os.path.abspath('../' + __file__)) + '/tmp/' + self.filename, 'green'))

        try:
            files = utils.list_rootfs_files('../machines/' + self.vm_guest + '/rootfs.ext2', os.path.join(os.getenv('LOGSYSCALL_REMOTEPATH'), self.filename))
        
            if not os.path.isdir(os.path.join("../tmp", self.filename)):
                os.mkdir(os.path.join("../tmp", self.filename))

            for f in files:
                utils.extract_from_root_file('../machines/' + self.vm_guest + '/rootfs.ext2',
                                            os.path.join(os.path.join(os.getenv('LOGSYSCALL_REMOTEPATH'), self.filename), f),
                                            os.path.join("../tmp", self.filename))
        except subprocess.CalledProcessError:
            print(colored("[+] Error listing files", 'red'))

        try:
            if not os.path.isdir('../network'):
                os.mkdir('../network')

            utils.extract_from_root_file('../machines/' + self.vm_guest + '/rootfs.ext2',
                                         os.path.join(os.getenv('NETWORK_REMOTEPATH'), self.filename) + ".pcap",
                                         os.path.join("../network", self.filename+".pcap"))
        except:
            print(colored("[+] No network files", 'red'))