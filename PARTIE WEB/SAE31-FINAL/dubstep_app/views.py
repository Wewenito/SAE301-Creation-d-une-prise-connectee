from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import PlageshorairesForm
from . import models
from django.views import View
from dubstep_app.models import Donnees
from django.contrib import messages
import random
import paho.mqtt.client as mqtt
from paho.mqtt import client as mqtt_client
import time
import os, platform, mysql.connector
from .models import Temp, Donnees, Humitide, Pression, Plageshoraires
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Create your views here.

@login_required(login_url='/login_user')
def index(request):
    Donnees = models.Donnees.objects.all()
    return render(request, 'dubstep_app/index.html', {'Donnees_charge': Donnees})


#+===========================================================================================================+
#|                                           PLAGES HORAIRES                                                 |
#+===========================================================================================================+

@login_required(login_url='/login_user')
def plages(request):
    if request.method == "POST":
        form = PlageshorairesForm(request)
        if form.is_valid(): 
            pt = form.save() 
            return render(request,"dubstep_app/plages.html",{"pt" : pt}) 
        else:
            form = PlageshorairesForm() 
            plageshoraires = Plageshoraires.objects.filter(topicname='PRISE1').order_by('-id')
            plageshoraires2 = Plageshoraires.objects.filter(topicname='PRISE2').order_by('-id')
            plageshoraires3 = Plageshoraires.objects.filter(topicname='PRISE3').order_by('-id')

            form = form
            data1 = plageshoraires
            data2 = plageshoraires2
            data3 = plageshoraires3

            context = {
            "form": form,
            "data1": data1,
            "data2": data2,
            "data3": data3,
            }

            return render(request,"dubstep_app/plages.html", context)
    else :
        form = PlageshorairesForm() 
        plageshoraires = Plageshoraires.objects.filter(topicname='PRISE1').order_by('-id')
        plageshoraires2 = Plageshoraires.objects.filter(topicname='PRISE2').order_by('-id')
        plageshoraires3 = Plageshoraires.objects.filter(topicname='PRISE3').order_by('-id')


        form = form
        data1 = plageshoraires
        data2 = plageshoraires2
        data3 = plageshoraires3

        context = {
        "form": form,
        "data1": data1,
        "data2": data2,
        "data3": data3,
        }

        return render(request,"dubstep_app/plages.html", context)



@login_required(login_url='/login_user')
def traitement(request):
    lform = PlageshorairesForm(request.POST)
    if lform.is_valid():
        try :
            pt = lform.save()
            return HttpResponseRedirect("/plages") 
        except IntegrityError:
            messages.error(request, 'Erreur d\'accès à la base de données : {}'.format(str('La plage horaire existe déjà.')))
            return HttpResponseRedirect("/plages")
        
    elif ValidationError: #si la date est dépassée
        messages.info(request, 'La date est passée !')
        return HttpResponseRedirect("/plages")
    else:
        return render(request,"dubstep_app/plages.html",{"form": lform})

@user_passes_test(lambda user: user.is_superuser, login_url='/login_user')
def delete(request, id):
    plages = models.Plageshoraires.objects.get(id=id)
    plages.delete()
    return HttpResponseRedirect('/plages')

#+===========================================================================================================+
#|                                           SYSTÈME DE LOG IN                                               |
#+===========================================================================================================+

def login_user(request):
    if request.user.is_authenticated:
        return redirect('/mainpage')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None:
                # check if user is "admin"
                if user.is_superuser:
                    auth.login(request, user)
                    return redirect('/mainpage')
                
                else:
                    auth.login(request, user)
                    return redirect('/mainpage')
            else:
                messages.info(request, 'Invalid Username or Password')
                return redirect(login_user)
        
        else:
            return render(request, 'dubstep_app/login.html')

def logout_user(request):
    auth.logout(request)
    return redirect(login_user)


#+===========================================================================================================+
#|                                   CONNEXION ET PUBLISH BROKER PRIVÉ                                       |
#+===========================================================================================================+


broker = 'wewenito.ddns.net'
port = 1883
topic = "SAE301/PRISE1"
topic2 = "SAE301/PRISE2"
topic3 = "SAE301/PRISE3"
client_id = f'publish-{random.randint(0, 1000)}'


class Mqtt(View):
    template_name = 'dubstep_app/mainpage.html'

    @staticmethod
    def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    @staticmethod
    def publish(client, msg):
        result = client.publish(topic, msg)
        status = result.rc
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    @staticmethod
    def publish2(client, msg):
        result = client.publish(topic2, msg)
        status = result.rc
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    @staticmethod
    def publish3(client, msg):
        result = client.publish(topic3, msg)
        status = result.rc
        if status == 0:
            print(f"Send `{msg}` to topic `{topic3}`")
        else:
            print(f"Failed to send message to topic {topic3}")
    

    def get(self, request):
        temp = Temp.objects.filter(topicname='PRISE1/TEMP').order_by('-id')[0]
        donnees = Donnees.objects.filter(topicname='PRISE1').order_by('-id')[0]
        pression = Pression.objects.filter(topicname='PRISE1/PRESSION').order_by('-id')[0]
        humidite = Humitide.objects.filter(topicname='PRISE1/HUMIDITE').order_by('-id')[0]
        data = zip([temp], [donnees], [pression], [humidite])

        temp2 = Temp.objects.filter(topicname='PRISE2/TEMP').order_by('-id')[0]
        donnees2 = Donnees.objects.filter(topicname='PRISE2').order_by('-id')[0]
        pression2 = Pression.objects.filter(topicname='PRISE2/PRESSION').order_by('-id')[0]
        humidite2 = Humitide.objects.filter(topicname='PRISE2/HUMIDITE').order_by('-id')[0]
        data2 = zip([temp2], [donnees2], [pression2], [humidite2])

        temp3 = Temp.objects.filter(topicname='PRISE3/TEMP').order_by('-id')[0]
        donnees3 = Donnees.objects.filter(topicname='PRISE3').order_by('-id')[0]
        pression3 = Pression.objects.filter(topicname='PRISE3/PRESSION').order_by('-id')[0]
        humidite3 = Humitide.objects.filter(topicname='PRISE3/HUMIDITE').order_by('-id')[0]
        data3 = zip([temp3], [donnees3], [pression3], [humidite3])

        context = {
        "data": data,
        "data2": data2,
        "data3": data3,
        }

        return render(request, self.template_name, context)
    

    def post(self, request):
        action = request.POST.get('action')
        client = self.connect_mqtt()
        client.loop_start()

        if action == "ON":
            self.publish(client, 1)
        elif action == "OFF":
            self.publish(client, 0)

        elif action == "ON2":
            self.publish2(client, 1)
        elif action == "OFF2":
            self.publish2(client, 0)
        
        elif action == "ON3":
            self.publish3(client, 1)
        elif action == "OFF3":
            self.publish3(client, 0)

        elif action == "TOUTON":
            self.publish(client, 1)
            self.publish2(client, 1)
            self.publish3(client, 1)
        
        elif action == "TOUTOFF":
            self.publish(client, 0)
            self.publish2(client, 0)
            self.publish3(client, 0)
        
        client.loop_stop()

        a = 1
        if a == 1:
            time.sleep(0.5)
            return HttpResponseRedirect("/mainpage")

        temp = Temp.objects.filter(topicname='PRISE1/TEMP').order_by('-id')[0]
        donnees = Donnees.objects.filter(topicname='PRISE1').order_by('-id')[0]
        pression = Pression.objects.filter(topicname='PRISE1/PRESSION').order_by('-id')[0]
        humidite = Humitide.objects.filter(topicname='PRISE1/HUMIDITE').order_by('-id')[0]
        data = zip([temp], [donnees], [pression], [humidite])

        temp2 = Temp.objects.filter(topicname='PRISE2/TEMP').order_by('-id')[0]
        donnees2 = Donnees.objects.filter(topicname='PRISE2').order_by('-id')[0]
        pression2 = Pression.objects.filter(topicname='PRISE2/PRESSION').order_by('-id')[0]
        humidite2 = Humitide.objects.filter(topicname='PRISE2/HUMIDITE').order_by('-id')[0]
        data2 = zip([temp2], [donnees2], [pression2], [humidite2])

        temp3 = Temp.objects.filter(topicname='PRISE3/TEMP').order_by('-id')[0]
        donnees3 = Donnees.objects.filter(topicname='PRISE3').order_by('-id')[0]
        pression3 = Pression.objects.filter(topicname='PRISE3/PRESSION').order_by('-id')[0]
        humidite3 = Humitide.objects.filter(topicname='PRISE3/HUMIDITE').order_by('-id')[0]
        data3 = zip([temp3], [donnees3], [pression3], [humidite3])

        context = {
        "data": data,
        "data2": data2,
        "data3": data3,
        }
        

        return render(request, self.template_name, context)


class Jukebox(View):
    template_name = 'dubstep_app/jukebox.html'

    @staticmethod
    def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    @staticmethod
    def publish(client, msg):
        result = client.publish(topic, msg)
        status = result.rc
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    def get(self, request):

        return render(request, self.template_name)

    def post(self, request):
        action = request.POST.get('action')
        client = self.connect_mqtt()
        client.loop_start()

        if action == "N":
            self.publish(client, 'N')
        elif action == "T":
            self.publish(client, 'T')
        

        client.loop_stop()
        
        time.sleep(0.5)
        return render(request, self.template_name)




#+===========================================================================================================+
#|                                           AFFICHAGE DE GRAPHIQUE                                          |
#+===========================================================================================================+

@login_required(login_url='/login_user')
def graphique(request):
    temp = Temp.objects.filter(topicname='PRISE1/TEMP').order_by('-id').values('date', 'temp')
    temp2 = Temp.objects.filter(topicname='PRISE2/TEMP').order_by('-id').values('date', 'temp')
    temp3 = Temp.objects.filter(topicname='PRISE3/TEMP').order_by('-id').values('date', 'temp')
    
    stepcount = []
    stepcount2 = []
    stepcount3 = []
    
    
    for donnee in reversed(temp):
        stepcount.append({
            'y': donnee['temp'],
            'label': donnee['date']
        })
    
    for donnee in reversed(temp2):
        stepcount2.append({
            'y': donnee['temp'],
            'label': donnee['date']
        })

    for donnee in reversed(temp3):
        stepcount3.append({
            'y': donnee['temp'],
            'label': donnee['date']
        })
    

    return render(request, 'dubstep_app/graphique.html',  {"stepcount": stepcount, "stepcount2" : stepcount2, "stepcount3" : stepcount3})




    

    

    

            