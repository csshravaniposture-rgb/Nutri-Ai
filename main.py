from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()
app = FastAPI(title="Complete Fitness & Diet Management API", version="2.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
HF_TOKEN = os.getenv('HF_TOKEN', 'your_token_here')
API_URL = "https://router.huggingface.co/v1/chat/completions"

# Enums
class Gender(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"

class FitnessLevel(str, Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"

class Goal(str, Enum):
    weight_loss = "Weight Loss"
    weight_gain = "Weight Gain"
    maintenance = "Maintenance"
    muscle_building = "Muscle Building"

class DietPreference(str, Enum):
    vegetarian = "Vegetarian"
    non_vegetarian = "Non-Vegetarian"
    vegan = "Vegan"
    eggetarian = "Eggetarian"
    pescatarian = "Pescatarian"
    no_preference = "No Preference"

class CuisineType(str, Enum):
    indian = "Indian"
    mexican = "Mexican"
    spanish = "Spanish"
    italian = "Italian"
    chinese = "Chinese"
    mediterranean = "Mediterranean"
    american = "American"
    japanese = "Japanese"
    korean = "Korean"
    thai = "Thai"
    middle_eastern = "Middle Eastern"

class MealType(str, Enum):
    breakfast = "Breakfast"
    lunch = "Lunch"
    dinner = "Dinner"
    snack = "Snack"
    appetizer = "Appetizer"
    main_course = "Main Course"
    dessert = "Dessert"
    soup = "Soup"
    salad = "Salad"
    beverage = "Beverage"

class MenstrualPhase(str, Enum):
    menstrual = "Menstrual Phase (Days 1-5)"
    follicular = "Follicular Phase (Days 6-13)"
    ovulation = "Ovulation Phase (Days 14-16)"
    luteal = "Luteal Phase (Days 17-28)"

class BudgetType(str, Enum):
    daily = "Daily"
    weekly = "Weekly"
    monthly = "Monthly"

# Pydantic Models
class UserProfile(BaseModel):
    age: int = Field(..., ge=10, le=100)
    gender: Gender
    weight_kg: float = Field(..., gt=0)
    height_cm: float = Field(..., gt=0)
    work_hours: str
    free_time: str
    fitness_level: FitnessLevel
    goal: Goal
    gym_access: bool
    diet_preference: DietPreference
    budget_amount: float = Field(..., gt=0)
    budget_type: BudgetType
    allergies: Optional[List[str]] = []
    health_conditions: Optional[List[str]] = []
    cuisine_preferences: Optional[List[CuisineType]] = []
    menstrual_cycle_day: Optional[int] = Field(None, ge=1, le=28)
    available_ingredients: Optional[List[str]] = []
    caffeine_sensitive: Optional[bool] = False
    sleep_hours: Optional[int] = Field(None, ge=4, le=12)

class RecipeRequest(BaseModel):
    available_ingredients: List[str]
    cuisine_type: Optional[CuisineType] = None
    meal_type: MealType
    servings: int = Field(default=2, ge=1, le=10)
    prep_time_max: Optional[int] = Field(None, ge=5, le=180)
    diet_preference: DietPreference
    allergies: Optional[List[str]] = []
    budget_per_serving: Optional[float] = None

class ChatMessage(BaseModel):
    message: str
    user_profile: Optional[UserProfile] = None
    conversation_history: Optional[List[Dict[str, str]]] = []

class CaffeineGuidance(BaseModel):
    max_caffeine_mg: int
    max_coffee_cups: float
    max_tea_cups: float
    coffee_preparation: Dict[str, str]
    tea_preparation: Dict[str, str]
    timing_recommendations: List[str]
    warnings: List[str]

class NutritionResponse(BaseModel):
    bmi: float
    bmi_category: str
    daily_calories: int
    macro_breakdown: Dict[str, float]
    hydration_liters: float
    caffeine_guidance: CaffeineGuidance

# Helper Functions
def calculate_bmi(weight_kg: float, height_cm: float) -> tuple:
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
    elif 25 <= bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return round(bmi, 2), category

def calculate_daily_calories(user: UserProfile) -> int:
    # Mifflin-St Jeor Equation
    if user.gender == Gender.male:
        bmr = 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5
    else:
        bmr = 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age - 161
    
    activity_multiplier = 1.55  # Moderate activity
    tdee = bmr * activity_multiplier
    
    if user.goal == Goal.weight_loss:
        return int(tdee - 500)
    elif user.goal in [Goal.weight_gain, Goal.muscle_building]:
        return int(tdee + 500)
    else:
        return int(tdee)

def get_menstrual_phase(cycle_day: int) -> MenstrualPhase:
    if 1 <= cycle_day <= 5:
        return MenstrualPhase.menstrual
    elif 6 <= cycle_day <= 13:
        return MenstrualPhase.follicular
    elif 14 <= cycle_day <= 16:
        return MenstrualPhase.ovulation
    else:
        return MenstrualPhase.luteal

def calculate_caffeine_limit(user: UserProfile) -> CaffeineGuidance:
    # Base caffeine limit (mg per day)
    base_limit = 400  # FDA recommendation for healthy adults
    
    # Adjust based on age
    if user.age < 18:
        base_limit = 100
    elif user.age > 65:
        base_limit = 300
    
    # Adjust based on BMI
    bmi, _ = calculate_bmi(user.weight_kg, user.height_cm)
    if bmi < 18.5 or bmi > 30:
        base_limit = int(base_limit * 0.75)
    
    # Adjust for caffeine sensitivity
    if user.caffeine_sensitive:
        base_limit = int(base_limit * 0.5)
    
    # Adjust for sleep
    if user.sleep_hours and user.sleep_hours < 6:
        base_limit = int(base_limit * 0.8)
    
    # Coffee and Tea calculations
    coffee_mg_per_cup = 95  # Average 8oz cup
    tea_mg_per_cup = 47     # Average 8oz cup
    
    max_coffee = round(base_limit / coffee_mg_per_cup, 1)
    max_tea = round(base_limit / tea_mg_per_cup, 1)
    
    # Preparation guidelines
    coffee_prep = {
        "beans": "15-18g per cup",
        "water": "240ml per cup",
        "sugar": "Max 1-2 teaspoons (if needed)",
        "milk": "Optional, prefer low-fat",
        "timing": "Best consumed 1-2 hours after waking"
    }
    
    tea_prep = {
        "leaves": "2-3g per cup (1 teaspoon)",
        "water": "240ml at 80-90°C",
        "sugar": "Max 1 teaspoon (preferably honey)",
        "steeping_time": "3-5 minutes",
        "timing": "Can be consumed throughout the day"
    }
    
    timing = [
        "Best time: 9:30 AM - 11:30 AM",
        "Avoid after 2 PM if sensitive to sleep disruption",
        "Never on empty stomach",
        "Wait 1 hour after meals for better iron absorption"
    ]
    
    warnings = []
    if user.age < 18:
        warnings.append("Limited caffeine for adolescents - focus on hydration")
    if bmi > 30:
        warnings.append("Monitor caffeine intake - may affect metabolism")
    if user.caffeine_sensitive:
        warnings.append("You're sensitive - consider decaf alternatives")
    
    return CaffeineGuidance(
        max_caffeine_mg=base_limit,
        max_coffee_cups=max_coffee,
        max_tea_cups=max_tea,
        coffee_preparation=coffee_prep,
        tea_preparation=tea_prep,
        timing_recommendations=timing,
        warnings=warnings
    )

def query_ai(messages: List[Dict], max_tokens: int = 2000) -> str:
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "messages": messages,
            "model": "deepseek-ai/DeepSeek-V3.2:novita",
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        elif "error" in result:
            return f"API Error: {result['error']}"
        else:
            return "Unexpected API response"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Query Error: {str(e)}")

# API Endpoints

@app.get("/")
def root():
    return {
        "message": "Complete Fitness & Diet Management API",
        "version": "2.0",
        "endpoints": {
            "nutrition_analysis": "/nutrition-analysis",
            "fitness_plan": "/fitness-plan",
            "meal_plan": "/meal-plan",
            "recipe_generator": "/recipe-generator",
            "period_nutrition": "/period-nutrition",
            "caffeine_guidance": "/caffeine-guidance",
            "chatbot": "/chatbot",
            "progress_tracking": "/progress-tracking"
        }
    }

@app.post("/nutrition-analysis", response_model=NutritionResponse)
def analyze_nutrition(user: UserProfile):
    """Complete nutrition analysis with caffeine guidance"""
    bmi, bmi_category = calculate_bmi(user.weight_kg, user.height_cm)
    daily_calories = calculate_daily_calories(user)
    
    # Macro breakdown
    if user.goal == Goal.muscle_building:
        protein_ratio, carb_ratio, fat_ratio = 0.35, 0.40, 0.25
    elif user.goal == Goal.weight_loss:
        protein_ratio, carb_ratio, fat_ratio = 0.40, 0.30, 0.30
    else:
        protein_ratio, carb_ratio, fat_ratio = 0.30, 0.45, 0.25
    
    protein_g = (daily_calories * protein_ratio) / 4
    carbs_g = (daily_calories * carb_ratio) / 4
    fats_g = (daily_calories * fat_ratio) / 9
    
    # Hydration
    hydration = round(user.weight_kg * 0.033, 1)
    
    # Caffeine guidance
    caffeine = calculate_caffeine_limit(user)
    
    return NutritionResponse(
        bmi=bmi,
        bmi_category=bmi_category,
        daily_calories=daily_calories,
        macro_breakdown={
            "protein_g": round(protein_g, 1),
            "carbs_g": round(carbs_g, 1),
            "fats_g": round(fats_g, 1)
        },
        hydration_liters=hydration,
        caffeine_guidance=caffeine
    )

@app.post("/fitness-plan")
def generate_fitness_plan(user: UserProfile):
    """Generate personalized fitness plan"""
    bmi, bmi_category = calculate_bmi(user.weight_kg, user.height_cm)
    
    prompt = f"""Create a comprehensive fitness plan for:

PROFILE:
- Age: {user.age}, Gender: {user.gender.value}
- Weight: {user.weight_kg}kg, Height: {user.height_cm}cm
- BMI: {bmi} ({bmi_category})
- Fitness Level: {user.fitness_level.value}
- Goal: {user.goal.value}
- Gym Access: {'Yes' if user.gym_access else 'No'}
- Work Hours: {user.work_hours}
- Free Time: {user.free_time}
- Health Conditions: {', '.join(user.health_conditions) if user.health_conditions else 'None'}

Create detailed plan with:
1. Weekly workout schedule (specific days/times)
2. Exercise list (sets, reps, rest periods)
3. Cardio recommendations
4. Warm-up/cool-down routines
5. Progressive overload strategy
6. Recovery protocols
7. Injury prevention tips
8. Motivation strategies

Make it {'gym' if user.gym_access else 'home'}-based and practical."""

    messages = [{"role": "user", "content": prompt}]
    response = query_ai(messages, max_tokens=3000)
    
    return {"fitness_plan": response, "user_bmi": bmi, "bmi_category": bmi_category}

@app.post("/meal-plan")
def generate_meal_plan(user: UserProfile):
    """Generate comprehensive meal plan with budget consideration"""
    daily_calories = calculate_daily_calories(user)
    bmi, bmi_category = calculate_bmi(user.weight_kg, user.height_cm)
    
    # Convert budget to daily
    if user.budget_type == BudgetType.weekly:
        daily_budget = user.budget_amount / 7
    elif user.budget_type == BudgetType.monthly:
        daily_budget = user.budget_amount / 30
    else:
        daily_budget = user.budget_amount
    
    # Menstrual phase info
    menstrual_info = ""
    if user.gender == Gender.female and user.menstrual_cycle_day:
        phase = get_menstrual_phase(user.menstrual_cycle_day)
        menstrual_info = f"\n- Menstrual Cycle: Day {user.menstrual_cycle_day} ({phase.value})"
    
    cuisine_list = ", ".join([c.value for c in user.cuisine_preferences]) if user.cuisine_preferences else "Any"
    ingredients_list = ", ".join(user.available_ingredients) if user.available_ingredients else "Standard pantry items"
    
    prompt = f"""Create a detailed meal plan for:

PROFILE:
- Age: {user.age}, Gender: {user.gender.value}
- BMI: {bmi} ({bmi_category})
- Daily Calorie Target: {daily_calories} calories
- Goal: {user.goal.value}{menstrual_info}

DIETARY:
- Preference: {user.diet_preference.value}
- Cuisines: {cuisine_list}
- Daily Budget: ${daily_budget:.2f}
- Available Ingredients: {ingredients_list}
- Allergies: {', '.join(user.allergies) if user.allergies else 'None'}
- Health Conditions: {', '.join(user.health_conditions) if user.health_conditions else 'None'}

Create comprehensive plan with:
1. Daily meal schedule (Breakfast, Lunch, Dinner, 2 Snacks)
2. Each meal with:
   - Specific dishes
   - Calorie count
   - Macro breakdown
   - Cost estimate
3. Weekly variety (3-4 options per meal)
4. Budget-friendly shopping list
5. Meal prep tips
6. Hydration schedule
7. Supplement recommendations
8. Special considerations for cuisine preferences

For EACH MEAL TYPE provide:
- Appetizer option
- Main course option
- Soup option
- Salad option
- Dessert option (healthy)

Ensure total daily cost stays within ${daily_budget:.2f}."""

    messages = [{"role": "user", "content": prompt}]
    response = query_ai(messages, max_tokens=4000)
    
    return {
        "meal_plan": response,
        "daily_calories": daily_calories,
        "daily_budget": round(daily_budget, 2),
        "cuisine_preferences": cuisine_list
    }

@app.post("/recipe-generator")
def generate_recipe(recipe_req: RecipeRequest):
    """Generate recipe from available ingredients"""
    
    ingredients = ", ".join(recipe_req.available_ingredients)
    allergies = ", ".join(recipe_req.allergies) if recipe_req.allergies else "None"
    
    prompt = f"""Create a detailed recipe for {recipe_req.meal_type.value}:

REQUIREMENTS:
- Available Ingredients: {ingredients}
- Cuisine: {recipe_req.cuisine_type.value if recipe_req.cuisine_type else 'Any'}
- Servings: {recipe_req.servings}
- Diet Type: {recipe_req.diet_preference.value}
- Max Prep Time: {recipe_req.prep_time_max if recipe_req.prep_time_max else 'Flexible'} minutes
- Budget per Serving: ${recipe_req.budget_per_serving if recipe_req.budget_per_serving else 'Flexible'}
- Allergies to Avoid: {allergies}

Provide:
1. Recipe name
2. Complete ingredient list with quantities
3. Step-by-step instructions
4. Prep time and cook time
5. Nutrition information (calories, protein, carbs, fats)
6. Cost breakdown
7. Serving suggestions
8. Storage tips
9. Variations or substitutions

Make it practical and use primarily the available ingredients."""

    messages = [{"role": "user", "content": prompt}]
    response = query_ai(messages, max_tokens=2500)
    
    return {"recipe": response, "meal_type": recipe_req.meal_type.value}

@app.post("/period-nutrition")
def period_nutrition_guide(user: UserProfile):
    """Generate menstrual cycle-specific nutrition guidance"""
    if user.gender != Gender.female:
        raise HTTPException(status_code=400, detail="This endpoint is for female users")
    
    if not user.menstrual_cycle_day:
        raise HTTPException(status_code=400, detail="Menstrual cycle day is required")
    
    phase = get_menstrual_phase(user.menstrual_cycle_day)
    daily_calories = calculate_daily_calories(user)
    
    prompt = f"""Create period-specific nutrition guidance:

PROFILE:
- Age: {user.age}
- Current Cycle Day: {user.menstrual_cycle_day}
- Current Phase: {phase.value}
- Daily Calories: {daily_calories}
- Diet Preference: {user.diet_preference.value}
- Allergies: {', '.join(user.allergies) if user.allergies else 'None'}

Provide detailed guidance for {phase.value}:

1. **Nutritional Needs**:
   - Key vitamins and minerals for this phase
   - Iron-rich foods
   - Anti-inflammatory foods
   - Foods to avoid

2. **Symptom Management**:
   - Foods for cramp relief
   - Bloating reduction
   - Mood stabilization
   - Energy maintenance

3. **Meal Suggestions**:
   - Breakfast options
   - Lunch options
   - Dinner options
   - Healthy snacks
   - Herbal teas and drinks

4. **Supplement Recommendations**:
   - Phase-specific supplements
   - Timing and dosage

5. **Hydration Strategy**:
   - Water intake
   - Electrolyte balance
   - Beverages to avoid

6. **Exercise & Nutrition Synergy**:
   - Pre-workout nutrition
   - Post-workout recovery

Make recommendations specific to {phase.value} and {user.diet_preference.value} diet."""

    messages = [{"role": "user", "content": prompt}]
    response = query_ai(messages, max_tokens=3000)
    
    return {
        "period_nutrition_guide": response,
        "current_phase": phase.value,
        "cycle_day": user.menstrual_cycle_day
    }

@app.post("/caffeine-guidance")
def get_caffeine_guidance(user: UserProfile):
    """Get detailed caffeine consumption guidance"""
    guidance = calculate_caffeine_limit(user)
    
    # Get AI recommendations
    prompt = f"""Provide personalized caffeine guidance for:

PROFILE:
- Age: {user.age}
- BMI: {calculate_bmi(user.weight_kg, user.height_cm)[0]}
- Caffeine Sensitive: {'Yes' if user.caffeine_sensitive else 'No'}
- Sleep Hours: {user.sleep_hours if user.sleep_hours else 'Not specified'}
- Goal: {user.goal.value}

CURRENT LIMITS:
- Max Caffeine: {guidance.max_caffeine_mg}mg/day
- Max Coffee: {guidance.max_coffee_cups} cups/day
- Max Tea: {guidance.max_tea_cups} cups/day

Provide:
1. Why these limits are appropriate
2. Best types of coffee/tea for them
3. Timing strategy throughout the day
4. Alternatives if they want to reduce caffeine
5. How to brew perfect coffee/tea for health
6. Signs of too much caffeine
7. How caffeine affects their specific goal

Be specific about brewing methods, sugar/milk additions, and timing."""

    messages = [{"role": "user", "content": prompt}]
    ai_recommendations = query_ai(messages, max_tokens=2000)
    
    return {
        "caffeine_limits": guidance.dict(),
        "detailed_recommendations": ai_recommendations
    }

@app.post("/chatbot")
def chatbot_conversation(chat: ChatMessage):
    """Interactive chatbot for fitness and nutrition queries"""
    
    # Build context from user profile if provided
    context = ""
    if chat.user_profile:
        bmi, bmi_cat = calculate_bmi(chat.user_profile.weight_kg, chat.user_profile.height_cm)
        context = f"""User Profile Context:
- Age: {chat.user_profile.age}, Gender: {chat.user_profile.gender.value}
- BMI: {bmi} ({bmi_cat})
- Goal: {chat.user_profile.goal.value}
- Fitness Level: {chat.user_profile.fitness_level.value}
- Diet: {chat.user_profile.diet_preference.value}
"""
    
    system_message = {
        "role": "system",
        "content": f"""You are an expert fitness and nutrition AI assistant. Provide personalized, 
scientifically-backed advice on:
- Workout routines and exercise techniques
- Meal planning and nutrition
- Weight management
- Supplement guidance
- Injury prevention and recovery
- Period-related nutrition (for female users)
- Caffeine and beverage recommendations
- Recipe suggestions
- Progress tracking

{context}

Be encouraging, practical, and specific. Always consider the user's profile when giving advice."""
    }
    
    # Build conversation history
    messages = [system_message]
    if chat.conversation_history:
        messages.extend(chat.conversation_history)
    messages.append({"role": "user", "content": chat.message})
    
    response = query_ai(messages, max_tokens=2000)
    
    return {
        "response": response,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/progress-tracking")
def generate_progress_tracking(user: UserProfile):
    """Generate progress tracking and milestone system"""
    bmi, bmi_category = calculate_bmi(user.weight_kg, user.height_cm)
    
    prompt = f"""Create a comprehensive progress tracking system for:

PROFILE:
- Age: {user.age}, Gender: {user.gender.value}
- Current BMI: {bmi} ({bmi_category})
- Goal: {user.goal.value}
- Fitness Level: {user.fitness_level.value}

Create detailed tracking plan:

1. **Key Metrics to Track**:
   - Body measurements (weight, body fat %, measurements)
   - Performance metrics (strength, endurance, flexibility)
   - Photos and visual progress
   - Energy levels and mood
   - Sleep quality

2. **Tracking Schedule**:
   - Daily tracking items
   - Weekly tracking items
   - Monthly tracking items
   - When to take progress photos

3. **Realistic Timeline**:
   - Week-by-week expectations
   - Monthly milestones
   - 3-month goals
   - 6-month goals
   - 1-year transformation potential

4. **Warning Signs**:
   - Overtraining indicators
   - Undereating signs
   - Injury risk factors
   - When to take rest days
   - When to see a professional

5. **Plan Adjustment Triggers**:
   - Plateaus - when and how to adjust
   - Rapid progress - how to maintain safely
   - Setbacks - how to recover

6. **Motivation System**:
   - Reward milestones
   - How to stay consistent
   - Dealing with bad days
   - Building sustainable habits

7. **Tools and Apps**:
   - Recommended tracking apps
   - What to log and how

Make it specific to their {user.goal.value} goal and {user.fitness_level.value} level."""

    messages = [{"role": "user", "content": prompt}]
    response = query_ai(messages, max_tokens=3000)
    
    return {
        "progress_tracking_system": response,
        "current_bmi": bmi,
        "goal": user.goal.value
    }

@app.get("/health-check")
def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)