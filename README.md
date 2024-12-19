# Project Setup

This document explains how to set up and run the project. Follow the steps below to install the required dependencies and get started.

## Prerequisites

Make sure you have the following installed:

- **Python**: Version 3.6 or above. You can download it from [python.org](https://www.python.org/).
- **pip**: Python's package installer (comes pre-installed with Python).

## Installation

### Step 1: Clone the Repository

Clone the project repository to your local machine:

```bash
git clone <repository-url>
cd <repository-directory>
```

### Step 2: Create a Virtual Environment (Optional but Recommended)

Create and activate a virtual environment to keep dependencies isolated:

**For Windows:**
```bash
python -m venv env
env\Scripts\activate
```

**For macOS/Linux:**
```bash
python -m venv env
source env/bin/activate
```

### Step 3: Install Dependencies

Install the required Python libraries listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Step 4: Verify the Installation

Run the following script to ensure all dependencies are installed correctly:

```bash
python -c "import serial; from PyQt5.QtCore import QThread, pyqtSignal; print('Setup complete!')"
```

If you see the message `Setup complete!`, everything is installed correctly.

## Requirements

The project requires the following Python packages:

- `pyserial`: For serial communication.
- `PyQt5`: For GUI development.

These dependencies are already listed in the `requirements.txt` file.

## Running the Project

To run the project, execute the main script:

```bash
python main.py
```

Replace `main.py` with the actual entry point script of your project.

## Troubleshooting

- If you encounter issues with missing packages, ensure you have followed the steps in the Installation section.
- For Python version-related issues, check your Python version with:

  ```bash
  python --version
  ```

- If you continue to face issues, create a new virtual environment and reinstall dependencies.

---

Feel free to reach out for support if you encounter any issues during the setup process!

