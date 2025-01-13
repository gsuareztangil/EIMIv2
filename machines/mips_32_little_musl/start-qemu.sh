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
exec qemu-system-mipsel -M malta -kernel vmlinux  -drive file=rootfs.ext2,format=raw -append "rootwait root=/dev/sda" -net nic,model=pcnet -net user  ${EXTRA_ARGS}
)
