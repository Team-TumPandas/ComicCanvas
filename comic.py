import os
import openai
from flask import Flask, url_for, request, jsonify
from flask_cors import CORS
import json 
import requests

# global variables
artist_server = "https://tum-pandas-artist.loophole.site/"

app = Flask(__name__, static_folder='frontend', static_url_path='/')
CORS(app)

class Project:
    #character_list = ["Batman: superhero", "joker: bad guy", "harley quinn: nurse"]
    def __init__(self):
        user_storyline = None
        style = None
        genre = None
        character_name_list = None
        character_gender_list = None
        character_look_list = None
        character_personality_list = None
        pannel_map = None


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
    print(f"server received request from: {title}") 
    print(f"user_storyline: {current_project.user_storyline}") 
    print(f"style: {current_project.style}")
    print(f"genre: {current_project.genre}")
    print(f"character_name_list: {current_project.character_name_list}")
    print(f"character_gender_list: {current_project.character_gender_list}")
    print(f"character_look_list: {current_project.character_look_list}")
    print(f"character_personality_list: {current_project.character_personality_list}")
    
    output = jsonify(construct_story_line_func(title))
    return output

@app.route("/storyLine", methods=['POST'])
def construct_first_draft():
    data = json.loads(request.data)
    title = data.get('title')
    output = jsonify(construct_first_draft_func(title))
    return output

@app.route("/frameGenerator", methods=['POST'])
def generate_frame():
    data = json.loads(request.data)
    title = data.get('title')
    planetIndex = data.get('planetIndex')
    output = generate_frame_func(title, planetIndex)
    return output


@app.route("/fake_global", methods=['POST'])
def fake_global():
    return "output"


openai.api_key = os.getenv("OPENAI_API_KEY")
model_engine = "text-davinci-003"


def ask_chat_GPT(input_prompt): 
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

def construct_story_line_func(project_id):
    current_project = project_dict.get(project_id)
    if current_project is None:
        return jsonify("ERROR: non existent proj")
    
    chatGPT_purpose_intro = f"You're an AI that helps comic book artists write the storyline and dialogues for the characters of a comic book. Given the general scenario and a list of characters, you create detailed and descriptive storyboards and dialogues of the characters. "
    chatGPT_characters_storyline_intro = "Given this storyline and this list of characters, please first create the a general script that summarizes the main content and twists of the short story. Please only provide the storyline."
    format = "Please start with: \n<Story Line>"

    output_to_chatGPT = chatGPT_purpose_intro
    output_to_chatGPT += f"Storyline: {current_project.user_storyline}\n\n"
    output_to_chatGPT += "List of characters:\n"
    for index in range(len(current_project.character_name_list)): 
        output_to_chatGPT += f"{index}. {current_project.character_name_list[index]} : {current_project.character_personality_list[index]}\n"
    output_to_chatGPT += "\n{chatGPT_characters_storyline_intro}\n{format}"


    chatGPT_response = ask_chat_GPT(output_to_chatGPT)
    try:
        chatGPT_response = chatGPT_response.split("<Story Line>")[1]
    except:
        pass
    
    print(chatGPT_response.strip())
    return chatGPT_response.strip()

def construct_first_draft_func(project_id):
    current_project = project_dict.get(project_id)
    if current_project is None:
        return jsonify("ERROR: non existent proj")
    
    chatGPT_characters_storyline_intro = f"Now please create detailed and descriptive storyboards and dialogues of the characters. Your output must be formatted like the following example:"
    format = "<Panel 1>\nSCENARIO DESCRIPTION: A comic book panel of a 25 year old female hacker in a darkly-lit room illuminated by the monitor, with code on the monitor. The female hacker is very focused on the monitor. In comic book style.\nDIALOGUES:\n[Dyla] \"I'm hacking into the main framework.\"\n[Anna] \"I agree with you.\”\n<Panel 2:> ..."

    output_to_chatGPT = "\n{chatGPT_characters_storyline_intro}\n{format}"
    chatGPT_response = ask_chat_GPT(output_to_chatGPT)

    ### Step 4: generate for each frame in the layout 
    panels = {}
    for panel_str in chatGPT_response.split("<Panel ")[1:]:

        panel = {"scenario_description": "", "dialogues": {}}
        panel_num, panel_str = panel_str.split(">", 1)
        scenario_description = panel_str.split("SCENARIO DESCRIPTION: ", 1)[1]
        scenario_description, dialogs = scenario_description.split("DIALOGUES:", 1)
        panel["scenario_description"] = scenario_description

        for line in dialogs.split("[")[1:]:
            character, quote = line.split("] \"", 1)
            quote = quote.split("\"")[0]
            panel["dialogues"][character] = quote

        panels[int(panel_num)] = panel

    print(panels)
    current_project.pannel_map = panels
    return panels



def edit_story_func(title):
    #TODO if needed 
    return 
    

def generate_frame_func(title, frameIndex, withImage=False):
    current_project = project_dict.get(title)
    
    if current_project is None:
        return jsonify("ERROR: non existent proj")
    
    scenario_description = current_project.pannel_map.get(frameIndex).get("scenario_description")

    #TODO: send to chatGPT for improvement 
    #print("THE SCENARIO DISCRIPTION!!!!!!", scenario_description)
    
    if withImage: 
        req = {
            #place holders for later
            "image" : "", #TODO: receive from ???
            "prompt" : scenario_description
        }
        response = requests.get(artist_server+"/img2img", params=req)
    else:
        # create a json request to a server that will generate the image
        req = {
            #place holders for later
            "prompt": scenario_description
        }
        response = requests.get(artist_server+"/txt2img", params=req)
        
    if response.status_code != 200:
        print("ERROR: could not generate image")
        return None
    data = response.json() # should be a list of base64 encoded images
    print(data)
    
    # cache the generated image
    current_project.pannel_map.get(frameIndex)["image"] = data
    return data
        
        













