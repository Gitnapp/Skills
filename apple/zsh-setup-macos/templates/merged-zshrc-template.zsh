# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="robbyrussell"

plugins=(
  git
  zsh-autosuggestions
  zsh-completions
  extract
  z
  web-search
  sudo
)

source $ZSH/oh-my-zsh.sh

# ========== User's original config below ==========

# PATH
export PATH="$HOME/.local/bin:$PATH"

# NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

# Bun
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
[ -s "/Users/eric/.bun/_bun" ] && source "/Users/eric/.bun/_bun"

# Aliases
alias ccc='claude --dangerously-skip-permissions'
alias hermes="~/.hermes/hermes-agent/venv/bin/python ~/.hermes/hermes-agent/hermes"
