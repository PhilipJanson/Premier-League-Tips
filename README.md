# Premier-League-Tips

Website written in Python powered by Flask and api-sports.io to display Premier League fixtures and 
to place simple bets on them.

Currently a work-in-progress

### Installation
Dependencies specified in [`requirements.txt`](./requirements.txt)

`PATH_TO_PYTHON_EXE`:
`C:\Users\%username%\AppData\Local\Programs\Python\Python36\python.exe`
```ps
pip install virtualenv
virtualenv --python <PATH_TO_PYTHON_EXE> .venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Start app
```ps
py main.py
```

### Lint repo
Linting rules specified in [`.pylintrc`](./.pylintrc)
```ps
pylint ${PWD}
```

### Notes 
`./keys.py` is omitted to protect `API_KEY` and `APP_SECRET_KEY`