FuZzy SheLl

Fuzzy file or path  searcher in the shell which provides path
completion similar to ctrlp.  Start a command and then hit Ctrl+t
to see a list of possible paths.  Enter search terms to narrow
down the list and then select the appropriate completion using
your arrow keys or Ctrl+j/k.

INSTALL:
    python setup.py install
    echo "source /etc/fzsl/fzsl.bash" >> ~/.bash_profile

Thanks to:
    Kien for hooking me on fuzzy path completion.
        https://github.com/kien/ctrlp.vim
    Junegunn for exposing me to shell-expand-line
        https://github.com/junegunn/fzf

