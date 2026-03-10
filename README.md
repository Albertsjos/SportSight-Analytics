# SportSight Analytics ⚽

SportSight is a comprehensive sports performance tracking and squad management web application designed for players and coaches. It provides deep statistical insights, AI-driven performance analysis, and automated attendance tracking with a premium, modern user interface.

## 🌟 Key Features

### 1. **AI Performance Intelligence**
- **Season Intelligence**: Detailed statistical profiles for every player.
- **AI Suggested Insights**: Automated performance analysis that highlights strengths (e.g., "Clinical Finisher") and identifies areas for improvement.
- **Dynamic Radar Charts**: Visual performance breakdowns comparing Goals, Assists, Tackles, and Shots.

### 2. **Advanced Comparisons**
- **1v1 Player Battle**: Compare two players head-to-head with radar charts and statistical breakdowns.
- **Playing XI Comparison**: Analyze multiple players simultaneously to optimize squad selection.
- **Trend Analysis**: Monitor performance fluctuations over time.

### 3. **Squad Management**
- **Dual Dashboard System**:
    - **Admin Dashboard**: Bulk import match data via CSV, manage attendance, and view top performers.
    - **User Dashboard**: Personalized stats for individual players.
- **Digital Attendance**: Track training and match attendance with automated summaries for coaches.

### 4. **Modern UI/UX**
- **Premium Aesthetics**: Glassmorphism design with sleek gradients and smooth animations.
- **Global Theme Support**: Seamlessly switch between **Dark Mode** and **Light Mode**.
- **Responsive Design**: Fully optimized for both desktop and tablet views.

## 🛠️ Technology Stack
- **Backend**: Django (Python)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6+)
- **Charts**: Chart.js
- **Database**: SQLite (Development)

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Pip (Python Package Manager)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Albertsjos/SportSight-Analytics.git
   cd SportSight-Analytics
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install django
   ```

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start the server**:
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000` in your browser.

## 📈 CSV Data Format
For bulk uploads, use a CSV with the following headers:
`match_date, opponent, venue, player_name, goals, assists, shots_on_target, tackles`

---
Developed with ❤️ by the SportSight Team.
