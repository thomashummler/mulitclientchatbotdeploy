#pip install pandas
#pip install openpyxl
#pip install openai


import os
import pandas as pd
import numpy as np
import re
import json
from openai import OpenAI

API_KEY = os.environ["API_KEY"]

openai_api_key = API_KEY

file_path = 'Rieker_SUMMERANDWINTER_DATA.xlsx'

Rieker_Database = pd.read_excel(file_path)

seed_value = 42
np.random.seed(seed_value)

# Your original code
df_groupByColor_Rieker = Rieker_Database.groupby('Main_Color', group_keys=False).apply(lambda x: x.sample(10, replace=True, random_state=seed_value))
df_groupByShoeType_Rieker = Rieker_Database.groupby('main_category', group_keys=False).apply(lambda x: x.sample(10, replace=True, random_state=seed_value))
df_groupByGender_Rieker = Rieker_Database.groupby('Warengruppe', group_keys=False).apply(lambda x: x.sample(10, replace=True, random_state=seed_value))
df_groupBySaison_Rieker = Rieker_Database.groupby('Saison_Catch', group_keys=False).apply(lambda x: x.sample(10, replace=True, random_state=seed_value))
df_groupByMaterial_Rieker = Rieker_Database.groupby('EAS Material', group_keys=False).apply(lambda x: x.sample(10, replace=True, random_state=seed_value))

result_df = pd.concat([df_groupByColor_Rieker, df_groupByShoeType_Rieker, df_groupByGender_Rieker, df_groupBySaison_Rieker, df_groupByMaterial_Rieker], ignore_index=True)
result_df = result_df.drop_duplicates(subset='ID', keep='first')
Rieker_Database = result_df


# Der gegebene String
def extractJsonOutOfResponse(string):
  text = string
  # Regex, um das JSON-Objekt zu finden

  json_str = re.search(r'```json\n(.+?)\n```', text, re.DOTALL)

  if json_str:
      # Konvertieren des gefundenen Strings in ein JSON-Objekt
      json_obj = json.loads(json_str.group(1))
     
      return json_obj
  else:
      return "NO JSOn"


import json
import re

def setDataAndFilterWithJSON(json_string):

  data = json.loads(json_string)

  data_color = data["Color"]
  data_shoe_type = data.get("Shoe Type")
  data_gender = data.get("Gender")
  data_season = data.get("Season")
  data_material = data.get("Material")



  return filter_rieker_database(color=data_color, shoe_type=data_shoe_type, gender=data_gender, season=data_season, material=data_material )


def filter_rieker_database(color, shoe_type, gender, season, material):
    conditions = []

    if color != "":
        conditions.append(Rieker_Database["Main_Color"] == color)

    if shoe_type != "":
        conditions.append(Rieker_Database["main_category"] == shoe_type)

    if gender != "":
        conditions.append(Rieker_Database["Warengruppe"] == gender)

    if season != "":
        conditions.append(Rieker_Database["Saison_Catch"] == season)

    if material != "":
        conditions.append(Rieker_Database["EAS Material"] == material)

 #   if closure != "":
 #       conditions.append(Rieker_Database["Verschluss"] == closure)

    if conditions:
        filtered_df = Rieker_Database.loc[pd.concat(conditions, axis=1).all(axis=1)]
        return filtered_df
    else:
        return Rieker_Database

client = OpenAI(
    api_key= openai_api_key
)


chatVerlauf_Information=[{
    "role": "system",
    "content":f"You try to recognize various information from the user and return it in json format. "
               f"The following information should be recognized: Color, shoe type, gender, season, material, size, closure type. "
               f"The color must correspond to one of the following colors: schwarz, grau, braun, beige, weiß, rot, blau, "
               f"grün, gelb, gold, lila, mehrfarbig, rosa, bunt, metallisch, silber, orange. The shoe type must correspond "
               f"to one of the following: Slipper, Chelsea Boots, Biker Boots, Stiefel, Stiefeletten, Sneaker, Halbschuhe, "
               f"Rieker EVOLUTION, Pantoletten, Sandalen, Sandaletten. Gender must be either Damen oder Herren. "
               f"Season must be one of the following: Winter, Sommer. Material must match one of the "
               f"following: Glattleder, Lackleder, Rauhleder/Stretch, Glattleder/Stretch, Rauleder, Kunstleder, Kunstlack, "
               f"Textil, Reptilleder, Kunststoff. The Closure Type must be in Reißverschluss, Klettverschluss, Elastikeinsatz , ohne Verschluss, Schnürung,Schnalle, Gummischnürung, Gummizug.If the user's input does not match the given information on color, "
               f"shoe type, gender, season, material, select the most suitable information unless the user has not entered "
               f"anything for the corresponding information. Then return a "" for the respective information and not null. The JSON format "
               f"should be: {{'Color': 'User Specified Color', 'Shoe Type': 'User Specified Shoe Type', "
               f"'Gender': 'User Specified Gender', 'Season': 'User Specified Season', "
               f"'Material': 'User Specified Material'}} In the following interaction a interactions with the User some Filers may already be set. Recognize that they are set and just change them if u got new Informations from the User about this Filter"
}]

#While Schleife die laufend User Input entegen nimmt
chatVerlauf_UserInteraction=[{
        "role": "system",
           "content": f"You are a polite and helpful assistant who should help the user find the right shoes out of a Shoes Database.That's why you greet the user first and ask how you can help them.  "
        }]
chat_User = client.chat.completions.create(
         model="gpt-4-1106-preview",
         messages=chatVerlauf_UserInteraction
        )
antwort_Message = chat_User.choices[0].message.content
print(antwort_Message)

while True:
    user_input = input("Type In what kind of shoe u want(type 'exit' or 'quit' to quit): ")
    if user_input.lower() == "exit" or user_input.lower() == "quit":
        break
    else:
        chatVerlauf_Information.append({"role": "user", "content": user_input}),
        chat_Filter = client.chat.completions.create(
        model="gpt-4-1106-preview",
        response_format={ "type": "json_object" },
        messages= chatVerlauf_Information
        )
        JSON_Data =  chat_Filter.choices[0].message.content
        chatVerlauf_Information.append({"role": "assistant", "content": JSON_Data}),
        #print(JSON_Data)
        filtered_DF = setDataAndFilterWithJSON(JSON_Data)
        #print(filtered_DF)
        lengthOfFilteredDatabase = filtered_DF.shape[0]
        #print(lengthOfFilteredDatabase)
        chatVerlauf_UserInteraction=[{
        "role": "system",
           "content": f"You are a polite and helpful assistant who should help the user find the right shoesv out of a database." 
                      f" For your first Messager you have none of the following Informations."  "You get a JSON file {JSON_Data} with the following variables Color, Shoe Type, Gender, Season and Material."
                      f" These are filters with which you want to help the user to find the right shoe for the customer." 
                      f" If a variable could not yet be recognized from the User_Input, there is a '' in the JSON file." 
                      f" If this is the case, explicitly ask the user again for the filter." 
                      f" You should mention the current amount of the filtered shoes matching to the User Input, given with this variable {lengthOfFilteredDatabase}." 
                      f" Mention {lengthOfFilteredDatabase} in the Answer. If {lengthOfFilteredDatabase} is greater than 10 then ask again for more information." 
                      f" But if {lengthOfFilteredDatabase} <= then give a description of the 10 filtered shoes."
                      f" I will give you a pandas dataframe { filtered_DF} with which you can find the necessary information about the filtered shoes and describe those as deatiled as you can with the given Information to the User. "
                      f"Please describe the shoes in a continuous text and not in embroidery dots. "
        }]
        chatVerlauf_UserInteraction.append({"role": "user", "content": user_input}),
        chat_User = client.chat.completions.create(
         model="gpt-4-1106-preview",
         messages=chatVerlauf_UserInteraction
        )
        antwort_Message = chat_User.choices[0].message.content
        chatVerlauf_UserInteraction.append({"role": "assistant", "content": antwort_Message}),
        print(antwort_Message)

















