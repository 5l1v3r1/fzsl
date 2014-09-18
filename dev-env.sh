#!/bin/bash

cleanup() {
	[ -n "${bashrc}" ] && rm -f "${bashrc}"
}

trap cleanup HUP TERM

topdir=$(realpath $(dirname $0))
bashrc=$(tempfile -d ${topdir} --prefix=.devrc)
cat > ${bashrc} <<-EOF
	[ -f ~/.bash_profile ] && source ~/.bash_profile
	source ${topdir}/virtualenv/bin/activate
	export PYTHONPATH=${topdir}:\${PYTHONPATH}
EOF

/bin/bash --rcfile ${bashrc} -i
rm -f ${bashrc}

# vim: noet
