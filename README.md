# vertexai-learnings
A collection of hands-on bite-sized examples distilled from my real-world explorations with VertexAI, Gemini and related tooling

## Steps to run

1. week1_jsonSchema.py
   - Create a folder called samples
   - Create a venv within the folder and activate it. The commands to create a virtual environment called .venv are:
     - cd samples
     - python3 -m venv .venv
     - source .venv/bin/activate
   - Install the required dependencies
     - pip install -r requirements.txt
   - Copy .env.example to .env
     - Update the parameters
   - Since you are using VertexAI, authenticate to gcloud on the command line
     - gcloud auth login
     - gcloud config set project your-project_id
   - Run the python progran
     - python week1_jsonSchema.py
