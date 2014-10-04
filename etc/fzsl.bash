# Bind fzsl to the specified keystroke.  This will allow a single
# keybinding to execute fzsl from the current directory.  The highest
# priority rule will be used to scan.
#
# Parameters:
#   $1  - If specified, the readline code for the keybinding that will
#         launch fzsl.  Defaults to ctrl+p (\C-p).
__fzsl_bind_default_matching() {
    local binding=${1:-\C-p}

    if set -o | grep -q 'vi\s*on'; then
        bind '"\C-x\C-E": shell-expand-line'
        bind '"\C-x\C-R": redraw-current-line'
        bind "'${binding}': '\e\$a \eddi\$(fzsl)\C-x\C-E\e0Pa \exddi\n\epa \C-x\C-R'"
        bind -m vi-command "'${binding}': 'i${binding}'"
    else
        bind '"\eR": redraw-current-line'
        bind "${binding}': ' \C-u \C-a\C-k\$(fzsl)\e\C-e\C-y\C-a\C-y\ey\C-a\C-k\n\C-y\C-e\eR \C-h'"
    fi
}



