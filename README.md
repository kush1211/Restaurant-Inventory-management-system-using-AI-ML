## 🎥 Demo Video

![Watch the demo](demo_final.mp4)


Smart Kitchen Inventory and Waste Management System

Overview

This project is a comprehensive solution for managing kitchen inventory, detecting food spoilage, forecasting consumption, and minimizing waste using advanced computer vision, OCR, and machine learning techniques. It integrates real-time stock updates, sales forecasting, waste-aware recipe generation, and cost optimization to improve profitability and sustainability in restaurant operations.

Features

1. Image-Based Food Health Detection





Objective: Detect the freshness or spoilage of fruits and vegetables.



Technology:





Roboflow model from the Proyecto Final DPI Dataset and Food Waste Dataset.



OpenCV for image preprocessing.



TensorFlow/Keras for model inference.



Metrics:





mAP@50: 82.4%



Precision: 79.8%



Recall: 79.3%

2. OCR for Ingredient Packet Analysis





Objective: Extract text (ingredient name, expiry date, weight) from ingredient packets.



Technology:





Google Cloud Vision API for text detection (~90% accuracy, preliminary estimate).



Mistral API via Groq for OCR support and potential recipe generation.



Output: Structured data for inventory updates.

3. Real-Time Stock Management





Objective: Automatically update inventory based on health detection and OCR results.



Technology:





Python (Pandas, NumPy) for data processing.



CSV files to store inventory data (ingredient name, weight, expiration date, stock levels).



Outcome: Accurate tracking of usable and spoiled items.

4. Sales Forecasting and Consumption Estimation





Objective: Predict daily dish sales and ingredient consumption to optimize stock.



Technology:





Auto ARIMA for time-series forecasting of dish sales.



Regression models for ingredient-level consumption and waste forecasting.



Pandas, NumPy, Scikit-learn for data preprocessing and modeling.



Matplotlib, Seaborn for visualizing trends and forecasts.



Outcome: Real-time dashboard for consumption and waste predictions.

5. Waste-Aware Recipe Generator





Objective: Generate recipes using ingredients predicted to go to waste.



Technology:





Groq API for recipe generation.



Custom logic to map surplus ingredients to recipes.



Outcome: Reduced food wastage through targeted dish suggestions.

6. Cost Optimization and Dish Offer System





Objective: Optimize dish costs and suggest offers to utilize surplus ingredients.



Technology:





Python (Pandas, NumPy) for cost analysis.



Groq API for personalized dish creation and substitutions.



Outcome: Improved profitability and reduced waste.

7. Image-Based Waste Classification





Objective: Analyze post-consumption waste to identify patterns.



Technology:





Roboflow’s Food Waste Dataset for detecting leftover food in images.



OpenCV for image preprocessing.



TensorFlow for object detection.



Matplotlib, Seaborn for waste heatmaps and reports.



Outcome: Insights into dish popularity, portion sizing, and over-serving for sustainability.

Tech Stack





Frontend: React.js for the user interface.



Backend: Python for processing vision data, OCR, and inventory management.



Database: CSV files for inventory and synthetic dataset storage.



AI/ML:





TensorFlow/Keras for object detection.



Auto ARIMA and regression models for forecasting.



Google Vision API for OCR.



Groq API for recipe generation and optimization.



Computer Vision: OpenCV for preprocessing and inference.



Visualization: Matplotlib, Seaborn for dashboards and reports.



Development Tools: Jupyter/Kaggle Notebooks for prototyping.

Datasets





Synthetic Dataset: Simulates inventory, ingredient prices, dish recipes, and purchase logs.



Roboflow Datasets:





Proyecto Final DPI for rotten fruit/vegetable detection.



Food Waste Dataset for waste classification.
