# PhotoManagerProto
Making REST calls to gcloud vision /image:annotate and azure /face/detect and /vision/describe + /vision/analyze

## Intro example
### Linux
```sh
python -m venv venv
. venv/Scripts/activate
pip install ipykernel requests Pillow
```
### Windows Powershell
```powershell
python -m venv venv
venv/Scripts/activate.ps1
pip install ipykernel requests Pillow
```

Then set the python interpreter to that in the venv ```Shift-Ctrl-P -> Python: Select Interpreter```

Open ```workbook.py``` and click the codelens  ```"Run below"``` at the very top of the file to execute all cells.    