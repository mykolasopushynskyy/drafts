# Define the name of your virtual environment directory
VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
BLACK = $(VENV_DIR)/bin/black
AUTOFLAKE = $(VENV_DIR)/bin/autoflake
PIPREQS = $(VENV_DIR)/bin/pipreqs

# Define the directories or files to format and check
SRC_DIRS = .

# Target to create a virtual environment
activate:
	python3 -m venv $(VENV_DIR)
	chmod +x $(VENV_DIR)/bin/activate
	. '$(VENV_DIR)/bin/activate'
	$(PIP) install --upgrade pip
	$(PIP) install black autoflake pipreqs

# Target to apply code style using black
format: activate
	$(BLACK) $(SRC_DIRS)

# Target to remove unused imports and variables using autoflake
clean-imports: activate
	$(AUTOFLAKE) --in-place --remove-all-unused-imports --recursive $(SRC_DIRS)

# Target to generate requirements.txt using pipreqs
requirements: activate
	$(PIP) install -r requirements.txt

# Target to run both formatting and import cleanup
lint: format clean-imports

.PHONY: format clean-imports lint activate requirements.txt
