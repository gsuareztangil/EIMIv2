import os
from helper import load_env_file, store_static_fields
from optparse import OptionParser
from connection_handler import *
from static_analyzer import Elf
from datetime import date
from parser import syscall_parser
import json
import glob
import pexpect
import time
import hashlib
import shutil
from create_database import *


def save_to_log(malware_data, sample_name):
    dst = os.getenv('LOG')
    filename = os.path.join(dst, sample_name) + ".log"
    with open(os.path.join(dst, filename), "w") as f:
        json.dump(malware_data, f, indent=2)

def get_list_syscalls(full_syscalls):
    syscalls = {}
    for i in full_syscalls:
        syscalls[i] = full_syscalls[i]['syscalls']
    return syscalls

def is_statically_linked(binary_path):
    output = subprocess.check_output("file {}".format(binary_path), shell=True).decode().split("\n")[0]
    return ("statically linked" in output)


def is_shared_object(binary_path):
    output = subprocess.check_output("file {}".format(binary_path), shell=True).decode().split("\n")[0]
    return ("shared object," in output)
def check_interpreter(binary_path):
    output = subprocess.check_output("file {}".format(binary_path), shell=True).decode().split("\n")[0]
    if "-uClibc." in output:
        return "uclibc"
    elif "-musl" in output:
        return "musl"
    else:
        return "glibc"

def pipeline(sample_path, sample_name, options):
    vm_handler = None
    #######################
    ### Static analysis ###
    #######################
    sample = Elf(sample_path)
    sample.information_file()

    if sample.bintype != 'elf':
        print(colored("[X] It is not a ELF sample", 'red'))
        return

    # Parse sample arch to deploy a virtual machine
    vm_guest = sample.arch + '_' + str(sample.bits) + '_' + sample.endian
    #if vm_guest == 'arm_32_little':
    #    output = subprocess.check_output("file {}".format(sample_path), shell=True).decode().split("\n")[0]
    #    if 'ARM, version 1' in output:
    #        vm_guest = 'armo_32_little'

    if not is_shared_object(sample_path):
        if is_statically_linked(sample_path):
             lib = 'uclibc'
        else:
            lib = check_interpreter(sample_path)
        vm_guest = vm_guest + "_" + lib
        vm_path = '../machines/' + vm_guest
        # Check if virtual machine is imported in the project
        if not os.path.isdir(vm_path):
            print(colored("[X] Virtual machine not found", 'red'))
            return



        print(colored("[+] Analyzing sample statically...", 'green'))

        # Radare2 static analysis fields
        sample.sections_file()
        sample.imports_file()
        sample.libs_file()
        sample.hash_file()
        # sample.get_strings()
        sample.get_function_list()
        sample.get_opcodes_func()
        sample.get_ngrams()
        sample.get_cyclomatic_complexity()

        # Parse above fields into dictionary
        sample_info = json.dumps(sample.dump_to_dict())

        ################################
        ### Handling virtual machine ###
        ################################
        print(colored("[+] Starting '" + vm_guest + "' virtual machine...", 'green'))

        print(os.getenv('USER_VM'))
        print(os.getenv('PASSWORD_VM'))
        h_vmachine = DynamicAnalysis(os.getenv('USER_VM'), os.getenv('PASSWORD_VM'), vm_guest, options.internet_access_mode, sample_path)
        h_vmachine.prepare_rootfs(sample_path, os.getenv('MACHINE_REMOTEPATH'))
        h_vmachine.start_qemu_machine()

        try:
            if h_vmachine.do_login():
                h_vmachine.run_sample(os.getenv('MACHINE_REMOTEPATH'))
                h_vmachine.stop_machine()
                h_vmachine.download_results()
        except:
            pass

        try:
            if len(os.listdir(os.path.join("../tmp", h_vmachine.get_filename())))>0:
                ok = True
            else:
                ok = False
        except FileNotFoundError:
            ok = False
            print(colored("[X] No dynamic files {} not found".format(os.path.join("../tmp", h_vmachine.get_filename())), 'red'))
        print(colored("[+] Destroying '" + vm_guest + "' virtual machine", 'green'))
        del h_vmachine
    else:
        ok = False

    if ok:
        ########################
        ### Dynamic analysis ###
        ########################
        syscalls = syscall_parser("../tmp/" + sample_name)  # Dynamic data

        ########################
        ### Database queries ###
        ########################
        print(colored("[+] Storing analysis results into database", 'green'))
        db_fields = (sample.md5, sample_name, str(json.dumps(syscalls)), None, vm_guest, str(sample_info), date.today())
        store_static_fields(db_fields)

        malware_data = {}
        malware_data['md5'] = sample.md5
        malware_data['name_file'] = sample_name
        malware_data['full_syscalls'] = syscalls
        malware_data['syscalls'] = get_list_syscalls(syscalls)
        malware_data['label'] = ""
        malware_data['vm_environment'] = vm_guest
        malware_data['arch_endianness'] = sample.arch + '_' + str(sample.bits) + '_' + sample.endian
        malware_data['sample_info'] = sample.dump_to_dict()
        malware_data['date'] = str(date.today())

        save_to_log(malware_data, sample_name)

        del sample
        # End of pipeline

        #cluster_ngrams(sample)
        #cluster_cc(sample)
        print(colored("[+] Done!\n", 'green'))
    else:
        del sample
        print((colored("[-] Error dynamic anaylisis", 'red')))
        shutil.copy(sample_path, os.getenv('REANALYZE'))


def main():
    # Load .env file
    load_env_file()
    database_init()
    # Parse args and options
    parser = OptionParser("Usage: python3 eimi.py -r MODE <sample_hash>")

    parser.add_option('-d', '--directory', dest='samples_directory', type='string', default=None,
                      help="directory containing samples to execute")

    parser.add_option('-r', '--restrict-internet', dest='internet_access_mode', type='string', default='on',
                      help="restrict ('on') or permit ('off') virtual machines internet access")

    (options, args) = parser.parse_args()
    # Validate options and args
    if options.samples_directory is not None and not os.path.isdir(options.samples_directory):
        print(colored("[X] Samples directory not found", 'red'))
        exit(1)

    if options.internet_access_mode not in ['on', 'off']:
        print(options.internet_access_mode)
        print("Usage: " + parser.usage)
        exit(1)

    if options.samples_directory is None and len(args) < 1:
        print(options)
        print("Usage: " + parser.usage)
        exit(1)


    if not os.path.exists(os.getenv('LOG')):
        os.mkdir(os.getenv('LOG'))

    if not os.path.exists(os.getenv('REANALYZE')):
        os.mkdir(os.getenv('REANALYZE'))
    # Multiple pipelines
    if options.samples_directory is None:  # Samples by args
        for arg in args:
            error = False
            if not os.path.isfile(arg):
                print(colored("[X] Sample file not found", 'red'))
                error = True

            if not os.access(arg, os.R_OK):
                print(colored("[X] Access denied to local sample file", 'red'))
                error = True

            # Execute pipeline
            if not error:
                # Split dir and sample file
                dirname, filename = os.path.split(arg)
                print(colored("[+] Sample: " + filename, 'blue'))

                pipeline(arg, filename, options)
    else:  # Samples in a directory
        samples_dir = glob.glob(options.samples_directory + "/*")

        for sample in samples_dir:
            error = False
            if not os.path.isfile(sample):
                continue
            m = hashlib.md5()
            f = open(sample, "rb")
            data = f.read()
            f.close()
            m.update(data)

            hash = m.hexdigest()

            try:
                # Connection
                sqliteConnection = sqlite3.connect(os.getenv('DATABASE_NAME'))
                cursor = sqliteConnection.cursor()

                # Execute query
                cursor.execute("SELECT hash FROM samples_analysis WHERE hash == '" + hash + "';")
                sample_data = cursor.fetchall()

                if sample_data:
                    print(colored("[X] Sample {} is already analyzed. skip! Hash: {}".format(sample, hash), 'blue'))
                    error = True

                if sample.split("/")[-1] in os.listdir(os.getenv('REANALYZE')):
                    error = True
                    print(colored("[X] Sample {} in check later. skip! Hash: {}".format(sample, hash), 'blue'))
                # Commit changes and close the connection
                sqliteConnection.commit()
                sqliteConnection.close()
            except sqlite3.Error as error:
                print(colored("[X] Failed to read data from sqlite table: " + str(error).lower(), 'red'))

            dirname, filename = os.path.split(sample)
            if os.path.exists("../tmp/"+filename): #we should use hash
                print(colored("[X] Sample {} is already analyzed. skip! Hash: {}".format(sample, hash), 'blue'))
                error = True

            if not os.path.isfile(sample):
                print(colored("[X] Sample file not found", 'red'))
                error = True

            if not os.access(sample, os.R_OK):
                print(colored("[X] Access denied to local sample file", 'red'))
                error = True

            # Execute pipeline
            if not error:
                # Split dir and sample file
                dirname, filename = os.path.split(sample)
                print(colored("[+] Sample: " + filename, 'blue'))

                pipeline(sample, filename, options)


if __name__ == '__main__':
    main()
