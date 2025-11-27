# https://raw.githubusercontent.com/mshlain/test/refs/heads/main/config/debian/.bashrc
#
# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=50000
HISTFILESIZE=100000
HISTIGNORE="ls:ll:cd:pwd:exit:date:clear:history"
HISTTIMEFORMAT="%F %T  "  # Human-readable: YYYY-MM-DD HH:MM:SS
shopt -s cmdhist lithist

# Save history immediately after each command
PROMPT_COMMAND="history -a; history -c; history -r${PROMPT_COMMAND:+; $PROMPT_COMMAND}"

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
shopt -s globstar

# Better shell options
shopt -s cdspell        # Auto-correct minor spelling errors in cd
shopt -s dirspell       # Auto-correct directory names
shopt -s nocaseglob     # Case-insensitive globbing
shopt -s autocd 2>/dev/null  # Just type directory name to cd

# make less more friendly for non-text input files, see lesspipe(1)
#[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# Colored man pages
export LESS_TERMCAP_mb=$'\e[1;32m'
export LESS_TERMCAP_md=$'\e[1;36m'
export LESS_TERMCAP_me=$'\e[0m'
export LESS_TERMCAP_se=$'\e[0m'
export LESS_TERMCAP_so=$'\e[01;44;33m'
export LESS_TERMCAP_ue=$'\e[0m'
export LESS_TERMCAP_us=$'\e[1;4;31m'

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color|*-256color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

# Git branch in prompt
parse_git_branch() {
    git branch 2>/dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}

if [ "$color_prompt" = yes ]; then
    # Badass prompt: user@host:path (git-branch) [exit-status] $ 
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[33m\]$(parse_git_branch)\[\033[00m\]\[\033[31m\]$([ $? != 0 ] && echo " [✗]")\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w$(parse_git_branch)\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias dir='dir --color=auto'
    alias vdir='vdir --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
    alias diff='diff --color=auto'
    alias ip='ip --color=auto'
fi

# colored GCC warnings and errors
export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# ============ BADASS SERVER ALIASES ============

# Enhanced ls aliases
alias ll='ls -lAhF --group-directories-first'
alias la='ls -A'
alias l='ls -CF'
alias lt='ls -lhArt'  # Sort by date, recent last
alias lsize='ls -lhSr'  # Sort by size
alias lx='ll -BX'  # Sort by extension

# Safety nets
alias rm='rm -I --preserve-root'
alias mv='mv -i'
alias cp='cp -i'
alias ln='ln -i'
alias chown='chown --preserve-root'
alias chmod='chmod --preserve-root'
alias chgrp='chgrp --preserve-root'

# Directory navigation
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias .4='cd ../../../..'
alias .5='cd ../../../../..'

# System monitoring
alias df='df -h'
alias du='du -h'
alias free='free -h'
alias ps='ps auxf'
alias psg='ps aux | grep -v grep | grep -i -e VSZ -e'
alias ports='netstat -tulanp'
alias listening='lsof -i -P -n | grep LISTEN'
alias meminfo='free -h -l -t'
alias cpuinfo='lscpu'
alias top='htop 2>/dev/null || top'

# Network
alias myip='curl -s ifconfig.me'
alias localip='hostname -I'
alias netstat='ss'
alias ping='ping -c 5'
alias fastping='ping -c 100 -i 0.2'

# Systemd shortcuts
alias syslog='journalctl -xe'
alias sysfail='systemctl --failed'
alias syslist='systemctl list-units --type=service'
alias sysenable='systemctl enable'
alias sysdisable='systemctl disable'
alias sysstart='systemctl start'
alias sysstop='systemctl stop'
alias sysrestart='systemctl restart'
alias sysstatus='systemctl status'

# Misc utilities
alias wget='wget -c'  # Continue downloads by default
alias histg='history | grep'
alias now='date +"%Y-%m-%d %H:%M:%S"'
alias path='echo -e ${PATH//:/\\n}'
alias mounted='mount | column -t'
alias busy='cat /dev/urandom | hexdump -C | grep "ca fe"'  # Fake busy

# Quick edits
alias ebash='${EDITOR:-nano} ~/.bashrc'
alias sbash='source ~/.bashrc'

# ============ USEFUL FUNCTIONS ============

# Extract any archive
extract() {
    if [ -f $1 ]; then
        case $1 in
            *.tar.bz2)   tar xjf $1     ;;
            *.tar.gz)    tar xzf $1     ;;
            *.bz2)       bunzip2 $1     ;;
            *.rar)       unrar x $1     ;;
            *.gz)        gunzip $1      ;;
            *.tar)       tar xf $1      ;;
            *.tbz2)      tar xjf $1     ;;
            *.tgz)       tar xzf $1     ;;
            *.zip)       unzip $1       ;;
            *.Z)         uncompress $1  ;;
            *.7z)        7z x $1        ;;
            *)           echo "'$1' cannot be extracted" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

# Create and cd into directory
mkcd() {
    mkdir -p "$1" && cd "$1"
}

# Find process by name
psfind() {
    ps aux | grep -v grep | grep -i -e VSZ -e "$1"
}

# Show disk usage of current directory
diskusage() {
    du -sh * 2>/dev/null | sort -h
}

# Find large files
findbig() {
    find . -type f -size +${1:-100M} -exec ls -lh {} \; 2>/dev/null | awk '{ print $9 ": " $5 }'
}

# Quick backup of a file
bak() {
    cp "$1" "$1.bak_$(date +%Y%m%d_%H%M%S)"
}

# Show server info
serverinfo() {
    echo -e "\n${BLUE}Server Information:${NC}"
    echo -e "${GREEN}Hostname:${NC} $(hostname)"
    echo -e "${GREEN}Kernel:${NC} $(uname -r)"
    echo -e "${GREEN}OS:${NC} $(cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '"')"
    echo -e "${GREEN}Uptime:${NC} $(uptime -p)"
    echo -e "${GREEN}Load Average:${NC} $(uptime | awk -F'load average:' '{print $2}')"
    echo -e "${GREEN}Memory:${NC} $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo -e "${GREEN}Disk Usage:${NC} $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
    echo ""
}

# Colors for functions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi
# ============ KUBERNETES/MICROK8S ALIASES ============
alias kubectl='microk8s.kubectl'
alias k='microk8s.kubectl'
alias kg='kubectl get'
alias kd='kubectl describe'
alias kdel='kubectl delete'
alias kl='kubectl logs'
alias kx='kubectl exec -it'
alias kn='kubectl config set-context --current --namespace'
alias kctx='kubectl config current-context'
alias kns='kubectl get namespaces'
alias kpods='kubectl get pods -A'
alias ksvc='kubectl get svc -A'
alias kdep='kubectl get deployments -A'
alias knode='kubectl get nodes'
alias helm='microk8s.helm'

# Kubectl bash completion
source <(microk8s.kubectl completion bash)
complete -F __start_kubectl k

export KUBE_EDITOR=/usr/bin/nano

# ============ CUSTOM APP ALIASES ============
alias appliance-manager='. /opt/zerto/zlinux/zvml-menu/appliance-manager.sh'
# appliance-manager  # Uncomment to auto-launch on shell start
