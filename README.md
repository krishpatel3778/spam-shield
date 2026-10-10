# SpamShield AI

A ready-to-run educational Flask project for email spam classification and cyber-safety guidance.

## Features
- Separate pages: Home, Email Scanner, Cyber Safety, Citizen Manual, Report Cybercrime, and After a Scam.
- Light, responsive design with animations and mobile navigation.
- Text classification using TF-IDF + Linear SVM.
- `/predict` JSON endpoint retained for the scanner UI.
- Official links to India's Cyber Crime Reporting Portal.
- Bundled small example dataset so the project can run without downloading a dataset.

## Requirements
- Python 3.10 or newer recommended
- Internet connection for the optional Google Fonts stylesheet; the site still works without it.

## Windows setup (VS Code terminal)
Open this folder in VS Code, then run these commands in the terminal:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe app.py
```

If `python` is not recognised, try `py` in the first command:
```powershell
py -m venv venv
```

Open http://127.0.0.1:5000 in your browser. Stop the server with Ctrl+C.

The first run trains the model from `dataset/emails.csv` and creates `model/spamshield_model.joblib`.

## Important notes
- The bundled dataset is small and only demonstrates the pipeline. It is **not suitable for real-world security decisions** and its apparent performance should not be treated as meaningful.
- The risk indicator is a simple educational heuristic, not a calibrated probability.
- A “safe” prediction does not guarantee an email is safe.
- The app does not register or track government complaints. Those actions happen on the official portal: https://cybercrime.gov.in/
- For financial cyber fraud in India, call 1930 promptly and follow official guidance.
- Change `SECRET_KEY` before any deployment and do not deploy Flask's debug server publicly.


## Explainable scan results
The scanner shows the model class, human-readable warning signals, suggested next steps, and what to do if the user already interacted. The risk indicator is an educational heuristic, not a calibrated probability. The bundled dataset is a small demonstration dataset; do not use this project as a sole basis for security decisions.
