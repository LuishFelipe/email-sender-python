# Automation to send emails

## Pre-settings Commands

**Clonning repository**
 - mkdir NEW_REPOSITORY
 - cd NEW_REPOSITORY
 - git clone https://github.com/USER/REPOSITORY.git
 - cd REPOSITORY

**Create & Install dependences**
 - python -m venv venv
 - source venv/bin/activate
 - pip install -r requirements.txt

**Execution Restricted Policy**
 - Get-ExecutionPolicy
 - Set-ExecutionPolicy Unrestricted -Scope Process
 - .\venv\Scripts\activate

## Api Execution
 - In the terminal run: uvicorn app:app --reload
 - Access the weeb borwser with http://localhost:8000/auth/login
 - Send emails with Postman or Insomnia running http://localhost:8000/send-emails as a POST or running in the terminal the command curl -X POST http://localhost:8000/send-emails
