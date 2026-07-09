import os
import sys
import time
import logging
import subprocess


class Installer:

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.marker_file = os.path.join(base_dir, ".setup_complete")

        # Stable package versions
        self.packages = {
            "python-can": "4.3.1",
            "can-isotp": "2.0.2",
            "udsoncan": "1.22.1",
            "Pillow": "10.3.0",
            "adafruit-blinka": "8.40.0",
            "adafruit-circuitpython-ssd1306": "2.12.17",
            "smbus2": "0.4.3",
            "GitPython": "3.1.43"
        }

    def is_first_run(self):
        """
        Returns True only if setup has never been completed.
        """
        return not os.path.exists(self.marker_file)

    def install(self, oled):
        """
        Install all required packages.
        Returns True if successful.
        Returns False if any package fails.
        """

        logging.info("========== FIRST TIME SETUP ==========")

        # ------------------------------------------------
        # Upgrade pip
        # ------------------------------------------------
        oled.display_centered_text("Updating\npip...")

        logging.info("Upgrading pip...")

        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip"
            ],
            check=False
        )

        installation_failed = False
        total_packages = len(self.packages)

        # ------------------------------------------------
        # Install Packages
        # ------------------------------------------------
        for index, (package, version) in enumerate(
            self.packages.items(),
            start=1
        ):

            oled.display_centered_text(
                f"Installing\n{index}/{total_packages}\n\n{package}\n{version}"
            )

            logging.info(
                f"[{index}/{total_packages}] Installing {package}=={version}"
            )

            try:

                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "--upgrade",
                        f"{package}=={version}"
                    ],
                    check=True
                )

                logging.info(
                    f"{package} installed successfully."
                )

            except subprocess.CalledProcessError as e:

                installation_failed = True

                logging.error(
                    f"Failed to install {package}: {e}"
                )

                oled.display_centered_text(
                    f"Failed\n\n{package}"
                )

                time.sleep(2)

        # ------------------------------------------------
        # Installation Result
        # ------------------------------------------------
        if installation_failed:

            logging.warning(
                "Some packages failed to install."
            )

            oled.display_centered_text(
                "Setup\nFailed"
            )

            time.sleep(3)

            return False

        # ------------------------------------------------
        # Create marker file
        # ------------------------------------------------
        self.mark_completed()

        logging.info(
            "========== SETUP COMPLETE =========="
        )

        oled.display_centered_text(
            "Setup\nComplete"
        )

        time.sleep(2)

        return True

    def mark_completed(self):
        """
        Creates the marker file so installation
        will not run again.
        """

        try:

            with open(self.marker_file, "w") as file:
                file.write("Setup Complete")

            logging.info(
                ".setup_complete created successfully."
            )

        except Exception as e:

            logging.error(
                f"Unable to create marker file: {e}"
            )