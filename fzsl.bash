
__fzsl_expand() {
    # TODO:  obviously this needs a real path
    python ~/scm/fzsl/fzsl/ui.py
}

bind '"\C-x\C-E": shell-expand-line'
bind '"\C-x\C-R": redraw-current-line'
bind '"\C-t": "\e$a \eddi$(__fzsl_expand)\C-x\C-E\e0Pa \exddi\n\epa \C-x\C-R"'
bind -m vi-command '"\C-t": "i\C-t"'
