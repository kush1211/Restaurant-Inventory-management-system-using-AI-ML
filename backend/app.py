from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw
import os
from collections import defaultdict
import uuid
from google.cloud import vision
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from prophet import Prophet
import os
import io
from PIL import Image, ImageDraw
import base64
from uuid import uuid4
import pandas as pd
from datetime import datetime
import csv

app = Flask(__name__)
CORS(app)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_API_BASE"] = ""

llm = ChatOpenAI(
    model="mistral-saba-24b",  # or llama3-8b-8192
    temperature=0.7,
    max_tokens=512
)

spanish_to_english = {
    "banano_bueno": "good_banana",
    "banano_malo": "bad_banana",
    "fresa_buena": "good_strawberry",
    "fresa_mala": "bad_strawberry",
    "mango_bueno": "good_mango",
    "mango_malo": "bad_mango",
    "manzana_buena": "good_apple",
    "manzana_mala": "bad_apple",
    "naranja_buena": "good_orange",
    "naranja_mala": "bad_orange",
    "papa_buena": "good_potato",
    "papa_mala": "bad_potato",
    "pepino_bueno": "good_cucumber",
    "pepino_malo": "bad_cucumber",
    "pimiento_bueno": "good_pepper",
    "pimiento_malo": "bad_pepper",
    "tomate_bueno": "good_tomato",
    "tomate_malo": "bad_tomato",
    "uva_buena": "good_grape",
    "uva_mala": "bad_grape",
    "zanahoria_buena": "good_carrot",
    "zanahoria_malo": "bad_carrot"
}


# Initialize Google Vision client
client = vision.ImageAnnotatorClient()

VEGETABLE_UPLOAD_FOLDER = "static/uploads/vegetables"
PACKET_UPLOAD_FOLDER = "static/uploads/packets"

# Create the directories if they don't exist
os.makedirs(VEGETABLE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PACKET_UPLOAD_FOLDER, exist_ok=True)

CLIENT = InferenceHTTPClient(
    api_url="http://localhost:9001",
    api_key="HIHYIMHr2i6igB3MRQv8"
)

from flask import send_from_directory
CSV_FOLDER = os.path.join(os.getcwd(), 'data')



@app.route('/data/<filename>')
def serve_csv(filename):
    return send_from_directory(CSV_FOLDER, filename)



@app.route('/api/forecast-data', methods=['POST'])
def forecast_data():
    try:
        stock_df = pd.read_csv("data/stock_table.csv", parse_dates=["Date"])
        purchase_df = pd.read_csv("data/purchase_table.csv", parse_dates=["Purchase_Date", "Expiry_Date"])
        days = request.json.get('data')
        days = int(days[0]) if days else 0
        file_path = "data/mcd_sales_2_years.csv"
        df = pd.read_csv(file_path)

        df.columns = df.columns.str.strip()
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['Day_Type_Encoded'] = df['Day_Type'].map({'Weekday': 0, 'Weekend': 1, 'Holiday': 2})

        dish_columns = [
            'McAloo_Tikki_Sales', 'McVeggie_Sales', 'Filet_O_Fish_Sales', 'Big_Mac_Sales',
            'McChicken_Sales', 'Fries_Sales', 'Coke_Sales', 'McFlurry_Sales',
            'Happy_Meal_Sales', 'Veg_Maharaja_Mac_Sales'
        ]

        def forecast_dishes(df, n):
            forecast_dict = {}
            for dish in dish_columns:
                dish_df = df[['Date', dish, 'Day_Type_Encoded']].rename(columns={'Date': 'ds', dish: 'y'})
                model = Prophet(daily_seasonality=True)
                model.add_regressor('Day_Type_Encoded')
                model.fit(dish_df)

                future_dates = pd.date_range(start=dish_df['ds'].max() + pd.Timedelta(days=1), periods=n)
                future = pd.DataFrame({'ds': future_dates})
                future['Day_Type_Encoded'] = future['ds'].apply(lambda d: 0 if d.weekday() < 5 else 1)

                forecast = model.predict(future)
                forecast_dict[dish.replace('_Sales', "")] = forecast['yhat'].round().astype(int).tolist()
            return forecast_dict

        result = forecast_dishes(df, days)

        print(f"\nTotal Forecasted Dish Quantities for {days} Days:\n")
        for dish, values in result.items():
            result[dish] = sum(values)

        ingredients_df = pd.read_csv("data/ingredient_usage.csv")
        ingredient_totals = {}

        for _, row in ingredients_df.iterrows():
            dish = row['Dish']
            ingredient = row['Ingredient']
            qty_per_dish = row['Quantity_per_Dish']

            if dish in result:
                forecasted_sales = result[dish]
                total_qty = forecasted_sales * qty_per_dish

                if ingredient in ingredient_totals:
                    ingredient_totals[ingredient] += total_qty
                else:
                    ingredient_totals[ingredient] = total_qty

        forecast_stock_df = pd.DataFrame([
            {"Ingredient": k, "Total_Quantity_Required": v}
            for k, v in ingredient_totals.items()
        ])

        print(forecast_stock_df)
        forecast_json = forecast_stock_df.to_dict(orient='records')

        current_stock = stock_df.iloc[-1]
        current_date = current_stock["Date"]
        results = {}

        for ingredient in current_stock.index:
            if ingredient == "Date":
                continue

            stock_quantity = current_stock[ingredient]
            if pd.isnull(stock_quantity) or stock_quantity == 0:
                continue

            ingredient_purchases = purchase_df[purchase_df["Ingredient"] == ingredient].copy()
            if ingredient_purchases.empty:
                continue

            ingredient_purchases.sort_values("Expiry_Date", inplace=True)
            allocation = []
            remaining_stock = stock_quantity

            for _, row in ingredient_purchases.iterrows():
                if remaining_stock <= 0:
                    break

                batch_qty = row["Quantity_Purchased"]
                expiry_date = row["Expiry_Date"]
                allocated_qty = min(batch_qty, remaining_stock)
                shelf_life_days = (expiry_date - current_date).days

                allocation.append({
                    "Ingredient": ingredient,
                    "Allocated_Quantity": allocated_qty,
                    "Expiry_Date": expiry_date.date(),
                    "Shelf_Life_Days": shelf_life_days
                })

                remaining_stock -= allocated_qty

            results[ingredient] = allocation

        for ingredient, allocations in results.items():
            print(f"Ingredient: {ingredient}")
            for alloc in allocations:
                print(alloc)
            print("")

        allocation_records = []
        for allocations in results.values():
            allocation_records.extend(allocations)

        allocation_df = pd.DataFrame(allocation_records)
        allocation_json = allocation_df.to_dict(orient="records")

        return jsonify({
            "forecasted_data": forecast_json,
            "allocation_data": allocation_json,
            "message": "Forecast data processed successfully!"
        }), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"message": "Failed to process forecast data."}), 500


@app.route('/api/save-data', methods=['POST'])
def save_data():
    try:
        # Get the input data from the request
        data = request.json.get('data')
        
        # Print the raw input data (which will be an array)
        print(f"Raw data received: {data}")
        
        sales = data[:2] + [int(x.strip()) for x in data[2:]]
        sales_file = "data\mcd_sales_2_years.csv"

        with open(sales_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(sales)

        # 2. Read latest sales data
        df_sales = pd.read_csv(sales_file)

        # 3. Extract dish sales as dict (excluding Date, Weekend, and Total)
        dish_sales = df_sales.iloc[-1, 2:-1].to_dict()
        dict = {k.replace("_Sales", ""): v for k, v in dish_sales.items()}
        print(dict)
        # 4. Read ingredient usage mapping
        ingredients_df = pd.read_csv("data/ingredient_usage.csv")
        consume_df = pd.read_csv("data/daily_ingredient_consumption.csv")

        # 5. Calculate total ingredient quantities needed
        ingredient_totals = {}

        for _, row in ingredients_df.iterrows():
            dish = row['Dish']
            ingredient = row['Ingredient']
            qty_per_dish = row['Quantity_per_Dish']

            if dish in dict:
                forecasted = dict[dish]
                total_qty = forecasted * qty_per_dish

                if ingredient in ingredient_totals:
                    ingredient_totals[ingredient] += total_qty
                else:
                    ingredient_totals[ingredient] = total_qty

        forecast_stock_df = pd.DataFrame([
            {"Ingredient": k, "Total_Quantity_Required": v}
            for k, v in ingredient_totals.items()
        ])

        stock_table = pd.read_csv("data/stock_table.csv")

        required_dict = forecast_stock_df.set_index('Ingredient')['Total_Quantity_Required'].to_dict()

        latest_stock_row = stock_table.iloc[-1].copy()
        latest_consume_row = consume_df.iloc[-1].copy()

        updated_stock_row = latest_stock_row.copy()
        updated_consume_row = latest_consume_row.copy()

        for ingredient, used_qty in required_dict.items():
            if ingredient in stock_table.columns:  # Only subtract if column exists
                updated_stock_row[ingredient] = updated_stock_row[ingredient] - used_qty
                updated_consume_row[ingredient] =  used_qty

        print(updated_consume_row)
        print(updated_stock_row)

        updated_stock_row['Date'] = (pd.to_datetime(latest_stock_row['Date']) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        updated_consume_row['Date'] = (pd.to_datetime(latest_consume_row['Date']) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')

        print(updated_stock_row)
        df_stock = pd.concat([stock_table, pd.DataFrame([updated_stock_row])], ignore_index=True)
        df_consume = pd.concat([consume_df, pd.DataFrame([updated_consume_row])], ignore_index=True)

        print(df_stock.tail())
        print(df_consume.tail())

        df_stock.to_csv("data/stock_table.csv", index=False)
        df_consume.to_csv("data/daily_ingredient_consumption.csv", index=False)

        # Get last rows transposed as dictionaries
        last_stock_row = df_stock.tail(1).transpose().to_dict()[df_stock.tail(1).index[-1]]
        last_consume_row = df_consume.tail(1).transpose().to_dict()[df_consume.tail(1).index[-1]]

        return jsonify({
            "message": "Data saved successfully!",
            "last_stock_row": last_stock_row,
            "last_consume_row": last_consume_row
        }), 200


    #     df_stock.to_csv("data/stock_table.csv",index=False)
    #     df_consume.to_csv("data/daily_ingredient_consumption.csv",index=False)


    #     return jsonify({"message": "Data saved successfully!"}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"message": "Failed to save data."}), 500
    



















@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    image = request.files["image"]
    image_id = str(uuid.uuid4()) + ".jpg"
    image_path = os.path.join(VEGETABLE_UPLOAD_FOLDER, image_id)
    image.save(image_path)

    result = CLIENT.infer(image_path, model_id="proyecto-final-dpi/1")

    # Draw boxes
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

   
    detection_counts = defaultdict(int)

    for pred in result["predictions"]:
        x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
        left = x - w / 2
        top = y - h / 2
        right = x + w / 2
        bottom = y + h / 2

        translated_label = spanish_to_english.get(pred["class"], pred["class"])
        detection_counts[translated_label] += 1

        draw.rectangle([left, top, right, bottom], outline="red", width=3)
        draw.text((left, top - 10), f"{translated_label} ({pred['confidence']:.2f})", fill="red")

    output_path = os.path.join(VEGETABLE_UPLOAD_FOLDER, f"result_{image_id}")
    img.save(output_path)

# Create text summary
    summary_text = ", ".join([f"{count} {label}" for label, count in detection_counts.items()])
    summary_text += " are Detected."
    return jsonify({
        "result_url": f"http://localhost:5000/{output_path}",
        "summary": summary_text
    })


@app.route("/static/uploads/<filename>")
def serve_file(filename):
    return send_file(os.path.join(VEGETABLE_UPLOAD_FOLDER, filename), mimetype="image/jpeg")


@app.route('/packet-upload', methods=['POST'])
def packet_upload():
    if 'images' not in request.files:
        return jsonify({'error': 'No image part'}), 400
    
    image_files = request.files.getlist('images')  # Get the list of images
    if not image_files:
        return jsonify({'error': 'No selected files'}), 400

    # Dictionary to group images by product (assumed by product name or label)
    grouped_results = {}

    # OCR and LLM extraction for each image
    for image_file in image_files:
        content = image_file.read()
        image = vision.Image(content=content)

        # OCR
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if response.error.message:
            return jsonify({'error': response.error.message}), 500

        if not texts:
            continue  # Skip this image if no text is found

        ocr_text = texts[0].description.strip()

        # LLM Extraction
        llm = ChatOpenAI(
            model="mistral-saba-24b",
            temperature=0.7,
            max_tokens=512
        )

        chef_prompt = PromptTemplate(
            input_variables=["input"],
            template=("You are a data extraction assistant that analyzes OCR text from product labels. "
            "Only extract information that is explicitly present in the OCR text. Do not guess or hallucinate any data.\n\n"
            "From the OCR text provided below, extract the following details strictly based on the text:\n\n"
            "1. The type of food ingredient (e.g., butter, bread, paneer, salt, chilli powder, etc.).\n"
            "2. The total weight (including the unit, such as '100 g' or '250 ml').\n"
            "3. The expiry date.\n\n"
            "Note: The expiry date might be given directly (e.g., '24/12/23', 'JAN24', etc.) or indirectly through a relative statement, such as:\n"
            "- 'Best before 2 years from packed on'\n"
            "- 'Use by 6 months from packaging date'\n"
            "- 'Expires 3 years after packing'\n\n"
            "When a relative expiry statement is present:\n"
            "- Identify the packaging date from phrases like 'Packed On:' or 'Packaging Date:'\n"
            "- Identify the relative time period (years or months)\n"
            "- Compute the absolute expiry date by adding that period to the packaging date\n\n"
            "Only use numbers and dates that are explicitly connected to these instructions. "
            "If any required detail is not present in the OCR text, return null for that field.\n\n"
            "Return your answer strictly as a JSON object with the following keys (and no additional information):\n"
            "- \"ingredient\"\n"
            "- \"total_weight\"\n"
            "- \"expiry_date\"\n\n"
            "OCR Text:\n{input}")  # Your prompt remains the same
        )

        prompt = chef_prompt.format(input=ocr_text)
        extracted_info = llm.predict(prompt)

        # Save the image to the packet upload folder
        image_id = str(uuid.uuid4()) + ".jpg"
        image_path = os.path.join(PACKET_UPLOAD_FOLDER, image_id)
        image_file.seek(0)  # Reset the pointer to the beginning of the file
        image_file.save(image_path)

        # Extract product name from OCR text (simple heuristic, modify as needed)
        # Assuming first text in OCR is the product name or a label that can identify the product
        product_name = ocr_text.split("\n")[0]

        # Add the result for this image under the corresponding product group
        if product_name not in grouped_results:
            grouped_results[product_name] = {
                'product_name': product_name,
                'ocr_texts': [],
                'extracted_info': [],
                'images': []
            }
        
        grouped_results[product_name]['ocr_texts'].append(ocr_text)
        grouped_results[product_name]['extracted_info'].append(extracted_info)
        grouped_results[product_name]['images'].append({
            'result_url': f"http://localhost:5000/static/uploads/packets/{image_id}"
        })

    # Convert grouped results into a list
    final_results = list(grouped_results.values())

    return jsonify({'results': final_results})


@app.route("/static/uploads/packets/<folder>/<filename>")
def serve_packet_image(folder, filename):
    return send_file(os.path.join(PACKET_UPLOAD_FOLDER, folder, filename), mimetype="image/jpeg")


chef_prompt = PromptTemplate(
        input_variables=["input"],
        template=("You are a data extraction assistant that analyzes OCR text from product labels. "
        "Only extract information that is explicitly present in the OCR text. Do not guess or hallucinate any data.\n\n"
        "From the OCR text provided below, extract the following details strictly based on the text:\n\n"
        "1. The type of food ingredient (e.g., butter, bread, paneer, salt, chilli powder, etc.).\n"
        "2. The total weight (including the unit, such as '100 g' or '250 ml').\n"
        "3. The expiry date.\n\n"
        "Note: The expiry date might be given directly (e.g., '24/12/23', 'JAN24', etc.) or indirectly through a relative statement, such as:\n"
        "- 'Best before 2 years from packed on'\n"
        "- 'Use by 6 months from packaging date'\n"
        "- 'Expires 3 years after packing'\n\n"
        "When a relative expiry statement is present:\n"
        "- Identify the packaging date from phrases like 'Packed On:' or 'Packaging Date:'\n"
        "- Identify the relative time period (years or months)\n"
        "- Compute the absolute expiry date by adding that period to the packaging date\n\n"
        "Only use numbers and dates that are explicitly connected to these instructions. "
        "If any required detail is not present in the OCR text, return null for that field.\n\n"
        "Return your answer strictly as a JSON object with the following keys (and no additional information):\n"
        "- \"ingredient\"\n"
        "- \"total_weight\"\n"
        "- \"expiry_date\"\n\n"
        "OCR Text:\n{input}")  # Your prompt remains the same
    )


llm = ChatOpenAI(
        model="mistral-saba-24b",
        temperature=0.7,
        max_tokens=512
    )
import json


@app.route('/packet-upload-multiple', methods=['POST'])
def packet_upload_multiple():
    if 'images' not in request.files:
        return jsonify({'error': 'No images part'}), 400

    images = request.files.getlist('images')
    results = []

    for image_file in images:
        if image_file.filename == '':
            continue

        # Read and process image for OCR
        content = image_file.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if response.error.message:
            ocr_text = f"OCR Error: {response.error.message}"
            extracted_info = '{"error": "OCR failed"}'
        elif not texts:
            ocr_text = ""
            extracted_info = '{"error": "No text found"}'
        else:
            ocr_text = texts[0].description.strip()
            prompt = chef_prompt.format(input=ocr_text)
            extracted_info = llm.predict(prompt)

        # Save image to unique folder
        folder_id = str(uuid.uuid4())
        folder_path = os.path.join(PACKET_UPLOAD_FOLDER, folder_id)
        os.makedirs(folder_path, exist_ok=True)
        filename = str(uuid.uuid4()) + ".jpg"
        image_file.seek(0)
        image_path = os.path.join(folder_path, filename)
        image_file.save(image_path)

        cleaned_str = extracted_info.strip().replace("```json", "").replace("```", "").strip()

        # Step 2: Parse it to a Python dictionary
        parsed_data = json.loads(cleaned_str)

        # ✅ Now you can access the fields
        ingredient = parsed_data["ingredient"]
        quantity, unit = parsed_data["total_weight"].split()  # "100 g" → ["100", "g"]
        expiry_date_str = parsed_data["expiry_date"]
        expiry_date = datetime.strptime(expiry_date_str, "%d-%b-%y").strftime("%Y-%m-%d")
        purchase_date = datetime.today().strftime("%Y-%m-%d")

        csv_file = "data/purchase_table.csv"
        header = ["Purchase_Date", "Ingredient", "Unit", "Quantity_Purchased", "Expiry_Date"]
        row = [purchase_date, ingredient, unit, quantity, expiry_date]

        try:
            with open(csv_file, "r") as f:
                pass  # If file exists, do nothing
            file_exists = True
        except FileNotFoundError:
            file_exists = False

        with open(csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(row)

        print("✅ Data appended to purchase_table.csv")

        results.append({
            'ocr_text': ocr_text,
            'extracted_info': extracted_info,
            'result_url': f"http://localhost:5000/static/uploads/packets/{folder_id}/{filename}"
        })

    return jsonify({'results': results})




# Session-based memory store
session_store = {}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get("session_id")
    user_input = data.get("message")

    # Prompt template inside the route
    chef_prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=(
            "You are a professional virtual assistant who only provides help with food, cooking, recipes, ingredients, kitchen tools, and culinary techniques.\n\n"
            "Your rules:\n"
            "- Do NOT answer or reference any question that is outside the domain of cooking and food.\n"
            "- Do NOT offer conditional suggestions (e.g., 'if you're referring to cooking...') for off-topic questions.\n"
            "- Do NOT redirect, pivot, or relate off-topic questions back to food in any way.\n"
            "- Do NOT provide extra information, jokes, trivia, or alternative topics unless explicitly requested in a food context.\n"
            "- Do NOT mention or recall unrelated user questions in any future response.\n"
            "- Do NOT apologize or explain — simply and clearly state your domain limitation.\n\n"
            "If the user asks something off-topic, reply only with:\n"
            "\"I'm here to help with food and cooking questions only.\"\n\n"
            "Stay fully in character and remain strictly within your expertise.\n\n"
            "Conversation History:\n{history}\n"
            "User: {input}\n"
            "Chef:"
        )
    )

    # Check or create conversation session
    if not session_id:
        session_id = str(uuid4())
        memory = ConversationBufferMemory()
        session_store[session_id] = ConversationChain(
            llm=llm,
            memory=memory,
            prompt=chef_prompt,
            verbose=False
        )
    elif session_id not in session_store:
        memory = ConversationBufferMemory()
        session_store[session_id] = ConversationChain(
            llm=llm,
            memory=memory,
            prompt=chef_prompt,
            verbose=False
        )

    # Get the current session's conversation
    conversation = session_store[session_id]
    response = conversation.predict(input=user_input)

    return jsonify({
        "response": response.strip(),
        "session_id": session_id
    })


@app.route("/api/waste-detection", methods=["POST"])
def waste_detection():
    if 'image' not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400

    image_file = request.files['image']
    image_path = "uploaded_image.png"
    image_file.save(image_path)

    try:
        # Initialize Roboflow inference client
        CLIENT = InferenceHTTPClient(
            api_url="http://localhost:9001",
            api_key="HIHYIMHr2i6igB3MRQv8"
        )

        # Run inference
        result = CLIENT.infer(image_path, model_id="food__waste/2")

        # Load and annotate image
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        for prediction in result['predictions']:
            x = prediction['x']
            y = prediction['y']
            w = prediction['width']
            h = prediction['height']
            class_name = prediction['class']
            confidence = prediction['confidence']

            left = x - w / 2
            top = y - h / 2
            right = x + w / 2
            bottom = y + h / 2

            draw.rectangle([left, top, right, bottom], outline="red", width=3)
            draw.text((left, top - 10), f"{class_name} ({confidence:.2f})", fill="red")

        # Convert image to base64 to return to frontend
        img_io = io.BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode()

        return jsonify({
            "predictions": result['predictions'],
            "annotated_image": img_base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate-recipes", methods=["POST"])
def generate_recipes():

    # LangChain LLM setup
    llm = ChatOpenAI(
        model="mistral-saba-24b",
        temperature=0.7,
        max_tokens=1024
    )

    # Recipe generation prompt
    recipe_prompt = PromptTemplate(
        input_variables=["ingredient_list", "existing_dishes"],
        template="""
    You are a creative and professional chef assistant.

    The restaurant already sells the following dishes:
    {existing_dishes}

    Based on the available ingredients below, suggest **3 new and unique dishes** that:
    - Are not already sold by the restaurant.
    - Match the overall cuisine and style of the existing menu.
    - Would be appealing additions to the menu.

    For each suggested dish, provide:
    1. A creative and relevant dish name.
    2. Estimated preparation and cooking time.
    3. A list of ingredients with reasonable quantities.
    4. Step-by-step cooking instructions.

    Only return the 3 full recipes. Do not explain your reasoning or process.

    Available Ingredients:
    {ingredient_list}
    """
    )

    data = request.get_json()
    ingredients = data.get("ingredients", "")
    existing_dishes = data.get("existing_dishes", "")

    prompt = recipe_prompt.format(
        ingredient_list=ingredients,
        existing_dishes=existing_dishes
    )

    try:
        response = llm.predict(prompt)
        return jsonify({"recipes": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)