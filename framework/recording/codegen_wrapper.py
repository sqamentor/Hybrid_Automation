"""
Playwright Codegen Wrapper
Provides easy-to-use interface for Playwright's code generation with enhanced features
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger


class PlaywrightCodegen:
    """
    Wrapper for Playwright's codegen with additional features:
    - Easy configuration
    - Multiple output formats
    - Browser selection
    - Viewport/device emulation
    - API capture integration
    """

    def __init__(self, output_dir: str = "recorded_tests"):
        """
        Initialize Playwright Codegen wrapper

        Args:
            output_dir: Directory to save recorded scripts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Playwright Codegen initialized. Output: {self.output_dir}")

    def start_recording(
        self,
        url: str,
        test_name: str,
        browser: str = "chromium",
        language: str = "python-pytest",
        device: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        capture_api: bool = True,
        additional_args: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Start Playwright codegen recording session

        Args:
            url: Starting URL for recording
            test_name: Name for the generated test file
            browser: Browser to use (chromium, firefox, webkit)
            language: Output language (python-pytest, python, javascript, java, csharp)
            device: Device to emulate (iPhone 12, Pixel 5, etc.)
            viewport: Custom viewport size {"width": 1280, "height": 720}
            capture_api: Enable API traffic capture
            additional_args: Additional playwright codegen arguments

        Returns:
            Dict with recording metadata
        """
        # Sanitize test name
        safe_name = test_name.replace(" ", "_").lower()
        output_file = self.output_dir / f"{safe_name}.py"

        # Build codegen command
        cmd = [
            "playwright",
            "codegen",
            "--target",
            language,
            "--output",
            str(output_file),
            "--browser",
            browser,
        ]

        # Add device emulation
        if device:
            cmd.extend(["--device", device])

        # Add viewport
        if viewport:
            cmd.extend(["--viewport-size", f"{viewport['width']},{viewport['height']}"])
        else:
            # Default: use screen dimensions so browser opens maximized
            try:
                import ctypes
                screen_w = ctypes.windll.user32.GetSystemMetrics(0)
                screen_h = ctypes.windll.user32.GetSystemMetrics(1)
            except Exception:
                screen_w, screen_h = 1920, 1080
            cmd.extend(["--viewport-size", f"{screen_w},{screen_h}"])


        # Add additional arguments
        if additional_args:
            cmd.extend(additional_args)

        # Add URL (must be last)
        cmd.append(url)

        logger.info(f"Starting Playwright Codegen recording for: {test_name}")
        logger.info(f"Command: {' '.join(cmd)}")
        logger.info(f"Output will be saved to: {output_file}")

        # Show instructions
        print("\n" + "=" * 80)
        print("🎬 PLAYWRIGHT CODEGEN RECORDING STARTED")
        print("=" * 80)
        print(f"📝 Test Name: {test_name}")
        print(f"🌐 Starting URL: {url}")
        print(f"🖥️  Browser: {browser}")
        print(f"💾 Output File: {output_file}")
        if device:
            print(f"📱 Device: {device}")
        print("\nINSTRUCTIONS:")
        print("1. Perform your test actions in the browser window")
        print("2. Playwright will record all interactions")
        print("3. Close the browser when done")
        print("4. Script will be saved automatically")
        print("=" * 80 + "\n")

        # Execute codegen
        try:
            result = subprocess.run(cmd, check=False)

            if result.returncode == 0:
                logger.info(f"✓ Recording completed: {output_file}")

                # Check if file was created
                if output_file.exists():
                    file_size = output_file.stat().st_size
                    logger.info(f"✓ Generated file size: {file_size} bytes")

                    return {
                        "status": "success",
                        "output_file": str(output_file),
                        "test_name": safe_name,
                        "file_size": file_size,
                        "browser": browser,
                        "url": url,
                        "capture_api": capture_api,
                    }
                else:
                    logger.warning("Recording completed but file not found")
                    return {
                        "status": "warning",
                        "message": "Recording completed but output file not created",
                    }
            else:
                logger.error(f"Recording failed with code: {result.returncode}")
                return {
                    "status": "error",
                    "message": f"Recording failed with exit code {result.returncode}",
                }

        except FileNotFoundError:
            logger.error("Playwright not found. Install with: playwright install")
            return {
                "status": "error",
                "message": "Playwright not installed. Run: pip install playwright && playwright install",
            }
        except Exception as e:
            logger.error(f"Recording error: {e}")
            return {"status": "error", "message": str(e)}

    def quick_record(self, url: str, test_name: str, mobile: bool = False) -> Dict[str, Any]:
        """
        Quick recording with sensible defaults

        Args:
            url: Starting URL
            test_name: Test name
            mobile: Use mobile viewport (iPhone 12)

        Returns:
            Recording metadata
        """
        device = "iPhone 12" if mobile else None
        return self.start_recording(url=url, test_name=test_name, device=device, capture_api=True)

    def record_with_auth(self, url: str, test_name: str, save_auth: bool = True) -> Dict[str, Any]:
        """
        Record with authentication state saving

        Args:
            url: Starting URL
            test_name: Test name
            save_auth: Save authentication state

        Returns:
            Recording metadata
        """
        additional_args = []
        if save_auth:
            auth_file = self.output_dir / f"{test_name}_auth.json"
            additional_args.extend(["--save-storage", str(auth_file)])

        return self.start_recording(url=url, test_name=test_name, additional_args=additional_args)

    def get_recording_metadata(self, test_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a recorded test"""
        safe_name = test_name.replace(" ", "_").lower()
        output_file = self.output_dir / f"{safe_name}.py"

        if not output_file.exists():
            return None

        return {
            "file_path": str(output_file),
            "file_size": output_file.stat().st_size,
            "created_at": output_file.stat().st_ctime,
            "modified_at": output_file.stat().st_mtime,
        }

    def list_recordings(self) -> List[Dict[str, Any]]:
        """List all recorded test files"""
        recordings = []

        for py_file in self.output_dir.glob("*.py"):
            recordings.append(
                {
                    "name": py_file.stem,
                    "path": str(py_file),
                    "size": py_file.stat().st_size,
                    "created": py_file.stat().st_ctime,
                }
            )

        return recordings


# Convenience functions
def record_test(url: str, test_name: str, **kwargs) -> Dict[str, Any]:
    """Quick function to start recording"""
    codegen = PlaywrightCodegen()
    return codegen.start_recording(url, test_name, **kwargs)


def quick_record(url: str, test_name: str, mobile: bool = False) -> Dict[str, Any]:
    """Quick recording with defaults"""
    codegen = PlaywrightCodegen()
    return codegen.quick_record(url, test_name, mobile)
