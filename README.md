# Fitness & Diet Management System

A comprehensive AI-powered fitness and diet management web application built with FastAPI and Streamlit, providing personalized nutrition analysis, workout plans, meal planning, and health tracking.

## Features

### 🏋️ **Fitness Planning**

- Personalized workout plans based on fitness level, goals, and available equipment
- Weekly schedules with specific exercises, sets, reps, and rest periods
- Progressive overload strategies and recovery protocols
- Home or gym-based workout options

### 🥗 **Nutrition Analysis**

- BMI calculation and categorization
- Daily calorie requirements based on Mifflin-St Jeor equation
- Macronutrient breakdown (protein, carbs, fats)
- Hydration recommendations
- Caffeine consumption guidance with personalized limits

### 📋 **Meal Planning**

- Comprehensive meal plans with daily/weekly/monthly budget considerations
- Cuisine preferences and dietary restrictions support
- Calorie tracking and macro breakdowns
- Shopping lists and meal prep tips
- Support for various diets (Vegetarian, Vegan, Keto, etc.)

### 👩‍🍳 **Recipe Generator**

- AI-powered recipe creation from available ingredients
- Customizable servings, prep time, and budget constraints
- Nutrition information and cost breakdowns
- Allergy-aware recipe suggestions

### 🌸 **Period Nutrition**

- Menstrual cycle-specific nutrition guidance
- Phase-based recommendations for different cycle stages
- Symptom management through diet
- Iron-rich food suggestions and anti-inflammatory options

### ☕ **Caffeine Guidance**

- Personalized caffeine limits based on age, weight, and sensitivity
- Coffee and tea preparation tips
- Timing recommendations for optimal consumption
- Health warnings and alternatives

### 🤖 **AI Chatbot**

- Interactive fitness and nutrition assistant
- Personalized advice based on user profile
- Answers to questions about workouts, meals, and health
- Conversation history support

### 📊 **Progress Tracking**

- Comprehensive tracking systems for fitness goals
- Milestone setting and achievement monitoring
- Warning signs for overtraining or inadequate nutrition
- Motivation strategies and habit building

## Installation

### Prerequisites

- Python 3.8 or higher
- Hugging Face API token (for AI features)

### Backend Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd diet-mgmt
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the root directory:

```env
HF_TOKEN=your_hugging_face_api_token_here
```

5. Start the FastAPI backend:

```bash
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Open a new terminal and activate the virtual environment (if not already activated)

2. Install Streamlit (if not included in requirements.txt):

```bash
pip install streamlit
```

3. Start the Streamlit frontend:

```bash
streamlit run app.py
```

The web application will open in your default browser at `http://localhost:8501`

## Usage

### Getting Started

1. Ensure both backend and frontend servers are running
2. Fill out your profile in the sidebar with personal information
3. Navigate through different features using the sidebar menu
4. Each feature provides personalized recommendations based on your profile

### API Endpoints

#### Core Endpoints

- `GET /` - API information and available endpoints
- `GET /health-check` - API health status

#### Main Features

- `POST /nutrition-analysis` - Complete nutrition analysis with BMI, calories, macros, and caffeine guidance
- `POST /fitness-plan` - Personalized workout plans
- `POST /meal-plan` - Comprehensive meal planning with budget considerations
- `POST /recipe-generator` - AI-generated recipes from available ingredients
- `POST /period-nutrition` - Menstrual cycle-specific nutrition guidance
- `POST /caffeine-guidance` - Detailed caffeine consumption recommendations
- `POST /chatbot` - Interactive AI assistant for fitness and nutrition queries
- `POST /progress-tracking` - Progress tracking systems and milestone planning

### User Profile Fields

- Age, gender, weight, height
- Fitness level and goals
- Dietary preferences and restrictions
- Budget constraints
- Health conditions and allergies
- Work schedule and available time
- Gym access and equipment availability

## API Documentation

### Request/Response Examples

#### Nutrition Analysis

```json
POST /nutrition-analysis
{
  "age": 25,
  "gender": "Female",
  "weight_kg": 65.0,
  "height_cm": 165.0,
  "fitness_level": "Intermediate",
  "goal": "Weight Loss",
  "diet_preference": "Vegetarian",
  "budget_amount": 50.0,
  "budget_type": "Daily"
}
```

#### Fitness Plan Generation

```json
POST /fitness-plan
{
  "age": 30,
  "gender": "Male",
  "weight_kg": 80.0,
  "height_cm": 180.0,
  "fitness_level": "Beginner",
  "goal": "Muscle Building",
  "gym_access": true,
  "work_hours": "9 AM - 5 PM",
  "free_time": "6 PM - 10 PM"
}
```

## Environment Variables

| Variable   | Description                            | Required |
| ---------- | -------------------------------------- | -------- |
| `HF_TOKEN` | Hugging Face API token for AI features | Yes      |

## Technologies Used

- **Backend**: FastAPI, Pydantic, Uvicorn
- **Frontend**: Streamlit
- **AI**: Hugging Face API (DeepSeek model)
- **Data Validation**: Pydantic models
- **CORS**: FastAPI middleware
- **Environment Management**: python-dotenv

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints for function parameters and return values
- Write comprehensive docstrings
- Add unit tests for new features
- Update documentation for API changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on the GitHub repository or contact the development team.

## Roadmap

- [ ] Mobile application development
- [ ] Integration with fitness wearables
- [ ] Advanced analytics and reporting
- [ ] Social features and community challenges
- [ ] Integration with nutrition databases
- [ ] Multi-language support

---

**Built with ❤️ for healthier lifestyles**
