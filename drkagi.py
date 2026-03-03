# coding: utf-8
"""
DRKagi v0.3 - AI Offensive Security Framework
Main entry point — Local execution only (Kali Linux native).
"""

import argparse
import json
import os
import sys
import subprocess
import ipaddress
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from config import config
from executor import LocalExecutor
from agent import PentestAgent
from logger import SessionLogger
from database import DatabaseManager
from cve_lookup import CVELookup
from profiles import ProfileManager
from plugin_loader import PluginLoader
from session_manager import SessionManager
from personas import get_persona, list_personas, DEFAULT_PERSONA
from vault import CredentialVault

VERSION = "0.4.0"
console = Console()


# ═══════════════════════════════════════════════════════════════
# BANNER & HELP
# ═══════════════════════════════════════════════════════════════

def print_banner():
    banner = (
        "\n"
        "██████╗ ██████╗ ██╗  ██╗ █████╗  ██████╗ ██╗\n"
        "██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔════╝ ██║\n"
        "██║  ██║██████╔╝█████╔╝ ███████║██║  ███╗██║\n"
        "██║  ██║██╔══██╗██╔═██╗ ██╔══██║██║   ██║██║\n"
        "██████╔╝██║  ██║██║  ██╗██║  ██║╚██████╔╝██║\n"
        "╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝"
    )
    console.print(f"[bold red]{banner}[/bold red]")
    console.print(Panel.fit(
        "[bold white]DRKagi Offensive Security Framework[/bold white]\n"
        "[dim]Advanced Penetration Testing & Red Team Operations[/dim]\n"
        f"[cyan]Version: {VERSION}[/cyan]  |  [yellow]Model: {config.MODEL_NAME}[/yellow]\n"
        "[dim]License: Authorized Security Testing Only[/dim]",
        border_style="red"
    ))
    console.print()
    console.print("[dim][+] Initializing core engine...[/dim]")
    console.print("[dim][+] Loading reconnaissance modules (80+ tools)...[/dim]")
    try:
        from api_middleware import get_middleware
        status = get_middleware().get_status()
        console.print(f"[dim][+] API Middleware: {status['total_keys']} keys loaded[/dim]")
    except Exception:
        console.print("[dim][+] API Middleware: active[/dim]")
    console.print("[dim][+] MITRE ATT&CK mapping: enabled[/dim]")
    console.print("[dim][+] Establishing secure runtime context...[/dim]")
    console.print(f"[bold green][+] DRKagi v{VERSION} ready.[/bold green]")
    console.print()


def print_help(persona_name=None):
    persona_str = f" | persona: {persona_name}" if persona_name else ""
    console.print(Panel(
        "[bold cyan]DRKagi Commands[/bold cyan]\n\n"

        "[yellow]Scanning & AI:[/yellow]\n"
        "  target <IP>            - Set target and start smart scan\n"
        "  scan <IP>              - Smart scan a target\n"
        "  scan <CIDR>            - Scan entire subnet\n"
        "  Any natural language   - AI picks the right tool\n\n"

        "[yellow]Autopilot:[/yellow]\n"
        "  autopilot <IP>         - Full 4-phase automated assessment\n"
        "  autopilot <CIDR>       - Autopilot entire subnet\n\n"

        "[yellow]Script Generator:[/yellow]\n"
        "  write script <task>    - Generate Python script\n"
        "  write script node <t>  - Generate Node.js script\n\n"

        "[yellow]Simulation:[/yellow]\n"
        "  simulate <scenario>    - Model attack (no execution)\n"
        "  what if <scenario>     - Same as simulate\n\n"

        "[yellow]AI Personas:[/yellow]\n"
        "  persona <name>         - Switch AI mode (stealth/aggressive/ctf/recon/web)\n"
        "  persona list           - Show all personas\n"
        "  persona off            - Reset to default\n\n"

        "[yellow]Profiles & Sessions:[/yellow]\n"
        "  profile save <name>    - Save current engagement\n"
        "  profile load <name>    - Load saved engagement\n"
        "  profile list           - List all profiles\n"
        "  session save <name>    - Save AI conversation\n"
        "  session load <name>    - Resume conversation\n"
        "  session list           - List saved sessions\n\n"

        "[yellow]Credential Vault:[/yellow]\n"
        "  vault add              - Store a credential\n"
        "  vault list             - Show stored creds (masked)\n"
        "  vault export           - Export to file\n\n"

        "[yellow]Wordlists:[/yellow]\n"
        "  wordlist <target>      - AI-generated targeted wordlist\n\n"

        "[yellow]Compliance:[/yellow]\n"
        "  compliance <framework> - Map findings (pci/hipaa/iso27001)\n\n"

        "[yellow]Visualization:[/yellow]\n"
        "  attack map             - Generate attack path diagram\n\n"

        "[yellow]Tools:[/yellow]\n"
        "  status                 - API middleware + stats\n"
        "  plugins                - List loaded plugins\n"
        "  plugins reload         - Reload plugins\n\n"

        "[yellow]Reports & Data:[/yellow]\n"
        "  generate pdf           - PDF report\n"
        "  show targets           - List discovered targets\n"
        "  dashboard              - Web dashboard\n"
        "  export md              - Export session to Markdown\n\n"

        "[yellow]General:[/yellow]\n"
        "  history                - Show command history\n"
        "  clear                  - Clear screen\n"
        "  help                   - This menu\n"
        "  exit / quit            - Exit\n\n"
        "[dim]Type any question or task — AI understands context.[/dim]",
        title=f"DRKagi Help{persona_str}",
        border_style="cyan"
    ))


# ═══════════════════════════════════════════════════════════════
# INTERACTIVE MENU
# ═══════════════════════════════════════════════════════════════

MENU_ITEMS = [
    # (number, category, label, command_to_run)
    ("1",  "SCAN",      "Port Scan (quick)",          "__scan_prompt__"),
    ("2",  "SCAN",      "Vulnerability Scan (deep)",  "__vscan_prompt__"),
    ("3",  "SCAN",      "Autopilot (full auto)",       "__autopilot_prompt__"),
    ("4",  "SCAN",      "Show all discovered targets", "show targets"),
    ("5",  "REPORT",    "Generate PDF Report",         "generate pdf"),
    ("6",  "REPORT",    "Export session to Markdown",  "export md"),
    ("7",  "REPORT",    "Attack Map (Mermaid)",         "attack map"),
    ("8",  "TOOLS",     "Dashboard (Web UI)",           "dashboard"),
    ("9",  "TOOLS",     "Credential Vault",             "vault list"),
    ("10", "TOOLS",     "Generate Wordlist",            "__wordlist_prompt__"),
    ("11", "TOOLS",     "Script Generator",             "__script_prompt__"),
    ("12", "TOOLS",     "Simulate Attack Scenario",     "__simulate_prompt__"),
    ("13", "SESSION",   "Save Session",                 "__session_save__"),
    ("14", "SESSION",   "Load Session",                 "__session_load__"),
    ("15", "SESSION",   "Command History",              "history"),
    ("16", "AI",        "Switch AI Persona",            "persona list"),
    ("17", "AI",        "API & System Status",          "status"),
    ("18", "AI",        "List Plugins",                 "plugins"),
    ("0",  "GENERAL",   "Exit DRKagi",                  "exit"),
]

CATEGORY_COLORS = {
    "SCAN":    "bold red",
    "REPORT":  "bold blue",
    "TOOLS":   "bold yellow",
    "SESSION": "bold green",
    "AI":      "bold magenta",
    "GENERAL": "dim",
}

def show_menu():
    """Display a Rich interactive numbered menu."""
    from rich.columns import Columns
    console.print()
    console.print("[bold red] DRKagi — Quick Menu[/bold red]")
    console.print("[dim] Type a number and press Enter[/dim]\n")

    current_cat = None
    for num, cat, label, _ in MENU_ITEMS:
        if cat != current_cat:
            current_cat = cat
            color = CATEGORY_COLORS.get(cat, "white")
            console.print(f"  [{color}]── {cat} ──[/{color}]")
        console.print(f"    [bold cyan]{num:>2}[/bold cyan]  {label}")
    console.print()

    choice = console.input("[bold white]  Choose (0-18): [/bold white]").strip()
    # Find matching item
    for num, cat, label, cmd in MENU_ITEMS:
        if choice == num:
            return cmd, label
    return None, None


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def handle_show_targets(db):
    targets = db.get_all_targets()
    if targets:
        table = Table(title="Discovered Targets", border_style="cyan")
        table.add_column("IP", style="bold")
        table.add_column("Hostname")
        table.add_column("Status", style="green")
        table.add_column("Last Scanned", style="dim")
        for t in targets:
            table.add_row(t[0], t[1] or "N/A", t[2] or "Up", str(t[3] or ""))
        console.print(table)
    else:
        console.print("[dim]  Database is empty. Run a scan first.[/dim]")


def handle_pdf_report(agent, logger):
    try:
        from pdf_reporter import PDFReporter
    except ImportError:
        console.print("[red]  reportlab not installed. Run: pip install reportlab[/red]")
        return
    console.print("[bold green][+] Generating PDF Report...[/bold green]")
    summary = agent.summarize_session(logger.get_session_data())
    reporter = PDFReporter()
    filename = f"DRKagi_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    if reporter.generate_report(filename, executive_summary=summary):
        console.print(f"[bold blue][+] Saved: [underline]{filename}[/underline][/bold blue]")
    else:
        console.print("[bold red][-] PDF generation failed.[/bold red]")


def _truncate_output(text, max_lines=60):
    """Truncate long command output for clean display."""
    if not text:
        return text
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    shown = "\n".join(lines[:max_lines])
    hidden = len(lines) - max_lines
    return shown + f"\n[dim]  ... {hidden} more lines. Use 'export md' to see full output.[/dim]"


def display_suggestion(suggestion, show_thinking=True):
    """Display AI suggestion in clean chat format."""
    thinking    = suggestion.get('thinking', '')
    explanation = suggestion.get('explanation', '')
    command     = suggestion.get('command')
    risk        = suggestion.get('risk_level', 'None')
    tool        = suggestion.get('tool_used', '')
    mitre       = suggestion.get('mitre_id', '')

    console.print()  # blank line before AI response

    # Chain-of-thought — very subtle
    if show_thinking and thinking:
        console.print(f"[dim]   ↳ {thinking}[/dim]")

    # AI : label + explanation on same line
    risk_str = ""
    if risk and risk != 'None':
        risk_color = {"Low": "green", "Medium": "yellow", "High": "red", "Critical": "bold red"}.get(risk, "white")
        risk_str = f" [{risk_color}][{risk}][/{risk_color}]"
    tool_str  = f" — [cyan]{tool}[/cyan]" if tool else ""
    mitre_str = f" [[magenta]{mitre}[/magenta]]" if mitre else ""

    console.print(f"[bold green]   AI :[/bold green] {explanation}{risk_str}{tool_str}{mitre_str}")

    if command:
        console.print(f"[bold cyan]      $[/bold cyan] {command}")

    console.print("[dim]   ─────────────────────────────────────[/dim]")
    return command


def store_findings(full_output, command, agent, db, cve_search, console):
    """Extract and store findings from command output (silent)."""
    if not full_output.strip():
        return
    try:
        db_text = agent.extract_findings_for_db(command, full_output)
        db_data = json.loads(db_text.strip().replace('```json', '').replace('```', ''))
        for t in db_data.get('targets', []):
            db.add_target(t.get('ip'), t.get('hostname'), t.get('status'))
        vuln_count = 0
        for p in db_data.get('ports', []):
            tid = db.add_target(p.get('ip'))
            if tid:
                db.add_port(tid, p.get('port'), p.get('service'), p.get('state'), p.get('version'))
                service = p.get('service')
                version = p.get('version')
                if version and service and service != 'unknown':
                    vulns = cve_search.search_cve(service, version)
                    for v in vulns:
                        db.add_vulnerability(tid, None, v['id'], v['severity'], v['description'])
                        vuln_count += 1
                        console.print(f"  [bold red][!] {v['id']} [{v['severity']}] — {service} {version}[/bold red]")
    except Exception:
        pass  # Silent — DB errors don't break the flow


# ═══════════════════════════════════════════════════════════════
# AUTOPILOT
# ═══════════════════════════════════════════════════════════════

def run_autopilot(target_ip, agent, local_exec, db, cve_search, logger):
    console.print(Panel(
        f"[bold red]AUTOPILOT MODE ENGAGED[/bold red]\n"
        f"[yellow]Target: {target_ip}[/yellow]\n"
        "[dim]All phases run automatically. Ctrl+C to abort.[/dim]",
        border_style="red"
    ))

    phases = [
        ("RECON",    f"quick stealth port scan of {target_ip} to find open ports and services"),
        ("ENUM",     f"enumerate all discovered open ports and services on {target_ip} in detail"),
        ("VULNSCAN", f"check for known vulnerabilities on all services found on {target_ip}"),
        ("EXPLOIT",  f"search for exploits for all discovered services on {target_ip} using searchsploit"),
    ]

    for phase_name, task in phases:
        console.print(f"\n[bold yellow][ AUTOPILOT - {phase_name} ][/bold yellow] {task}")
        logger.log("AUTOPILOT", task, {"phase": phase_name, "target": target_ip})

        with console.status(f"[bold yellow]  AI planning {phase_name}...[/bold yellow]"):
            resp_text = agent.get_suggestion(task)

        try:
            clean = resp_text.strip().replace('```json', '').replace('```', '')
            suggestion = json.loads(clean)
            cmd = suggestion.get('command')
            console.print(f"  [bold cyan]Command:[/bold cyan] {cmd}")
            console.print(f"  [dim]{suggestion.get('explanation', '')}[/dim]")
            mitre = suggestion.get('mitre_id')
            if mitre:
                console.print(f"  [magenta]MITRE: {mitre}[/magenta]")

            if not cmd:
                continue

            stdout, stderr = local_exec.execute(cmd, timeout=180)
            full_out = (stdout or "") + (stderr or "")
            if stdout:
                console.print(f"\n[green]{stdout[:3000]}[/green]")
            if stderr:
                console.print(f"\n[dim red]{stderr[:1000]}[/dim red]")

            logger.log("AUTOPILOT_RESULT", full_out[:5000], {"command": cmd, "phase": phase_name})

            if full_out.strip():
                with console.status("[dim]  Storing findings...[/dim]"):
                    store_findings(full_out, cmd, agent, db, cve_search, console)

        except Exception as e:
            console.print(f"  [red]  Phase error: {e}[/red]")
            continue

    console.print(Panel(
        "[bold green][+] AUTOPILOT COMPLETE[/bold green]\n"
        "Type 'generate pdf' for a full report.\n"
        "Type 'show targets' to see discoveries.\n"
        "Type 'attack map' to visualize the attack path.",
        border_style="green"
    ))


def run_multi_autopilot(cidr, agent, local_exec, db, cve_search, logger):
    """Autopilot for entire subnet — discover hosts then autopilot each."""
    console.print(Panel(
        f"[bold red]MULTI-TARGET AUTOPILOT[/bold red]\n"
        f"[yellow]Subnet: {cidr}[/yellow]\n"
        "[dim]Phase 0: Host discovery, then full autopilot per host.[/dim]",
        border_style="red"
    ))

    discover_cmd = f"nmap -sn -T4 {cidr}"
    console.print(f"\n[bold yellow][ PHASE 0 - DISCOVERY ][/bold yellow] {discover_cmd}")
    stdout, stderr = local_exec.execute(discover_cmd, timeout=300)
    full = (stdout or "") + (stderr or "")
    console.print(f"[green]{stdout[:3000]}[/green]")

    db_text = agent.extract_findings_for_db(discover_cmd, full)
    try:
        db_data = json.loads(db_text.strip().replace('```json', '').replace('```', ''))
        live_hosts = [t['ip'] for t in db_data.get('targets', []) if t.get('ip')]
    except Exception:
        live_hosts = []

    if not live_hosts:
        console.print("[yellow]  No live hosts found.[/yellow]")
        return

    console.print(f"\n[bold green]  Found {len(live_hosts)} live hosts:[/bold green]")
    for ip in live_hosts:
        console.print(f"    [cyan]{ip}[/cyan]")

    for i, ip in enumerate(live_hosts, 1):
        console.print(f"\n{'='*60}")
        console.print(f"[bold]  HOST {i}/{len(live_hosts)}: {ip}[/bold]")
        console.print(f"{'='*60}")
        run_autopilot(ip, agent, local_exec, db, cve_search, logger)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    # ── CLI Args ──────────────────────────────────────────────
    parser = argparse.ArgumentParser(
        description="DRKagi - AI Offensive Security Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n  python drkagi.py\n  python drkagi.py --version\n  python drkagi.py --api"
    )
    parser.add_argument("--version", action="version", version=f"DRKagi v{VERSION}")
    parser.add_argument("--api", action="store_true", help="Start REST API server instead of REPL")
    args = parser.parse_args()

    if args.api:
        from api_server import app
        print(f"DRKagi REST API v{VERSION} starting on port 5000...")
        app.run(host="0.0.0.0", port=5000, debug=False)
        return

    print_banner()

    # ── Init components ──────────────────────────────────────
    logger = SessionLogger()
    db = DatabaseManager()
    cve_search = CVELookup()
    local_exec = LocalExecutor()
    profiles = ProfileManager()
    plugins = PluginLoader()
    sessions = SessionManager()
    vault = CredentialVault()
    active_persona = None
    current_target = None        # <-- context: active target IP

    try:
        agent = PentestAgent()
    except Exception as e:
        console.print(f"[bold red][-] AI Agent init failed: {e}[/bold red]")
        return

    loaded = plugins.list_plugins()
    if loaded:
        console.print(f"[dim][+] Plugins loaded: {len(loaded)}[/dim]")

    console.print("[bold green][+] Running in LOCAL mode (Kali native).[/bold green]\n")

    # ═══════════════════ MAIN LOOP ═══════════════════════════
    while True:
        try:
            p_icon = ""
            if active_persona:
                p_info = get_persona(active_persona)
                if p_info:
                    p_icon = f"{p_info['icon']} "
            tgt = f"[dim]({current_target})[/dim] " if current_target else ""
            console.rule(style="dim")
            prompt = f"{p_icon}[bold red]DRKagi[/bold red] {tgt}[bold white]>>[/bold white] "
            user_input = console.input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue
        cmd = user_input.lower().strip()

        # ── Exit ─────────────────────────────────────────────
        if cmd in ['exit', 'quit']:
            console.print("[yellow]Session ended. Stay safe.[/yellow]")
            break

        # ── Help ─────────────────────────────────────────────
        if cmd == 'help':
            print_help(active_persona)
            continue

        # ── Menu ─────────────────────────────────────────────
        if cmd in ['menu', 'm']:
            menu_cmd, menu_label = show_menu()
            if not menu_cmd:
                continue
            # Handle prompts that need user input
            if menu_cmd == '__scan_prompt__':
                ip = console.input("  [cyan]Target IP: [/cyan]").strip()
                user_input = f"scan {ip}"
            elif menu_cmd == '__vscan_prompt__':
                ip = console.input("  [cyan]Target IP: [/cyan]").strip()
                user_input = f"vulnscan {ip}"
            elif menu_cmd == '__autopilot_prompt__':
                ip = console.input("  [cyan]Target IP/CIDR: [/cyan]").strip()
                user_input = f"autopilot {ip}"
            elif menu_cmd == '__wordlist_prompt__':
                t = console.input("  [cyan]Target info: [/cyan]").strip()
                user_input = f"wordlist {t}"
            elif menu_cmd == '__script_prompt__':
                t = console.input("  [cyan]Describe the script: [/cyan]").strip()
                user_input = f"write script {t}"
            elif menu_cmd == '__simulate_prompt__':
                t = console.input("  [cyan]Scenario: [/cyan]").strip()
                user_input = f"simulate {t}"
            elif menu_cmd == '__session_save__':
                n = console.input("  [cyan]Session name: [/cyan]").strip()
                user_input = f"session save {n}"
            elif menu_cmd == '__session_load__':
                n = console.input("  [cyan]Session name: [/cyan]").strip()
                user_input = f"session load {n}"
            elif menu_cmd == 'exit':
                console.print("[yellow]Session ended. Stay safe.[/yellow]")
                break
            else:
                user_input = menu_cmd
            cmd = user_input.lower().strip()
            console.print(f"[dim]  Running: {user_input}[/dim]")
            # Fall through to normal command handlers below

        # ── Clear ────────────────────────────────────────────
        if cmd == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            continue

        # ── Set Target ───────────────────────────────────────
        if cmd.startswith('target '):
            new_target = user_input.split()[1].strip()
            current_target = new_target
            agent.set_context("target", current_target)
            console.print(f"[bold green][+] Target set: {current_target}[/bold green]")
            console.print(f"[dim]  AI will now focus all suggestions on {current_target}[/dim]")
            # Auto-suggest first action
            with console.status("[bold green]  AI is planning the first move...[/bold green]"):
                resp = agent.get_suggestion(f"I've set my target to {current_target}. What should I do first? Suggest the best initial reconnaissance command.")
            try:
                suggestion = json.loads(resp.strip().replace('```json', '').replace('```', ''))
                display_suggestion(suggestion)
            except Exception:
                pass
            continue

        # ── History ──────────────────────────────────────────
        if cmd == 'history':
            data = logger.get_session_data()
            entries = [e for e in data if e.get('type') in ['USER_INPUT', 'COMMAND_EXECUTION']]
            if entries:
                for i, e in enumerate(entries[-20:], 1):
                    tag = "CMD" if e['type'] == 'COMMAND_EXECUTION' else "USR"
                    content = str(e.get('content', ''))[:100]
                    console.print(f"  [dim]{i}.[/dim] [{tag}] {content}")
            else:
                console.print("[dim]  No history yet.[/dim]")
            continue

        # ── Status ───────────────────────────────────────────
        if cmd == 'status':
            try:
                from api_middleware import get_middleware
                s = get_middleware().get_status()
                table = Table(title="DRKagi Status", border_style="cyan")
                table.add_column("Metric", style="bold")
                table.add_column("Value", style="cyan")
                table.add_row("Version", VERSION)
                table.add_row("Active Target", current_target or "None (use 'target <IP>')")
                table.add_row("Persona", active_persona or "default")
                table.add_row("API Keys (total)", str(s['total_keys']))
                table.add_row("API Keys (active)", str(s['active_keys']))
                table.add_row("API Keys (failed)", str(s['failed_keys']))
                table.add_row("Total Requests", str(s.get('total_requests', 0)))
                table.add_row("Vault Credentials", str(vault.count()))
                table.add_row("Plugins Loaded", str(len(plugins.list_plugins())))
                console.print(table)
            except Exception as e:
                console.print(f"[red]  Error: {e}[/red]")
            continue

        # ── Export ────────────────────────────────────────────
        if cmd.startswith('export'):
            data = logger.get_session_data()
            fname = f"DRKagi_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            lines = [f"# DRKagi Session Export\n**Date:** {datetime.now().isoformat()}\n"]
            for e in data:
                lines.append(f"### [{e['type']}] {e['timestamp']}\n```\n{str(e.get('content',''))[:500]}\n```\n")
            with open(fname, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            console.print(f"[bold blue][+] Exported: {fname}[/bold blue]")
            continue

        # ── Persona ──────────────────────────────────────────
        if cmd.startswith('persona'):
            parts = user_input.split()
            if len(parts) < 2 or parts[1].lower() == 'list':
                table = Table(title="AI Personas", border_style="magenta")
                table.add_column("Key", style="bold")
                table.add_column("Name")
                table.add_column("Description")
                for p in list_personas():
                    active = " <<" if p['key'] == active_persona else ""
                    table.add_row(p['key'], f"{p['icon']} {p['name']}", p['description'] + active)
                console.print(table)
                continue
            name = parts[1].lower()
            if name == 'off':
                active_persona = None
                agent.clear_persona()
                console.print("[bold green][+] Persona reset to default.[/bold green]")
            else:
                p = get_persona(name)
                if p:
                    active_persona = name
                    agent.set_persona(p['prompt_addon'])
                    console.print(f"[bold magenta][+] Persona: {p['icon']} {p['name']} activated![/bold magenta]")
                    console.print(f"[dim]  {p['description']}[/dim]")
                else:
                    console.print(f"[red]  Unknown persona: {name}. Try: persona list[/red]")
            continue

        # ── Profiles ─────────────────────────────────────────
        if cmd.startswith('profile'):
            parts = user_input.split()
            if len(parts) < 2:
                console.print("[dim]  Usage: profile save|load|list|delete <name>[/dim]")
                continue
            action = parts[1].lower()
            if action == 'list':
                plist = profiles.list_profiles()
                if plist:
                    table = Table(title="Saved Profiles", border_style="green")
                    table.add_column("Name", style="bold")
                    table.add_column("Created")
                    table.add_column("Targets")
                    table.add_column("Vulns")
                    for p in plist:
                        table.add_row(p['name'], p['created'][:19], str(p['targets']), str(p['vulns']))
                    console.print(table)
                else:
                    console.print("[dim]  No profiles saved yet.[/dim]")
            elif action == 'save' and len(parts) >= 3:
                name = parts[2]
                fp, t, p, v = profiles.save(name)
                console.print(f"[bold green][+] Profile '{name}' saved ({t} targets, {p} ports, {v} vulns)[/bold green]")
            elif action == 'load' and len(parts) >= 3:
                name = parts[2]
                result = profiles.load(name)
                if result:
                    console.print(f"[bold green][+] Profile '{name}' loaded![/bold green]")
                else:
                    console.print(f"[red]  Profile '{name}' not found.[/red]")
            elif action == 'delete' and len(parts) >= 3:
                if profiles.delete(parts[2]):
                    console.print(f"[green]  Deleted: {parts[2]}[/green]")
                else:
                    console.print(f"[red]  Not found: {parts[2]}[/red]")
            continue

        # ── Sessions ─────────────────────────────────────────
        if cmd.startswith('session'):
            parts = user_input.split()
            if len(parts) < 2:
                console.print("[dim]  Usage: session save|load|list|delete <name>[/dim]")
                continue
            action = parts[1].lower()
            if action == 'list':
                slist = sessions.list_sessions()
                if slist:
                    table = Table(title="Saved Sessions", border_style="yellow")
                    table.add_column("Name", style="bold")
                    table.add_column("Saved At")
                    table.add_column("Messages")
                    for s in slist:
                        table.add_row(s['name'], s['saved_at'][:19], str(s['messages']))
                    console.print(table)
                else:
                    console.print("[dim]  No sessions saved.[/dim]")
            elif action == 'save' and len(parts) >= 3:
                fp = sessions.save(parts[2], agent)
                console.print(f"[bold green][+] Session '{parts[2]}' saved![/bold green]")
            elif action == 'load' and len(parts) >= 3:
                result = sessions.load(parts[2], agent)
                if result:
                    msgs = len(result.get('conversation_history', []))
                    console.print(f"[bold green][+] Session '{parts[2]}' loaded ({msgs} messages restored)[/bold green]")
                else:
                    console.print(f"[red]  Session '{parts[2]}' not found.[/red]")
            elif action == 'delete' and len(parts) >= 3:
                if sessions.delete(parts[2]):
                    console.print(f"[green]  Deleted: {parts[2]}[/green]")
            continue

        # ── Vault ────────────────────────────────────────────
        if cmd.startswith('vault'):
            parts = user_input.split()
            action = parts[1].lower() if len(parts) > 1 else 'list'
            if action == 'add':
                svc = console.input("  [cyan]Service (ssh/http/ftp): [/cyan]").strip()
                host = console.input("  [cyan]Host/IP: [/cyan]").strip()
                user = console.input("  [cyan]Username: [/cyan]").strip()
                pw = console.input("  [cyan]Password: [/cyan]").strip()
                notes = console.input("  [cyan]Notes (optional): [/cyan]").strip()
                vault.add(svc, host, user, pw, notes)
                console.print(f"[bold green][+] Credential stored![/bold green]")
            elif action == 'list':
                creds = vault.list_credentials()
                if creds:
                    table = Table(title="Credential Vault", border_style="red")
                    table.add_column("Service", style="bold")
                    table.add_column("Host")
                    table.add_column("Username")
                    table.add_column("Password", style="dim")
                    table.add_column("Found")
                    for c in creds:
                        table.add_row(c['service'], c['host'], c['username'], c['password'], c.get('found_at', '')[:10])
                    console.print(table)
                else:
                    console.print("[dim]  Vault is empty.[/dim]")
            elif action == 'export':
                fp = vault.export_txt()
                console.print(f"[bold blue][+] Exported: {fp}[/bold blue]")
            elif action == 'clear':
                vault.clear()
                console.print("[green]  Vault cleared.[/green]")
            continue

        # ── Wordlist ────────────────────────────────────────
        if cmd.startswith('wordlist'):
            target_info = ' '.join(user_input.split()[1:]) or current_target or console.input("  [cyan]Target info: [/cyan]").strip()
            console.print("[bold green][+] Generating targeted wordlist...[/bold green]")
            with console.status("[bold green]  AI analyzing target...[/bold green]"):
                result_text = agent.generate_wordlist(target_info)
            try:
                result = json.loads(result_text.strip().replace('```json', '').replace('```', ''))
                words = result.get('wordlist', [])
                fname = result.get('filename', 'drkagi_wordlist.txt')
                with open(fname, 'w') as f:
                    f.write('\n'.join(words))
                console.print(f"[bold blue][+] Wordlist saved: {fname} ({len(words)} words)[/bold blue]")
                console.print(f"[dim]  {result.get('explanation', '')}[/dim]")
            except Exception as e:
                console.print(f"[red]  Error: {e}[/red]")
            continue

        # ── Compliance ──────────────────────────────────────
        if cmd.startswith('compliance'):
            parts = user_input.split()
            framework = parts[1] if len(parts) > 1 else console.input("  [cyan]Framework (pci/hipaa/iso27001): [/cyan]").strip()
            console.print(f"[bold green][+] Running {framework.upper()} compliance check...[/bold green]")
            targets = db.get_all_targets()
            summary = f"Targets: {len(targets)}. "
            for t in targets[:10]:
                summary += f"{t[0]} ({t[2]}), "
            with console.status("[bold green]  Mapping findings...[/bold green]"):
                result_text = agent.check_compliance(framework, summary)
            try:
                result = json.loads(result_text.strip().replace('```json', '').replace('```', ''))
                console.print(f"\n[bold]{result.get('framework', framework.upper())} Compliance Report[/bold]")
                console.print(f"  Score: {result.get('overall_score', 'N/A')}")
                for m in result.get('mappings', [])[:15]:
                    color = "red" if m.get('status') == 'FAIL' else "green"
                    console.print(f"  [{color}]{m.get('status')}[/{color}] {m.get('control')}: {m.get('finding', '')}")
            except Exception as e:
                console.print(f"[red]  Error: {e}[/red]")
            continue

        # ── Attack Map ──────────────────────────────────────
        if cmd in ['attack map', 'attackmap', 'attack tree']:
            console.print("[bold green][+] Generating attack path diagram...[/bold green]")
            with console.status("[bold green]  Analyzing session...[/bold green]"):
                result_text = agent.generate_attack_tree(logger.get_session_data())
            try:
                result = json.loads(result_text.strip().replace('```json', '').replace('```', ''))
                mermaid = result.get('mermaid_code', '')
                fname = f"attack_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(f"# DRKagi Attack Map\n\n```mermaid\n{mermaid}\n```\n\n{result.get('summary', '')}")
                console.print(f"[bold blue][+] Attack map saved: {fname}[/bold blue]")
                console.print(f"[dim]  {result.get('summary', '')}[/dim]")
                console.print(f"[dim]  Open in any Mermaid viewer or GitHub to see the diagram.[/dim]")
            except Exception as e:
                console.print(f"[red]  Error: {e}[/red]")
            continue

        # ── Plugins ──────────────────────────────────────────
        if cmd.startswith('plugins'):
            if 'reload' in cmd:
                plugins.reload()
                console.print(f"[green][+] Plugins reloaded: {len(plugins.list_plugins())}[/green]")
            else:
                plist = plugins.list_plugins()
                if plist:
                    table = Table(title="Loaded Plugins", border_style="green")
                    table.add_column("Command", style="bold")
                    table.add_column("Description")
                    table.add_column("File", style="dim")
                    for p in plist:
                        table.add_row(p['command'], p['description'], p['file'])
                    console.print(table)
                else:
                    console.print("[dim]  No plugins loaded. Add .py files to plugins/[/dim]")
            continue

        # ── Show targets ─────────────────────────────────────
        if cmd in ['show targets', 'targets']:
            handle_show_targets(db)
            continue

        # ── Dashboard ────────────────────────────────────────
        if cmd in ['dashboard', 'web ui', 'gui']:
            try:
                subprocess.Popen(
                    [sys.executable, "-m", "streamlit", "run", "dashboard.py",
                     "--server.headless=true", "--server.port=8501"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                console.print("[bold green][+] Dashboard launched![/bold green]")
                console.print("  [cyan]Open: http://localhost:8501[/cyan]")
                console.print("  [dim]Ctrl+C in browser tab to stop.[/dim]")
            except FileNotFoundError:
                console.print("[red]  streamlit not installed.[/red]")
                console.print("  [dim]Run: pip install streamlit pandas pyvis[/dim]")
            continue

        # ── PDF report ───────────────────────────────────────
        if 'generate pdf' in cmd or ('report' in cmd and 'pdf' in cmd):
            handle_pdf_report(agent, logger)
            continue

        # ── Autopilot ────────────────────────────────────────
        if cmd.startswith('autopilot'):
            parts = user_input.split()
            target = parts[1] if len(parts) >= 2 else (current_target or console.input("  [cyan]Target IP/CIDR: [/cyan]").strip())
            try:
                net = ipaddress.ip_network(target, strict=False)
                if net.num_addresses > 1:
                    run_multi_autopilot(str(net), agent, local_exec, db, cve_search, logger)
                else:
                    run_autopilot(str(net.network_address), agent, local_exec, db, cve_search, logger)
            except ValueError:
                run_autopilot(target, agent, local_exec, db, cve_search, logger)
            continue

        # ── VulnScan ─────────────────────────────────────────
        if cmd.startswith('vulnscan'):
            vscan_target = user_input.split()[1] if len(user_input.split()) > 1 else current_target
            if not vscan_target:
                vscan_target = console.input("  [cyan]Target IP: [/cyan]").strip()
            console.print(f"[bold red][!] Running vulnerability scan on {vscan_target}...[/bold red]")
            console.print("[dim]  Running: nmap -sV --script vuln,auth,exploit,default[/dim]")
            vuln_cmd = f"nmap -sV -sC --script vuln,auth,exploit -T4 --open {vscan_target}"
            try:
                stdout, stderr = local_exec.execute(vuln_cmd, timeout=300)
                out = stdout or stderr or ""
                if out.strip():
                    console.print(f"\n[red]{_truncate_output(out, 80)}[/red]")
                    # Also run searchsploit on found services
                    console.print("\n[bold yellow][+] Checking searchsploit...[/bold yellow]")
                    sp_out, _ = local_exec.execute(f"searchsploit --nmap {vscan_target} 2>/dev/null || echo 'searchsploit not available'")
                    if sp_out and 'not available' not in sp_out:
                        console.print(f"[yellow]{_truncate_output(sp_out, 30)}[/yellow]")
                    with console.status("[bold red]  AI analyzing vulnerabilities...[/bold red]"):
                        analysis = agent.get_suggestion(f"Analyze these vulnerability scan results for {vscan_target} and identify the most critical issues to exploit:\n{out[:3000]}")
                    try:
                        vuln_sug = json.loads(analysis.strip().replace('```json','').replace('```',''))
                        display_suggestion(vuln_sug)
                    except Exception:
                        console.print(f"[dim]{analysis[:500]}[/dim]")
                    store_findings(out, vuln_cmd, agent, db, cve_search, console)
                else:
                    console.print("[yellow]  No output. Target may be offline or all ports filtered.[/yellow]")
            except FileNotFoundError:
                console.print("[red]  nmap not found. Install: sudo apt install nmap[/red]")
            except Exception as e:
                console.print(f"[red]  Scan error: {e}[/red]")
            continue

        # ── Scan (shortcut) ──────────────────────────────────
        if cmd.startswith('scan '):
            scan_target = user_input.split()[1] if len(user_input.split()) > 1 else current_target
            if not scan_target:
                console.print("[red]  Usage: scan <IP>[/red]")
                continue
            current_target = scan_target
            agent.set_context("target", current_target)
            console.print(f"[bold green][+] Scanning {scan_target}...[/bold green]")
            # Direct robust scan — no AI intermediary for basic scan
            scan_phases = [
                ("Port Discovery",  f"nmap -sV -sC -T4 --open {scan_target}"),
            ]
            for phase_name, scan_cmd in scan_phases:
                console.print(f"[dim]  [{phase_name}] {scan_cmd}[/dim]")
                try:
                    stdout, stderr = local_exec.execute(scan_cmd, timeout=120)
                    out = stdout or ""
                    if out.strip():
                        console.print(f"\n[green]{_truncate_output(out, 60)}[/green]")
                        store_findings(out, scan_cmd, agent, db, cve_search, console)
                        # AI analysis of results
                        with console.status("[bold green]  AI analysing scan...[/bold green]"):
                            analysis_text = agent.analyze_output(scan_cmd, out[:3000])
                        try:
                            next_sug = json.loads(analysis_text.strip().replace('```json','').replace('```',''))
                            console.print()
                            display_suggestion(next_sug)
                            confirm = console.input("[bold white]  Run it? (y/n/e=edit): [/bold white]").strip().lower()
                            if confirm == 'e':
                                next_sug['command'] = console.input("[bold cyan]  Edit: [/bold cyan]").strip()
                                confirm = 'y'
                            if confirm == 'y' and next_sug.get('command'):
                                f_out, f_err = local_exec.execute(next_sug['command'])
                                if f_out: console.print(f"[green]{_truncate_output(f_out)}[/green]")
                                if f_err: console.print(f"[dim red]{_truncate_output(f_err, 20)}[/dim red]")
                        except Exception:
                            pass
                    elif stderr and stderr.strip():
                        console.print(f"[dim red]  {stderr[:300]}[/dim red]")
                    else:
                        console.print("[yellow]  No results. Target may be offline or ports filtered.[/yellow]")
                except FileNotFoundError:
                    console.print("[red]  nmap not found. Install: sudo apt install nmap[/red]")
                except Exception as e:
                    console.print(f"[red]  Scan error: {e}[/red]")
            continue

        # ── Script Generator ─────────────────────────────────
        if cmd.startswith('write script') or cmd.startswith('generate script') or cmd.startswith('create script'):
            words = user_input.split()
            task_desc = ' '.join(words[2:]) if len(words) > 2 else console.input("  [cyan]Describe: [/cyan]").strip()
            lang = 'node' if any(k in cmd for k in ['node', 'javascript', 'js']) else 'python'
            console.print(f"[bold green][+] Generating {lang} script...[/bold green]")
            with console.status(f"[bold green]  Writing code...[/bold green]"):
                result_text = agent.generate_script(task_desc, lang)
            try:
                result = json.loads(result_text.strip().replace('```json', '').replace('```', ''))
                ext = 'py' if lang == 'python' else 'js'
                fname = result.get('filename', f'drkagi_script.{ext}')
                code = result.get('script_code', '')
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(code)
                console.print(f"[bold blue][+] Script: {fname}[/bold blue]")
                console.print(f"  [bold cyan]Run:[/bold cyan] {result.get('run_command', f'{lang} {fname}')}")
                console.print(f"  [dim]{result.get('explanation', '')}[/dim]")
            except Exception as e:
                console.print(f"[red]  Error: {e}[/red]\n{result_text}")
            continue

        # ── Simulation ───────────────────────────────────────
        if cmd.startswith('simulate') or cmd.startswith('what if') or cmd.startswith('what-if'):
            scenario = ' '.join(user_input.split()[1:])
            console.print("[bold yellow][~] SIMULATION MODE[/bold yellow]")
            with console.status("[bold yellow]  Simulating...[/bold yellow]"):
                result_text = agent.simulate_attack(scenario)
            try:
                result = json.loads(result_text.strip().replace('```json', '').replace('```', ''))
                console.print(f"\n[bold yellow]  Scenario:[/bold yellow] {result.get('explanation', '')}")
                steps = result.get('simulation_steps', [])
                if steps:
                    for i, step in enumerate(steps, 1):
                        console.print(f"  [dim cyan]  {i}.[/dim cyan] {step}")
            except Exception:
                console.print(result_text)
            continue

        # ── Plugin check ─────────────────────────────────────
        first_word = cmd.split()[0] if cmd.split() else ""
        plugin = plugins.get_plugin(first_word)
        if plugin:
            args_str = ' '.join(user_input.split()[1:])
            context = {
                "agent": agent, "console": console, "db": db,
                "logger": logger, "local_exec": local_exec,
                "target": current_target
            }
            plugins.execute(first_word, args_str, context)
            continue

        # ═════════════════════════════════════════════════════
        # AI SUGGESTION FLOW (default handler)
        # ═════════════════════════════════════════════════════

        # Inject target context if set
        final_input = user_input
        if current_target and current_target not in user_input:
            final_input = f"[Active target: {current_target}] {user_input}"

        logger.log("USER_INPUT", user_input)

        with console.status("[bold green]  Thinking...[/bold green]"):
            response_text = agent.get_suggestion(final_input)

        logger.log("AI_SUGGESTION", response_text)

        try:
            clean_json = response_text.strip().replace('```json', '').replace('```', '')
            suggestion = json.loads(clean_json)
            console.print()
            command = display_suggestion(suggestion)

            # Handle inline script
            if not command and suggestion.get('script_code'):
                sc = suggestion.get('script_code', '')
                stype = suggestion.get('script_type', 'python')
                ext = 'py' if stype == 'python' else 'js'
                fname = f"drkagi_gen.{ext}"
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(sc)
                console.print(f"[bold blue][+] Script saved: {fname}[/bold blue]")
                continue

            if not command:
                continue

            # User approval
            confirm = console.input("[bold white]  Execute? (y/n/e=edit): [/bold white]").strip().lower()
            if confirm == 'e':
                command = console.input("[bold cyan]  Edit: [/bold cyan]").strip()
                confirm = 'y'
            if confirm != 'y':
                console.print("[dim]  Skipped.[/dim]")
                continue

            # Execute locally
            console.print("[dim]  Executing...[/dim]")
            try:
                stdout, stderr = local_exec.execute(command)
            except FileNotFoundError as fnf:
                console.print(f"[red]  Command not found: {fnf}. Is the tool installed?[/red]")
                continue
            except Exception as exec_err:
                console.print(f"[red]  Execution error: {exec_err}[/red]")
                continue

            full_output = ""
            if stdout:
                console.print(f"\n[green]{_truncate_output(stdout)}[/green]")
                full_output += stdout
            if stderr:
                console.print(f"\n[dim red]{_truncate_output(stderr, 20)}[/dim red]")
                full_output += stderr

            logger.log("COMMAND_EXECUTION", full_output[:5000], {"command": command})

            if not full_output.strip():
                continue

            # Auto-extract target from output if none set
            if not current_target and command:
                # Try to detect IP in command
                import re
                ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', command)
                if ip_match:
                    current_target = ip_match.group()
                    agent.set_context("target", current_target)
                    console.print(f"[dim]  Auto-detected target: {current_target}[/dim]")

            # Analysis + DB + follow-up
            console.print("\n[bold magenta]  Analysing output...[/bold magenta]")
            with console.status("[bold magenta]  Processing...[/bold magenta]"):
                analysis_text = agent.analyze_output(command, full_output)
                store_findings(full_output, command, agent, db, cve_search, console)

            logger.log("AI_ANALYSIS", analysis_text)

            # Follow-up suggestion
            try:
                next_step = json.loads(analysis_text.strip().replace('```json', '').replace('```', ''))
                if next_step.get('command'):
                    console.print("[bold yellow]  Recommended next step:[/bold yellow]")
                    display_suggestion(next_step)
                    if console.input("[bold white]  Run follow-up? (y/n): [/bold white]").strip().lower() == 'y':
                        f_out, f_err = local_exec.execute(next_step['command'])
                        if f_out:
                            console.print(f"\n[green]{f_out}[/green]")
                        if f_err:
                            console.print(f"\n[dim red]{f_err}[/dim red]")
                        logger.log("COMMAND_EXECUTION", (f_out or "") + (f_err or ""), {"command": next_step['command']})
            except Exception:
                pass

        except json.JSONDecodeError:
            console.print(f"[dim red]  Could not parse AI response:[/dim red]\n{response_text}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting...[/bold red]")
        sys.exit(0)
