

<div align="center">
<!--   <img src="your-project-logo.png" alt="Project Logo" width="200"> -->
  <h1>🍽️ Smart Kitchen Management System: AI-Powered Food Optimization</h1>
  <p>Leveraging Computer Vision, OCR, and Machine Learning to Minimize Food Waste and Optimize Restaurant Operations.</p>
</div>

---

## 🎥 Demo Video
[![Watch the demo](https://img.shields.io/badge/Watch%20Demo-Click%20Here-%23FF0000?style=for-the-badge&logo=play&logoColor=white)](demo_final.mp4)


## ✨ Overview

This project implements a comprehensive smart kitchen management system designed to revolutionize how restaurants handle inventory, predict sales, and minimize food waste. By integrating cutting-edge technologies like computer vision for food health and waste detection, OCR for ingredient data extraction, and machine learning for sales forecasting and recipe optimization, we aim to create a more efficient, cost-effective, and sustainable kitchen environment.

**Key Modules:**

* **🍎 Smart Inventory Management:** Automatically tracks the health and details of ingredients, ensuring only fresh items are used and providing real-time stock updates.
* **📈 Sales Forecasting & Consumption Estimation:** Predicts daily dish sales and estimates ingredient consumption to optimize purchasing and reduce spoilage.
* **🗑️ Waste-Aware Operations:** Identifies potential food waste and suggests intelligent solutions like recipe generation and dish offers to minimize it.
* **💰 Cost Optimization Engine:** Analyzes ingredient costs and suggests substitutions or dishes based on available, low-cost ingredients.
* **📸 Image-Based Waste Classification:** Provides visual insights into post-consumption waste patterns to inform recipe adjustments and portion control.

---

## 🚀 Key Features

* **Real-time Ingredient Health Detection:** Utilizes a Roboflow-trained model to classify fruits and vegetables as fresh or spoiled based on image analysis.
* **Automated Inventory Updates:** Extracts ingredient details (name, expiry, weight) from packaging using Google Cloud Vision OCR and automatically updates stock levels.
* **Accurate Sales Forecasting:** Employs time-series models (Auto ARIMA) to predict daily dish sales based on historical data.
* **Intelligent Consumption Tracking:** Combines sales data with recipe information to estimate daily ingredient usage.
* **Proactive Waste Management:** Predicts potential ingredient waste based on expiry dates and consumption patterns.
* **AI-Powered Recipe Generation:** Leverages the Groq API (Mistral model) to generate recipes utilizing ingredients nearing their expiration.
* **Dynamic Dish Offer System:** Suggests special offers or combo deals for dishes with surplus ingredients to encourage their use.
* **Cost-Effective Menu Optimization:** Calculates dish costs and proposes ingredient substitutions to improve profitability.
* **Personalized Dish Creation:** Enables the creation of custom dishes based on available, low-cost, or soon-to-expire ingredients.
* **Visual Waste Analysis:** Employs computer vision to detect and classify leftover food in images, providing insights into waste patterns.
* **Comprehensive Dashboards:** Visualize sales trends, consumption patterns, waste forecasts, and cost analyses to facilitate informed decision-making.

---

## 🛠️ Technologies Used

**Backend & Data Processing:**

* **Python:** The primary programming language for data processing, model development, and API integration.
* **Pandas:** For data manipulation and analysis.
* **NumPy:** For numerical computations.
* **Scikit-learn:** For implementing regression models for consumption and waste forecasting.
* **TensorFlow/Keras:** For preprocessing and inference of the object detection model.
* **OpenCV:** For image preprocessing and visual monitoring tasks.

**AI/ML Models & APIs:**

* **Object Detection (TensorFlow):** To identify and verify ingredients in uploaded images.
* **OCR (Google Cloud Vision API):** To extract text data from ingredient packaging.
    * 🔗 [Google Cloud Vision API Documentation](https://console.cloud.google.com/marketplace/product/google/vision.googleapis.com)
* **Waste/Health Detection Model (Roboflow):** Trained on the Proyecto Final DPI and food\_waste datasets to identify spoiled produce and leftover food.
    * 🔗 [Proyecto Final DPI Dataset](https://universe.roboflow.com/imageprocessing-cahoi/proyecto-final-dpi)
    * 🔗 [Food Waste Dataset](https://universe.roboflow.com/food-detection-a3dtf/food__waste/dataset/2/images/?split=test&predictions=true)
* **Time Series Forecasting (Auto ARIMA):** For predicting daily dish sales.
* **Large Language Model (Mistral via Groq API):** For OCR support, recipe generation, cost optimization, and personalized dish creation.
    * 🔗 [Groq Models Documentation](https://console.groq.com/docs/models)

**Frontend:**

* **React Js:** For building the user interface and visualizing the data.

**Database:**

* **CSV Files (Synthetic):** To store and manage inventory data, sales history, ingredient details, and purchase logs.

**Visualization:**

* **Matplotlib:** For generating basic plots and charts.
* **Seaborn:** For creating more informative and visually appealing statistical graphics.

---

## 📊 Performance Metrics

**Rotten Fruit/Vegetable Detection:**

* **mAP@50:** 82.4%
* **Precision:** 79.8%
* **Recall:** 79.3%
    *(Based on Roboflow dataset tests)*

**OCR Text Detection (Google Vision API):**

* **Accuracy:** ~90%
    *(Preliminary estimate, further validation with diverse data recommended)*

---

## 📂 Dataset References

* **Synthetic Inventory, Sales, and Cost Data:** Generated to simulate real-world restaurant operations.
* **Roboflow Proyecto Final DPI Dataset:** For training the spoiled fruit and vegetable identification model.
    * 🔗 [https://universe.roboflow.com/imageprocessing-cahoi/proyecto-final-dpi](https://universe.roboflow.com/imageprocessing-cahoi/proyecto-final-dpi)
* **Roboflow Food Waste Dataset:** For training the leftover food detection model.
    * 🔗 [https://universe.roboflow.com/food-detection-a3dtf/food\_\_waste/dataset/2/images/?split=test\&predictions=true](https://universe.roboflow.com/food-detection-a3dtf/food__waste/dataset/2/images/?split=test&predictions=true)

---
