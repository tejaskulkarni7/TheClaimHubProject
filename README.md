# TheClaimHubProject

# Setup
 - In project root directory run the following command: python -m pip install -r requirements.txt (You may have to do python3 -m pip install -r requirements.txt)
 - in the __init__.py file, change the connection details to match your database.
 - then run the project by doing: python3 run.py

# Libraries to Download
 - Install the latest python from https://www.python.org/downloads/ or go to the terminal and type:
    Linux: sudo apt-get install python3
    Mac OS: brew install python (install brew https://brew.sh/)
 - Install pip by going to the terminal and typing
    Linux/Mac OS: $ python -m ensurepip --upgrade
    Windows: C:> py -m ensurepip --upgrade
# How to Run
 - Download the repository from: https://github.com/tejaskulkarni7/theclaimhubproject.git from terminal
 - Configure your MySQL details in __init__.py
 - Run the provided sql file in your MySQL workbench to create tables and insert sample data
 - To run the project: (in terminal) navigate into TheClaimHubProject folder and type in the terminal: python3 run.py left click on http://127.0.0.1:5000/ (while pressing ctrl or cmd)
 - To run the project: (IDE) on your ide, open the project repository navigate to TheClaimHubProject run run.py left click on http://127.0.0.1:5000/ (while pressing ctrl or cmd)


# Division of Work
 Tejas Kulkarni (Team Leader) - User signup/login backend logic, claim page (all claims as well as update 
                                status, comment, delete, etc.), search and sort functionality, admin page.
 Anubhav Sawhney - Feature to allow user to create and add their own insurance / hospital. Edit log captures 
                   for claim update status, delete, and addition. Was primary contributor to canva presentation
 Alfred Koh - Backend/Frontend development to "add claims" feature. Developed an info page that gave user feedback.
              Primary contributor to design schema and ER diagram.
 Aung Bo Bo - Profile page backend and frontend development. Change password, delete profile functionality. Patient page as 
              well as add patient functionality. Primary contributor to architecture design.
 Kaung Sithu Hein - Fully developed procedure page as well as add procedure functionality. User signup/login frontend and 
                    forms creation. Regularly modified and maintained schema and ensured it reflected projects needs
 
