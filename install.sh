#!/bin/bash
# ─────────────────────────────────────────────────────────────
# DRKagi — One-Line Installer for Kali Linux
# Usage: curl -sL https://raw.githubusercontent.com/Bebayadamohamed17/DRKagi/main/install.sh | bash
# ─────────────────────────────────────────────────────────────

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${RED}"
echo "██████╗ ██████╗ ██╗  ██╗ █████╗  ██████╗ ██╗"
echo "██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔════╝ ██║"
echo "██║  ██║██████╔╝█████╔╝ ███████║██║  ███╗██║"
echo "██║  ██║██╔══██╗██╔═██╗ ██╔══██║██║   ██║██║"
echo "██████╔╝██║  ██║██║  ██╗██║  ██║╚██████╔╝██║"
echo "╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝"
echo -e "${NC}"
echo -e "${CYAN}DRKagi Installer v0.3${NC}"
echo ""

# ── Check if running on Kali ───────────────────────────────
if ! grep -qi 'kali' /etc/os-release 2>/dev/null; then
    echo -e "${YELLOW}[!] Warning: This doesn't appear to be Kali Linux.${NC}"
    echo -e "${YELLOW}    DRKagi works best on Kali. Continue? (y/n)${NC}"
    read -r answer
    if [ "$answer" != "y" ]; then
        echo "Aborted."
        exit 1
    fi
fi

INSTALL_DIR="$HOME/DRKagi"

# ── Clone or update repo ──────────────────────────────────
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}[*] DRKagi directory exists. Updating...${NC}"
    cd "$INSTALL_DIR"
    git pull origin main 2>/dev/null || echo -e "${YELLOW}  Could not git pull. Using existing files.${NC}"
else
    echo -e "${GREEN}[+] Cloning DRKagi...${NC}"
    git clone https://github.com/Bebayadamohamed17/DRKagi.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# ── Parse flags ──────────────────────────────────────────
FULL_INSTALL=false
for arg in "$@"; do
    [ "$arg" = "--full" ] && FULL_INSTALL=true
done

# ── Install system dependencies ────────────────────────────
echo -e "${GREEN}[+] Installing core system tools...${NC}"
sudo apt-get update -qq 2>/dev/null
sudo apt-get install -y -qq python3 python3-pip python3-venv nmap 2>/dev/null || true

if $FULL_INSTALL; then
    echo -e "${GREEN}[+] Installing full security toolkit (--full)...${NC}"
    sudo apt-get install -y -qq \
        masscan gobuster nikto hydra sqlmap smbclient smbmap \
        enum4linux whatweb wafw00f exploitdb 2>/dev/null || true
fi


# ── Create virtual environment ────────────────────────────
echo -e "${GREEN}[+] Setting up Python virtual environment...${NC}"
python3 -m venv .venv
source .venv/bin/activate

# ── Install Python dependencies ───────────────────────────
echo -e "${GREEN}[+] Installing Python dependencies...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q

# ── Create directories ───────────────────────────────────
mkdir -p logs sessions profiles plugins vault

# ── Create launch script ─────────────────────────────────
echo -e "${GREEN}[+] Creating launch command...${NC}"
sudo tee /usr/local/bin/drkagi > /dev/null << LAUNCHEOF
#!/bin/bash
cd $INSTALL_DIR
source .venv/bin/activate
python3 drkagi.py "\$@"
LAUNCHEOF
sudo chmod +x /usr/local/bin/drkagi

# ── Create drkagi-anon (AnonSurf/Tor compatible) ─────────
echo -e "${GREEN}[+] Installing drkagi-anon (AnonSurf support)...${NC}"
sudo cp "$INSTALL_DIR/drkagi-anon" /usr/local/bin/drkagi-anon
sudo chmod +x /usr/local/bin/drkagi-anon

# ── Done ─────────────────────────────────────────────────
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  DRKagi installed successfully!               ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${CYAN}API keys are embedded — no setup required.${NC}"
echo -e "  ${CYAN}Launching DRKagi now...${NC}"
echo ""
sleep 1

# ── Auto-launch ──────────────────────────────────────────
exec python3 "$INSTALL_DIR/drkagi.py"
