FuZzy SheLl

Fuzzy file or path  searcher in the shell which provides path
completion similar to ctrlp.  Start a command and then hit Ctrl+p
to see a list of possible paths.  Enter search terms to narrow
down the list and then select the appropriate completion using
your arrow keys or Ctrl+j/k.

INSTALL:
    python setup.py install
    echo "source /etc/fzsl/fzsl.bash" >> ~/.bash_profile
    echo "__fzsl_bind_default_matching" >> ~/.bash_profile
    echo "__fzsl_create_fzcd" >> ~/.bash_profile

COMMANDS:
    fzcd:  Created with __fzsl_create_fzcd, this function will
        launch a fuzzy matcher which only scans directories.  On
        selection, the current working directory will be changed.
    ctrl-p:  Created with __fzsl_bind_default_matching, this
        binds ctrl-p to a fuzzy matcher which selects the best
        rule for the current directory and expands the current
        command line.

Thanks to:
    Kien for hooking me on fuzzy path completion.
        https://github.com/kien/ctrlp.vim
    Junegunn for exposing me to shell-expand-line
        https://github.com/junegunn/fzf

