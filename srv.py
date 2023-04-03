# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, flash, Markup, redirect, url_for
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import DataRequired, Length, Regexp
from wtforms.fields import *
from flask_bootstrap import Bootstrap5, SwitchField
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import requests
import csv



app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = '123456790'

activities = dict()
with open('int_courts_naf_rev_2.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        print(row)
        activities[row['Code']] = row['Intitules']
        
    

class Form(FlaskForm):
    denomination = StringField('Denomination de la société', validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField()

def callApi(societe_name):
    url = "https://recherche-entreprises.api.gouv.fr/search?q="+societe_name

    payload={}
    headers = {
    'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()


@app.route("/", methods=['GET', 'POST'])
def mapview():
    # creating a map in the view
    form_societe = Form()
    m = folium.Map(
        width=800,
        height=600,location=[48.85661, 2.35222],zoom_start=5)
    marker_cluster = MarkerCluster().add_to(m)


    folium.Marker(
        location=[48.85661, 2.35222],
        popup="Paris",
        icon=folium.Icon(color="green", icon="ok-sign"),
    ).add_to(marker_cluster)
    
    
   

    #Display the map
    if form_societe.validate_on_submit():
        flash('Form validated!')
        data = form_societe.denomination.data
        response = callApi(data)
        for r in response["results"]:
            if r["siege"]["coordonnees"] is not None:
                print(r["nom_complet"])
            
                latitude  = (r["siege"]["coordonnees"]).split(",")[0]
                longitude = (r["siege"]["coordonnees"]).split(",")[1]
                
                    
                popup = r["nom_raison_sociale"]+"<br/>Adresse : "+r["siege"]["geo_adresse"]+"<br/>Code activité : "+r["activite_principale"] +"<br/> Intitules de l'activités : "+activities[r["activite_principale"]]
                folium.Marker(
                    location=[latitude, longitude],
                    popup=popup,
                    icon=folium.Icon(color="blue", icon="ok-sign"),
                ).add_to(marker_cluster)
        m.get_root().render()
        header = m.get_root().header.render()
        body_html = m.get_root().html.render()
        script = m.get_root().script.render()
        #Define coordinates of where we want to center our map
        return render_template('exemple.html',form = form_societe,header=header, body_html=body_html,script=script)
        
    m.get_root().render()
    header = m.get_root().header.render()
    body_html = m.get_root().html.render()
    script = m.get_root().script.render()
    return render_template('exemple.html',form = form_societe, header=header, body_html=body_html, script=script)

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host="0.0.0.0", port=5080)