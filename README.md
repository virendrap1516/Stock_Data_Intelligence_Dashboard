# 📈 Stock Data Intelligence Dashboard ⚡

## 🚀 Live Demo

- **Frontend (Vercel):**  
  https://stock-data-intelligence-dashboard-nine.vercel.app/ 🚀

- **Backend (Render):**  
  https://stockdata-intelligence.onrender.com 🚀
## 🛠 Tech Stack

### Frontend
- HTML
- CSS
- JavaScript
- Chart.js
- Deployed on **Vercel**

### Backend
- Python
- FastAPI
- Uvicorn
- Pandas
- Deployed on **Render**

---
## ✨ Features

- 📈 Interactive stock price charts
- 🏢 Company-wise stock listing
- 📊 7-day moving average visualization
- 🔁 Stock comparison with normalized prices
- 📅 Time-range filtering
- 📉 52-week high, low & average price summary
- ⚡ FastAPI-powered REST APIs

  ## 🔗 API Endpoints

| Method | Endpoint | Description |
|------|---------|------------|
| GET | `/` | Health check |
| GET | `/companies` | List of available companies |
| GET | `/data/{symbol}` | Stock price data for a company |
| GET | `/summary/{symbol}` | 52-week summary |
| GET | `/compare` | Compare two stocks |

## 📦▶ How to Run
### Backend Setup ⚙️
```sh
 cd backend📂
   ```
* Install requirements
```sh
 pip install -r requirements.txt📂
   ```
* Python data
```sh
python data_prep.py📂
   ```
* Run project
```sh
 uvicorn main:app --reload📂
   ```
### Backend runs on:
http://127.0.0.1:8000 🚀

### Frontend Setup 🌟
```sh
 Open frontend/index.html📂
   ```
* Run project 
```sh
 Show in browser 🚀
   ```
* Update API base URL in script.js if needed
```sh
const API_BASE = "http://127.0.0.1:8000";
   ```
## Screenshots🎆 - 
### Backend running ⚙️ -
<img width="1920" height="1080" alt="Screenshot 2026-01-16 162054" src="https://github.com/user-attachments/assets/7a65dbcf-95c7-4fb9-85dc-99c40a24093c" />
<img width="1919" height="1079" alt="Screenshot 2026-01-17 185151" src="https://github.com/user-attachments/assets/ab0232b9-7e72-4d7c-beaa-03be88f51e07" />

### Api test 🔗
<img width="1920" height="1080" alt="Screenshot 2026-01-16 162217" src="https://github.com/user-attachments/assets/578ec2d5-b9ad-44e1-ab8b-9a81d5958706" />

### Frontend 🎉
<img width="1920" height="1080" alt="Screenshot 2026-01-16 162152" src="https://github.com/user-attachments/assets/cb9cd19f-99a1-4ea0-bd71-5d4fdedccb76" />

### Comparing two stocks ⚖️
<img width="1917" height="1024" alt="Screenshot 2026-01-17 172028" src="https://github.com/user-attachments/assets/5859e359-76e5-4549-98b5-3b32324b5d23" />

## 📌 Deployment

* Frontend: Deployed on Vercel
* Backend: Deployed on Render
* CORS configured for cross-origin communication

_Made with ❤️ by [Virendra Pawar](https://github.com/virendrap1516)_

Email: Virendrapawar47@gmail.com 📧
