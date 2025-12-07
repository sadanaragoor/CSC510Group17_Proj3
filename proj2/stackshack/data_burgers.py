"""
Pre-defined burger configurations for personalized recommendations.

Each burger is defined with:
- name: Display name
- slug: URL-friendly identifier
- description: Flavor profile description
- ingredients: List of ingredient names (must match MenuItem.name in database)
- dietary_tags: List of preferences this burger satisfies
- image: Path relative to /static/images/
"""

PREDEFINED_BURGERS = [
    # ========================================
    # VEGAN + GLUTEN-FREE COMBINATION
    # ========================================
    {
        "name": "The Rainbow Root Burger",
        "slug": "rainbow_root_burger",
        "description": "Earthy bun, refreshing mint sauce, full vegan flavor.",
        "ingredients": ["beetroot bun", "mixed veg patty", "tomato", "lettuce", "green sauce"],
        "dietary_tags": ["vegan", "gluten_free"],
        "image": "vegan_gluten/Rainbow Root Burger.png"
    },
    {
        "name": "The Carrot Garden Crunch",
        "slug": "carrot_garden_crunch",
        "description": "Naturally sweet carrot bun + crunchy veggies.",
        "ingredients": ["carrot bun", "veg patty", "capsicum", "onion", "tomato sauce"],
        "dietary_tags": ["vegan", "gluten_free"],
        "image": "vegan_gluten/Carrot Garden Crunch.png"
    },
    {
        "name": "The Double Veggie Glow Burger",
        "slug": "double_veggie_glow_burger",
        "description": "Double vegan patties, bold mustard, fully GF.",
        "ingredients": ["carrot bun", "mixed veg patty", "veg patty", "tomato", "mustard sauce"],
        "dietary_tags": ["vegan", "gluten_free"],
        "image": "vegan_gluten/Double Veggie Glow Burger.png"
    },
    {
        "name": "The Beet & Heat Vegan Burger",
        "slug": "beet_heat_vegan_burger",
        "description": "Tangy, spicy, colorful, completely allergen-friendly.",
        "ingredients": ["beetroot bun", "veg patty", "pickles", "onion", "green sauce"],
        "dietary_tags": ["vegan", "gluten_free"],
        "image": "vegan_gluten/Beet & Heat Vegan Burger.png"
    },
    
    # ========================================
    # NO PREFERENCE (Top Picks)
    # ========================================
    {
        "name": "The Classic All-Star Burger",
        "slug": "classic_all_star_burger",
        "description": "Classic, juicy, cheesy, perfectly balanced.",
        "ingredients": ["plain bun", "beef patty", "cheddar cheese", "onion", "lettuce", "tomato", "tomato sauce"],
        "dietary_tags": ["no_preference"],
        "image": "no_preferences/Classic All-Star Burger.png"
    },
    {
        "name": "The Honey Melt Crunch Burger",
        "slug": "honey_melt_crunch_burger",
        "description": "Slightly sweet bun, creamy cheese, crispy chicken.",
        "ingredients": ["honeywheat bun", "chicken patty", "swiss cheese", "pickles", "lettuce", "mayo"],
        "dietary_tags": ["no_preference"],
        "image": "no_preferences/Honey Melt Crunch Burger.png"
    },
    {
        "name": "The Supreme Sesame Sizzler",
        "slug": "supreme_sesame_sizzler",
        "description": "Smoky, rich, tangy — great texture.",
        "ingredients": ["sesame bun", "pork patty", "parmesan cheese", "onion", "capsicum", "mustard sauce"],
        "dietary_tags": ["no_preference"],
        "image": "no_preferences/Supreme Sesame Sizzler.png"
    },
    {
        "name": "The Keto Beast Burger",
        "slug": "keto_beast_burger",
        "description": "Low-carb but indulgent & rich; great for meat lovers.",
        "ingredients": ["keto bun", "beef patty", "cheddar cheese", "tomato", "onion", "mayo"],
        "dietary_tags": ["no_preference"],
        "image": "no_preferences/Keto Beast Burger.png"
    },
    {
        "name": "The Smoky Swiss Stack",
        "slug": "smoky_swiss_stack",
        "description": "Mild, creamy, slightly smoky, universally loved.",
        "ingredients": ["wheat bun", "pork patty", "swiss cheese", "lettuce", "tomato", "tomato sauce"],
        "dietary_tags": ["no_preference"],
        "image": "no_preferences/Smoky Swiss Stack.png"
    },
    {
        "name": "The Crunchy Veg Surprise",
        "slug": "crunchy_veg_surprise",
        "description": "Fresh, crunchy, comforting veggie option.",
        "ingredients": ["plain bun", "veg patty", "swiss cheese", "tomato", "pickles", "green sauce"],
        "dietary_tags": ["no_preference"],
        "image": "no_preferences/Crunchy Veg Surprise.png"
    },
    
    # ========================================
    # LOW CALORIE
    # ========================================
    {
        "name": "The Skinny Crunch Burger",
        "slug": "skinny_crunch_burger",
        "description": "Fresh, light, very low cal, minty finish.",
        "ingredients": ["keto bun", "mixed veg patty", "tomato", "lettuce", "green sauce"],
        "dietary_tags": ["low_calorie"],
        "image": "low_calorie/Skinny Crunch Burger.png"
    },
    {
        "name": "The Lean & Clean Beet Burger",
        "slug": "lean_clean_beet_burger",
        "description": "Tangy, crunchy, stays under your calorie threshold.",
        "ingredients": ["beetroot bun", "low-calorie beef patty", "onion", "pickles", "mustard sauce"],
        "dietary_tags": ["low_calorie"],
        "image": "low_calorie/Lean & Clean Beet Burger.png"
    },
    {
        "name": "The Carrot Lite Delight",
        "slug": "carrot_lite_delight",
        "description": "Mildly sweet, veggie-packed, extremely light.",
        "ingredients": ["carrot bun", "mixed veg patty", "capsicum", "tomato", "tomato sauce"],
        "dietary_tags": ["low_calorie"],
        "image": "low_calorie/Carrot Lite Delight.png"
    },
    
    # ========================================
    # HIGH PROTEIN
    # ========================================
    {
        "name": "The PowerHouse Protein Stack",
        "slug": "powerhouse_protein_stack",
        "description": "Massive protein punch.",
        "ingredients": ["black sesame bun", "chicken patty", "swiss cheese", "onion", "tomato"],
        "dietary_tags": ["high_protein"],
        "image": "high_protein/PowerHouse Protein Stack.png"
    },
    {
        "name": "The Muscle Melt Burger",
        "slug": "muscle_melt_burger",
        "description": "High-protein + rich cheesy melt.",
        "ingredients": ["sesame bun", "beef patty", "cheddar cheese", "lettuce", "pickles"],
        "dietary_tags": ["high_protein"],
        "image": "high_protein/Muscle Melt Burger.png"
    },
    {
        "name": "The Keto Max Protein Burger",
        "slug": "keto_max_protein_burger",
        "description": "Low-carb, high-protein, premium flavor.",
        "ingredients": ["keto bun", "pork patty", "swiss cheese", "tomato", "capsicum"],
        "dietary_tags": ["high_protein"],
        "image": "high_protein/Keto Max Protein Burger.png"
    },
    {
        "name": "The Triple Protein Crunch",
        "slug": "triple_protein_crunch",
        "description": "Simple but super macro-friendly.",
        "ingredients": ["wheat bun", "chicken patty", "onion", "mustard sauce"],
        "dietary_tags": ["high_protein"],
        "image": "high_protein/Triple Protein Crunch.png"
    },
    
    # ========================================
    # VEGAN ONLY (not gluten-free)
    # ========================================
    {
        "name": "The Garden Glow Burger",
        "slug": "garden_glow_burger",
        "description": "Bright, earthy, colorful.",
        "ingredients": ["beetroot bun", "mixed veg patty", "tomato", "lettuce", "green sauce"],
        "dietary_tags": ["vegan"],
        "image": "vegan/Garden Glow Burger.png"
    },
    {
        "name": "The Carrot Crunch Vegan Delight",
        "slug": "carrot_crunch_vegan_delight",
        "description": "Crunchy, sweet, super vegan-friendly.",
        "ingredients": ["carrot bun", "veg patty", "onion", "capsicum", "tomato sauce"],
        "dietary_tags": ["vegan"],
        "image": "vegan/Carrot Crunch Vegan Delight.png"
    },
    {
        "name": "The Rustic Wheat Veggie Stack",
        "slug": "rustic_wheat_veggie_stack",
        "description": "Rustic, tangy, simple vegan stack.",
        "ingredients": ["wheat bun", "mixed veg patty", "pickles", "lettuce", "mustard sauce"],
        "dietary_tags": ["vegan"],
        "image": "vegan/Rustic Wheat Veggie Stack.png"
    },
    {
        "name": "The Double Veg Rainbow Burger",
        "slug": "double_veg_rainbow_burger",
        "description": "Double patties, fully vegan.",
        "ingredients": ["carrot bun", "mixed veg patty", "veg patty", "tomato", "onion"],
        "dietary_tags": ["vegan"],
        "image": "vegan/Double Veg Rainbow Burger.png"
    },
    
    # ========================================
    # GLUTEN-FREE ONLY (not vegan)
    # ========================================
    {
        "name": "The Keto Crunch Supreme",
        "slug": "keto_crunch_supreme",
        "description": "Classic taste without gluten.",
        "ingredients": ["keto bun", "chicken patty", "lettuce", "onion", "mustard sauce"],
        "dietary_tags": ["gluten_free"],
        "image": "gluten_free/Keto Crunch Supreme.png"
    },
    {
        "name": "The Beet GF Classic",
        "slug": "beet_gf_classic",
        "description": "Vibrant pink bun + classic beef taste.",
        "ingredients": ["beetroot bun", "beef patty", "tomato", "pickles", "tomato sauce"],
        "dietary_tags": ["gluten_free"],
        "image": "gluten_free/Beet GF Classic.png"
    },
    {
        "name": "The Carrot Garden GF Burger",
        "slug": "carrot_garden_gf_burger",
        "description": "Sweet, veg-forward, completely GF.",
        "ingredients": ["carrot bun", "veg patty", "tomato", "capsicum", "green sauce"],
        "dietary_tags": ["gluten_free"],
        "image": "gluten_free/Carrot Garden GF Burger.png"
    },
    {
        "name": "The GF Power Lift Burger",
        "slug": "gf_power_lift_burger",
        "description": "Gluten-free + high-protein combo.",
        "ingredients": ["beetroot bun", "pork patty", "swiss cheese", "onion"],
        "dietary_tags": ["gluten_free"],
        "image": "gluten_free/GF Power Lift Burger.png"
    },
]

