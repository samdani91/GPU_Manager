# GPU Manager

A modern PyQt6-based GUI application for monitoring and switching between integrated and discrete GPUs on Linux systems using NVIDIA Prime technology. Features automatic dependency checking and installation.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6.0+-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)

## Features

🔄 **GPU Switching**
- Seamlessly switch between NVIDIA and integrated GPUs
- Support for Intel and AMD integrated graphics
- Automatic detection of available GPUs

📊 **Real-time Monitoring**
- Live GPU utilization statistics
- Memory usage tracking
- Temperature monitoring
- Real-time utilization charts

⚡ **Process Management**
- View GPU processes with memory usage
- Kill GPU processes with elevated privileges
- Process filtering and monitoring

🎨 **Modern Dark UI**
- Sleek dark theme with Catppuccin-inspired colors
- Responsive design with scrollable interface
- Intuitive user experience

🔧 **Automatic Setup**
- Built-in dependency checker with GUI
- Automatic installation of missing packages
- Smart NVIDIA driver detection and installation

## Screenshots

![GPU Manager Main Interface](https://drive.google.com/uc?export=view&id=1GsmFZJuBgZf3BNsYHwJaUvHHaMLenzlg)

## Prerequisites

### System Requirements
- Linux distribution with NVIDIA Prime support (Ubuntu 18.04+, Fedora 30+, Arch Linux)
- NVIDIA GPU with proprietary drivers (automatically installed if missing)
- Python 3.8 or higher
- X11 or Wayland display server
- 4GB+ RAM recommended

### Runtime Dependencies (Auto-installed)
- `prime-select` utility (nvidia-prime package)
- `nvidia-smi` (nvidia-utils-535 package)
- `pkexec` for privilege escalation
-  PyQt6 and PyQt6-Charts

## Installation

### Method 1: Debian Package (Recommended)

Download and install the pre-built `.deb` package:

```bash
# Download the latest release
wget https://github.com/samdani91/GPU_Manager/blob/main/deb_dist/python3-gpu-settings_0.2-1_all.deb

# Install the package
sudo dpkg -i python3-gpu-settings_0.1-1_all.deb

# Fix any missing dependencies
sudo apt-get install -f

# Run the application
gpu-settings
```

### Method 2: From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gpu_settings.git
cd gpu_settings
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python src/gpu_settings/main.py
```

### Method 3: Python Package Install

1. Install in development mode:
```bash
pip install -e .
```

2. Run the application:
```bash
gpu-settings
```

### Method 4: Building from Source

Create your own `.deb` package:

```bash
# Install build dependencies
sudo apt install python3-stdeb dh-python

# Build the package
python3 setup.py --command-packages=stdeb.command bdist_deb

# Install the built package
sudo dpkg -i deb_dist/python3-gpu-settings_0.2-1_all.deb
```

### Method 5: Standalone Executable

Build a standalone executable using PyInstaller:

```bash
pyinstaller --onefile --windowed src/gpu_settings/main.py --name gpu-settings
```

## Usage

### First Launch

When you first run the application, the built-in dependency checker ([`dependency_checker.py`](src/gpu_settings/dependency_checker.py)) will:

1. Check for required system packages and Python modules
2. Prompt for your system password if installations are needed
3. Automatically install missing dependencies:
   - `python3-pyqt6` - Main GUI framework
   - `python3-pyqt6.qtcharts` - Charts for GPU utilization
   - `nvidia-prime` - GPU switching utility
   - `nvidia-utils-535` - NVIDIA monitoring tools
   - `nvidia-driver-535` - NVIDIA graphics driver (if needed)

### Basic Operations

1. **View Current GPU**: The main interface displays your currently active GPU
2. **Switch GPU**: Select desired GPU mode and click "Apply"
3. **Monitor Stats**: Real-time GPU statistics are updated every second
4. **Manage Processes**: View and terminate GPU processes as needed
5. **Reboot**: Use the reboot button after GPU switching

### GPU Modes

- **NVIDIA**: Discrete NVIDIA GPU (high performance, higher power consumption)
- **Intel/AMD Integrated**: Integrated graphics (power efficient, lower performance)

### Permissions

The application requires elevated privileges for:
- GPU switching via `prime-select`
- Process termination
- System reboot
- Dependency installation

These operations use `pkexec` and `sudo` for secure privilege escalation.

## Configuration

### Supported GPUs

The [`gpu_utils.get_integrated_gpu()`](src/gpu_settings/gpu_utils.py) function automatically detects:

- **NVIDIA**: Any NVIDIA GPU with Prime support
- **Intel**: Integrated Intel graphics
- **AMD**: Integrated AMD APUs (Renoir, Lucienne, Cezanne series)

### Dependencies

Core dependencies are listed in [`requirements.txt`](requirements.txt):

```
PyQt6>=6.6.0
PyInstaller>=5.13.0
PyQt6-Charts>=6.6.0
```

Package configuration in [`setup.py`](setup.py):

```python
install_requires=[
    "PyQt6",
    "psutil",
    "PyQt6-Charts"
]
```

## File Structure

```
gpu_settings/
├── src/
│   └── gpu_settings/
│       ├── main.py              # Application entry point with dependency checking
│       ├── window.py            # Main UI implementation with charts and tables  
│       ├── gpu_utils.py         # GPU detection, switching, and monitoring
│       ├── styles.py            # Dark theme styling for UI components
│       └── dependency_checker.py # Automatic dependency installation
├── deb_dist/                    # Built Debian packages
│   └── python3-gpu-settings_0.1-1_all.deb
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup configuration
├── .gitignore                   # Git ignore rules
└── README.md                   # Project documentation
```

## Development

### Key Modules

- [`main.py`](src/gpu_settings/main.py): Application entry point with [`DependencyChecker`](src/gpu_settings/dependency_checker.py) integration
- [`window.py`](src/gpu_settings/window.py): [`MainWindow`](src/gpu_settings/window.py) class with real-time monitoring and GPU switching
- [`gpu_utils.py`](src/gpu_settings/gpu_utils.py): Core GPU management functions including [`switch_gpu()`](src/gpu_settings/gpu_utils.py) and [`parse_nvidia_smi()`](src/gpu_settings/gpu_utils.py)
- [`styles.py`](src/gpu_settings/styles.py): Catppuccin-inspired dark theme styling
- [`dependency_checker.py`](src/gpu_settings/dependency_checker.py): [`DependencyChecker`](src/gpu_settings/dependency_checker.py) with [`InstallerWorker`](src/gpu_settings/dependency_checker.py) for background installation

### Building Packages

Create Debian package:

```bash
python3 setup.py --command-packages=stdeb.command bdist_deb
```

The built package will be available in [`deb_dist/`](deb_dist/).

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit with descriptive messages: `git commit -m "Add feature description"`
5. Push to your fork: `git push origin feature-name`
6. Submit a pull request

## Troubleshooting

### Common Issues

**GPU switching fails**
- Ensure NVIDIA drivers are properly installed (auto-installed on first run)
- Verify `prime-select` is available and functional
- Check if user has sudo privileges

**Charts not displaying**
- The dependency checker should install PyQt6-Charts automatically
- Manually install: `sudo apt install python3-pyqt6.qtcharts`
- Check if NVIDIA drivers are loaded: `nvidia-smi`

**Permission denied errors**
- Ensure `pkexec` is installed: `sudo apt install policykit-1`
- Verify PolicyKit is running: `systemctl status polkit`

**Dependency installation fails**
- Check internet connection
- Verify user has sudo privileges
- Run `sudo apt update` before installation

**Application won't start**
- Run from terminal to see error messages: `gpu-settings`
- Check if all dependencies are installed: `dpkg -l | grep -E "(pyqt6|nvidia)"`

### Manual Dependency Installation

If the automatic installer fails, install dependencies manually:

```bash
# System packages
sudo apt update
sudo apt install python3-pyqt6 python3-pyqt6.qtcharts nvidia-prime nvidia-utils-535

# NVIDIA driver (if needed)
sudo apt install nvidia-driver-535

# Python packages (if using pip)
pip install PyQt6 PyQt6-Charts
```

### Debug Mode

Run with debug output:

```bash
python3 -u src/gpu_settings/main.py
```

## Uninstallation

### Remove Debian Package

```bash
sudo dpkg -r python3-gpu-settings
```

### Remove pip Installation

```bash
pip uninstall gpu-settings
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**A. M Samdani Mozumder**
- Portfolio: [https://portfolio.samdani1412.me](https://portfolio.samdani1412.me)
- GitHub: [@samdani1412](https://github.com/samdani1412)
- Email: bsse1412@iit.du.ac.bd

## Acknowledgments

- NVIDIA for Prime technology and driver ecosystem
- PyQt6 team for the excellent GUI framework
- Catppuccin theme for color inspiration
- Linux community for GPU switching utilities
- Debian packaging tools and community


---

*For support or questions, please open an issue on GitHub or contact the author.*