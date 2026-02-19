<p align="center">
  <img src="https://img.shields.io/badge/Version-0.3.0-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/AI-Groq%20Llama%203.3%2070B-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Platform-Kali%20Linux-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Tools-80%2B-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/MITRE-ATT%26CK-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

```
██████╗ ██████╗ ██╗  ██╗ █████╗  ██████╗ ██╗
██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔════╝ ██║
██║  ██║██████╔╝█████╔╝ ███████║██║  ███╗██║
██║  ██║██╔══██╗██╔═██╗ ██╔══██║██║   ██║██║
██████╔╝██║  ██║██║  ██╗██║  ██║╚██████╔╝██║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝
```

# DRKagi — AI Offensive Security Framework

> **The AI-powered penetration testing framework built for elite Red Teams.**

DRKagi combines **80+ security tools** with **AI reasoning** to automate reconnaissance, exploitation, and reporting. It thinks like a pentester — adapting attacks, evading firewalls, mapping to MITRE ATT&CK, and generating professional reports.

**⚠️ DISCLAIMER:** For **authorized security testing only**. Unauthorized use is **illegal**.

---

## 🔥 Features

| Feature | Description |
|---------|-------------|
| 🧠 **AI Brain** | Groq Llama 3.3 70B — reasons about findings and chains attacks |
| 🛡️ **80+ Tools** | Nmap, SQLMap, Hydra, Metasploit, Nuclei, BloodHound, and more |
| 👻 **Stealth by Default** | 6 firewall evasion techniques applied automatically |
| 🔑 **Multi-Key API** | Rotate up to 50 Groq keys — auto-cooldown on rate limits |
| 🤖 **Autopilot** | 4-phase automated assessment (single target or entire subnet) |
| 🎭 **AI Personas** | 5 modes: Ghost, Blitz, CTF, Recon, Web Hunter |
| 🧩 **Plugin System** | Drop `.py` scripts in `plugins/` to add custom commands |
| 🗂️ **Profiles & Sessions** | Save/resume engagements across restarts |
| 🔐 **Credential Vault** | AES-encrypted storage for discovered credentials |
| 🗺️ **MITRE ATT&CK** | Every suggestion mapped to ATT&CK technique IDs |
| 💭 **Chain-of-Thought** | See the AI's reasoning process step by step |
| 📜 **Script Generator** | AI writes custom Python/Node.js tools on demand |
| 📊 **Dashboard** | Streamlit web UI with network topology maps |
| 📄 **PDF Reports** | AI-written executive summaries + MITRE mapping |
| ✅ **Compliance** | Map findings to PCI-DSS, HIPAA, ISO 27001 |
| 🌐 **REST API** | Flask API for Burp/ZAP/tool integration |
| 🐳 **Docker** | One command: `docker run drkagi` |

---

## 🚀 Quick Start

### Option 1: One-Line Install (Kali Linux)
```bash
curl -sL https://raw.githubusercontent.com/yourusername/DRKagi/main/install.sh | bash
```

### Option 2: Manual Install
```bash
git clone https://github.com/yourusername/DRKagi.git
cd DRKagi
pip install -r requirements.txt
```

### Option 3: Docker
```bash
docker build -t drkagi .
docker run -it --env-file .env drkagi
```

### Configure
Create a `.env` file:
```ini
# Single key (optional — keys are embedded by default)
GROQ_API_KEY=gsk_your_key_here

# OR multi-key pool (recommended for heavy use)
GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3
```

> **Note:** `.env` is optional — DRKagi has a built-in key pool and works with zero configuration.

### Launch
```bash
python drkagi.py        # Interactive REPL
python drkagi.py --api  # Start REST API server
python drkagi.py --help # Show all options
```

---

## 🎮 Commands

### Scanning & AI
| Command | Description |
|---------|-------------|
| `scan <IP>` | AI-powered smart scan |
| `autopilot <IP>` | Full 4-phase assessment |
| `autopilot <CIDR>` | Autopilot entire subnet |
| Any text | AI picks the right tool |

### AI Personas
| Command | Description |
|---------|-------------|
| `persona stealth` | 👻 Ghost — maximum evasion |
| `persona aggressive` | ⚡ Blitz — speed over stealth |
| `persona ctf` | 🏴 CTF — flag hunting mode |
| `persona recon` | 🔍 Recon — passive intelligence |
| `persona web` | 🌐 Web — SQLi/XSS specialist |
| `persona off` | Reset to default |

### Tools & Scripting
| Command | Description |
|---------|-------------|
| `write script <task>` | Generate Python script |
| `write script node <task>` | Generate Node.js script |
| `simulate <scenario>` | Model attack (no execution) |
| `wordlist <target>` | AI-generated targeted wordlist |
| `compliance <framework>` | PCI/HIPAA/ISO compliance check |
| `attack map` | Generate attack path diagram |

### Data Management
| Command | Description |
|---------|-------------|
| `profile save <n>` / `load <n>` | Save/load engagement profiles |
| `session save <n>` / `load <n>` | Save/resume AI conversations |
| `vault add` / `list` / `export` | Credential vault |
| `show targets` | List discovered assets |
| `generate pdf` | Create PDF report |
| `dashboard` | Launch web UI |

### Utility
| Command | Description |
|---------|-------------|
| `status` | Show middleware + stats |
| `history` | Command history |
| `export md` | Export session to Markdown |
| `plugins` / `plugins reload` | Plugin management |
| `mode local` / `mode ssh` | Switch execution mode |
| `clear` | Clear terminal |

---

## 🎭 AI Personas

Switch between specialized AI personalities:

| Persona | Focus | Example |
|---------|-------|---------|
| 👻 **Ghost** | Maximum stealth, -T0, decoys, proxychains | `persona stealth` |
| ⚡ **Blitz** | All ports, -T5, aggressive detection | `persona aggressive` |
| 🏴 **CTF** | Flags, default creds, GTFOBins | `persona ctf` |
| 🔍 **Recon** | Passive OSINT, no active scanning | `persona recon` |
| 🌐 **Web** | SQLi, XSS, SSRF, auth bypass | `persona web` |

---

## 🗺️ MITRE ATT&CK Integration

Every AI suggestion includes the relevant ATT&CK technique:
```
  Thinking: Target has SSH on port 22. Credential attack is the logical next step.
  Explanation: Brute force SSH credentials using common wordlist
  Risk: High  |  Tool: hydra
  MITRE: T1110 (Brute Force)
  Command: hydra -L users.txt -P passwords.txt ssh://10.10.10.5
```

---

## 🧩 Plugin System

Create custom commands by dropping `.py` files in `plugins/`:

```python
# plugins/my_plugin.py
COMMAND = "portsweep"
DESCRIPTION = "Quick TCP sweep of common ports"

def run(args, context):
    console = context["console"]
    console.print(f"[green]Sweeping {args}...[/green]")
```

---

## 🌐 REST API

Start the API server: `python drkagi.py --api`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/suggest` | POST | AI suggestion for a task |
| `/api/analyze` | POST | Analyze command output |
| `/api/script` | POST | Generate security script |
| `/api/targets` | GET | List discovered targets |
| `/api/simulate` | POST | Simulate attack scenario |
| `/api/cve` | GET | CVE lookup by service |

---

## 🏗️ Architecture

```
DRKagi/
├── drkagi.py              # Core REPL (30+ commands)
├── agent.py             # AI brain (MITRE, CoT, personas)
├── api_middleware.py     # Multi-key rotation + cooldown
├── executor.py          # Local command execution
├── ssh_client.py        # SSH execution (optional)
├── config.py            # Environment config
├── database.py          # SQLite storage
├── logger.py            # JSONL session logging
├── cve_lookup.py        # NVD CVE lookup
├── pdf_reporter.py      # PDF report generator
├── dashboard.py         # Streamlit web dashboard
├── profiles.py          # Engagement profiles
├── plugin_loader.py     # Plugin system
├── session_manager.py   # Session resume
├── personas.py          # 5 AI personas
├── vault.py             # Encrypted credential vault
├── api_server.py        # Flask REST API
├── Dockerfile           # Kali Docker image
├── install.sh           # One-line installer
└── plugins/             # Custom plugins
```

---

## 🤝 Contributing

Contributions welcome! Open an issue or PR.

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Built with ❤️ for the security community</b><br>
  <i>DRKagi v0.3.0 — Think like an attacker. Act like a professional.</i>
</p>
