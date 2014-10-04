#!/bin/bash

cleanup() {
	[ -n "${bashrc}" ] && rm -f "${bashrc}"
}

trap cleanup HUP TERM

topdir=$(realpath $(dirname $0))
bashrc=$(mktemp --tmpdir=${topdir} .devrc-XXXXXX)

make dev-install

cat > ${bashrc} <<-EOF
	[ -f ~/.bash_profile ] && source ~/.bash_profile
	source ${topdir}/virtualenv/bin/activate
	source ${topdir}/virtualenv/etc/fzsl/fzsl.bash
	__fzsl_bind_default_matching
	__fzsl_create_fzcd
EOF

/bin/bash --rcfile ${bashrc} -i
rm -f ${bashrc}

# vim: noet
