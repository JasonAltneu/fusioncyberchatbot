Deployment Instructions:

1) Package Installations: Ensure that you have Next and NPM installed with the following scripts
    a) npm -v   (Should give 11.11.0)
    b) node -v  (Should give v22.18.0)
2) Open Two Terminals (Called Terminal 1 and Terminal 2)
    a) Terminal 1 instructions
        i) Navigate to backend directory
        ii) Enter a virtual environment with venv\Scripts\activate
        iii) Run python main.py to launch the backend server
    b) Terminal 2 instructions
        i) Navigate to frontend directory
        ii) Run npm run start

Design Choice Justifications
1) Backend - Uvicorn: Chosen due to easy of implementation 
2) UI/UX - React: This was chosen due to familiarity with the React system after prior implementation in other projects.
3) Memory - SQLite: Chosen due to familiarity with SQL as a result of completing Database Design at the University of Maryland. Additionally, the DATETIME datatype for SQL allows me to rebuild the dialogue history for a specific chat by going through the timestamps from oldest to newest.