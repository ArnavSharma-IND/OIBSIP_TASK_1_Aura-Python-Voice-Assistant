"""
Desktop Application Launcher Module for ArnavSharma_Task1.
Handles opening commonly used desktop software and tools on Windows.
"""

import os
import shutil
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

from utils.logger import get_logger

logger = get_logger("AppLauncher")


# Standard Windows application executables & aliases
APP_REGISTRY: Dict[str, List[str]] = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "explorer": ["explorer.exe"],
    "file explorer": ["explorer.exe"],
    "command prompt": ["cmd.exe"],
    "cmd": ["cmd.exe"],
    "powershell": ["powershell.exe"],
    "task manager": ["taskmgr.exe"],
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "chrome.exe",
    ],
    "google chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "chrome.exe",
    ],
    "edge": ["msedge.exe"],
    "microsoft edge": ["msedge.exe"],
    "vscode": ["code.cmd", "code.exe"],
    "vs code": ["code.cmd", "code.exe"],
    "visual studio code": ["code.cmd", "code.exe"],
}


class AppLauncher:
    """Launches local desktop applications upon voice command."""

    def __init__(self, custom_apps: Optional[Dict[str, List[str]]] = None):
        self.registry = dict(APP_REGISTRY)
        if custom_apps:
            self.registry.update(custom_apps)

    def launch(self, app_name: str) -> Tuple[bool, str]:
        """
        Launches an application matching the requested name.

        Args:
            app_name: Name of the application (e.g. 'calculator', 'notepad').

        Returns:
            Tuple of (success: bool, spoken_feedback: str)
        """
        clean_name = app_name.strip().lower()
        if not clean_name:
            return False, "Please specify which application you would like to open."

        # Find matching key in registry
        target_executables = None
        for key, paths in self.registry.items():
            if key == clean_name or key in clean_name or clean_name in key:
                target_executables = paths
                clean_name = key
                break

        if not target_executables:
            # Attempt to run directly as a system command if it looks like a single command
            if re_match := clean_name.replace(" ", ""):
                target_executables = [f"{re_match}.exe", re_match]

        for exe_target in target_executables:
            try:
                # If absolute path, check existence
                if os.path.isabs(exe_target):
                    if os.path.exists(exe_target):
                        subprocess.Popen([exe_target], shell=True)
                        logger.info(f"Launched application: {exe_target}")
                        return True, f"Opening {clean_name.title()}."
                    continue

                # If command name, check if in PATH or shell
                if shutil.which(exe_target) or sys.platform == "win32":
                    subprocess.Popen([exe_target], shell=True)
                    logger.info(f"Launched application via shell: {exe_target}")
                    return True, f"Opening {clean_name.title()}."

            except Exception as err:
                logger.warning(f"Could not launch executable '{exe_target}': {err}")

        return False, f"Could not find or launch application '{app_name}'."

