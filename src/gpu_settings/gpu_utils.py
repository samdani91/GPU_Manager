import subprocess
import csv
from io import StringIO

def get_integrated_gpu():
    try:
        output = subprocess.check_output(["lspci"], text=True).splitlines()
        for line in output:
            line_lower = line.lower()

            # Consider VGA or display controllers
            if "vga" in line_lower or "display controller" in line_lower:

                # Skip NVIDIA discrete GPUs
                if "nvidia" in line_lower:
                    continue

                # Skip discrete AMD GPUs
                # Heuristic: discrete AMD GPUs usually contain "amd/ati" but are not "lucienne" or "renoir" (APUs)
                if "amd/ati" in line_lower:
                    # Common integrated AMD keywords: Renoir, Lucienne, Cezanne
                    if any(keyword in line_lower for keyword in ["renoir", "lucienne", "cezanne"]):
                        return "Integrated (AMD)"
                    else:
                        continue  # discrete AMD GPU, skip

                # Intel GPU detection
                if "intel" in line_lower:
                    return "Integrated (Intel)"

        # Fallback if no GPU matched
        return "Integrated (Unknown)"

    except Exception:
        return "Integrated (Unknown)"



def get_current_gpu():
    try:
        output = subprocess.check_output(["prime-select", "query"], stderr=subprocess.STDOUT).decode().strip()
        return output
    except Exception as e:
        return f"Error: {str(e)}"

def switch_gpu(mode: str):
    subprocess.check_call(["pkexec", "prime-select", mode])

def is_nvidia_loaded():
    try:
        output = subprocess.check_output(["lsmod | grep nvidia"], shell=True).decode().strip()
        return bool(output)
    except:
        return False

def parse_nvidia_smi():
    """Return dict with GPU stats instead of raw text."""
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu,driver_version",
             "--format=csv,noheader,nounits"],
            stderr=subprocess.STDOUT
        ).decode().strip()

        name, mem_total, mem_used, util, temp, driver = output.split(", ")
        return {
            "Name": name,
            "Driver": driver,
            "Memory Total (MB)": mem_total,
            "Memory Used (MB)": mem_used,
            "GPU Utilization (%)": util,
            "Temperature (°C)": temp
        }
    except Exception as e:
        return {"Error": str(e)}

def parse_nvidia_processes():
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-compute-apps=pid,process_name,used_gpu_memory",
                "--format=csv,noheader,nounits"
            ],
            stderr=subprocess.STDOUT
        ).decode().strip()

        processes = []
        if not output:
            return processes

        csv_reader = csv.reader(StringIO(output), skipinitialspace=True)
        for row in csv_reader:
            if len(row) >= 3:
                pid, name, mem = row[0], row[1], row[2]
                processes.append({
                    "PID": pid,
                    "Name": name,
                    "GPU Memory (MB)": mem
                })
        return processes

    except subprocess.CalledProcessError as e:
        return []
    except Exception:
        return []
    
def has_nvidia_gpu():
    try:
        output = subprocess.check_output(["lspci"], text=True)
        return "NVIDIA" in output
    except Exception:
        return False

def get_available_gpus():
    gpus = [get_integrated_gpu()]
    if has_nvidia_gpu():
        gpus.insert(0, "NVIDIA GPU")  # placeholder if driver inactive
    return gpus
