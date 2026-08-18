\# 💰 Expense Tracker



A \*\*full-stack web application\*\* to track daily expenses with interactive charts, reports, and secure user authentication. Built with Python, Flask, and SQLite.



!\[Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)

!\[License](https://img.shields.io/badge/License-MIT-blue)

!\[Python](https://img.shields.io/badge/Python-3.9+-yellow)

!\[Flask](https://img.shields.io/badge/Flask-3.1.3-red)

!\[Render](https://img.shields.io/badge/Deployed-Render-purple)



\---



\## 🚀 Live Demo



🌐 \*\*\[View the Live Application](https://expense-tracker-5rf6.onrender.com)\*\*



> ⚠️ \*Free tier may take 30-50 seconds to wake up after inactivity.\*



\---



\## 📸 Screenshots



\### Dashboard

!\[Dashboard](https://via.placeholder.com/600x300?text=Dashboard+Screenshot)



\### Expense Management

!\[Expenses](https://via.placeholder.com/600x300?text=Expenses+Screenshot)



\### Charts \& Analytics

!\[Charts](https://via.placeholder.com/600x300?text=Charts+Screenshot)



\---



\## ✨ Features



| Feature | Description |

|---------|-------------|

| 🔐 \*\*User Authentication\*\* | Secure registration/login with bcrypt password hashing |

| 📊 \*\*Interactive Dashboard\*\* | Visual charts using Chart.js (Pie, Bar, Line charts) |

| ➕ \*\*CRUD Operations\*\* | Create, Read, Update, Delete expenses |

| 🔍 \*\*Search \& Filter\*\* | Search by description, filter by category, and date range |

| 📄 \*\*CSV Export\*\* | Download expense data as CSV for external analysis |

| 📈 \*\*Summary Reports\*\* | Category-wise and monthly spending breakdown |

| 📱 \*\*Responsive Design\*\* | Works on desktop, tablet, and mobile |

| 🛡️ \*\*Error Handling\*\* | Comprehensive input validation and error pages |



\---



\## 🛠️ Tech Stack



\### Backend

\- \*\*Python\*\* 3.9+

\- \*\*Flask\*\* 3.1.3 - Web framework

\- \*\*SQLite\*\* - Lightweight database

\- \*\*bcrypt\*\* - Password hashing

\- \*\*Gunicorn\*\* - Production WSGI server



\### Frontend

\- \*\*HTML5\*\* - Structure

\- \*\*CSS3\*\* - Styling with gradients and animations

\- \*\*Chart.js\*\* - Interactive charts



\### Deployment

\- \*\*Render\*\* - Cloud hosting (free tier)

\- \*\*Git\*\* - Version control

\- \*\*GitHub\*\* - Code repository



\---



\## 🏗️ Project Structure



expense-tracker/

├── app.py # Main Flask application

├── database.py # Database operations

├── auth.py # Authentication helpers

├── requirements.txt # Python dependencies

├── .env # Environment variables

├── .gitignore # Git ignore rules

├── README.md # Project documentation

├── exports/ # CSV export folder

├── templates/

│ ├── index.html # Home page

│ ├── dashboard.html # Analytics dashboard

│ ├── report.html # Summary report

│ ├── add.html # Add expense form

│ ├── edit.html # Edit expense form

│ ├── login.html # Login page

│ ├── register.html # Registration page

│ ├── 404.html # Custom 404 page

│ └── 500.html # Custom 500 page

└── static/

└── style.css # Global styles





\---



\## 📥 Installation (Run Locally)



\### 1. Clone the Repository

```bash

git clone https://github.com/likhitha816/expense-tracker.git

cd expense-tracker



