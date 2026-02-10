import random
import string
import customtkinter as ctk
import subprocess
import os

# V1: Root Password
APP_PASSWORD = None

# V2: MAC
interface = subprocess.check_output("ls /sys/class/net | grep -v 'lo' | head -n 1", shell=True).decode().strip()

# V3: Hostname
current_hostname = subprocess.check_output(["hostname"]).decode().strip()

def get_password_gui():
    global APP_PASSWORD
    dialog = ctk.CTkInputDialog(text="Enter Root Password:", title="Authentication")
    password = dialog.get_input()
    if password:
        APP_PASSWORD = password
        return True
    return False

def command(cmd_list):
    global APP_PASSWORD
    if not APP_PASSWORD:
        if not get_password_gui(): return
    
    full_cmd = ["sudo", "-S"] + cmd_list
    try:
        process = subprocess.run(full_cmd, input=f"{APP_PASSWORD}\n", text=True, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        # To reset the password if it gets failed
        APP_PASSWORD = None 
        return False

# F1: MAC
def change_mac():
    try:
        if mac_switch_var.get() == "on":
            print(f"Targeting interface: {interface}")
            command(["macchanger", "-r", interface])
        else:
            print(f"Restoring the original mac of {interface}")
            command(["macchanger", "-p", interface])
    except Exception as e:
        print(f"Interface check failed: {e}")

# F2: Hostname
def randomize_hostname():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    new_hostname = f"Workstation-{suffix}"
    
    if hostname_switch_var.get() == "on":
        # To change the hostname.
        command(["hostnamectl", "set-hostname", "--pretty", new_hostname])
    else:
        # To revert the hostname.
        command(["hostnamectl", "set-hostname", "--pretty", current_hostname])

#F3: DNS
def toggle_dns():
    if dns_switch_var.get() == "on":
        # Backup of the original settings.
        command(["cp", "-n", "/etc/resolv.conf", "/etc/resolv.conf.bak"])
        
        dns_cmd = "echo 'nameserver 9.9.9.9\nnameserver 1.1.1.1' > /etc/resolv.conf"
        command(["sh", "-c", dns_cmd])
    else:
        # Restore from backup.
        if os.path.exists("/etc/resolv.conf.bak"):
            command(["mv", "/etc/resolv.conf.bak", "/etc/resolv.conf"])

# The UI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.geometry("400x350")
app.title("ShadowSwitch")

header = ctk.CTkLabel(app, text="SHADOWSWITCH", font=("JetBrains Mono", 20, "bold"))
header.pack(pady=20)

frame = ctk.CTkFrame(app, corner_radius=15)
frame.pack(padx=20, pady=10, fill="both", expand=True)

# B1: MAC
mac_switch_var = ctk.StringVar(value="off")
change_mac = ctk.CTkSwitch(frame, text="Change the MAC address", command=change_mac,
                           variable=mac_switch_var, onvalue="on", offvalue="off")
change_mac.pack(pady=15, padx=20, anchor="w")

# B2: Hostname
hostname_switch_var = ctk.StringVar(value="off")
new_hostname = ctk.CTkSwitch(frame, text="Change the pretty hostname", command=randomize_hostname,
                           variable=hostname_switch_var, onvalue="on", offvalue="off")
new_hostname.pack(pady=15, padx=20, anchor="w")

# B3: DNS
dns_switch_var = ctk.StringVar(value="off")
dns_switch = ctk.CTkSwitch(frame, text="Secure DNS", command=toggle_dns,
                           variable=dns_switch_var, onvalue="on", offvalue="off")
dns_switch.pack(pady=15, padx=20, anchor="w")

app.mainloop()
