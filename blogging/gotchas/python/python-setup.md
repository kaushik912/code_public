# Syncing Python Virtual Environment and VSCode

Below steps really simplify the development experience in Python. 

Its always good to use the same python interpreter in both VSCode and the virtual environment.

This will avoid conflicts with dependencies.

### Install Python from Self -Service

- First install the PayPal official supported Python version. 
- At the time of writing this, it was version=3.12.8
- This version already has pip settings to function over zscalar proxy.
- Also, install Python Proxy configs.
- Try `python3 --version`
    - It displayed  3.12.8
- `which python3`
    - It displayed `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3`
- Remember this path as it would be useful while specifying the environment in VSCode.

### Python Extension
- Make sure you have installed the Python extension in VS Code before proceeding to next steps.

## Running Python code using Visual Studio Code

1. Now, press Ctrl + Shift + P > Python Create Environment
    - Select  Venv : creates ‘.venv’ virtual environment in the current workspace
    - Select  python interpreter of your choice , I chose 3.12.8 which is system default.
    - Once that’s done, wait for the virtual environment to get created

2. Now, kill old  terminals and start a fresh one (shortcut: Ctrl+~).
    - Type  python --version  and it should display 3.12.8
    - Also, in vscode, it should activate the virtual env in the new terminal.

3. After this, run the python programs underneath that directory.

### Running Notebooks using Jupyter (Recommended)

- Now, activate the virtual environment and select runtime as 3.12.8
- With all this in place, we can either run it inside VSCode notebook or we could run separately.
- I recommend to run separately.

- `pip install jupyter`
- Now, run using  `jupyter notebook`

- Using Jupyter Notebook (Browser): So the sequence is Create venv → Install  Jupyter  → Run  jupyter notebook 
 

## Manual Steps

1. Identify Python Versions
    - To know the available python versions on your system, use
    - `which python3.11` , `which python3.12` ,  `which python3.13`  
    - You can identify where each version is coming from. For me, few were coming from homebrew.
    -  We can also know default version python3 is using  `python3 --version` , it was  `Python 3.13.1`  on my mac
    - One can also search in brew using `brew list | grep python`

2. Create a virtual env 
    - `python -m venv .venv`

3. Activate the New Virtual Environment
    - `source .venv/bin/activate`

4. Install Your Dependencies
    - `pip install -r requirements.txt`

### Generating requirements.txt

Once you have successfully run the program, you could generate the requirements.txt

1. Move to the code directory where you want to run the code

    a. `cd kkailasnath-testing/localchatbot/src`

    b. Run,  `pip install pipreqs`

    c. Then run,  `pipreqs .`

    d. It generates a `requirements.txt`

    e. then, finally run  `pip install -r requirements.txt`

### De-activating virtual environment

1. You can de-activative existing environment using  the command `deactivate` in the terminal

2. Then remove the virtual env using:
    - `rm -rf .venv`

 ### Working with different versions of python and related packages
- One simple way is to open vscode in the nearest directory where the code resides.
    - Create a virtual env 
    - That way we can isolate the python version specific to that directory
    - For another directory, if it requires different version, we could create a new virtual env.
- There are other ways like de-activating old virtual env and activating new virtual env.
- Its a good idea to run `python -version` in the activated terminal or notebooks to cross check if the python version is coming as expected or not. 

