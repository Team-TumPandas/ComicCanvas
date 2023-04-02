import os
import openai
from flask import Flask, url_for, request, jsonify
from flask_cors import CORS
import json 
import requests
import re

# global variables
artist_server = "https://tum-pandas-artist.loophole.site/"
openai.api_key = os.getenv("OPENAI_API_KEY")
model_engine = "text-davinci-003"
conversation_history = {}



def general_comic_info(project_id): 
    current_project = project_dict.get(project_id)
    if current_project is None:
        return jsonify("ERROR: non existent proj")
    system_prompt = "You're an AI that helps comic book artists write the storyline and dialogues for the characters of a comic book."
    user_prompt = ""
    user_prompt += f"The style is: {current_project.style}\n"
    user_prompt += f"The genre is: {current_project.genre}\n\n"
    user_prompt += f"Storyline: {current_project.user_storyline}\n"
    user_prompt += "List of characters:\n"
    for index in range(len(current_project.character_name_list)): 
        user_prompt += f"{index}. {current_project.character_name_list[index]} : {current_project.character_personality_list[index]}\n"
    user_prompt += "\n"
    return system_prompt, user_prompt

chatGPT_intro_1 = "Given these information, please first create the a general script that summarizes the main content and twists of the short story. Please only provide the storyline. Please start with: \n<Story Line>"
chatGPT_intro_2 = "Given the general storyline and a list of characters and all the information, please create detailed and descriptive storyboards and dialogues of the characters. Your output must be formatted like the following example:\n<Panel 1>\nSCENARIO DESCRIPTION: A comic book panel of a 25 year old female hacker in a darkly-lit room illuminated by the monitor, with code on the monitor. The female hacker is very focused on the monitor. In comic book style.\nDIALOGUES:\n[Dyla] \"I'm hacking into the main framework.\"\n[Anna] \"I agree with you.\”\n<Panel 2:> ..."
chatGPT_intro_3 = ""





app = Flask(__name__, static_folder='frontend', static_url_path='/')
CORS(app)

class Project:
    def __init__(self):
        user_storyline = None
        style = None
        genre = None
        character_name_list = None
        character_gender_list = None
        character_look_list = None
        character_personality_list = None
        panel_map = None

    def beauty_print(self):
        print(f"user_storyline: {self.user_storyline}") 
        print(f"style: {self.style}")
        print(f"genre: {self.genre}")
        print(f"character_name_list: {self.character_name_list}")
        print(f"character_gender_list: {self.character_gender_list}")
        print(f"character_look_list: {self.character_look_list}")
        print(f"character_personality_list: {self.character_personality_list}")

project_dict = {}


@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/test", methods=['POST', 'GET'])
def test(): 
    data = json.loads(request.data)
    title = data.get('title')
    return "fake storyline"


@app.route("/global", methods=['POST'])
def construct_storyline():
    data = json.loads(request.data)
    title = data.get('title')

    current_project = project_dict.get(title)
    if current_project is None:
        project_dict[title] = Project()
        current_project = project_dict.get(title)

    current_project.user_storyline = data.get('setting') 
    current_project.style = data.get('style')
    current_project.genre = data.get('genre')
    current_project.character_name_list = [data.get('character_' + str(i) + '_name') for i in range(1,4)]
    current_project.character_gender_list = [data.get('character_' + str(i) + '_gender') for i in range(1,4)]
    current_project.character_look_list = [data.get('character_' + str(i) + '_look') for i in range(1,4)]
    current_project.character_personality_list = [data.get('character_' + str(i) + '_personality') for i in range(1,4)]
    
    print(data)
    print(f"BEAUTY_PRINT PROJECT {title} \n{current_project.beauty_print()}")
    output = jsonify(construct_story_line_func(title))
    return output

def construct_story_line_func(project_id):
    current_project = project_dict.get(project_id)
    if current_project is None:
        return jsonify("ERROR: non existent proj")
    
    system_prompt, user_prompt = general_comic_info(project_id)
    chatGPT_response = ask_chat_GPT(system_prompt=system_prompt, user_prompt= user_prompt+chatGPT_intro_1)
    try:
        chatGPT_response = chatGPT_response.split("<Story Line>")[1]
    except:
        pass
    print(chatGPT_response.strip())
    return chatGPT_response.strip()

@app.route("/storyline", methods=['POST'])
def construct_first_draft():
    data = json.loads(request.data)
    #print(data)
    
    title = data.get('title')
    story_line = data.get('storyline')
    output = jsonify(construct_first_draft_func(title, story_line))
    return output

def construct_first_draft_func(project_id, story_line):
    current_project = project_dict.get(project_id)
    if current_project is None:
        return jsonify("ERROR: non existent proj")
    
    current_project.user_storyline = story_line
    
    system_prompt, user_prompt = general_comic_info(project_id)
    chatGPT_response = ask_chat_GPT(system_prompt=system_prompt, user_prompt= user_prompt+chatGPT_intro_2)

    ### Step 4: generate for each frame in the layout 
    print("\n\nchatGPT_response::::" , chatGPT_response)
    panels = parse(chatGPT_response)

    print("\n\nPARSED PANELS", panels)
    current_project.pannel_map = panels

    print(f"\n\nBEAUTY_PRINT PROJECT {project_id} : ") #without panel for now 
    current_project.beauty_print()
    return panels

@app.route("/generate_panel", methods=['POST'])
def generate_frame():
    data = json.loads(request.data)
    #print(data)
    current_project = project_dict.get(data.get('title'))
    #if current_project is None:
    #    return jsonify("ERROR: non existent proj")

    panel_index = data.get('panel_index') #TODO
    panel_info = data.get('panel_info')

    #chatGPT_response = ask_GPT(general_comic_info(project_id) + chatGPT_intro_3)
    #TODO: bauen panel_index und panel_info in chatGPT_response ein

    #current_project.panel_map[panel_index] = panel_info
    output = generate_frame_func(panel_info.get('scenario_description'))

    # cache the generated image
    #current_project.panel_map.get(panel_index)["image"] = output
    return output

def generate_frame_func(scenario_description, withImage=False):

    #TODO: send to chatGPT for improvement (I don't want to do this haha)
    #print("THE SCENARIO DISCRIPTION!!!!!!", scenario_description)
    if withImage: 
        req = {
            "image" : "", #TODO: receive from ???
            "prompt" : scenario_description
        }
        response = requests.get(artist_server+"/img2img", params=req)
    else:
        req = {
            "prompt": scenario_description
        }
        response = requests.get(artist_server+"/txt2img", params=req)
        
    if response.status_code != 200:
        print("ERROR: could not generate image")
        return None
    data = response.json() # should be a list of base64 encoded images
    #print(data)
    
    return data



@app.route("/chat", methods=['POST'])
def role_acting():
    data = json.loads(request.data)
    #output = ask_chat_GPT(data.get('user_prompt'), system_prompt=data.get('system_prompt'))
    output = chat_with_history(data.get('user_prompt'), data.get('system_prompt'), convo_id=data.get('convo_id'))
    return output

def ask_chat_GPT(user_prompt, system_prompt='You are a helpful assistant to a comic book writer.'): 
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    response = completion.choices[0].message.content
    return response

def chat_with_history(user_prompt, system_prompt, USERNAME="user", SYSTEM="system", ASSISTANT="assistant", convo_id="default"):
    # Generate a response using GPT-3
    
    if conversation_history.get(convo_id) is None:
        conversation_history[convo_id] = ""

    current_history = conversation_history[convo_id]
    message = ask_chat_GPT(user_prompt, system_prompt + current_history)
    # Update the conversation history
    current_history += f"{USERNAME}: {user_prompt}\n"
    current_history += f"{ASSISTANT}: {message}\n"
    conversation_history[convo_id] = current_history
    return message


def ask_GPT(input_prompt): 
    completion = openai.Completion.create(
       engine=model_engine,
       prompt=input_prompt,
       max_tokens=1024,
       n=1,
       stop=None,
       temperature=0.5,
    )
    response = completion.choices[0].text
    #response_planes = "Sure, here's a storyboard and dialogue for the three panels:\n\n<Panel 1>\nSCENARIO DESCRIPTION: Spiderman and Joker are facing each other on a busy street. The sun is setting in the background, casting an orange glow over the scene. Spiderman is in a crouched position, ready to pounce. Joker is holding a knife, grinning maniacally.\nDIALOGUES:\n[Spiderman] \"You're not getting away with this, Joker.\"\n[Joker] \"Oh, but Spiderman, that's the fun part!\"\n\n<Panel 2>\nSCENARIO DESCRIPTION: Spiderman jumps over a car, narrowly avoiding a swipe from Joker's knife. Joker is now on top of the car, taunting Spiderman. The car is parked near a fruit stand, which Spiderman uses to his advantage.\nDIALOGUES:\n[Spiderman] \"You're going to have to do better than that, Joker.\"[Joker] \"I'm just getting started, Spiderman!\"\n\n<Panel 3>\nSCENARIO DESCRIPTION: Spiderman has used his web-slinging ability to wrap Joker up in a bundle of fruit. Joker is squirming and shouting, while Spiderman looks on triumphantly. The police are arriving on the scene to take Joker into custody.\nDIALOGUES:\n[Spiderman] \"Looks like you're not so tough after all, Joker.\"\n[Joker] \"This isn't over, Spiderman!\"\n[Police officer] \"Thanks for your help, Spiderman. We'll take it from here.\"\n"
    #response_story_line = "<Story Line>\nAs the city of Gotham fell into chaos, Spiderman arrived on the scene to confront the notorious Joker. The two clashed in a brutal battle of wits and strength, with the unpredictable nature of the Joker making him a difficult opponent for Spiderman to take down.\nDespite the odds, Spiderman's quick thinking and agility allowed him to stay one step ahead of the Joker, dodging his attacks and launching his own counterattacks. The Joker's devious schemes and cunning traps only served to increase Spiderman's determination to bring him to justice.\nIn the end, Spiderman outsmarted the Joker by using his own tricks against him, leading to the villain's capture and imprisonment. With the city safe once again, Spiderman swung off into the night, ready to face whatever new challenges awaited him.\n<Dialogues>"
    return response


def parse(input_string):
    # Define a regular expression pattern to match the panels
    panel_pattern = r'<Panel:? (\d+)>:?'

    # Define a regular expression pattern to match the scenario description
    description_pattern = r'SCENARIO DESCRIPTION:? (.+)'

    # Define a regular expression pattern to match the dialogues
    dialogue_pattern = r'\[(.+)\]:? (.+)'

    # Initialize a dictionary to hold the panel objects
    panel_objects = {}

    # Split the input string into panels using the panel pattern
    panels = re.split(panel_pattern, input_string)[1:]

    # Iterate over the panels and create the panel objects
    for i in range(0, len(panels), 2):
        panel_num = int(panels[i])
        panel_description = re.search(description_pattern, panels[i+1]).group(1)
        dialogues = re.findall(dialogue_pattern, panels[i+1])
        dialogue_objects = {}
        for dialogue in dialogues:
            speaker = dialogue[0]
            text = dialogue[1]
            dialogue_objects |= {speaker: text}
        panel_objects[panel_num] = {'scenario_description': panel_description, 'dialogues': dialogue_objects}
    
    return panel_objects



def edit_story_func(title):
    #TODO if needed 
    return 
    
    
    
        













