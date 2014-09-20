bind '"\C-x\C-E": shell-expand-line'
bind '"\C-x\C-R": redraw-current-line'
bind '"\C-t": "\e$a \eddi$(fzsl)\C-x\C-E\e0Pa \exddi\n\epa \C-x\C-R"'
bind -m vi-command '"\C-t": "i\C-t"'

