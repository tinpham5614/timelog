# Timelog App

## Overview
Timelog is a command-line application designed to help users track the time they spend on various tasks. It provides a simple interface to start and stop time entries, as well as to view summaries of logged time.

## Use Cases
- Problem: You need to track how much time you spend on different tasks.
- Solution: Use the timelog app to start and stop time entries, and view summaries of your logged time with simple commands.

## Features
- Start a new time entry
- Stop the current time entry
- View all time entries
- View total time spent on tasks

## Installation
1. Clone the repository and redirect to the project directory
   ```
    git clone https://github.com/tinpham5614/timelog.git
    cd timelog
   ```
2. Create a virtual environment (optional but recommended)
    ```
    python -m venv .venv
    source .venv/bin/activate # macOS/Linux
    source .venv\Scripts\activate # Windows
    ```
3. Install dependencies
    `pip install -e .` 

    Wait for the installation to complete. This will set up the timelog app and its dependencies.
    Congratulations! You have successfully set up the timelog app.

## Usage
- Start a new time entry: `timelog start`
- Stop the current time entry: `timelog stop`
- View the current time entry: `timelog current`
- View all time entries for today: `timelog summary`

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any bugs or feature requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details