import os
import time
import random
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from sqlalchemy import create_engine
from webdriver_manager.chrome import ChromeDriverManager
from dagster import asset, Output

# Define relevant categories
RELEVANT_CATEGORIES = ["Healthy", "Vegetarian", "Low Carb", "High Protein", "Vegan", "Snacks"]

# Asset 1: Scraping recipes and storing in MongoDB
@asset
def scrape_and_store_recipes():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Tasty_Co"]
    collection = db["Recipes"]

    service = Service(ChromeDriverManager().install())
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)

    base_url = 'https://tasty.co'

    inserted_count = 0

    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, "html.parser")
        category_links = soup.select('.nav__desktop-submenu-content .nav__submenu-category-wrapper .nav__submenu-item')

        for info in category_links:
            link = info.get('href')
            category_name = info.get_text(strip=True)
            
            # Skip categories not in RELEVANT_CATEGORIES
            if category_name not in RELEVANT_CATEGORIES:
                continue

            full_link = f"{base_url}{link}"

            print(f"Processing category: {category_name}")

            driver.get(full_link)
            while True:
                try:
                    show_more_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Show more')]"))
                    )
                    driver.execute_script("arguments[0].click();", show_more_button)
                    time.sleep(random.uniform(1, 3))
                except Exception:
                    break

            category_soup = BeautifulSoup(driver.page_source, 'html.parser')
            recipe_links = category_soup.select('.feed-item a')

            for recipe_info in recipe_links:
                recipe_link = f"{base_url}{recipe_info.get('href')}"
                try:
                    recipe_response = requests.get(recipe_link)
                    recipe_soup = BeautifulSoup(recipe_response.text, "html.parser")
                    recipe_page = recipe_soup.select_one('.recipe-page')

                    if recipe_page:
                        recipe_data = {
                            "category": category_name,
                            "name": recipe_page.select_one('.recipe-name').get_text(strip=True) if recipe_page.select_one('.recipe-name') else "N/A",
                            "total_time": recipe_page.select_one('.desktop-cooktimes .recipe-time-container div:nth-child(1) p').get_text(strip=True) if recipe_page.select_one('.desktop-cooktimes .recipe-time-container div:nth-child(1) p') else "N/A",
                            "prep_time": recipe_page.select_one('.desktop-cooktimes .recipe-time-container div:nth-child(2) p').get_text(strip=True) if recipe_page.select_one('.desktop-cooktimes .recipe-time-container div:nth-child(2) p') else "N/A",
                            "cook_time": recipe_page.select_one('.desktop-cooktimes .recipe-time-container div:nth-child(3) p').get_text(strip=True) if recipe_page.select_one('.desktop-cooktimes .recipe-time-container div:nth-child(3) p') else "N/A",
                            "ingredients": [item.get_text(strip=True) for item in recipe_page.select('.ingredients__section li')],
                            "preparation_steps": [item.get_text(strip=True) for item in recipe_page.select('.preparation li')],
                            "nutrition": [item.get_text(strip=True) for item in recipe_page.select('.nutrition-details li')]
                        }

                        if not collection.find_one({"category": category_name, "name": recipe_data["name"]}):
                            collection.insert_one(recipe_data)
                            inserted_count += 1
                            print(f"Inserted recipe: {recipe_data['name']} in category: {category_name}")
                        else:
                            print(f"Recipe '{recipe_data['name']}' already exists in category: {category_name}.")

                except Exception as e:
                    print(f"Error processing recipe {recipe_link}: {e}")

    finally:
        driver.quit()

    # Return metadata with inserted record count
    return Output(value=None, metadata={"inserted_count": inserted_count})

# Asset 2: Fetching and preprocessing data
@asset
def fetch_and_preprocess_data(scrape_and_store_recipes):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Tasty_Co"]
    collection = db["Recipes"]
    data = list(collection.find())
    df = pd.DataFrame(data)

    # Extract and preprocess columns
    df['ingredients'] = df['ingredients'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')
    df['preparation_steps'] = df['preparation_steps'].apply(lambda x: ' | '.join(x) if isinstance(x, list) else '')
    df['nutrition'] = df['nutrition'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')

    def extract_nutrition(nutrition_str):
        pattern = {
            'calories': r"Calories\s*(\d+)",
            'fat': r"Fat\s*([\d.]+)g",
            'protein': r"Protein\s*([\d.]+)g",
            'carbs': r"Carbs\s*([\d.]+)g",
            'fiber': r"Fiber\s*([\d.]+)g",
            'sugar': r"Sugar\s*([\d.]+)g"
        }
        nutrition_data = {}
        for nutrient, regex in pattern.items():
            match = re.search(regex, nutrition_str)
            nutrition_data[nutrient] = float(match.group(1)) if match else None
        return nutrition_data

    nutrition_columns = df['nutrition'].apply(extract_nutrition)
    nutrition_df = pd.json_normalize(nutrition_columns)

    # Merge and clean up
    df = pd.concat([df, nutrition_df], axis=1)
    df = df.drop(columns=['nutrition'], errors='ignore')
    
    # Convert to numeric and impute missing values
    numeric_columns = ['calories', 'fat', 'protein', 'carbs', 'fiber', 'sugar']
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
        median_value = df[column].median()
        df[column] = df[column].fillna(median_value if not pd.isna(median_value) else 0)

    # Debugging output
    print(df.head())

    return Output(value=df, metadata={"row_count": len(df)})

import sqlalchemy

@asset
def store_data_in_postgres(fetch_and_preprocess_data):
    # Drop '_id' column if it exists
    if '_id' in fetch_and_preprocess_data.columns:
        fetch_and_preprocess_data = fetch_and_preprocess_data.drop(columns=['_id'])

    # Convert columns to appropriate types before storing
    numeric_columns = ['calories', 'fat', 'protein', 'carbs', 'fiber', 'sugar']
    for column in numeric_columns:
        fetch_and_preprocess_data[column] = pd.to_numeric(fetch_and_preprocess_data[column], errors='coerce')

        # Impute missing values with median
        median_value = fetch_and_preprocess_data[column].median()
        fetch_and_preprocess_data[column] = fetch_and_preprocess_data[column].fillna(median_value if not pd.isna(median_value) else 0)

    # Debugging: Print a sample of the data being inserted
    print("Data being inserted into PostgreSQL:")
    print(fetch_and_preprocess_data.head())

    # Define SQLAlchemy engine
    engine = create_engine("postgresql+psycopg2://postgres:Performance%4099@localhost:5432/Recipe")

    # Map column types for PostgreSQL
    dtype_mapping = {
        'calories': sqlalchemy.types.Float,
        'fat': sqlalchemy.types.Float,
        'protein': sqlalchemy.types.Float,
        'carbs': sqlalchemy.types.Float,
        'fiber': sqlalchemy.types.Float,
        'sugar': sqlalchemy.types.Float,
        'category': sqlalchemy.types.Text,
        'name': sqlalchemy.types.Text,
        'total_time': sqlalchemy.types.Text,
        'prep_time': sqlalchemy.types.Text,
        'cook_time': sqlalchemy.types.Text,
        'ingredients': sqlalchemy.types.Text,
        'preparation_steps': sqlalchemy.types.Text
    }

    # Write to PostgreSQL table
    fetch_and_preprocess_data.to_sql(
        "recipes", 
        engine, 
        if_exists="replace", 
        index=False, 
        dtype=dtype_mapping
    )
    print(f"Data successfully stored in PostgreSQL. Total rows: {len(fetch_and_preprocess_data)}")
