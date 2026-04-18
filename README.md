# SoftwareManager
SoftwareManager is a Python-based GUI tool that simplifies searching and downloading software from various sources, including Rutracker, Uztracker, Steamrip and the official M0nkrus Telegram channel.

> [!NOTE]  
> Our Steamrip implementation is currently very experimental and potentially unstable.<br>
> Downloads will fail if there's no BuzzHeavier download available. We're working on this.

## Features
- Searching & Downloading Software from various pages
- Network Interface Binding
- Simple UI, Speed Limiting etc.
- No Logins required

## Installation
1. Download the binary file for your operating system from releases 
   https://github.com/KeksPirates/SoftwareManager/releases
2. Run the file

## Manual Installation
1. Ensure Python 3.x is installed on your system.
2. Clone the Repository:
   ```bash
   git clone https://github.com/KeksPirates/SoftwareManager.git && cd SoftwareManager
   ```
2. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run main.py:
   ```bash
   python main.py
   ```

## Additional Information
- SoftwareManager is still in Development and most likely contains issues. Please report any bugs you find via the Issues tab. Contributions are also greatly appreciated.
- MacOS Builds haven't been properly tested - We're thankful to receive feedback.
- If you want to host your own server, clone our [server repository](https://github.com/KeksPirates/SoftwareManager-Server), enter your cookie for rutracker.org and run server.py. Detailed Instructions on how to get your rutracker cookie are in the README of the server repo.

## Python Dependencies
(also included in requirements.txt)

<!-- python-dependencies:start -->
   ```text
   requests (2.33.1)
   PySide6-Essentials (6.11.0)
   beautifulsoup4 (4.14.3)
   darkdetect (0.7.1)
   pyinstaller (6.19.0)
   PyQtDarkTheme-fork (2.3.6)
   plyer (2.1.0)
   psutil (7.2.2)
   libtorrent (2.0.11)
   libtorrent-windows-dll (0.0.3)
   send2trash (2.1.0)
   ```
<!-- python-dependencies:end -->

## Star History

<a href="https://www.star-history.com/#KeksPirates/SoftwareManager&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=KeksPirates/SoftwareManager&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=KeksPirates/SoftwareManager&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=KeksPirates/SoftwareManager&type=date&legend=top-left" />
 </picture>
</a>

**Disclaimer:** SoftwareManager is intended for legal and ethical use only. Ensure compliance with applicable laws and regulations when using this tool.

