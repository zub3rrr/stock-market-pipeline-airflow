# Stock Market Pipeline Using Apache Airflow
A scalable end-to-end stock market ETL pipeline orchestrated with Apache Airflow. It extracts real-time and historical data from APIs, applies validation and transformations, and loads clean, analytics-ready datasets to support dashboards, ML models, and financial analysis.

## How to do a Project Setup [Easiest Way]
### 📌 Prerequisites

Before running the project, ensure the following tools are installed:

- **Astro CLI**
- **Docker Desktop**
- **Git**

---

# 🛠️ Install Astro CLI

Astro CLI helps you run Airflow locally using a simple developer-friendly workflow.

---

## macOS Installation (via Homebrew)

1. Update Homebrew:
   ```bash
   brew update
   brew install astro

2. Verify Install
    ```bash
    astro version

If in this step everything runs fine and you are able to see your version then you've successfully installed Astro CLI.

---

## Windows (via Powershell)

1. Open PowerShell as Administrator.

2. Run the Powershell Command
    ```bash
    winget install -e --id Astronomer.Astro
3. Verify - using same command as used in MacOS.

---

## Lets Run Airflow to run the pipeline

### 📦 Clone the Repository

1. Use the following commands to download and enter the project folder:

    ```bash
    https://github.com/zub3rrr/stock-market-pipeline-airflow.git



2. Once done then go to project folder
```bash
    cd stock-market-pipeline-airflow

3. Initialize Airflow (Terminal)
    ```bash
    astro dev start (To Start)

    astor dev stop (To Stop)


**Note:** Username = password = admin.


    

















