# Agentic Cybersecurity Pipeline Documentation

This document provides a detailed overview of the Agentic Cybersecurity Pipeline, a sophisticated system that leverages LangGraph and LangChain to autonomously decompose security tasks into a series of executable steps. The pipeline is designed to enforce strict target scopes, execute security scans, dynamically update task lists, and log every action for comprehensive reporting.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Dependencies](#dependencies)
- [Installation Instructions](#installation-instructions)
  - [For Windows](#for-windows)
  - [For Mac](#for-mac)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Agent Structure](#agent-structure)
  - [agent_graph.py](#agent_graphpy)
  - [task_manager.py](#task_managerpy)
  - [task_executor.py](#task_executorpy)
- [Technologies Used](#technologies-used)
- [Testing & Verification](#testing--verification)
- [Code Structure](#code-structure)
- [License](#license)

---

## Overview

The Agentic Cybersecurity Pipeline is engineered to streamline and automate cybersecurity assessments. By breaking down high-level security instructions into a series of granular, executable tasks, the system:
- **Dynamically generates and updates task lists** based on ongoing scan results.
- **Ensures rigorous scope enforcement** to prevent scans from impacting unintended targets.
- **Integrates seamlessly with industry-standard security tools** (e.g., `nmap`, `gobuster`, `ffuf`, `sqlmap`).
- **Executes tasks sequentially** with robust error handling and retry mechanisms.
- **Logs every action** for comprehensive analysis and reporting.

This automation is critical for scaling security assessments while maintaining strict adherence to defined target boundaries.

---

## Features

- **Task Decomposition**: Automatically breaks down high-level security goals into step-by-step tasks.
- **Dynamic Task List Management**: Continuously updates the task list based on real-time scan outputs and intermediate results.
- **Scope Enforcement**: Validates each target against allowed domains and IP ranges to prevent unauthorized scanning.
- **Integrated Security Tools**:
  - **nmap**: Performs network mapping and port scanning.
  - **gobuster**: Conducts directory brute-forcing.
  - **ffuf**: Executes web fuzzing to detect vulnerabilities.
  - **sqlmap**: Tests for SQL injection vulnerabilities.
- **Robust Error Handling**: Implements retries and error logs to manage task failures efficiently.
- **Comprehensive Logging and Reporting**: Captures detailed logs of each operation and compiles a final report for audit and review.
- **User-Friendly Interface**: Utilizes Streamlit for an interactive web interface that displays scan progress and results in real time.

---

## Dependencies

### Python Dependencies

- **[streamlit](https://streamlit.io/)**: Builds the interactive web interface.
- **[pytest](https://docs.pytest.org/en/latest/)**: Runs unit tests to ensure reliability.
- **[requests](https://docs.python-requests.org/en/latest/)**: Facilitates HTTP requests.
- **[python-dotenv](https://pypi.org/project/python-dotenv/)**: Loads environment variables from a `.env` file.

### System-Level Dependencies

- **[nmap](https://nmap.org/book/man.html)**: A network scanning tool used for mapping and port scanning.
- **[gobuster](https://github.com/OJ/gobuster)**: A directory and file brute-forcing tool.
- **[ffuf](https://github.com/ffuf/ffuf)**: A web fuzzing tool for identifying hidden web content.
- **[sqlmap](https://github.com/sqlmapproject/sqlmap)**: Automates the process of detecting and exploiting SQL injection vulnerabilities.

---

## Installation Instructions

### For Windows

1. **Install Python 3.11**  
   Download and install Python 3.11 from [python.org](https://www.python.org/downloads/).

2. **Create a Virtual Environment**  
   Open Command Prompt and run:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Python Dependencies**  
   In the activated environment, run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install System-Level Dependencies**  
   Follow the respective installation guides:
   - [nmap Installation](https://nmap.org/book/inst-windows.html)
   - [gobuster](https://github.com/OJ/gobuster)
   - [ffuf](https://github.com/ffuf/ffuf)
   - [sqlmap](https://github.com/sqlmapproject/sqlmap)

### For Mac

1. **Install Python 3.11**  
   Download and install Python 3.11 from [python.org](https://www.python.org/downloads/).

2. **Create a Virtual Environment**  
   Open Terminal and run:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Python Dependencies**  
   With the virtual environment activated, run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install System-Level Dependencies**  
   Follow the respective installation guides:
   - [nmap Installation](https://nmap.org/book/inst-macosx.html)
   - [gobuster](https://github.com/OJ/gobuster)
   - [ffuf](https://github.com/ffuf/ffuf)
   - [sqlmap](https://github.com/sqlmapproject/sqlmap)

---

## Configuration

Before running the application, create a `.env` file in the project root directory with the following content:

```env
ALLOWED_DOMAINS=google.com,example.com
ALLOWED_IPS=192.168.0.0/24,10.0.0.0/24
```

- **ALLOWED_DOMAINS**: Specifies which domains can be scanned.
- **ALLOWED_IPS**: Defines IP ranges allowed for scanning.
  
This configuration ensures that the system strictly adheres to the defined target scope.

---

## Running the Application

To start the interactive Streamlit application:

1. Ensure your virtual environment is activated.
2. Run the following command:
   ```bash
   streamlit run streamlit_app.py
   ```
3. **User Interface**:  
   - Use the sidebar to define the scan scope.
   - Enter the target domain/IP.
   - Select the type of scan you wish to perform.
   - Click **"Start Scan"** to initiate the pipeline.

The application will display real-time progress, task execution logs, and a final report summarizing all actions taken.

---

## Agent Structure

The system is modularized into several key Python modules, each responsible for a distinct aspect of the cybersecurity pipeline.

### `agent_graph.py`

- **Purpose**: Manages the main workflow of the agent.
- **Key Functions**:
  - **`execute_task(task)`**: Executes a specific task based on the designated tool. It logs the operation and handles errors or retries.
  - **`run_agent(target)`**: 
    - Generates a sequence of tasks for the given target.
    - Executes each task in order.
    - Collects and saves outputs into a comprehensive final report.
- **Workflow**: Utilizes LangGraph to define the agent’s task flow and LangChain to handle dynamic task management and error recovery.

### `task_manager.py`

- **Purpose**: Oversees task generation and ensures that every target falls within the allowed scope.
- **Key Functions**:
  - **`is_within_scope(target)`**: Validates the target against the configured domains and IP ranges.
  - **`generate_tasks(target)`**: Constructs an ordered list of tasks with proper protocol handling, ensuring compliance with the defined scope.
- **Scope Enforcement**: Prevents unauthorized scanning by strictly checking each target before execution.

### `task_executor.py`

- **Purpose**: Executes shell commands associated with various security tools and manages retries on failure.
- **Key Functions**:
  - **`run_command(command)`**: A generic function to execute shell commands with robust error handling.
  - **`run_nmap(target)`**: Launches an `nmap` scan to map the target’s network and open ports.
  - **`run_gobuster(target)`**: Executes a `gobuster` scan to discover hidden directories and files.
  - **`run_ffuf(target)`**: Initiates a `ffuf` scan for web fuzzing, identifying potential vulnerabilities.
  - **`run_sqlmap(target)`**: Runs `sqlmap` to test for SQL injection vulnerabilities.
- **Error Handling**: Implements retry logic and logs all outputs for audit purposes.

---

## Technologies Used

- **[LangGraph](https://github.com/langchain-ai/langgraph)**: Orchestrates the agent workflow and task dependencies.
- **[LangChain](https://www.langchain.com/)**: Manages dynamic task lists, error handling, and retry mechanisms.
- **[Streamlit](https://streamlit.io/)**: Provides a responsive web interface for visualizing scan progress and results.
- **[Pytest](https://docs.pytest.org/en/latest/)**: Used for unit testing to ensure the system's reliability and robustness.

---

## Testing & Verification

To ensure the pipeline operates correctly:

1. **Run Unit Tests**:  
   Execute the following command in your virtual environment:
   ```bash
   pytest
   ```
2. **Verification in Streamlit**:  
   - Launch the Streamlit app as described above.
   - Monitor the log output and final report to verify that each task is executed correctly.
   - Confirm that only targets within the allowed scope are scanned.

Regular testing and monitoring are essential to maintain system reliability and adherence to security protocols.

---

## Code Structure

The project is organized into several key modules:

- **`streamlit_app.py`**
  - **Purpose**: Provides the web interface.
  - **Key Sections**:
    - **Configuration**: Sets scan scope and selects scan types.
    - **Task Execution**: Initiates scans and displays real-time progress.
    - **Result Formatting**: Organizes and presents scan results clearly.

- **`agent_graph.py`**
  - **Purpose**: Orchestrates the overall agent workflow.
  - **Key Functions**: `execute_task(task)`, `run_agent(target)`.

- **`task_manager.py`**
  - **Purpose**: Generates and validates task lists.
  - **Key Functions**: `is_within_scope(target)`, `generate_tasks(target)`.

- **`task_executor.py`**
  - **Purpose**: Executes security tool commands and handles errors.
  - **Key Functions**: `run_command(command)`, `run_nmap(target)`, `run_gobuster(target)`, `run_ffuf(target)`, `run_sqlmap(target)`.

Each module is designed to operate independently while contributing to the overall security assessment workflow.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*This detailed documentation is designed to help you set up, configure, and operate the Agentic Cybersecurity Pipeline effectively. For further customization or troubleshooting, refer to the inline comments in the source code and the official documentation of the integrated tools.*
