import subprocess
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QRadioButton,
    QMessageBox, QGridLayout, QTableWidget, QTableWidgetItem,
    QScrollArea
)
from PyQt6.QtCore import QTimer, QPointF, Qt
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

from gpu_settings.gpu_utils import (
    get_current_gpu, switch_gpu, is_nvidia_loaded,
    parse_nvidia_smi, parse_nvidia_processes, get_available_gpus
)
import gpu_settings.styles as styles


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPU Settings")
        self.showMaximized()  # fullscreen
        self.setStyleSheet(styles.MAIN_WINDOW_STYLE)

        # --- Scrollable central widget ---
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # --- Current GPU section ---
        h1 = QHBoxLayout()
        self.current_label = QLabel()
        self.current_label.setTextFormat(Qt.TextFormat.RichText)
        self.current_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.refresh_btn.clicked.connect(self.update_current)
        h1.addWidget(self.current_label)
        h1.addWidget(self.refresh_btn)
        main_layout.addLayout(h1)

        # --- Switch GPU section ---
        switch_group = QGroupBox("Switch GPU")
        switch_group.setStyleSheet(styles.GROUPBOX_STYLE)
        switch_layout = QHBoxLayout()
        self.nvidia_radio = QRadioButton()
        self.intel_radio = QRadioButton()
        apply_btn = QPushButton("Apply")
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.setStyleSheet(styles.BUTTON_STYLE)
        apply_btn.clicked.connect(self.apply_switch)
        switch_layout.addWidget(self.nvidia_radio)
        switch_layout.addWidget(self.intel_radio)
        switch_layout.addWidget(apply_btn)
        switch_group.setLayout(switch_layout)
        main_layout.addWidget(switch_group)

        # --- GPU Stats section ---
        stats_group = QGroupBox("GPU Stats")
        stats_group.setStyleSheet(styles.GROUPBOX_STYLE)
        stats_group.setMinimumHeight(350)
        stats_layout = QVBoxLayout()

        # Stats grid
        self.stats_grid = QGridLayout()
        self.stats_labels = {}
        fields = ["Name", "Driver", "Memory Total (MB)", "Memory Used (MB)",
                  "GPU Utilization (%)", "Temperature (°C)"]
        for i, field in enumerate(fields):
            lbl = QLabel(f"{field}: ")
            val = QLabel("-")
            self.stats_labels[field] = val
            self.stats_grid.addWidget(lbl, i, 0)
            self.stats_grid.addWidget(val, i, 1)
        stats_layout.addLayout(self.stats_grid)

        # Utilization chart
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("GPU Utilization (%) Over Time")
        self.chart.legend().hide()

        self.axisX = QValueAxis()
        self.axisX.setRange(0, 60)
        self.axisX.setLabelFormat("%d")
        self.axisX.setTitleText("Time (s)")

        self.axisY = QValueAxis()
        self.axisY.setRange(0, 100)
        self.axisY.setTitleText("Utilization (%)")

        self.chart.addAxis(self.axisX, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axisX)
        self.series.attachAxis(self.axisY)

        chart_view = QChartView(self.chart)
        chart_view.setMinimumHeight(250)
        stats_layout.addWidget(chart_view)

        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)

        # --- GPU Processes section ---
        proc_group = QGroupBox("GPU Processes")
        proc_group.setStyleSheet(styles.GROUPBOX_STYLE)
        proc_layout = QVBoxLayout()

        self.proc_table = QTableWidget()
        self.proc_table.setColumnCount(4)
        self.proc_table.setHorizontalHeaderLabels(["PID", "Name", "GPU Memory (MB)", "Action"])
        self.proc_table.setMinimumHeight(200)
        self.proc_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.proc_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # --- Custom column widths ---
        header = self.proc_table.horizontalHeader()
        header.setSectionResizeMode(0, self.proc_table.horizontalHeader().ResizeMode.Fixed)
        self.proc_table.setColumnWidth(0, 140)  # PID wider

        header.setSectionResizeMode(1, self.proc_table.horizontalHeader().ResizeMode.Stretch)  # Name slightly narrower

        header.setSectionResizeMode(2, self.proc_table.horizontalHeader().ResizeMode.Fixed)
        self.proc_table.setColumnWidth(2, 140)  # Memory column wider

        header.setSectionResizeMode(3, self.proc_table.horizontalHeader().ResizeMode.Fixed)
        self.proc_table.setColumnWidth(3, 120)  # Kill button wider

        proc_layout.addWidget(self.proc_table)
        proc_group.setLayout(proc_layout)
        main_layout.addWidget(proc_group)

        # --- Reboot button ---
        self.reboot_btn = QPushButton("Reboot Now")
        self.reboot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reboot_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.reboot_btn.clicked.connect(self.reboot)
        self.reboot_btn.setVisible(False)
        main_layout.addWidget(self.reboot_btn)

        # --- Scroll area ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)

        # --- Timer for auto refresh ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)
        self.time_counter = 0

        # Initial update
        self.update_current()
        self.update_stats()
        self.update_processes()

    # --- GPU Switch and Current GPU ---
    def update_switch_options(self):
        gpus = get_available_gpus()
        self.nvidia_radio.setVisible(False)
        self.intel_radio.setVisible(False)

        if len(gpus) == 2:
            self.nvidia_radio.setText(gpus[0])
            self.nvidia_radio.setVisible(True)
            self.intel_radio.setText(gpus[1])
            self.intel_radio.setVisible(True)
        else:
            self.intel_radio.setText(gpus[0])
            self.intel_radio.setVisible(True)

    def update_current(self):
        self.update_switch_options()
        current_mode = get_current_gpu()

        if current_mode == "nvidia" and is_nvidia_loaded():
            stats = parse_nvidia_smi()
            gpu_name = stats.get("Name", "NVIDIA GPU")
        elif current_mode == "nvidia":
            gpu_name = "NVIDIA GPU"
        else:
            gpu_name = get_available_gpus()[-1]  # Integrated GPU name dynamically

        self.current_label.setText(
            f'<span style="color:#50fa7b;">Current GPU:</span> {gpu_name}'
        )

        if current_mode == "nvidia":
            self.nvidia_radio.setChecked(True)
        else:
            self.intel_radio.setChecked(True)

    def apply_switch(self):
        mode = "nvidia" if self.nvidia_radio.isChecked() else "intel" if self.intel_radio.isChecked() else None
        if not mode:
            QMessageBox.warning(self, "Error", "Select a GPU mode.")
            return
        if get_current_gpu() == mode:
            QMessageBox.information(self, "Info", "Already in that mode.")
            return
        try:
            switch_gpu(mode)
            QMessageBox.information(self, "Success", "GPU switched successfully. Reboot required.")
            self.reboot_btn.setVisible(True)
            self.update_current()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to switch: {str(e)}")

    # --- Stats and chart ---
    def update_stats(self):
        if is_nvidia_loaded():
            stats = parse_nvidia_smi()
            for key, lbl in self.stats_labels.items():
                lbl.setText(stats.get(key, "-"))

            util_str = stats.get("GPU Utilization (%)", "0")
            try:
                util_val = int(util_str)
            except ValueError:
                util_val = 0
            self.series.append(QPointF(self.time_counter, util_val))
            self.time_counter += 1
            if self.time_counter > 60:
                self.series.removePoints(0, self.series.count() - 60)
                self.axisX.setRange(self.time_counter - 60, self.time_counter)
        else:
            for lbl in self.stats_labels.values():
                lbl.setText("N/A")

        self.update_processes()

    # --- GPU Processes ---
    def update_processes(self):
        processes = parse_nvidia_processes()
        self.proc_table.setRowCount(len(processes))
        for row, proc in enumerate(processes):
            self.proc_table.setItem(row, 0, QTableWidgetItem(proc["PID"]))
            self.proc_table.setItem(row, 1, QTableWidgetItem(proc["Name"]))
            self.proc_table.setItem(row, 2, QTableWidgetItem(proc["GPU Memory (MB)"]))

            kill_btn = QPushButton("Kill")
            kill_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            kill_btn.setStyleSheet(
                "background-color: red; color: white; font-weight: bold; border-radius: 5px;"
            )
            kill_btn.clicked.connect(lambda _, pid=proc["PID"]: self.kill_process(pid))
            self.proc_table.setCellWidget(row, 3, kill_btn)

    def kill_process(self, pid):
        reply = QMessageBox.question(self, "Confirm",
                                     f"Kill process {pid}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                subprocess.check_call(["pkexec", "kill", "-9", pid])
                QMessageBox.information(self, "Success", f"Process {pid} killed.")
                self.update_processes()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to kill {pid}: {str(e)}")

    # --- Reboot ---
    def reboot(self):
        reply = QMessageBox.question(self, "Confirm", "Reboot now?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                subprocess.call(["pkexec", "reboot"])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reboot: {str(e)}")
