import subprocess  # For running shell commands
import logging  # For logging events and errors
from config import MAX_RETRIES  # Importing the retry limit from config file
import os  # For file and directory operations
from pathlib import Path  # For handling file paths
import shutil  # For checking if required tools are installed
import json  # For handling JSON output from ffuf
from datetime import datetime  # For timestamping reports

# Ensure the logs and reports directories exist
os.makedirs("logs", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Configure logging (logs will be written to logs/audit.log)
logging.basicConfig(
    filename="logs/audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_wordlist_path():
    """Retrieve the path to the wordlist file, creating it if it does not exist."""
    wordlist_path = os.path.expanduser("~/wordlists/common.txt")  # Define the wordlist path
    
    if not os.path.exists(wordlist_path):
        os.makedirs(os.path.dirname(wordlist_path), exist_ok=True)  # Create directory if needed
        with open(wordlist_path, 'w') as f:
            # Write common directory names to the wordlist
            f.write("admin\nlogin\nwp-admin\napi\ntest\ndev\n")
    
    return wordlist_path  # Return the path to the wordlist file

def run_command(command, retries=MAX_RETRIES):
    """Execute a shell command with retry logic and error handling."""
    attempt = 0
    while attempt < retries:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,  # Capture stdout and stderr
                text=True,
                timeout=300  # Set a timeout of 5 minutes
            )
            
            if result.returncode == 0:  # Check if command executed successfully
                logging.info(f"Command succeeded: {command}")
                return {"status": "success", "output": result.stdout}
            else:
                error_msg = f"Command failed: {result.stderr}"
                logging.error(error_msg)
                attempt += 1
                if attempt < retries:
                    logging.info(f"Retrying command ({attempt}/{retries}): {command}")
                else:
                    return {"status": "failed", "error": error_msg}
                    
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after 300 seconds: {command}"
            logging.error(error_msg)
            attempt += 1
            if attempt < retries:
                logging.info(f"Retrying command ({attempt}/{retries}): {command}")
            else:
                return {"status": "failed", "error": error_msg}
        except Exception as e:
            error_msg = f"Error executing command {command}: {str(e)}"
            logging.error(error_msg)
            attempt += 1
            if attempt < retries:
                logging.info(f"Retrying command ({attempt}/{retries}): {command}")
            else:
                return {"status": "failed", "error": error_msg}

def check_environment():
    """Verify that all required tools are installed, logging any missing ones."""
    tools = {
        'nmap': 'brew install nmap',
        'gobuster': 'brew install gobuster',
        'ffuf': 'brew install ffuf',
        'sqlmap': 'brew install sqlmap'
    }
    
    for tool, install_cmd in tools.items():
        if not shutil.which(tool):  # Check if the tool is installed
            logging.error(f"{tool} not found. Install with: {install_cmd}")
            return False
    return True

def run_nmap(target):
    """Run an Nmap scan on the target."""
    command = f"nmap -Pn {target}"
    return run_command(command)

def run_gobuster(target):
    """Run Gobuster for directory enumeration using a predefined wordlist."""
    wordlist = get_wordlist_path()
    
    # Fix double protocol issue
    target = target.replace('https://https://', 'https://')
    
    command = f"gobuster dir -u {target} -w {wordlist} -t 50"
    logging.info(f"Running gobuster with command: {command}")
    return run_command(command)

def run_ffuf(target):
    """Run FFUF for directory fuzzing with optimized settings."""
    wordlist = get_wordlist_path()
    
    # Ensure proper URL formatting
    if not target.startswith(('http://', 'https://')):
        target = f"https://{target}"
    
    # Fix double protocol issue
    target = target.replace('https://https://', 'https://')
    target = target.replace('http://http://', 'http://')
    
    # Ensure target ends with trailing slash
    if not target.endswith('/'):
        target = f"{target}/"
    
    # Create a unique output filename
    output_file = f"ffuf_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Build FFUF command with additional parameters
    command = (
        f"ffuf "
        f"-u {target}FUZZ "
        f"-w {wordlist} "
        f"-mc 200,301,302,403 "  # Match codes
        f"-c "  # Enable colors
        f"-v "  # Verbose output
        f"-r "  # Follow redirects
        f"-t 40 "  # Number of threads
        f"-timeout 10 "  # Timeout in seconds
        f"-o {output_file} "  # Save output to JSON
        f"-of json "  # Output format as JSON
        f"-recursion "  # Enable recursion
        f"-recursion-depth 2"  # Set recursion depth
    )
    
    logging.info(f"Running ffuf with command: {command}")
    
    # Execute the command
    result = run_command(command)
    
    # Try to read the JSON output file if it exists
    try:
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                ffuf_json = json.load(f)
                
                # Format the output for better readability
                formatted_output = []
                if "results" in ffuf_json:
                    for entry in ffuf_json["results"]:
                        url = entry.get("url", "N/A")
                        status = entry.get("status", "N/A")
                        length = entry.get("length", "N/A")
                        words = entry.get("words", "N/A")
                        lines = entry.get("lines", "N/A")
                        
                        formatted_output.append(
                            f"Found: {url}\n"
                            f"Status: {status}\n"
                            f"Length: {length}\n"
                            f"Words: {words}\n"
                            f"Lines: {lines}\n"
                            f"{'-' * 40}"
                        )
                
                if formatted_output:
                    result["output"] = "\n".join(formatted_output)
                else:
                    result["output"] = "No results found"
                    
            # Clean up the temporary file
            os.remove(output_file)
    except Exception as e:
        logging.error(f"Error processing ffuf output: {str(e)}")
        if result.get("status") == "success":
            result["output"] = result.get("output", "No results found")
    
    logging.info(f"FFUF output: {result.get('output', '')}")
    return result

def run_sqlmap(target):
    """Run SQLMap with automated SQL injection testing."""
    command = (
        f"sqlmap -u {target} "
        "--batch "  # Run in batch mode (no user input)
        "--random-agent "  # Use a random user agent
        "--level 1 "  # Set testing level
        "--risk 1 "  # Set risk level
        "--threads 4 "  # Use multiple threads
        "--timeout 30"  # Set timeout
    )
    logging.info(f"Running sqlmap with command: {command}")
    return run_command(command)