#!/usr/bin/env bash
set -euo pipefail

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
# Progress spinner utilities
spinner() {
    local pid=$1
    local msg=$2
    local delay=0.1
    local spinstr='|/-\'
    printf "%s " "$msg"
    while kill -0 "$pid" 2>/dev/null; do
        for ((i=0; i<${#spinstr}; i++)); do
            printf "\b%s" "${spinstr:i:1}"
            sleep $delay
        done
    done
    wait "$pid"
    local rc=$?
    if [[ $rc -eq 0 ]]; then
        printf "\b✓\n"
    else
        printf "\b✗ (exit %d)\n" "$rc"
    fi
    return $rc
}

# Run a command in background and show spinner with message
run_with_spinner() {
    local msg="$1"; shift
    ("$@") &
    local pid=$!
    spinner "$pid" "$msg"
    return $?
}

# is python 3.11 if not uninstall and install python 3.11
if [[ "$PYTHON_VERSION" != 3.11* ]]; then
    echo "Python 3.11 is required. Found version $PYTHON_VERSION"
    # Check if pyenv is installed
    if ! command -v pyenv &> /dev/null; then
      echo "pyenv is not installed. Installing pyenv (this may take a few minutes)..."
      if [[ -d "$HOME/.pyenv" ]]; then
        echo "Found existing ~/.pyenv directory; reusing instead of re-installing."
      else
        run_with_spinner "Installing pyenv" bash -lc 'curl https://pyenv.run | bash'
      fi
      export PATH="$HOME/.pyenv/bin:$PATH"
      # shellcheck disable=SC2155
      export PYENV_ROOT="$HOME/.pyenv"
      eval "$(pyenv init --path)" >/dev/null 2>&1 || true
      eval "$(pyenv init -)" >/dev/null 2>&1 || true

        echo "pyenv installed. Installing Python 3.11 (this can be slow)..."
        run_with_spinner "Installing Python 3.11 via pyenv" pyenv install -s 3.11
        echo "Setting local Python version to 3.11"
        run_with_spinner "Activating Python 3.11" pyenv local 3.11
        exec "$0" "$@"
    # Check if pyenv has python 3.11 installed
    elif ! pyenv versions --bare | grep -q "^3.11"; then
        echo "Python 3.11 is not installed in pyenv. Installing (this can take a while)..."
        run_with_spinner "Installing Python 3.11 via pyenv" pyenv install -s 3.11
        echo "Setting local Python version to 3.11"
        run_with_spinner "Activating Python 3.11" pyenv local 3.11
        exec "$0" "$@"
    else
        echo "pyenv manages 3.11 but it is not active. Activating now."
        run_with_spinner "Activating Python 3.11" pyenv local 3.11
        exec "$0" "$@"
    fi
fi

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/.venv"
BACKEND_PORT="${AI_LIE_BACKEND_PORT:-8000}"
FRONTEND_PORT="${AI_LIE_FRONTEND_PORT:-5175}"

info() {
  printf "[start-workspace] %s\n" "$*"
}

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]]; then
    info "Stopping backend process $BACKEND_PID"
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT

if [[ ! -d "$VENV_DIR" ]]; then
  info "Python virtualenv missing, creating at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
else
  info "Python virtualenv already exists at $VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

REQ_HASH=$(sha256sum "$BACKEND_DIR/requirements.txt" 2>/dev/null | awk '{print $1}')
REQ_MARK="$VENV_DIR/.requirements-hash"
if [[ -f "$REQ_MARK" ]]; then
  EXISTING_HASH=$(<"$REQ_MARK")
else
  EXISTING_HASH=""
fi

if [[ "$EXISTING_HASH" != "$REQ_HASH" ]]; then
  info "Installing backend dependencies"
  pip install --upgrade pip >/dev/null
  pip install -r "$BACKEND_DIR/requirements.txt"
  printf "%s" "$REQ_HASH" > "$REQ_MARK"
else
  info "Backend dependencies already installed (requirements hash matches)"
fi

info "Starting backend on http://localhost:$BACKEND_PORT"
(
  cd "$BACKEND_DIR"
  uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload
) &
BACKEND_PID=$!

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  info "Installing frontend dependencies"
  cd "$FRONTEND_DIR"
  npm install
fi

info "Starting frontend on http://localhost:$FRONTEND_PORT"
cd "$FRONTEND_DIR"
npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT"