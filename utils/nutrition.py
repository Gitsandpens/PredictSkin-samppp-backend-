"""General nutrition guidance. Not medical advice; never recommends crash dieting."""

ACTIVITY_HYDRATION = {
    "Sedentary": "About 2 to 2.5 litres of fluids spread through the day.",
    "Lightly active": "About 2.5 litres of fluids a day, a little more on warm days.",
    "Moderately active": "About 2.5 to 3 litres a day; drink extra around exercise.",
    "Very active": "About 3 litres or more a day; replace fluids during and after training.",
}

# (food, allergens, diet) - diet: veg (everyone), egg (egg-eaters and non-veg), nonveg (non-veg only)
M = {
 "lose": {
  "breakfast": [("Oats porridge with fruit", {"gluten"}, "veg"), ("Vegetable poha", set(), "veg"),
                ("Moong dal chilla with mint chutney", set(), "veg"), ("Boiled eggs with sprouts", {"eggs"}, "egg"),
                ("Vegetable upma", {"gluten"}, "veg")],
  "lunch": [("Roti, dal, vegetables and salad", {"gluten"}, "veg"), ("Rice, dal, vegetables and salad", set(), "veg"),
            ("Grilled chicken with vegetables and salad", set(), "nonveg"), ("Paneer bhurji with salad and one roti", {"milk", "gluten"}, "veg"),
            ("Curd with cucumber raita", {"milk"}, "veg")],
  "snack": [("Seasonal fruit", set(), "veg"), ("Roasted chana", set(), "veg"), ("Sprouts chaat", set(), "veg"),
            ("A small handful of nuts", {"tree nuts", "peanuts"}, "veg"), ("Buttermilk", {"milk"}, "veg")],
  "dinner": [("Dal with vegetables and a moderate roti or rice portion", {"gluten"}, "veg"), ("Vegetable khichdi", set(), "veg"),
             ("Grilled paneer with sauteed vegetables", {"milk"}, "veg"), ("Grilled chicken with vegetables", set(), "nonveg"),
             ("Grilled fish with vegetables", {"seafood"}, "nonveg")],
 },
 "maintain": {
  "breakfast": [("Vegetable paratha with curd", {"gluten", "milk"}, "veg"), ("Idli with sambar", set(), "veg"),
                ("Besan chilla with vegetables", set(), "veg"), ("Egg bhurji with whole-wheat toast", {"eggs", "gluten"}, "egg"),
                ("Oats with fruit and seeds", {"gluten"}, "veg")],
  "lunch": [("Roti, dal, a vegetable dish and salad", {"gluten"}, "veg"), ("Rice, rajma or chole and salad", set(), "veg"),
            ("Chicken curry with rice and vegetables", set(), "nonveg"), ("Paneer sabzi with roti", {"milk", "gluten"}, "veg"),
            ("Fish curry with rice", {"seafood"}, "nonveg")],
  "snack": [("Fruit", set(), "veg"), ("Roasted makhana", set(), "veg"), ("Peanut chikki or a handful of nuts", {"peanuts", "tree nuts"}, "veg"),
            ("Lassi or milk", {"milk"}, "veg"), ("Corn chaat", set(), "veg")],
  "dinner": [("Dal, roti and mixed vegetables", {"gluten"}, "veg"), ("Vegetable pulao with raita", {"milk"}, "veg"),
             ("Egg curry with rice", {"eggs"}, "egg"), ("Grilled chicken with roti and salad", {"gluten"}, "nonveg"),
             ("Moong dal khichdi with vegetables", set(), "veg")],
 },
 "gain": {
  "breakfast": [("Banana milkshake with nuts", {"milk", "tree nuts"}, "veg"), ("Paneer paratha with curd", {"milk", "gluten"}, "veg"),
                ("Peanut butter sandwich on whole-grain bread", {"peanuts", "gluten"}, "veg"), ("Omelette with toast and fruit", {"eggs", "gluten"}, "egg"),
                ("Poha with peanuts and a banana", {"peanuts"}, "veg"), ("Vegetable upma with a banana", {"gluten"}, "veg")],
  "lunch": [("Rice, dal, ghee, vegetables and curd", {"milk"}, "veg"), ("Roti, paneer curry and potatoes", {"milk", "gluten"}, "veg"),
            ("Chicken curry with rice and a potato dish", set(), "nonveg"), ("Rajma rice with salad", set(), "veg"),
            ("Egg biryani with raita", {"eggs", "milk"}, "egg")],
  "snack": [("Dates with nuts", {"tree nuts"}, "veg"), ("Banana with peanut butter", {"peanuts"}, "veg"), ("Lassi", {"milk"}, "veg"),
            ("Roasted chana with jaggery", set(), "veg"), ("Boiled potato chaat", set(), "veg")],
  "dinner": [("Whole-grain roti, dal and paneer", {"gluten", "milk"}, "veg"), ("Rice with lentils and vegetables", set(), "veg"),
             ("Egg curry with rice", {"eggs"}, "egg"), ("Chicken with potatoes and roti", {"gluten"}, "nonveg"),
             ("Fish with rice and vegetables", {"seafood"}, "nonveg"), ("Khichdi with ghee and a glass of milk", {"milk"}, "veg")],
 },
}
PREFER = {
 "lose": ["Vegetables and salads", "Dal, sprouts and other pulses", "Whole grains in moderate portions", "Fruit", "Lean protein"],
 "maintain": ["Balanced plates with vegetables, protein and whole grains", "Fruit", "Pulses and lentils", "Moderate portions"],
 "gain": ["Whole grains and rice", "Lentils, paneer, eggs or chicken", "Bananas, dates and potatoes", "Nuts and seeds", "Regular meals plus snacks"],
}
LIMIT = ["Deep-fried snacks", "Sugary drinks and sweets in large amounts", "Highly processed packaged foods", "Very large late-night meals"]
SKIN = [  # (food, allergens, diet, nutrient)
 ("Guava, amla, orange, lemon", set(), "veg", "Vitamin C"), ("Almonds", {"tree nuts"}, "veg", "Vitamin E"),
 ("Sunflower and pumpkin seeds", set(), "veg", "Vitamin E"), ("Flax and chia seeds", set(), "veg", "Omega-3"),
 ("Fish, where appropriate", {"seafood"}, "nonveg", "Omega-3"), ("Lentils", set(), "veg", "Protein"),
 ("Eggs", {"eggs"}, "egg", "Protein"), ("Paneer", {"milk"}, "veg", "Protein"), ("Chicken", set(), "nonveg", "Protein"),
 ("Water and water-rich fruits such as watermelon and cucumber", set(), "veg", "Hydration"),
]
DIETS = {"veg": {"veg"}, "egg": {"veg", "egg"}, "nonveg": {"veg", "egg", "nonveg"}}


def bmi_info(weight_kg, height_cm, age=None):
    bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
    cat = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obesity range"
    note = "Adult BMI categories may not apply accurately to children and adolescents." if age is not None and age < 18 else None
    return {"bmi": bmi, "category": cat, "note": note}


def build_plan(p):
    goal = {"LOSE": "lose", "MAINTAIN": "maintain", "GAIN": "gain"}[p["goal"]]
    allergies = {a.lower() for a in p.get("allergies", []) if a.lower() != "none"}
    diets = DIETS[p.get("diet", "veg")]
    ok = lambda alg, d: not (alg & allergies) and d in diets
    sections = {}
    for meal in ("breakfast", "lunch", "snack", "dinner"):
        items = [f for f, alg, d in M[goal][meal] if ok(alg, d)][:4]
        sections[meal] = items or ["Choose simple home-cooked foods that avoid your listed allergies."]
    notes = ["This is general guidance, not a prescription. A registered dietitian can personalise it."]
    if goal == "lose":
        notes.append("Aim for gradual change. Crash dieting and skipping meals are not recommended.")
    if goal == "gain":
        notes.append("Aim for gradual, healthy weight gain with regular meals and snacks.")
    if p["age"] < 18:
        notes.append("For anyone under 18, speak to a doctor or dietitian before changing weight.")
    if allergies:
        notes.append("Foods linked to your listed allergies were excluded. Always read ingredient labels.")
    return {
        "goal": p["goal"],
        "sections": sections,
        "hydration": ACTIVITY_HYDRATION.get(p.get("activity"), ACTIVITY_HYDRATION["Lightly active"]),
        "prefer": PREFER[goal],
        "limit": LIMIT,
        "skin": [{"food": f, "nutrient": n} for f, alg, d, n in SKIN if ok(alg, d)],
        "skin_statement": "These foods can support overall nutritional and skin health.",
        "notes": notes,
    }
