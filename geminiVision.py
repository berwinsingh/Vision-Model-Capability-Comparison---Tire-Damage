#Using Google Gemini 1.5 Pro as the Vision model to analyze the image and generate a JSON response
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=GEMINI_API_KEY, 
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    })

damaged_wheel_directory = "./data"
files = os.listdir(damaged_wheel_directory)

for i, file in enumerate(files):
    print(f"Index Number: {i}")
    if os.path.isdir(os.path.join(damaged_wheel_directory, file)):
        continue

    messages = HumanMessage(
        content=[{
            "type": "text",
            "text": """
            Check carefully if this wheel is damaged. If it is could you write me a json that gives type of wheel, type of damage, and other necessary details

            Example Output:
            {
                "wheel": {
                    "type": "Alloy Wheel",
                    "size": "Not specified",
                    "style": "Five-spoke design"
                },
                "tire": {
                    "condition": "Damaged",
                    "damage": {
                    "type": "Sidewall tear",
                    "description": "A visible tear or rupture along the tire's sidewall, potentially caused by external impact or sharp objects.",
                    "severity": "High",
                    "recommended_action": "Replace tire immediately to avoid risk of blowout"
                    }
                },
                "other_details": {
                    "vehicle_type": "Not specified",
                    "location_of_damage": "Visible on the external sidewall of the tire",
                    "safety_risk": "High risk of blowout, unsafe to drive"
                }
            }
        """
        },
        {"type": "image_url", "image_url": os.path.join(damaged_wheel_directory, file)}
        ]
    )

    llm_response = llm.invoke([messages])
    response = llm_response.content

    # Remove the markdown syntax
    json_string = response.replace('```json\n', '').replace('\n```', '')

    # Parse the JSON string into a Python dictionary
    data = json.loads(json_string)

    with open (f"response_{i}.json", "w") as f:
        json.dump(data, f, indent=4)