import sys  # Module for handling command-line arguments
from agent.agent_graph import run_agent  # Import the main agent function to run the scan

# Check if the script is executed as the main module
if __name__ == "__main__":
    # Ensure that a target is provided via command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <target>")
        sys.exit(1)  # Exit if no target is provided
    
    # Retrieve the target (domain or IP) from the command-line arguments
    target = sys.argv[1]
    print(f"Starting scan on: {target}")
    
    # Call the main agent function to perform the scan on the target
    results = run_agent(target)
    
    # Inform the user that the scan has been completed and where to find the report
    print("Scan completed. Check reports/final_report.json for details.")