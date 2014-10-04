__fzsl_bind_default_matching() {
    if set -o | grep -q 'vi\s*on'; then
        bind '"\C-x\C-E": shell-expand-line'
        bind '"\C-x\C-R": redraw-current-line'
        bind '"\C-t": "\e$a \eddi$(fzsl)\C-x\C-E\e0Pa \exddi\n\epa \C-x\C-R"'
        bind -m vi-command '"\C-t": "i\C-t"'
    else
        bind '"\eR": redraw-current-line'
        bind '"\C-t": " \C-u \C-a\C-k$(fzsl)\e\C-e\C-y\C-a\C-y\ey\C-a\C-k\n\C-y\C-e\eR \C-h"'
    fi
}



