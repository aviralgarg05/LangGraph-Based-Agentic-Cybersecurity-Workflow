import streamlit as st
import json
from datetime import datetime
from agent.agent_graph import run_agent, execute_task
from config import ALLOWED_DOMAINS, ALLOWED_IPS

# Set the title of the Streamlit app
st.title("Agentic Cybersecurity Pipeline")

# Sidebar configuration section for scan parameters
st.sidebar.header("Scan Configuration")
# Allow the user to select the type of scan: Basic, Full, or Custom
scan_type = st.sidebar.selectbox(
    "Select Scan Type",
    ["Basic", "Full", "Custom"]
)

# Provide descriptions for the different scan types
if scan_type == "Basic":
    st.sidebar.write("**Basic Scan includes:**\n- Nmap\n- Gobuster")
elif scan_type == "Full":
    st.sidebar.write("**Full Scan includes:**\n- Nmap\n- Gobuster\n- FFuF\n- SQLMap")

# Sidebar section for scope configuration (allowed domains and IP ranges)
st.sidebar.header("Scope Configuration")
allowed_domains = st.sidebar.text_input("Allowed Domains (comma-separated):", value="google.com,example.com")
allowed_ips = st.sidebar.text_input("Allowed IP Ranges (comma-separated):", value="192.168.0.0/24,10.0.0.0/24")

# Update the ALLOWED_DOMAINS and ALLOWED_IPS variables based on user input.
# Note: This may override the defaults from config for the duration of the app session.
ALLOWED_DOMAINS = allowed_domains.split(",")
ALLOWED_IPS = allowed_ips.split(",")

# Main input area for the target and protocol selection, using two columns for layout
col1, col2 = st.columns(2)

with col1:
    # Input field for the target domain/IP
    target = st.text_input("Enter target domain/IP:", 
                           help=f"Allowed domains: {', '.join(ALLOWED_DOMAINS)}")

with col2:
    # Dropdown to select the protocol for web-based scans (http or https)
    protocol = st.selectbox(
        "Protocol",
        ["http", "https"],
        help="Select protocol for web-based scans"
    )

# For custom scan type, allow users to choose which tools to run
if scan_type == "Custom":
    st.subheader("Tool Selection")
    use_nmap = st.checkbox("Run Nmap", value=True)
    use_gobuster = st.checkbox("Run Gobuster")
    use_ffuf = st.checkbox("Run FFuF")
    use_sqlmap = st.checkbox("Run SQLMap")

def format_scan_results(results):
    """
    Formats the scan results to include descriptions for each tool,
    making it easier for users to understand the output.

    Args:
        results (dict): A dictionary with scan tool outputs.

    Returns:
        dict: A formatted dictionary with additional description for each tool.
    """
    # Descriptions for each scanning tool
    descriptions = {
        "nmap": "Nmap is a network scanning tool used to discover hosts and services on a computer network.",
        "gobuster": "Gobuster is a tool used to brute-force URIs (directories and files) in web sites.",
        "ffuf": "FFuF (Fuzz Faster U Fool) is a web fuzzer written in Go, used to discover hidden files and directories.",
        "sqlmap": "SQLMap is an open-source penetration testing tool that automates the process of detecting and exploiting SQL injection flaws."
    }
    
    formatted = {}
    for tool, result in results.items():
        if result is None:
            formatted[tool] = {
                "status": "Failed",
                "error": "Tool execution failed or not installed",
                "description": descriptions.get(tool, "")
            }
        else:
            formatted[tool] = {
                "status": "Success",
                "output": result.get("output", ""),
                "error": result.get("error", ""),
                "description": descriptions.get(tool, "")
            }
    return formatted

# Create a progress bar and a placeholder for status updates
progress_bar = st.progress(0)
status_text = st.empty()

# Define the action when the "Start Scan" button is pressed
if st.button("Start Scan", type="primary"):
    if not target:
        # Display an error if no target is provided
        st.error("Please enter a valid target.")
    else:
        # Clean the target by removing protocol prefixes and extra spaces
        clean_target = target.replace('http://', '').replace('https://', '').strip()
        
        # Start a spinner to indicate the scan is running
        with st.spinner(f"Starting scan for {clean_target} ..."):
            # Based on the scan type, build the list of selected tools
            if scan_type == "Custom":
                selected_tools = []
                if use_nmap:
                    selected_tools.append({"tool": "nmap", "target": clean_target})
                if use_gobuster:
                    selected_tools.append({"tool": "gobuster", "target": clean_target, "protocol": protocol})
                if use_ffuf:
                    selected_tools.append({"tool": "ffuf", "target": clean_target, "protocol": protocol})
                if use_sqlmap:
                    selected_tools.append({"tool": "sqlmap", "target": clean_target, "protocol": protocol})
            elif scan_type == "Basic":
                # Basic scan includes only Nmap and Gobuster
                selected_tools = [
                    {"tool": "nmap", "target": clean_target},
                    {"tool": "gobuster", "target": clean_target, "protocol": protocol}
                ]
            elif scan_type == "Full":
                # Full scan includes all four tools
                selected_tools = [
                    {"tool": "nmap", "target": clean_target},
                    {"tool": "gobuster", "target": clean_target, "protocol": protocol},
                    {"tool": "ffuf", "target": clean_target, "protocol": protocol},
                    {"tool": "sqlmap", "target": clean_target, "protocol": protocol}
                ]
                    
            results = {}
            total_tasks = len(selected_tools)
            # Loop through each selected tool and execute its task
            for i, task in enumerate(selected_tools):
                # Append protocol to target if provided in the task dictionary
                task_target = task["target"]
                if "protocol" in task:
                    task_target = f"{task['protocol']}://{task_target}"
                # Execute the task using the execute_task function from the agent
                result = execute_task(task)
                if result["status"] == "failed":
                    st.error(f"Task {task['tool']} failed: {result['error']}")
                results[task["tool"]] = result
                # Update progress bar and status text based on task completion
                progress_bar.progress((i + 1) / total_tasks)
                status_text.text(f"Completed {i + 1}/{total_tasks} tasks")
            
            # Format the results for improved readability and description
            formatted_results = format_scan_results(results)
            st.write("## Scan Results")
            
            # Check for errors in the results and display allowed scope if errors exist
            if "error" in results:
                st.error(results["error"])
                st.info(f"Allowed domains: {', '.join(ALLOWED_DOMAINS)}")
                st.info(f"Allowed IP ranges: {', '.join(ALLOWED_IPS)}")
            else:
                # Create tabs for each tool's output
                tabs = st.tabs(list(formatted_results.keys()))
                for tab, (tool, data) in zip(tabs, formatted_results.items()):
                    with tab:
                        st.subheader(f"{tool.upper()} Scan")
                        st.write(data["description"])
                        if data["status"] == "Success":
                            st.code(data["output"])
                        else:
                            st.error(data["error"])
                            # Provide installation hints for specific tools if needed
                            if tool in ["gobuster", "ffuf"]:
                                st.info("To fix this, ensure the tool is installed:\n```bash\nbrew install {tool}```")
                
                # Save the final report with a timestamp in the filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_filename = f"final_report_{timestamp}.json"
                # Provide a download button for the JSON report of the scan results
                st.download_button(
                    label="Download Full Report",
                    data=json.dumps(formatted_results, indent=4),
                    file_name=report_filename,
                    mime="application/json"
                )