#include <ESP8266WiFi.h> //Wifi
#include <PubSubClient.h> //Mqtt 
#include <Adafruit_BME280.h> // BME 280 (temp, humi etc)
#include <pitches.h>

/*===================================INIT DES VARIABLES===================================*/

const char* ssid = "AndroidAP96EF"; //SSID du telephone servant d'AP
const char* password = "azerty123"; //MDP du telephone servant d'AP
const char* mqtt_server = "wewenito.ddns.net"; //Adresse du serv MQTT (Rpi 400 maison)

int statut_bouton = 0; //Utilisé pour le statut du bouton (pressé ou non)
int statut_boitier = 0; //Utilisé pour le statut du boitier (0 = courant non actif / 1 = courant actif)

int button=15; //Pin associee au bouton du boitier

int led_courant_on=2;

int led_courant_off=0;

int interrupt_pin = 12;

boolean detect_interrupt = false;



int loop_number=0; // variable utilise pour determiner quand envoyer des donnees meteo

bool incendie_en_cour = false;// variable utilisee en cas de detection d'incendie

volatile bool message_redondant = false; // variable utilisee pour eviter les redondances d'un envoi mqtt depuis la carte HUZZAH


void reaction_incendie(){
    incendie_en_cour = true;

    digitalWrite(led_courant_on, LOW);
    digitalWrite(led_courant_off, HIGH);
    
    Serial.println("FIRE FIRE FIRE FIRE FIRE FIRE FIRE FIRE FIRE FIRE FIRE");
}


WiFiClient espClient;//creation instance client wifi
PubSubClient client(espClient); //creation instance client MQTT

void setup_wifi() { //mise en place du service WIFI
  //Serial.println("Starting-up Wifi");

  delay(10);

  //Serial.println();
  //Serial.print("Connection à l'AP ");
  //Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);//demarrage du wifi avec les crédentiels déclarés plus haut

  while (WiFi.status() != WL_CONNECTED) {//tant que l'ESP n'est pas connecté à l'AP, on continue de réessayer
    delay(500);
    Serial.print(".");
    
  }

  randomSeed(micros());
  //une fois la conecction établie, on affiche les infos réseau obtenues :
  //Serial.println("");
  //Serial.println("WiFi connected");
  //Serial.println("IP address: ");
  //Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {//gestion recup des messages MQTT
  if (!incendie_en_cour){
     if (!message_redondant) {//uniquement si le message ne vient pas directement du bouton de la prise
        Serial.println("reception code MQTT");
        for (int i = 0; i < length; i++) { //imprime l'entièreté du message lettre par lettre
          Serial.println((char)payload[i]);
          set_changement_statut_mqtt((char)payload[i]);
      }
      Serial.println();
    
      delay(500);
 
    }else{
      Serial.println("message non pris en compte car envoyé par le controlleur");
      message_redondant = false;
    }
  }else{
    Serial.println("Un incendie est potentiellement en cour, merci de verifier la prise !");
  }
}

void reconnect() { //Mise en place du service MQTT
  // Loop en attendant d'être reco
  while (!client.connected()) {
    Serial.println("Connection au brocker MQTT (HomePi)");
    
    // Generation code client unique
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    
    // Tentative de connection
    if (client.connect(clientId.c_str())) {
      Serial.println("Connection au broker établie !");
      // Une fois connecté, envoie du statut de base de prise (0) associe a la variable 'statut'
      client.publish("SAE301/PRISE2", "0");
      // Puis connection au topic pour recevoir les messages
      client.subscribe("SAE301/PRISE2");
    } else {

      Serial.print("erreur, raison : ");
      Serial.print(client.state());
      Serial.println("Nouvel essai dans 5 secondes...");

      delay(5000);
    }
  }
}

void set_changement_statut_bouton(){
  if (!incendie_en_cour){
      if (statut_boitier == 0){
      statut_boitier = 1;

      digitalWrite(led_courant_on, HIGH);
      digitalWrite(led_courant_off, LOW);

      message_redondant = true;
      client.publish("SAE301/PRISE2", "1");
    }else{
      statut_boitier = 0;

      digitalWrite(led_courant_on, LOW);
      digitalWrite(led_courant_off, HIGH);

      message_redondant = true;
      client.publish("SAE301/PRISE2", "0");
    }
  }else{
    incendie_en_cour = false;

  }
}

void set_changement_statut_mqtt(char valeur){
  if (valeur == '1'){
    Serial.println("Passage boitier ON");
    statut_boitier = 1;

    digitalWrite(led_courant_on, HIGH);
    digitalWrite(led_courant_off, LOW);
    
  }else if (valeur == '0'){
    Serial.println("Passage boitier OFF");
    statut_boitier = '0';

    digitalWrite(led_courant_on, LOW);
    digitalWrite(led_courant_off, HIGH);
    
  }else if (valeur == 'S'){
    if (statut_boitier == 1){
      client.publish("SAE301/PRISE2/STATUT", "1");
    }else{
      client.publish("SAE301/PRISE2/STATUT", "0");
    }
  }else{
    Serial.println("valeur troll recue");
  }
}


ICACHE_RAM_ATTR void start_interrupt() {
  Serial.println("START INTERRUPT");
  digitalWrite(led_courant_on, HIGH);
  digitalWrite(led_courant_off, HIGH);
  detect_interrupt = true;
}



void setup() {

  pinMode(led_courant_off,OUTPUT);
  pinMode(led_courant_on, OUTPUT);

  pinMode(interrupt_pin, INPUT);
 
  pinMode(button, INPUT);
  
  Serial.begin(9600);

  setup_wifi();
  
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  
  attachInterrupt(digitalPinToInterrupt(interrupt_pin), start_interrupt, CHANGE);

  digitalWrite(led_courant_off, HIGH);
  digitalWrite(led_courant_on, LOW);
}




void loop() {

  if(detect_interrupt){
    Serial.println("Sending temp due to interrupt");
    client.publish("SAE301/PRISE2/TEMP", "19.34");
    delay(500);
    if(statut_boitier == 1){
      digitalWrite(led_courant_off, LOW);
    }else{
      digitalWrite(led_courant_on, LOW);
    }
    Serial.println("Temp sent !");
    detect_interrupt = false;
  }
  
  if (!incendie_en_cour){

    statut_bouton = digitalRead(button);
  
    if (statut_bouton == HIGH) {
      Serial.println("Bouton pressé");
      set_changement_statut_bouton();
      delay(1000);
    }else{
      Serial.println(".");
    }
    
    if (WiFi.status() != WL_CONNECTED){
      setup_wifi();
    }

    if (!client.connected()) {// si client n'est plus connecté

      reconnect(); // on retente de connecter jusqu'a recuperation du brocker
    }
    
    client.loop();
  
    delay(10);

    
  }else{
      statut_bouton = digitalRead(button);
      if (statut_bouton == HIGH) {
        Serial.println("Bouton pressé, arret alerte feu");
        set_changement_statut_bouton();

        delay(1000);
      }else{
        Serial.println("POTENTIEL INCENDIE EN COUR");

        delay(10);
      }
  }
}
