import os
import openai
from flask import Flask, url_for

app = Flask(__name__, static_folder='frontend', static_url_path='/')

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/global", methods=['POST'])
def test():
    print("test")
    # print post data
    print(request.data)
    return "storyline"

#openai.api_key = os.getenv("OPENAI_API_KEY")
#model_engine = "text-davinci-003"


def ask_chat_GPT(input_prompt): 
    prompt = input_prompt
    #completion = openai.Completion.create(
    #    engine=model_engine,
    #    prompt=prompt,
    #    max_tokens=1024,
    #    n=1,
    #    stop=None,
    #    temperature=0.5,
    #)
    #response = completion.choices[0].text
    print(prompt)

character_list = ["Batman: superhero", "joker: bad guy", "harley quinn: nurse"]
chatGPT_purpose_intro = "CHAT GPT PURPOSE INTRO"
chatGPT_characters_registation = "CHARACTERS INTRO"
senario_format_example = "FORMAT EXAMPLE"


def update_global():
    ### Step 1: tell chatGPT about the general task aka. the purpose of the app 
    ask_chat_GPT(chatGPT_purpose_intro)

    ### Step 2: TODO user choose layout /frame positioning 
    amount_of_panel = 3 

    ### Step 3: user register characters 
    # "Anna: a supermodel, who ..."
    # "Anna's dog : pet of Anna, who ..."
    def register_character(name, description): 
        character_list.append("{name} : {description}")
        return; 

    ask_chat_GPT("List of characters:\n{0}\n\n{1}\n{2}".format('\n'.join(character_list), chatGPT_characters_registation, senario_format_example))


    ### Step 4: generate for each frame in the layout 
    example_response_from_chatGPT = "Certainly! Here's an example of what the script for the three panels of the comic book could look like:\n\n<Panel 1>\nSCENARIO DESCRIPTION: A comic book panel of Gotham City's skyline at night. Batman is standing on a rooftop, looking down on the city with his arms crossed. The full moon is shining behind him.\nDIALOGUES:\n[Batman] \"Another night in Gotham. Time to clean up the streets.\"\n\n<Panel 2>\nSCENARIO DESCRIPTION: A comic book panel of a dark alleyway. Joker and Harley Quinn are standing in the middle of the alleyway, with Joker holding a smoking bomb in his hand.\nDIALOGUES:\n[Joker] \"Ha ha! Looks like we're going to have some fun tonight!\"\n[Harley Quinn] \"Oh, Puddin', you always know how to make me smile.\"For each panel, here are the prompts you could use to generate the corresponding image using DALL-E 2."
    panels = []

    for panel_str in example_response_from_chatGPT.split("<Panel ")[1:]:

        panel = {"scenario_discription": "", "dialogues": {}}
        panel_num, panel_str = panel_str.split(">", 1)
        panel["num"] = int(panel_num)
        scenario_discription = panel_str.split("SCENARIO DESCRIPTION: ", 1)[1]
        scenario_discription, dialogs = scenario_discription.split("DIALOGUES:", 1)
        panel["scenario_discription"] = scenario_discription

        for line in dialogs.split("[")[1:]:
            character, quote = line.split("] \"", 1)
            quote = quote.split("\"")[0]
            panel["dialogues"][character] = quote
            
        panels.append(panel)

    print(panels)

        
        













