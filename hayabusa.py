import os
import subprocess

def parse_event_logs(event_logs_path, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define Hayabusa executable path
    hayabusa_exe = r"C:\Users\2482964\Desktop\TAPE\tools\hayabusa-3.0.1-win-x64\hayabusa-3.0.1-win-x64.exe"

    # Define output file
    csv_timeline_output = os.path.join(output_dir, "csv_timeline.csv")

    # CSV timeline command
    csv_timeline_command = [
        hayabusa_exe, "csv-timeline",
        "-d", event_logs_path,
        "-o", csv_timeline_output
    ]
    
    try:
        # Run Hayabusa with automated input using subprocess.run
        result = subprocess.run(
            csv_timeline_command,
            input="1\ny\n",  # Simulate user input (1 + Enter, then y + Enter)
            text=True,
            capture_output=True,
            encoding="utf-8"
        )

        # Debugging: Print output and errors
        print("Hayabusa Output:\n", result.stdout)
        if result.stderr:
            print("Hayabusa Errors:\n", result.stderr)

        # Check if file was created
        if os.path.exists(csv_timeline_output):
            print(f"File successfully created: {csv_timeline_output}")
        else:
            print(f"File not found: {csv_timeline_output}. Check for errors.")

    except FileNotFoundError:
        print(f"Error: Hayabusa executable not found at {hayabusa_exe}. Check the path.")
    except subprocess.CalledProcessError as e:
        print(f"Error running Hayabusa: {e}")

if __name__ == "__main__":
    event_logs_path = r'C:\Users\2482964\Desktop\TAPE\output\eventlogs\Logs'  # Use a valid Windows path
    output_dir = r"C:\Users\2482964\Desktop\TAPE\parsed_artifacts\eventlogs"  # Use raw strings for paths
    
    parse_event_logs(event_logs_path, output_dir)
