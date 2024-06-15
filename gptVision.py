from openai import OpenAI
import os
import boto3
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

s3 = boto3.client('s3')
bucket_name = 'tire-test-1'
files = s3.list_objects(Bucket=bucket_name)['Contents']
# print(files)

file_urls = []
for file in files:
    # print(file)
    params = {'Bucket': bucket_name, 'Key': file['Key']}
    url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=24*60*60)  # URL expires in 24 hour
    print (url)
    file_urls.append(url)

# print(file_urls)

client = OpenAI(api_key=OPENAI_API_KEY)

def getDamage(url):
    response = client.chat.completions.create(
    model="gpt-4o",

    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", 
            "text": """
                Check carefully if this wheel is damaged. If it is could you write me a json that gives type of wheel, type of damage, and other necessary details
                Only give me the json output.
                Example Output:
                {
                    "wheel": {
                        "type": "Alloy Wheel",
                        "size": "Not specified",
                        "style": "Five-spoke design"
                        "tire_number": "T-123"
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
            {
            "type": "image_url",
            "image_url": {
                "url": url,
            },
            },
        ],
        }
    ],
    max_tokens=300,
    )

    content = response.choices[0].message.content
    print("==="*10, "URL:", url, "==="*10)
    print(content)
    print("==="*10, "URL:", url, "==="*10)
    return content

for i, url in enumerate(file_urls):
   data = getDamage(url)

   # Remove the markdown syntax
   json_string = data.replace('```json\n', '').replace('\n```', '')

   # Parse the JSON string into a Python dictionary
   data = json.loads(json_string)

   with open (f"response_{i}.json", "w") as f:
       json.dump(data, f, indent=4)
