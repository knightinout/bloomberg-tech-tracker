#!/usr/bin/env python3
"""
Scheduler Setup Script
Helps configure daily automation using cron (Linux/Mac) or Task Scheduler (Windows).
"""

import os
import sys
import platform
import subprocess
from pathlib import Path


def get_project_paths():
    """Get absolute paths for the project."""
    script_dir = Path(__file__).parent.absolute()
    project_dir = script_dir.parent
    main_script = script_dir / "main.py"
    venv_python = project_dir / "venv" / "bin" / "python"

    # For Windows
    if platform.system() == "Windows":
        venv_python = project_dir / "venv" / "Scripts" / "python.exe"

    return {
        'project_dir': str(project_dir),
        'script_dir': str(script_dir),
        'main_script': str(main_script),
        'venv_python': str(venv_python) if venv_python.exists() else sys.executable,
    }


def setup_cron_linux_mac(schedule_time="9:00"):
    """Set up cron job for Linux/Mac."""
    paths = get_project_paths()

    print("Setting up cron job for Linux/Mac...")
    print(f"Project directory: {paths['project_dir']}")
    print(f"Python interpreter: {paths['venv_python']}")

    # Parse time
    try:
        hour, minute = schedule_time.split(":")
        hour = int(hour)
        minute = int(minute)
    except:
        print("Error: Invalid time format. Use HH:MM (e.g., 9:00)")
        return False

    # Create cron command
    cron_command = f"{hour} {minute} * * * cd {paths['project_dir']} && {paths['venv_python']} {paths['main_script']} >> {paths['project_dir']}/logs/cron.log 2>&1"

    print("\nProposed cron entry:")
    print("-" * 70)
    print(cron_command)
    print("-" * 70)

    print("\nTo add this cron job, run the following commands:")
    print("\n1. Open crontab editor:")
    print("   crontab -e")
    print("\n2. Add this line to the file:")
    print(f"   {cron_command}")
    print("\n3. Save and exit")

    print("\nTo verify it was added:")
    print("   crontab -l")

    print("\nTo remove the cron job later:")
    print("   crontab -e  (then delete the line)")

    # Optionally try to add automatically
    response = input("\nWould you like to try adding this automatically? (y/n): ")
    if response.lower() == 'y':
        try:
            # Get current crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_cron = result.stdout if result.returncode == 0 else ""

            # Check if already exists
            if paths['main_script'] in current_cron:
                print("A cron job for this script already exists!")
                return True

            # Add new entry
            new_cron = current_cron.rstrip() + f"\n{cron_command}\n"

            # Install new crontab
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_cron)

            if process.returncode == 0:
                print("✓ Cron job added successfully!")
                return True
            else:
                print("✗ Failed to add cron job. Please add manually.")
                return False

        except Exception as e:
            print(f"Error adding cron job: {e}")
            print("Please add the cron job manually using the instructions above.")
            return False

    return True


def setup_task_scheduler_windows(schedule_time="9:00"):
    """Set up Task Scheduler for Windows."""
    paths = get_project_paths()

    print("Setting up Windows Task Scheduler...")
    print(f"Project directory: {paths['project_dir']}")
    print(f"Python interpreter: {paths['venv_python']}")

    # Create XML for task
    task_name = "BloombergTechAutomation"

    print(f"\nTo set up Task Scheduler manually:")
    print("1. Open Task Scheduler (search in Start menu)")
    print("2. Click 'Create Basic Task'")
    print(f"3. Name: {task_name}")
    print("4. Trigger: Daily")
    print(f"5. Start time: {schedule_time}")
    print("6. Action: Start a program")
    print(f"7. Program: {paths['venv_python']}")
    print(f"8. Arguments: {paths['main_script']}")
    print(f"9. Start in: {paths['project_dir']}")

    # Try to create using schtasks
    response = input("\nWould you like to try creating the task automatically? (y/n): ")
    if response.lower() == 'y':
        try:
            # Parse time
            hour, minute = schedule_time.split(":")

            cmd = [
                'schtasks', '/create',
                '/tn', task_name,
                '/tr', f'"{paths["venv_python"]}" "{paths["main_script"]}"',
                '/sc', 'daily',
                '/st', schedule_time,
                '/f'  # Force create/update
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✓ Task '{task_name}' created successfully!")
                print(f"\nTo view the task: schtasks /query /tn {task_name}")
                print(f"To delete the task: schtasks /delete /tn {task_name}")
                return True
            else:
                print(f"✗ Failed to create task: {result.stderr}")
                print("Please create the task manually using the instructions above.")
                return False

        except Exception as e:
            print(f"Error creating task: {e}")
            print("Please create the task manually using the instructions above.")
            return False

    return True


def setup_systemd_linux():
    """Set up systemd service and timer for Linux."""
    paths = get_project_paths()

    print("Setting up systemd service and timer...")

    service_content = f"""[Unit]
Description=Bloomberg Technology Automation
After=network.target

[Service]
Type=oneshot
User={os.getenv('USER', 'user')}
WorkingDirectory={paths['project_dir']}
ExecStart={paths['venv_python']} {paths['main_script']}
StandardOutput=append:{paths['project_dir']}/logs/automation.log
StandardError=append:{paths['project_dir']}/logs/automation.log

[Install]
WantedBy=multi-user.target
"""

    timer_content = """[Unit]
Description=Bloomberg Technology Automation Timer
Requires=bloomberg-tech.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
"""

    service_path = Path.home() / ".config" / "systemd" / "user" / "bloomberg-tech.service"
    timer_path = Path.home() / ".config" / "systemd" / "user" / "bloomberg-tech.timer"

    print("\nSystemd service file:")
    print("-" * 70)
    print(service_content)
    print("-" * 70)

    print("\nSystemd timer file:")
    print("-" * 70)
    print(timer_content)
    print("-" * 70)

    response = input("\nWould you like to create these systemd files? (y/n): ")
    if response.lower() == 'y':
        try:
            # Create directory
            service_path.parent.mkdir(parents=True, exist_ok=True)

            # Write files
            service_path.write_text(service_content)
            timer_path.write_text(timer_content)

            print("\n✓ Systemd files created!")
            print("\nTo enable and start the timer:")
            print("   systemctl --user daemon-reload")
            print("   systemctl --user enable bloomberg-tech.timer")
            print("   systemctl --user start bloomberg-tech.timer")
            print("\nTo check status:")
            print("   systemctl --user status bloomberg-tech.timer")
            print("   systemctl --user list-timers")

            return True

        except Exception as e:
            print(f"Error creating systemd files: {e}")
            return False

    return True


def main():
    """Main entry point."""
    print("="*70)
    print("Bloomberg Technology Automation - Scheduler Setup")
    print("="*70)

    system = platform.system()
    print(f"\nDetected OS: {system}")

    schedule_time = input("\nEnter daily run time (HH:MM format, e.g., 9:00): ").strip() or "9:00"

    if system in ["Linux", "Darwin"]:  # Darwin is macOS
        print("\nChoose scheduling method:")
        print("1. Cron (simple, works on all Unix systems)")
        print("2. Systemd (Linux only, more features)")

        choice = input("\nEnter choice (1 or 2): ").strip()

        if choice == "2" and system == "Linux":
            setup_systemd_linux()
        else:
            setup_cron_linux_mac(schedule_time)

    elif system == "Windows":
        setup_task_scheduler_windows(schedule_time)
    else:
        print(f"Unsupported operating system: {system}")
        return 1

    print("\n" + "="*70)
    print("Setup complete!")
    print("="*70)
    print("\nThe automation will run daily and generate:")
    print("  - Daily reports in: reports/daily/")
    print("  - Master document: reports/weekly_review_master.md")
    print("  - Logs in: logs/automation.log")

    return 0


if __name__ == "__main__":
    sys.exit(main())
