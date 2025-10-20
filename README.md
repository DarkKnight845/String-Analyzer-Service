## Local Setup Instructions
1. Prerequisites: Install Python 3.9+ and pip (or uv)
2. Clone the repositroy:
    ```
    git clone https://github.com/DarkKnight845/String-Analyzer-Service.git
    cd string-analyzer-service
    ```
3. Setup Environment and Dependencies
    ```
    # create and activate virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Install dependencies using uv or pip
    pip install requirements.txt
    ```
4. Running Locally:
    ```
    uvicorn main:app --reload --port 8000
    ```
The API documentation will be available at http://127.0.0.1:8000/docs