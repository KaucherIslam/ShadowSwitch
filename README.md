<h1 align="center">ShadowSwitch: The Universal Linux Anonymity Dashboard</h1>

<h2>Overview</h2>

ShadowSwitch is an open-source privacy and security dashboard built to bridge the gap between complex command-line scripts and user-friendly automation. While most Linux security tools require manual terminal execution, ShadowSwitch provides a unified Graphical User Interface (GUI) to mask your digital footprint with a single click.

This tool is designed for security enthusiasts who want a "Universal Switch" for their anonymity stack without the friction of managing multiple individual scripts.

<h2>Developer & Vision</h2>

**Developed by *Kaucher Islam Forhad***. I am a cybersecurity professional-in-training (Google Cybersecurity & CompTIA Security+ Professional Certificate) focused on creating tools that reduce "security fatigue" through intuitive automation. ShadowSwitch was born from the need for a distribution-agnostic, one-click anonymity solution.

[**Connect with me on LinkedIn**](https://www.linkedin.com/in/kaucherislamforhad)

<h2>Installation:</h2>

***Note:** This is an early development version; please monitor this repository for the full release.*

 - **Update your system repositories**

```bash
sudo apt update -y
```
 
 - **Ensure Git is installed on your system**

If Git is not present, install it using:

```bash
sudo apt install git -y
```

 - **The core installation:**

Clone the repository to your local machine:

```bash
git clone https://github.com/KaucherIslam/ShadowSwitch
```

Navigate into the directory and install the necessary prerequisites:

```bash
cd ShadowSwitch
```
```bash
bash setup.sh
```

 - **Launch the Application**

Once the setup is complete, start the dashboard:

```bash
python3 ShadowSwitch.py
```

<h2>Core Features</h2>

 - Automatic Mode: A "Set and Forget" toggle that executes the full anonymity stack—MAC randomization, hostname spoofing, firewall activation, and proxy routing—sequentially and verifies each step.

 - Manual Mode: Granular control over specific security modules for users who need targeted privacy without full system re-routing.

 - MAC Address Randomizer: Instantly spoof your hardware address to prevent device tracking on local networks.

 - Hostname Spoofing: Randomize your machine's network name to blend in with standard devices.

- Firewall Killswitch: Integrated `ufw` management to ensure no traffic leaves your device unless specified.

 - Tor/I2P Transparent Proxy: Route system-wide traffic through anonymity networks with real-time status monitoring.

- DNS over HTTPS (DoH): Encrypt DNS queries to bypass ISP tracking and prevent DNS hijacking.

<h2>Technical Architecture</h2>

*ShadowSwitch is built with a focus on stability, system safety, and a modern user experience:*

 - Language: Python 3

 - Frontend: `CustomTkinter` for a professional, responsive, and dark-mode-native interface.

 - Backend: `subprocess` for secure interaction with the Linux networking stack.

 - Privilege Management: Utilizes `pkexec` for just-in-time root escalation, ensuring the GUI itself does not run with unnecessary administrative rights.

 - Concurrency: Multi-threaded execution to keep the interface responsive during long-running network operations.

<h2>Why ShadowSwitch?</h2>

In the current Linux ecosystem, anonymity tools are often fragmented or restricted to specific distributions. ShadowSwitch aims to be a distribution-agnostic solution that brings professional-grade privacy controls to any user, regardless of their comfort level with the command line.

<h2>License</h2>

*Distributed under the GNU GPLv3 License. See LICENSE for more information. This ensures the tool remains open-source and that any future iterations or improvements by the community are shared back with the public.*

<h2>Project Roadmap</h2>

 - [ ] **Phase 1:** *Core CLI logic and networking functions.*

 - [ ] **Phase 2:** *Development of the CustomTkinter dashboard.*

 - [ ] **Phase 3:** *Implementation of "Automatic" vs "Manual" logic.*

 - [ ] **Phase 4:** *Beta testing on Debian-based and Arch-based systems.*

<h1 align="center">Project Roadmap & Community Input</h1>

 - **Status:** Under Active Development

 - **Target Completion:** March 2026

I am currently building out the core logic and GUI for ShadowSwitch, with a full version expected by March 2026! I’m always looking to improve this tool and make it as useful as possible.

If you have any security tools, privacy features, or innovative ideas you'd like to see integrated, let's connect! Please share your suggestions with me through my [LinkedIn Profile](https://www.linkedin.com/in/kaucherislamforhad/).

Thank you for reading and for your support!
