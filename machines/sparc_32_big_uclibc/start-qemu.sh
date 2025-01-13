#!/bin/sh
(
BINARIES_DIR="${0%/*}/"
cd ${BINARIES_DIR}

if [ "${1}" = "serial-only" ]; then
    EXTRA_ARGS='-nographic'
else
    EXTRA_ARGS='-serial stdio'
fi

export PATH="/home/dankitani/Descargas/buildroot-2023.02/output/host/bin:${PATH}"
exec qemu-system-sparc -M SS-10 -kernel zImage -drive file=rootfs.ext2,format=raw -append "rootwait root=/dev/sda console=ttyS0,115200"  -net nic,model=lance -net user  ${EXTRA_ARGS}
)
