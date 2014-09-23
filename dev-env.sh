#!/bin/bash

cleanup() {
	[ -n "${bashrc}" ] && rm -f "${bashrc}"
}

trap cleanup HUP TERM

topdir=$(realpath $(dirname $0))
bashrc=$(mktemp --tmpdir=${topdir} .devrc-XXXXXX)

cat > ${bashrc} <<-EOF
	[ -f ~/.bash_profile ] && source ~/.bash_profile
	source ${topdir}/virtualenv/bin/activate
	export PYTHONPATH=${topdir}:\${PYTHONPATH}
	export PATH=${topdir}/bin:\${PATH}
EOF

/bin/bash --rcfile ${bashrc} -i
rm -f ${bashrc}

# vim: noet
