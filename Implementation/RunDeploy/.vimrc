"git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/vundle
":BundleInstall
"vundle
set nocompatible               " be iMproved
filetype off                   " required!

set rtp+=~/.vim/bundle/vundle/
call vundle#rc()

""""""""""""""""""""""""""""""""
" Vendle
""""""""""""""""""""""""""""""""
" let Vundle manage Vundle
"  " required!
Bundle 'gmarik/vundle'

" Tagbar
Bundle 'Tagbar'
map <C-J> :Tagbar<CR>
" nerd tree
Bundle 'scrooloose/nerdtree'
noremap <C-H> :NERDTreeToggle<CR>
nmap <C-Y> :NERDTreeFind<CR><CR>

" nerd commenter
Bundle 'scrooloose/nerdcommenter'
let NERDSpaceDelims=1
" easymotion
Bundle 'Lokaltog/vim-easymotion'
map f <Plug>(easymotion-bd-w)
let g:EasyMotion_use_upper = 1
let g:EasyMotion_keys = 'SADFJKLEWCMPGH'

" cscope_maps: :cscope
Bundle 'cscope_macros.vim'
set cscopetag
set csto=0

if filereadable("cscope.out")
   cs add cscope.out
elseif $CSCOPE_DB != ""
    cs add $CSCOPE_DB
endif
set cscopeverbose

nmap zs :cs find s <C-R>=expand("<cword>")<CR><CR>
nmap zg :cs find g <C-R>=expand("<cword>")<CR><CR>
nmap zc :cs find c <C-R>=expand("<cword>")<CR><CR>
nmap zt :cs find t <C-R>=expand("<cword>")<CR><CR>
nmap ze :cs find e <C-R>=expand("<cword>")<CR><CR>
nmap zf :cs find f <C-R>=expand("<cfile>")<CR><CR>
nmap zi :cs find i ^<C-R>=expand("<cfile>")<CR>$<CR>
nmap zd :cs find d <C-R>=expand("<cword>")<CR><CR>



" ack
Bundle 'mileszs/ack.vim'
map <C-N> :Ack! <cword><CR>

syntax on
set encoding=utf-8
set background=dark
set expandtab
set tabstop=4
set shiftwidth=4
set number
"set term=builtin_ansi
color desert
set cursorline
hi CursorLine term=bold cterm=bold guibg=Grey
"hi CursorLine cterm=none ctermbg=DarkMagenta ctermfg=Grey guibg=Grey
set hlsearch
highlight Visual cterm=bold ctermbg=DarkMagenta ctermfg=NONE
highlight Search cterm=bold ctermbg=DarkMagenta ctermfg=NONE
packadd termdebug
