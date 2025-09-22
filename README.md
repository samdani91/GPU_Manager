# GPU Settings

A modern PyQt6-based GUI application for monitoring and switching between integrated and discrete GPUs on Linux systems using NVIDIA Prime technology.

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

## Screenshots

*Add screenshots of your application here*

## Prerequisites

- Linux distribution with NVIDIA Prime support
- NVIDIA GPU with proprietary drivers installed
- Python 3.8 or higher
- `prime-select` utility available
- `pkexec` for privilege escalation


## Installation

### From Source

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
python src/main.py
```

### Using pip (Development Install)

1. Install in development mode:
```bash
pip install -e .
```

2. Run the application:
```bash
gpu-settings
```

### Building Executable

Build a standalone executable using PyInstaller:

```bash
pyinstaller --onefile --windowed src/main.py --name gpu-settings
```

## Usage

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

These operations use `pkexec` for secure privilege escalation.

## Configuration

### Supported GPUs

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

## File Structure

```
gpu_settings/
├── src/
│   ├── main.py          # Application entry point
│   ├── window.py        # Main window and UI components
│   ├── gpu_utils.py     # GPU detection and management utilities
│   └── styles.py        # UI styling and themes
├── requirements.txt     # Python dependencies
├── setup.py            # Package setup configuration
└── README.md           # Project documentation
```

## Development

### Key Modules

- [`main.py`](src/main.py): Application entry point and PyQt6 setup
- [`window.py`](src/window.py): Main UI implementation with charts and tables
- [`gpu_utils.py`](src/gpu_utils.py): GPU detection, switching, and monitoring
- [`styles.py`](src/styles.py): Dark theme styling for UI components

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
- Ensure NVIDIA drivers are properly installed
- Verify `prime-select` is available and functional
- Check if user has sudo privileges

**Charts not displaying**
- Verify PyQt6-Charts is installed: `pip install PyQt6-Charts`
- Check if NVIDIA drivers are loaded: `nvidia-smi`

**Permission denied errors**
- Ensure `pkexec` is installed and configured
- Verify PolicyKit is running on your system

### System Requirements

- Ubuntu 18.04+ / Fedora 30+ / Arch Linux (or equivalent)
- NVIDIA GPU with 396+ drivers
- X11 or Wayland display server
- 4GB+ RAM recommended

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**A. M Samdani Mozumder**
- Portfolio: [https://portfolio.samdani1412.me](https://portfolio.samdani1412.me)
- GitHub: [@samdani1412](https://github.com/samdani1412)

## Acknowledgments

- NVIDIA for Prime technology
- PyQt6 team for the excellent GUI framework
- Catppuccin theme for color inspiration
- Linux community for GPU switching utilities

---

*For support or questions, please open an issue on GitHub.*