# HeartCare+ 🫀

A comprehensive heart disease prediction system that combines machine learning with an intuitive web interface to provide accurate cardiovascular risk assessments.

## 🚀 Features

### Core Functionality
- **Heart Disease Prediction**: Advanced ML models predict cardiovascular risk based on patient data
- **Multiple ML Models**: Support for Logistic Regression, Random Forest, and XGBoost algorithms
- **Risk Assessment**: Detailed risk analysis with percentage-based predictions
- **Patient Management**: Comprehensive patient record management system
- **Admin Dashboard**: Administrative interface for system oversight

### User Experience
- **Intuitive Interface**: Clean, responsive React-based frontend
- **Real-time Predictions**: Instant risk assessment results
- **Data Visualization**: Interactive charts and graphs using Recharts
- **PDF Reports**: Downloadable prediction reports with jsPDF
- **Mobile Responsive**: Optimized for all device sizes

## 🛠️ Technology Stack

### Backend
- **Flask 2.3.0** - Python web framework
- **Python 3.7+** - Core programming language
- **SQLite** - Database for data storage
- **scikit-learn 1.7.0** - Machine learning library
- **TensorFlow** - Deep learning framework
- **XGBoost** - Gradient boosting framework
- **Pandas & NumPy** - Data manipulation
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **React 18.2.0** - JavaScript UI library
- **TypeScript 4.9.5** - Type-safe development
- **Tailwind CSS 3.2.7** - Utility-first CSS framework
- **Axios 1.3.4** - HTTP client
- **React Router Dom 6.8.1** - Client-side routing
- **Recharts 3.1.2** - Data visualization
- **jsPDF 2.5.1** - PDF generation

## 📋 Prerequisites

- Python 3.7 or higher
- Node.js 14.0 or higher
- npm or yarn package manager

## 🔧 Installation

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/NuhaRizan/HeartCare.git
   cd HeartCare
   ```

2. **Navigate to the backend directory**
   ```bash
   cd "source code/web"
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the web directory:
   ```env
   # Email Configuration
   SENDGRID_API_KEY=your_sendgrid_api_key
   SENDER_EMAIL=your_verified_email@domain.com
   SENDER_NAME=Heart Care
   
   # Server Configuration
   LOCAL_SERVER_HOST=localhost
   LOCAL_SERVER_PORT=5000
   LOCAL_SERVER_PROTOCOL=http
   ```

5. **Initialize the database**
   ```bash
   python migrations/add_is_admin_column.py
   ```

### Frontend Setup

1. **Navigate to the frontend directory**
   ```bash
   cd ../../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

## 🚀 Running the Application

### Start the Backend Server
```bash
cd "source code/web"
python app.py
```
The backend will run on `http://localhost:5000`

### Start the Frontend Development Server
```bash
cd frontend
npm start
```
The frontend will run on `http://localhost:3000`

## 📊 Machine Learning Models

The system includes three trained models for heart disease prediction:

1. **Logistic Regression**: Fast, interpretable linear model
2. **Random Forest**: Ensemble method with high accuracy
3. **XGBoost**: Advanced gradient boosting for optimal performance

Models are trained on the UCI Heart Disease dataset and achieve accuracy rates above 85%.

## 🏗️ Project Structure

```
HeartCare/
├── source code/
│   ├── web/
│   │   ├── app.py                 # Main Flask application
│   │   ├── config.py              # Configuration settings
│   │   ├── requirements.txt       # Python dependencies
│   │   ├── controllers/           # Flask route controllers
│   │   ├── models/               # Database models and ML models
│   │   ├── services/             # External service integrations
│   │   └── migrations/           # Database migrations
│   └── notebook/                 # Jupyter notebooks for ML training
├── frontend/                     # React frontend application
├── README.md                     # Project documentation
└── Implementation_Report.md      # Detailed implementation report
```

## 🔒 Security Features

- Environment-based configuration for sensitive data
- No hardcoded API keys or secrets
- Input validation and sanitization
- CORS protection
- Secure database operations

## 📈 Usage

1. **User Registration**: Create an account to access the system
2. **Patient Data Input**: Enter patient information including:
   - Age, gender, chest pain type
   - Blood pressure and cholesterol levels
   - ECG results and exercise data
3. **Risk Assessment**: Get instant heart disease risk prediction
4. **Report Generation**: Download detailed PDF reports
5. **Admin Access**: Manage users and view system analytics

## 🧪 Testing

The project includes comprehensive test files:
- `test_email_download_link.py` - Email functionality testing
- `test_whatsapp.py` - WhatsApp integration testing
- `test_network_config.py` - Network configuration testing

Run tests with:
```bash
python -m pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Nuha Rizan** - Initial work and development
- **Contributors** - Thanks to all who contributed to this project

## 🙏 Acknowledgments

- UCI Machine Learning Repository for the Heart Disease dataset
- Flask and React communities for excellent documentation
- All open-source contributors who made this project possible

## 📞 Support

For support, email shinanmohamed363@gmail.com or create an issue in the GitHub repository.

---

**Made with ❤️ for better heart health**