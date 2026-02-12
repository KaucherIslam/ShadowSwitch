import random
import string
import customtkinter as ctk
import subprocess
import os
import threading
import time
import json
import shutil
import sys

# --- 1. CONFIGURATION ---
CONFIG_FILE = os.path.expanduser("~/.shadow_conf.json")
UFW_BACKUP_DIR = "/etc/shadow_ufw_backup"

# Global State
APP_PASSWORD = None
APP_RUNNING = True
IS_STARTUP = True      
IS_AUDITING = False    
auth_lock = threading.Lock()

# Global Switch Variables
master_switch_var = None
mac_switch_var = None
hostname_switch_var = None
dns_switch_var = None
ufw_switch_var = None

# Default Config
config = {
    "ufw_mode": "ShadowSwitch",
    "setup_completed": False
}

# --- 2. SYSTEM UTILITIES ---
def load_config():
    global config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                loaded = json.load(f)
                config.update(loaded)
        except: pass

def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def get_active_interface():
    try:
        route = subprocess.check_output(["ip", "route", "get", "8.8.8.8"]).decode().strip()
        if "dev" in route:
            start = route.find("dev") + 4
            end = route.find(" ", start)
            return route[start:end].strip()
    except: pass
    return "eth0" 

# --- 3. VERIFIED PASSWORD DIALOG ---
class PasswordDialog(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.geometry("320x180")
        self.title("Authentication")
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 160
        y = (self.winfo_screenheight() // 2) - 90
        self.geometry(f"+{x}+{y}")
        self.attributes("-topmost", True)
        self.password = None
        
        self.label = ctk.CTkLabel(self, text="Enter Root Password:")
        self.label.pack(pady=(15, 5))
        
        self.entry = ctk.CTkEntry(self, show="*", width=200) 
        self.entry.pack(pady=5)
        self.entry.focus()
        
        self.status_label = ctk.CTkLabel(self, text="", text_color="red", font=("Arial", 11))
        self.status_label.pack(pady=2)

        self.btn = ctk.CTkButton(self, text="Unlock", command=self.on_submit, width=100)
        self.btn.pack(pady=10)
        
        self.bind('<Return>', lambda e: self.on_submit())
        self.grab_set()
        self.wait_window()

    def on_submit(self):
        pwd = self.entry.get()
        if not pwd: return

        self.status_label.configure(text="Verifying...", text_color="yellow")
        self.update_idletasks()

        try:
            cmd = ["sudo", "-S", "true"] 
            proc = subprocess.run(cmd, input=f"{pwd}\n", text=True, capture_output=True)
            
            if proc.returncode == 0:
                self.password = pwd
                self.destroy() 
            else:
                self.status_label.configure(text="Incorrect Password. Try again.", text_color="#FF5555")
                self.entry.delete(0, 'end')
                self.entry.configure(border_color="#FF5555")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="red")

def get_password_gui():
    global APP_PASSWORD
    with auth_lock:
        if APP_PASSWORD: return True
        dialog = PasswordDialog()
        if dialog.password:
            APP_PASSWORD = dialog.password
            return True
        return False

def command(cmd_list, silent=False):
    global APP_PASSWORD
    tool = cmd_list[0]
    
    if tool not in ["sh", "cp", "mv", "echo", "mkdir", "ip", "hostnamectl", "macchanger"] and not shutil.which(tool):
        if not silent: print(f"Error: {tool} not found.")
        return False

    if silent and not APP_PASSWORD: return False
    
    if not APP_PASSWORD:
        if not get_password_gui(): return False
    
    full_cmd = ["sudo", "-S"] + cmd_list
    try:
        # TIMEOUT INCREASED TO 60 SECONDS
        subprocess.run(full_cmd, input=f"{APP_PASSWORD}\n", text=True, capture_output=True, check=True, timeout=60)
        return True
    except: return False

# --- 4. UI HELPER ---
def set_ui_state(variable, state):
    if APP_RUNNING and app:
        app.after(0, lambda: variable.set(state))

# --- 5. FEATURE LOGIC ---

# --- MAC ---
def toggle_mac():
    if IS_STARTUP or IS_AUDITING: return 
    threading.Thread(target=_mac_thread).start()

def _mac_thread():
    if not APP_RUNNING: return
    iface = get_active_interface()
    state = mac_switch_var.get()
    
    if state == "on":
        command(["macchanger", "-r", iface])
    else:
        command(["macchanger", "-p", iface])
    check_master_status()

# --- HOSTNAME ---
def toggle_hostname():
    if IS_STARTUP or IS_AUDITING: return
    threading.Thread(target=_hostname_thread).start()

def _hostname_thread():
    if not APP_RUNNING: return
    state = hostname_switch_var.get()
    if state == "on":
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        command(["hostnamectl", "set-hostname", "--pretty", f"Workstation-{suffix}"])
    else:
        try:
            real_name = subprocess.check_output(["hostname"]).decode().strip()
            command(["hostnamectl", "set-hostname", "--pretty", real_name])
        except: pass
    check_master_status()

# --- DNS ---
def toggle_dns():
    if IS_STARTUP or IS_AUDITING: return
    threading.Thread(target=_dns_thread).start()

def _dns_thread():
    if not APP_RUNNING: return
    state = dns_switch_var.get()
    if state == "on":
        command(["cp", "-n", "/etc/resolv.conf", "/etc/resolv.conf.bak"])
        dns_cmd = "echo 'nameserver 9.9.9.9\nnameserver 1.1.1.1' > /etc/resolv.conf"
        command(["sh", "-c", dns_cmd])
    else:
        if os.path.exists("/etc/resolv.conf.bak"):
            command(["mv", "/etc/resolv.conf.bak", "/etc/resolv.conf"])
    check_master_status()

# --- FIREWALL ---
def toggle_firewall(value=None):
    if IS_STARTUP or IS_AUDITING: return
    threading.Thread(target=_ufw_thread).start()

def _ufw_thread():
    if not APP_RUNNING: return
    state = ufw_switch_var.get()
    mode = config["ufw_mode"]
    
    if not os.path.exists(UFW_BACKUP_DIR):
        command(["mkdir", "-p", UFW_BACKUP_DIR])
        command(["cp", "/etc/ufw/user.rules", f"{UFW_BACKUP_DIR}/user.rules"])
    
    if state == "on":
        if mode == "ShadowSwitch":
            command(["ufw", "--force", "reset"])
            command(["ufw", "default", "deny", "incoming"])
            command(["ufw", "default", "allow", "outgoing"])
            command(["ufw", "allow", "22/tcp"])
            command(["ufw", "allow", "53"])
            command(["ufw", "allow", "443/tcp"])
            command(["ufw", "--force", "enable"])
        elif mode == "Hybrid":
            command(["ufw", "default", "deny", "incoming"])
            command(["ufw", "--force", "enable"])
        else:
            command(["ufw", "--force", "enable"])
    else:
        command(["ufw", "disable"])
        if mode != "Custom" and os.path.exists(f"{UFW_BACKUP_DIR}/user.rules"):
            command(["cp", f"{UFW_BACKUP_DIR}/user.rules", "/etc/ufw/user.rules"])
            command(["ufw", "reload"])
    check_master_status()

# --- MASTER SWITCH ---
def check_master_status():
    if not APP_RUNNING: return
    def sync():
        try:
            m = mac_switch_var.get()
            h = hostname_switch_var.get()
            d = dns_switch_var.get()
            u = ufw_switch_var.get()
            if m == "on" and h == "on" and d == "on" and u == "on":
                master_switch_var.set("on")
            else:
                master_switch_var.set("off")
        except: pass
    app.after(0, sync)

def toggle_master():
    if IS_STARTUP or IS_AUDITING: return
    if not APP_PASSWORD:
        if not get_password_gui(): 
            master_switch_var.set("off")
            return 
    threading.Thread(target=_master_thread).start()

def _master_thread():
    if not APP_RUNNING: return
    state = master_switch_var.get()
    def update_all():
        mac_switch_var.set(state)
        hostname_switch_var.set(state)
        dns_switch_var.set(state)
        ufw_switch_var.set(state)
    app.after(0, update_all)
    threading.Thread(target=_mac_thread).start()
    threading.Thread(target=_hostname_thread).start()
    threading.Thread(target=_dns_thread).start()
    threading.Thread(target=_ufw_thread).start()

# --- 6. INTELLIGENT STARTUP AUDIT (FIXED MAC LOGIC) ---
def perform_silent_audit():
    """Detects active system states."""
    global IS_AUDITING
    IS_AUDITING = True 
    
    # 1. MAC ADDRESS Check (Robust Method)
    # Parsing 'macchanger -s' is the only reliable way to check for spoofing.
    # It compares Current vs Permanent MAC.
    try:
        iface = get_active_interface()
        # macchanger -s usually runs without root for display
        out = subprocess.check_output(["macchanger", "-s", iface], text=True)
        
        current_mac = ""
        perm_mac = ""
        
        for line in out.splitlines():
            if "Current MAC:" in line:
                current_mac = line.split()[2].strip().lower()
            elif "Permanent MAC:" in line:
                perm_mac = line.split()[2].strip().lower()
        
        # If we found both and they are different, MAC is spoofed
        if current_mac and perm_mac and current_mac != perm_mac:
            set_ui_state(mac_switch_var, "on")
            
    except: pass

    # 2. DNS Check
    try:
        if os.path.exists("/etc/resolv.conf"):
            with open("/etc/resolv.conf", "r") as f:
                if "nameserver 9.9.9.9" in f.read():
                    set_ui_state(dns_switch_var, "on")
    except: pass

    # 3. Hostname Check
    try:
        pretty_host = subprocess.check_output(["hostnamectl", "--pretty"]).decode().strip()
        if "Workstation-" in pretty_host:
             set_ui_state(hostname_switch_var, "on")
    except: pass

    # 4. Firewall Check
    try:
        if os.path.exists("/etc/ufw/ufw.conf"):
            with open("/etc/ufw/ufw.conf", "r") as f:
                content = f.read()
                if "ENABLED=yes" in content:
                    set_ui_state(ufw_switch_var, "on")
    except: pass
    
    # 5. Finish
    app.after(1000, lambda: enable_buttons())

def check_first_run():
    if shutil.which("ufw") and not config["setup_completed"]:
        show_popup()

def show_popup():
    if not APP_RUNNING: return
    dialog = ctk.CTkToplevel(app)
    dialog.geometry("350x300")
    dialog.title("Firewall Setup")
    dialog.attributes("-topmost", True)
    
    dialog.update_idletasks()
    x = (app.winfo_screenwidth() // 2) - 175
    y = (app.winfo_screenheight() // 2) - 150
    dialog.geometry(f"+{x}+{y}")
    
    ctk.CTkLabel(dialog, text="First Run Configuration", font=("Arial", 18, "bold")).pack(pady=10)
    
    def set_mode(m):
        config["ufw_mode"] = m
        config["setup_completed"] = True
        save_config()
        dialog.destroy()
        
    ctk.CTkButton(dialog, text="ShadowSwitch (Recommended)", command=lambda: set_mode("ShadowSwitch"), fg_color="#FF4444", hover_color="#CC0000").pack(pady=10)
    ctk.CTkButton(dialog, text="Hybrid (Merge Rules)", command=lambda: set_mode("Hybrid")).pack(pady=5)
    ctk.CTkButton(dialog, text="Custom (Don't Touch)", command=lambda: set_mode("Custom"), fg_color="gray").pack(pady=5)
    
    dialog.grab_set() 
    app.wait_window(dialog)

def enable_buttons():
    global IS_STARTUP, IS_AUDITING
    IS_AUDITING = False 
    IS_STARTUP = False
    check_master_status()

def on_closing():
    global APP_RUNNING
    APP_RUNNING = False
    app.destroy()
    sys.exit()

# --- 7. UI SETUP ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.geometry("400x500")
app.title("ShadowSwitch")
app.protocol("WM_DELETE_WINDOW", on_closing)

load_config()

header = ctk.CTkLabel(app, text="SHADOWSWITCH", font=("JetBrains Mono", 24, "bold"))
header.pack(pady=(20, 10))

master_frame = ctk.CTkFrame(app, corner_radius=10, fg_color="#2B2B2B")
master_frame.pack(padx=20, pady=10, fill="x")
master_switch_var = ctk.StringVar(value="off")
master_switch = ctk.CTkSwitch(master_frame, text="TOTAL ANONYMITY (Master)", 
                              command=toggle_master, variable=master_switch_var, 
                              onvalue="on", offvalue="off", font=("Roboto", 14, "bold"))
master_switch.pack(pady=15, padx=20)

frame = ctk.CTkFrame(app, corner_radius=15)
frame.pack(padx=20, pady=10, fill="both", expand=True)

mac_switch_var = ctk.StringVar(value="off")
ctk.CTkSwitch(frame, text="Randomize MAC", command=toggle_mac, variable=mac_switch_var, onvalue="on", offvalue="off").pack(pady=15, padx=20, anchor="w")

hostname_switch_var = ctk.StringVar(value="off")
ctk.CTkSwitch(frame, text="Randomize Hostname", command=toggle_hostname, variable=hostname_switch_var, onvalue="on", offvalue="off").pack(pady=15, padx=20, anchor="w")

dns_switch_var = ctk.StringVar(value="off")
ctk.CTkSwitch(frame, text="Secure DNS", command=toggle_dns, variable=dns_switch_var, onvalue="on", offvalue="off").pack(pady=15, padx=20, anchor="w")

ufw_switch_var = ctk.StringVar(value="off")
ctk.CTkSwitch(frame, text="Firewall (UFW)", command=toggle_firewall, variable=ufw_switch_var, onvalue="on", offvalue="off").pack(pady=15, padx=20, anchor="w")

app.after(500, check_first_run)       
app.after(1000, lambda: threading.Thread(target=perform_silent_audit, daemon=True).start()) 

app.mainloop()
