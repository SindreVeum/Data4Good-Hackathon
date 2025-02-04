from flask import Flask, request, jsonify, render_template
import openai
import pandas as pd
import numpy as np
import json

app = Flask(__name__)

openai.api_key = "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"

@app.route('/')
def index():

    data = pd.read_excel("/Users/sindreveum/Documents/Coding/Personal Code/Hertie D4G/app/Final_Data_Final_Final.xlsx")
    data = data.round(2)
    data.sort_values(by="Name")

    # Convert to JSON
    city_data_json = json.dumps(data.to_dict(orient="records"))

    # Pass the JSON to the template
    return render_template('index.html', city_data=city_data_json)

message_history = [
    {"role": "system", "content": "You are a helpful assistant providing information about cities based on user preferences."}
]

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form.get('user_input')  # Get user input from form
    
    # Construct the input message
    input_message = f"""
        {user_input}
    """
    
    try:
        # Add the user's message to the conversation history
        message_history.append({"role": "user", "content": input_message})
        
        # Call the OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4",  # Use the desired model
            messages=message_history,
            temperature=1,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        
        # Extract the assistant's reply
        ai_response = response.choices[0].message.content
        
        # Add the assistant's response to the conversation history
        message_history.append({"role": "assistant", "content": ai_response})
        
        return jsonify({'response': ai_response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_response_auto', methods=['POST'])
def get_response_auto():
    try:
        # Get city data from the request
        city_name = request.json.get('city')  # City name
        city_values = request.json.get('values')  # City values
        
        # Construct the input message for the AI
        user_input = f"""
            Provide detailed insights for the commune {city_name}.
            Here is the data for the commune:
            - Economy and Employment Index: {city_values['economy_and_employment_index']}
            - Quality of Life Index: {city_values['quality_of_life_index']}
            - Inequality and Sustainability Index: {city_values['inequality_and_sustainability_index']}
            - Eco-Friendliness Index: {city_values['eco_friendliness_index']}
            """
        
        # Call OpenAI API for response
        response = openai.chat.completions.create(
            model="gpt-4",  # Replace with your desired model
            messages=[  # No message history, only a single message
                {"role": "system", "content": "You are an AI that provides ultra-concise diagnostics for a selected German city based on an index score from 0-10. Your task is to summarize the city's overall standing clearly and explain reasons for why they might have gotten this score. Only use short bullet points—no full sentences. Guidelines: Overall Score → General assessment of the city (⭐ Excellent, ✅ Good, ➖ Average, ⚠️ Below Average, ❌ Poor). Keep it super brief. Max 5-7 key points total . Write 1 sentence per aspect explaining it and giving reasons. Write as if you are addressing the user. Make the output structured with Heading, sub-heading etc. Use ONLY! HTML tags for formatting, for lists use <br> instead of <li>. use <b> instead of h1, h2, h3, etc."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.82,
            max_completion_tokens=280,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        
        # Extract the assistant's reply
        ai_response = response.choices[0].message.content
        
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
