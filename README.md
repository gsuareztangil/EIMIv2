# EIMI
***
## Description
EIMI is a sandbox for the analysis and extraction of static and dynamic characteristics of Linux-based malware samples that target IoT devices.
For static analysis we use the radare2 framework. For the emulation of virtual machines and their architecture, we use QEMU. The virtual machines for the different architectures have been built using buildroot. Our sandbox supports the following architectures:
- arm little endian
- mips little and big endian
- PowerPC big endian
- x86 little endian
- x86_64 little endian
- Sparc big endian
- Motorola m68k big endian

## Preparation
First of all, unzip the file system for each of the supported runtime architectures and libraries with the following command:

```
for i in `ls -1 ./machines`; do unzip -d ./machines/$i/ ./machines/$i/filesystem.zip; done
```

## Installation
Next, we need to install the following packages and python dependencies:
```
sudo apt-get install qemu qemu-system
pip install -r requeriments.txt
```
## Usage
We use the following command to start the analyis:
```
Usage: python3 eimi.py -r MODE <sample_hash>

Options:
  -h, --help            show this help message and exit
  -d SAMPLES_DIRECTORY, --directory=SAMPLES_DIRECTORY
                        directory containing samples to execute
  -r INTERNET_ACCESS_MODE, --restrict-internet=INTERNET_ACCESS_MODE
                        restrict ('on') or permit ('off') virtual machines
                        internet access
```

By default, the system has restricted the internet connection. In case we want to allow connections with the outside we have to use the "-r off" parameter
The tool also allows you to pass a directory of malware samples for analysis using the -d parameter

## Analysis results
Once the analysis is finished, the results are stored in the following directories:

- tmp: Stores the result of the execution traces with strace in a directory with the name of the file
- network: Stores the result of the network traces obtained with tcpdump in a directory with the name of the file
- log: Stores the results in log format in a folder with the file name. The content of this file is also stored in malware.sqlite3, a sqlite3 database.

In the event that an error occurs with the sample or no suitable execution environment is found, the sample will be stored in the reanalyze directory for manual inspection.


## Acknowledgements



Use the following citation to acknowledge our work: 

Carrillo-Mondejar, Javier, et al. "Exploring Shifting Patterns in Recent IoT Malware." European Conference on Cyber Warfare and Security. Vol. 23. No. 1. 2024.

@inproceedings{carrillo2024exploring,
  title={Exploring Shifting Patterns in Recent IoT Malware},
  author={Carrillo-Mondejar, Javier and Suarez-Tangil, Guillermo and Costin, Andrei and Rodr{\'\i}guez, Ricardo J},
  booktitle={European Conference on Cyber Warfare and Security},
  volume={23},
  number={1},
  year={2024}
}


This research was supported in part by TED2021-132900A-I00 and by TED2021-131115A-I00, funded by MCIN/AEI/10.13039/501100011033, by the Recovery, Transformation and Resilience Plan funds, financed by the European Union (Next Generation), by the Spanish National Cybersecurity Institute (INCIBE) under Proyectos Estratégicos de Ciberseguridad -- CIBERSEGURIDAD EINA UNIZAR, and by the University, Industry and Innovation Department of the Aragonese Government under Programa de Proyectos Estratégicos de Grupos de Investigación (DisCo research group, ref. T21-23R). G. Suarez-Tangil was appointed as 2019 Ramon y Cajal fellow (RYC-2020-029401-I) funded by MCIN/AEI/10.13039/501100011033 and ESF Investing in your future.


(Part of) This work was supported by the European Commission under the Horizon Europe Programme, as part
of the project LAZARUS (https://lazarus-he.eu/) (Grant Agreement no. 101070303). The content of this article
does not reflect the official opinion of the European Union. Responsibility for the information and views
expressed therein lies entirely with the authors.
