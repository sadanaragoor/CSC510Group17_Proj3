"""
Script to list all burger images and update paths in data_burgers.py
"""

import os

# Define the directories
image_dirs = {
    "no_preferences": "static/images/no_preferences",
    "vegan": "static/images/vegan",
    "vegan_gluten": "static/images/vegan_gluten",
    "low_calorie": "static/images/low_calorie",
    "high_protein": "static/images/high_protein",
    "gluten_free": "static/images/gluten_free",
}

print("Burger Images Available:\n")
print("=" * 70)

for category, dirpath in image_dirs.items():
    print(f"\n{category.upper().replace('_', ' ')}:")
    if os.path.exists(dirpath):
        files = [
            f
            for f in os.listdir(dirpath)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        for f in sorted(files):
            print(f"  - {f}")
    else:
        print(f"  Directory not found: {dirpath}")

print("\n" + "=" * 70)
