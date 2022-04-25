import pandas as pd
import numpy as np
from flask import Flask,render_template, request, redirect, make_response, jsonify, json #for web page
import os, json

#for web page
app = Flask(__name__) #creates a new website in a variable called app

Flora_data = pd.read_excel('Flora_data.xlsx', sheet_name='Data')
Flora_data.fillna('', inplace=True) #replave nan by blank string

Flora_data = Flora_data.sort_values(['Family', 'Botanical_name'], ascending=[True, True])

Dictionary = pd.read_excel('Flora_data.xlsx', sheet_name='Dictionary')
photo_gallery = pd.read_excel('Flora_data.xlsx', sheet_name='Gallery')
image_data = pd.read_excel('Flora_data.xlsx', sheet_name='Image_data')
image_data['Photo_DateTime'] = image_data['Photo_DateTime'].dt.strftime('%d-%b-%Y %H:%M %p')

attribute_list = ['Title','Bark','Leaf','Inflorescence','Flower','Floralparts','Fruit','Seed']

#used in HomePage.html
all_image_title = image_data[image_data['File_Name'].str.contains('Title')][['File_Name','Botanical_name']]
all_species = Flora_data[['Botanical_name', 'Family', 'Common_name']]
all_species_title = all_species.merge(all_image_title, how='left')
all_speciesj = json.loads(all_species_title.to_json(orient ='records')) 

@app.route("/", methods=['GET', 'POST']) #decorator - Flask uses route() to say that if the browser requests the address / (the default, or home address), then our app should route that request to this index function.
@app.route("/flora", methods=['GET', 'POST'])
def index():
    return render_template("HomePage.html", all_speciesj = all_speciesj, os=os)
                                   
@app.route('/species/<botanical_name>', methods = ['GET'])
def search(botanical_name):
    flora_to_display = Flora_data.loc[(Flora_data['Botanical_name']==botanical_name)]
    json_flora = json.loads(flora_to_display.to_json(orient ='records')) # to_json: output looks like a json object, single quotes will wrap at beginning and end. hence needed additional transformation using json.loads
    
    #new code start
    count = 0
    species_images =  image_data.loc[(image_data['Botanical_name']==json_flora[count]['Botanical_name'])]
    for attr in attribute_list:
        image = species_images[species_images['Attribute'].str.contains(attr)]
        image_j = json.loads(image.to_json(orient ='records'))
        
        attr_c = attr + '_i'
        json_flora[count][attr_c]= image_j    
          
    return render_template("SelectSpecies_horizontal.html", flora_on_webpagej = json_flora[0], os=os)

@app.route('/compare_flora', methods = ['GET', 'POST'])
def compare():
    flora_to_display1 = pd.DataFrame()
    json_flora_comp = []
    if request.values.get('botanical_name1', None) is not None: #request.values.get - works for both GET & POST
        name1 = request.values.get('botanical_name1', None) 
        name2 = request.values.get('botanical_name2', None) 
        print(name1, name2)
        flora_to_display1 = Flora_data.loc[Flora_data['Botanical_name'] == name1]
        flora_to_display2 = Flora_data.loc[Flora_data['Botanical_name'] == name2]
        flora_to_display1 = flora_to_display1.append(flora_to_display2) # to maintain sequenec of search words on compare screen
        json_flora_comp = json.loads(flora_to_display1.to_json(orient ='records'))
        
        count = 0
        while count < len(json_flora_comp): #ability to compare more than 2 flora
            species_images =  image_data.loc[(image_data['Botanical_name']==json_flora_comp[count]['Botanical_name'])]
            for attr in attribute_list:
                image = species_images[species_images['Attribute'].str.contains(attr)]
                image_j = json.loads(image.to_json(orient ='records'))
                
                attr_c = attr + '_i'
                json_flora_comp[count][attr_c]= image_j
            count = count +1    

    return render_template("compare_flora_horizontal.html", flora_on_webpagej = json_flora_comp, os=os)

@app.route('/search_flora', methods = ['GET','POST'])
def search_flora():
    json_flora_search = []
    to_search = None
    print('Search Value', request.values)
    #if request.method == 'GET' and request:
    if request.values.get('search_word', None) is not None:# will return the value of 'search_word' in the dict if its set, otherwise it returns None
        to_search = request.values.get('search_word', None)
        mask = Flora_data.apply(lambda row: row.astype(str).str.contains(r'{}'.format(to_search), case=False).any(), axis=1)
        flora_to_display = Flora_data[np.array(mask,dtype=bool)]
        
        flora_search = flora_to_display[['Botanical_name', 'Family', 'Common_name']]
        json_flora_search = json.loads(flora_search.to_json(orient ='records')) 
        count = 0
        while count < len(json_flora_search):
            species_images =  image_data.loc[(image_data['Botanical_name']==json_flora_search[count]['Botanical_name'])]
            
            species_images_df = species_images[['File_Name','Botanical_name','Attribute']]
            for attr in attribute_list:
                image = species_images_df[species_images_df['Attribute'].str.contains(attr)].head(1)
                attr_c = attr + '_i'
                if not image.empty:
                    json_flora_search[count][attr_c]= image['File_Name'].iat[0]
                else:
                    json_flora_search[count][attr_c]= ''
            count = count +1
    
    return render_template("search_flora.html", search_species_j = json_flora_search, os=os, search_word=to_search)

""" static compare photos to be used in "why this website article"
@app.route("/photo_gallery", methods=['GET', 'POST'])
def gallery():
    
    return render_template("photo_gallery.html", photo_gallery = photo_gallery)
"""

@app.route('/openmic', methods = ['GET','POST'])
def openmic():

    return render_template("open_mic.html")

""" reference links are covered in OpenMic
@app.route('/reference_links', methods = ['GET','POST'])
def about():

    return render_template("reference_links.html")
"""
@app.route("/fetchdata",methods=["POST","GET"])
def fetchdata():
    meaning = pd.DataFrame()
    photo = pd.DataFrame()
    if request.method == 'POST':
        id = request.form['id']
        #print(id)
        rs = Dictionary.loc[Dictionary['BOTANICAL TERMS'] == id] 
        if not rs.empty:
            meaning = rs['Meaning'].iat[0]
            if not rs['Sketch Name'].isnull().values.any():
                photo = rs['Sketch Name'].iat[0]
            else:
                photo = 'Default_sketch.jpg'
        else:
            meaning = 'Add term to the Directory'
            photo = 'Default_sketch.jpg'
        #print(meaning)
        return jsonify({'htmlresponse': render_template('response.html', meaning=meaning, photo=photo)})
    else:
        return jsonify({'htmlresponse': render_template('response.html', meaning=meaning, photo=photo)})

@app.route("/searchlist",methods=["GET"])
def searchlist():
    
        return Flora_data['Botanical_name'].sort_values(ascending=True).to_json(orient = 'records')
               
if __name__ == "__main__": #if this script is run directly then start the application
    app.run()

"""
Steps to run flask from Terminal
> $env:FLASK_APP = "species_visualization.py"
> flask run
"""

#compare website codes - to try
#https://codyhouse.co/gem/products-comparison-table

#jquey ajex call for tooltip
#https://tutorial101.blogspot.com/2021/02/displaying-popups-data-on-mouse-hover.html

#Ajex call for dynamic Image caption
#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiv-ajax


#Hosting Python-Flask website on Azure
# https://medium.com/@nikovrdoljak/deploy-your-flask-app-on-azure-in-3-easy-steps-b2fe388a589e
# https://docs.microsoft.com/en-in/azure/app-service/quickstart-python?tabs=bash&pivots=python-framework-flask
# https://medium.com/geekculture/create-basic-web-application-%EF%B8%8F-and-deployment-using-python-eb027e57c5ee

#Autocomplete code	
#https://api.jqueryui.com/autocomplete/
	
#Jinja check if file exists	
#https://stackoverflow.com/questions/66867667/how-to-check-file-exist-in-system-or-not-using-jinja-in-html-page

#for with if condition	
#https://stackoverflow.com/questions/12655155/jinja2-for-loop-with-conditions
#https://stackoverflow.com/questions/48002297/how-to-concatenate-int-with-str-type-in-jinja2-template/48002358#48002358

#Variable assignment in Jinja	
#https://stackoverflow.com/questions/9486393/jinja2-change-the-value-of-a-variable-inside-a-loop