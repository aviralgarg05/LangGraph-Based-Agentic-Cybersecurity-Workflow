import json
import logging
from datetime import datetime
from agent.task_manager import generate_tasks
from agent.task_executor import run_nmap, run_gobuster, run_ffuf, run_sqlmap

# Define our "node" function (simulating a LangGraph node)
def execute_task(task):
    """
    Executes a given security scanning task based on the tool specified.
    
    - Logs the execution details.
    - Calls the appropriate function based on the tool name.
    - Returns the output of the executed command.

    Args:
        task (dict): A dictionary containing the tool name and target.

    Returns:
        dict: The output of the tool execution, or an error message if the tool is unknown.
    """
    tool = task.get("tool")  # Extract the tool name
    target = task.get("target")  # Extract the target domain/IP
    logging.info(f"Executing task: {tool} on target: {target}")

    # Run the corresponding tool function based on the tool name
    if tool == "nmap":
        return run_nmap(target)
    elif tool == "gobuster":
        return run_gobuster(target)
    elif tool == "ffuf":
        return run_ffuf(target)
    elif tool == "sqlmap":
        return run_sqlmap(target)
    else:
        # Log an error if an unknown tool is specified
        logging.error(f"Unknown tool specified: {tool}")
        return {"status": "failed", "error": f"Unknown tool specified: {tool}"}

def run_agent(target):
    """
    Main function that orchestrates the security scanning process.

    - Generates a list of tasks for the given target.
    - Executes each task sequentially.
    - Dynamically adds new tasks based on results.
    - Saves the final output as a JSON report.

    Args:
        target (str): The domain or IP address to be scanned.

    Returns:
        dict: A dictionary containing the results of the executed tasks.
    """
    # Generate an initial list of security tasks for the target
    tasks = generate_tasks(target)
    
    if not tasks:
        # If no tasks were generated (e.g., target is out of scope), log an error and return
        logging.error("No tasks generated. The target might be out of scope.")
        return {"error": "Target is out of scope or no valid tasks were generated."}
    
    results = {}  # Dictionary to store results of each task

    # Iterate over each generated task and execute it
    for task in tasks:
        output = execute_task(task)  # Run the corresponding security tool
        results[task["tool"]] = output  # Store the output in results dictionary
        
        # Dynamically update tasks based on previous results
        if task["tool"] == "nmap" and "open" in output.get("output", ""):
            # If Nmap finds open ports, add extra scanning tasks
            if "80/tcp" in output.get("output", ""):
                tasks.append({"tool": "gobuster", "target": f"http://{target}"})  # Scan HTTP if port 80 is open
            if "443/tcp" in output.get("output", ""):
                tasks.append({"tool": "gobuster", "target": f"https://{target}"})  # Scan HTTPS if port 443 is open
    
    # Generate a timestamp for the report file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"reports/final_report_{timestamp}.json"

    # Save the final scan results to a JSON file
    with open(report_filename, "w") as f:
        json.dump(results, f, indent=4)  # Pretty-print JSON data
    
    logging.info(f"Final report saved to {report_filename}")  # Log the report location
    return results  # Return the final results