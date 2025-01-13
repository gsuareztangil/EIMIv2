#!/bin/sh
(
BINARIES_DIR="${0%/*}/"
cd ${BINARIES_DIR}

if [ "${1}" = "serial-only" ]; then
    EXTRA_ARGS='-serial stdio -display none'
else
    EXTRA_ARGS='-serial stdio'
fi

export PATH="/home/dankitani/Descargas/buildroot-2023.02/output/host/bin:${PATH}"
exec qemu-system-sh4 -M r2d -kernel zImage -drive file=rootfs.ext2,if=ide,format=raw -append "rootwait root=/dev/sda console=ttySC1,115200 noiotrap" -serial null  -net nic,model=rtl8139 -net user  ${EXTRA_ARGS}
)
