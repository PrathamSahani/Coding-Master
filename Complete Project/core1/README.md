 
 Follow the steps below to set up and run the project.
   Make sure Python is installed on your system. Download it from the [official Python website](https://www.python.org/downloads/).

   ```bash
   # Check if Python is installed
   python --version

2. **setup Django**

 ```bash
   #  Django is installed
   pip install django

   # Verify the installation
   django-admin --version
```

### Set Up Your Virtual Environment 
To avoid dependency issues, it is recommended to create a virtual environment. Here's how:
1. Open the extracted folder in **VS Code**.
2. In the terminal, create the virtual environment:
   ```bash
   python -m venv env
   ```
3. Activate the virtual environment:
   ```bash
   .\env\Scripts\activate.ps1
   ```

### Install Dependencies
Once inside the virtual environment, install Django:
```bash
pip install django
pip install -r requirement.txt
```

### Navigate to the Project Directory
Move to the main `core1` directory where the `manage.py` file is located:

### Migrate the Database
Apply database migrations using the following commands:
```bash
python manage.py makemigrations
python manage.py makemigrations compiler
python manage.py migrate
```

### Start the Server
Finally, start the Django development server:
```bash
python manage.py runserver