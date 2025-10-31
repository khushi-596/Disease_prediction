# Indradhanu — Climatic Risk Modeling (Full Web App)

## Quickstart (local, using docker-compose)
1. Build & run:
docker-compose up --build
2. Backend: http://localhost:8000
- API docs: http://localhost:8000/docs
3. Frontend: http://localhost:3000

## If running locally without Docker
### Backend
cd backend
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python simulate_data.py
python etl.py
python train.py

### Frontend
cd frontend
npm install
npm start

## Notes
- `train.py` generates `models/rf_model.pkl` and `models/lstm_model.h5`.
- `/predict` in the backend uses RF + LSTM ensemble to return predicted cases and risk level.
- `/alert` is a demo endpoint — integrate Twilio in `app.py` where commented.
