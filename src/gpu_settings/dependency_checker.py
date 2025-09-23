import sys
import subprocess
import time
import importlib.util
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QMessageBox, QApplication,
    QProgressBar, QInputDialog, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject


class InstallerWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    reboot_required = pyqtSignal()

    def __init__(self, packages, password):
        super().__init__()
        self.packages = packages
        self.password = password

    def is_installed(self, package, is_python=False):
        if is_python:
            # Check if Python package is installed
            spec = importlib.util.find_spec(package)
            return spec is not None
        else:
            # Check Debian package via dpkg
            result = subprocess.run(
                ["dpkg", "-s", package],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.returncode == 0

    def validate_password(self):
        """Check if sudo password is correct."""
        proc = subprocess.run(
            ["sudo", "-S", "echo", "ok"],
            input=(self.password + "\n").encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return proc.returncode == 0

    def run(self):
        try:
            # Validate password first
            if not self.validate_password():
                raise Exception("Incorrect password.")

            time.sleep(1)  # Small delay for GUI

            total_packages = len(self.packages)
            reboot_needed = False

            for i, pkg in enumerate(self.packages):
                if not self.is_installed(pkg, is_python=pkg.startswith("python3-")):
                    cmd = ["sudo", "-S", "apt", "install", "-y", pkg]
                    proc = subprocess.run(
                        cmd,
                        input=(self.password + "\n").encode(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    if proc.returncode != 0:
                        raise Exception(proc.stderr.decode())

                    if pkg == "nvidia-driver-535":
                        reboot_needed = True

                # Update progress
                progress = int(((i + 1) / total_packages) * 100)
                self.progress_updated.emit(progress)

            if reboot_needed:
                self.reboot_required.emit()

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))


class DependencyChecker(QWidget):
    dependencies_ready = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPU Settings - Dependency Check")
        self.setFixedSize(500, 300)

        layout = QVBoxLayout()

        self.label = QLabel("🔍 Checking requirements...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.center()

        QTimer.singleShot(300, self.check_dependencies)

    def center(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def is_installed(self, package, is_python=False):
        if is_python:
            spec = importlib.util.find_spec(package)
            return spec is not None
        else:
            result = subprocess.run(
                ["dpkg", "-s", package],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.returncode == 0

    def has_nvidia_gpu(self):
        """Check if the system has a dedicated NVIDIA GPU."""
        try:
            result = subprocess.run(
                ["lspci"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return "NVIDIA" in result.stdout
        except Exception:
            return False

    def check_dependencies(self):
        self.missing = []

        # Python requirements (always needed)
        python_reqs = [
            ("PyQt6", "python3-pyqt6"),
            ("PyQt6.QtCharts", "python3-pyqt6.qtcharts"),
            # ("psutil", "python3-psutil"),
        ]

        # NVIDIA-specific requirements (optional)
        nvidia_reqs = [
            ("nvidia_prime", "nvidia-prime"),
            ("nvidia_utils_535", "nvidia-utils-535"),
        ]

        # Build requirements list
        requirements = python_reqs[:]
        if self.has_nvidia_gpu():
            requirements += nvidia_reqs

        # Check Python and system packages
        for module_name, pkg in requirements:
            if module_name in ("nvidia_prime", "nvidia_utils_535"):
                if not self.is_installed(pkg):  # System package
                    self.missing.append(pkg)
            else:
                if not self.is_installed(module_name.split('.')[0], is_python=True):
                    self.missing.append(pkg)

        # NVIDIA driver check (only if GPU exists)
        if self.has_nvidia_gpu() and not self.is_nvidia_working():
            self.missing.append("nvidia-driver-535")

        if self.missing:
            self.label.setText(
                "⚠️ Missing dependencies:\n" + ", ".join(self.missing) + "\nInstalling..."
            )

            password = self.get_password()
            if not password:
                sys.exit(1)

            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)

            self.thread = QThread()
            self.worker = InstallerWorker(self.missing, password)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.install_finished)
            self.worker.error.connect(self.handle_install_error)
            self.worker.progress_updated.connect(self.progress_bar.setValue)
            self.worker.reboot_required.connect(self.show_reboot_prompt)
            self.worker.finished.connect(self.thread.quit)
            self.worker.error.connect(self.thread.quit)

            self.thread.start()
        else:
            self.dependencies_ready.emit()

    def get_password(self):
        """Prompt GUI for sudo password with retry on wrong input."""
        while True:
            password, ok = QInputDialog.getText(
                self, "Admin Password", "Enter your system password:", QLineEdit.EchoMode.Password
            )
            if not ok:
                return None

            proc = subprocess.run(
                ["sudo", "-S", "echo", "ok"],
                input=(password + "\n").encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if proc.returncode == 0:
                return password
            else:
                QMessageBox.warning(self, "Wrong Password", "The password you entered is incorrect. Please try again.")

    def install_finished(self):
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Success", "Dependencies installed successfully.")
        self.dependencies_ready.emit()

    def handle_install_error(self, error):
        QMessageBox.critical(self, "Error", f"Failed to install dependencies:\n{error}")
        sys.exit(1)

    def is_nvidia_working(self):
        try:
            result = subprocess.run(
                ["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def show_reboot_prompt(self):
        reply = QMessageBox()
        reply.setWindowTitle("Reboot Required")
        reply.setText("nvidia-driver-535 was installed.\nA system reboot is required.")
        reply.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        ok_button = reply.button(QMessageBox.StandardButton.Ok)
        ok_button.setText("Reboot Now")
        if reply.exec() == QMessageBox.StandardButton.Ok:
            subprocess.run(["sudo", "reboot"])
