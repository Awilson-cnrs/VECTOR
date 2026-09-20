# VECTOR Project

A Python 3.12 project for data analysis and visualization, designed to run in **Spyder** or **JupyterLab** with isolated Conda environments.

## 🚀 Setup Instructions

### 1️⃣ Clone the Repository
```
git clone https://github.com/Awilson-cnrs/VECTOR.git
cd VECTOR
```

### 2️⃣ Create a ```VECTOR_env``` conda virtual environment
The project requires Python 3.12 and specific dependencies. Run:

```
conda env create -f environment.yml
conda activate VECTOR_env
```



For Jupyter Notebook Users: install the Jupyter kernel in ```VECTOR_env``` virtual environment:
```
python -m ipykernel install --user --name=VECTOR_env
```

For Spyder Users:
Open Spyder after activating the environment (conda activate VECTOR_env).
Spyder will automatically use the environment’s Python interpreter.
3️⃣ Install Local Dependencies
The VECTORtools package is included in the repository. To make it importable:
bash
Copier

pip install -e .




This installs the package in editable mode, so changes to VECTORtools are reflected immediately.
4️⃣ Configure Paths (If Needed)
The project references a data directory (Z:\RawData\TestCata). To avoid hardcoding paths:
Option 1: Environment Variable
Set the DATA_PATH variable before running scripts/notebooks:
bash
Copier

# Linux/Mac:
export DATA_PATH="Z:/RawData/TestCata"

# Windows (Command Prompt):
set DATA_PATH=Z:\RawData\TestCata




Then, in your code:
python
Copier

import os
from pathlib import Path
data_path = Path(os.getenv("DATA_PATH"))





Option 2: Config File
Create a config.yaml in the project root:
yaml
Copier

data_path: Z:/RawData/TestCata




Load it in Python:
python
Copier

import yaml
with open("config.yaml") as f:
    config = yaml.safe_load(f)
data_path = Path(config["data_path"])





🛠 Usage
For JupyterLab:
Activate the environment:bash
Copier

conda activate VECTOR_env





Launch JupyterLab:bash
Copier

jupyter lab





Select the VECTOR_env kernel when opening a notebook.
For Spyder:
Activate the environment:bash
Copier

conda activate VECTOR_env





Open Spyder from the terminal (to inherit the environment):bash
Copier

spyder





Run scripts directly in Spyder.
🔧 Environment Management
Update the Environment
If environment.yml changes, update the environment:
bash
Copier

conda env update -f environment.yml




Deactivate the Environment
bash
Copier

conda deactivate




Remove the Environment
bash
Copier

conda env remove --name VECTOR_env




📝 Notes
Python 3.12 Compatibility: Ensure all dependencies support Python 3.12. If not, downgrade specific packages in environment.yml.
Path Handling: Avoid hardcoding paths like Z:\RawData\TestCata. Use environment variables or config files (as shown above).
Local Imports: The VECTORtools package is installed in editable mode (pip install -e .), so changes to its code take effect immediately.
Git Ignore: Add the following to .gitignore to avoid committing environment files:text
Copier

# Conda
envs/
VECTOR_env/

# Jupyter
.ipynb_checkpoints/

# Spyder
.spyderproject/





🤝 Contributing
Fork the repository.
Create a new branch (git checkout -b feature-branch).
Commit your changes (git commit -m "Add new feature").
Push to the branch (git push origin feature-branch).
Open a Pull Request.
📄 License
This project is licensed under the MIT License.
