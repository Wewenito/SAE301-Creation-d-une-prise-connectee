#include <ESP8266WiFi.h> //Wifi
#include <PubSubClient.h> //Mqtt 
#include <Adafruit_BME280.h> // BME 280 (temp, humi etc)
#include <pitches.h>

/*===================================INIT DES VARIABLES===================================*/

//variables en rapport avec le module BME280
#define adresseI2CduBME280 0x76 //addresse i2c trouvee via script i2c_finder.ino

Adafruit_BME280 bme; //creation instance BME

const char* ssid = "AndroidAP96EF"; //SSID du telephone servant d'AP
const char* password = "azerty123"; //MDP du telephone servant d'AP
const char* mqtt_server = "wewenito.ddns.net"; //Adresse du serv MQTT (Rpi 400 maison)

int statut_bouton = 0; //Utilisé pour le statut du bouton (pressé ou non)
int statut_boitier = 0; //Utilisé pour le statut du boitier (0 = courant non actif / 1 = courant actif)

int button=15; //Pin associee au bouton du boitier

int buzzer=16; //Pin associee au buzzer pour l'alerte feu

int led_courant_on=2;

int led_courant_off=0;

int red_RGB_pin=14, green_RGB_pin=12, blue_RGB_pin=13; //Pins associees a la LED RGB pour les statuts du boitier

int loop_number=0; // variable utilise pour determiner quand envoyer des donnees meteo

bool incendie_en_cour = false;// variable utilisee en cas de detection d'incendie

volatile bool message_redondant = false; // variable utilisee pour eviter les redondances d'un envoi mqtt depuis la carte HUZZAH

float getTemp(){
  return bme.readTemperature();
}

float getHumi(){
  return bme.readHumidity();
}

float getPr(){
  return bme.readPressure() / 100.0F;
}

int melody_mario[] = {
  NOTE_E5, NOTE_E5, REST, NOTE_E5, REST, NOTE_C5, NOTE_E5,
  NOTE_G5, REST, NOTE_G4, REST, 
  NOTE_C5, NOTE_G4, REST, NOTE_E4,
  NOTE_A4, NOTE_B4, NOTE_AS4, NOTE_A4,
  NOTE_G4, NOTE_E5, NOTE_G5, NOTE_A5, NOTE_F5, NOTE_G5,
  REST, NOTE_E5,NOTE_C5, NOTE_D5, NOTE_B4,
  NOTE_C5, NOTE_G4, REST, NOTE_E4,
  NOTE_A4, NOTE_B4, NOTE_AS4, NOTE_A4,
  NOTE_G4, NOTE_E5, NOTE_G5, NOTE_A5, NOTE_F5, NOTE_G5,
  REST, NOTE_E5,NOTE_C5, NOTE_D5, NOTE_B4,
  
  REST, NOTE_G5, NOTE_FS5, NOTE_F5, NOTE_DS5, NOTE_E5,
  REST, NOTE_GS4, NOTE_A4, NOTE_C4, REST, NOTE_A4, NOTE_C5, NOTE_D5,
  REST, NOTE_DS5, REST, NOTE_D5,
  NOTE_C5, REST,
  
  REST, NOTE_G5, NOTE_FS5, NOTE_F5, NOTE_DS5, NOTE_E5,
  REST, NOTE_GS4, NOTE_A4, NOTE_C4, REST, NOTE_A4, NOTE_C5, NOTE_D5,
  REST, NOTE_DS5, REST, NOTE_D5,
  NOTE_C5, REST,
  
  // Game over sound
  NOTE_C5, NOTE_G4, NOTE_E4,
  NOTE_A4, NOTE_B4, NOTE_A4, NOTE_GS4, NOTE_AS4, NOTE_GS4,
  NOTE_G4, NOTE_D4, NOTE_E4
};

int durations_mario[] = {
  8, 8, 8, 8, 8, 8, 8,
  4, 4, 8, 4, 
  4, 8, 4, 4,
  4, 4, 8, 4,
  8, 8, 8, 4, 8, 8,
  8, 4,8, 8, 4,
  4, 8, 4, 4,
  4, 4, 8, 4,
  8, 8, 8, 4, 8, 8,
  8, 4,8, 8, 4,
  
  
  4, 8, 8, 8, 4, 8,
  8, 8, 8, 8, 8, 8, 8, 8,
  4, 4, 8, 4,
  2, 2,
  
  4, 8, 8, 8, 4, 8,
  8, 8, 8, 8, 8, 8, 8, 8,
  4, 4, 8, 4,
  2, 2,
  
  //game over sound
  4, 4, 4,
  8, 8, 8, 8, 8, 8,
  8, 8, 2
};

int melody_doom[] = {
   NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2, 
  NOTE_C3, NOTE_E2, NOTE_E2, NOTE_AS2, NOTE_E2, NOTE_E2, NOTE_B2, NOTE_C3,
  NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2,
  NOTE_C3, NOTE_E2, NOTE_E2, NOTE_AS2,
  
  NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2, 
  NOTE_C3, NOTE_E2, NOTE_E2, NOTE_AS2, NOTE_E2, NOTE_E2, NOTE_B2, NOTE_C3,
  NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2,
  NOTE_C3, NOTE_E2, NOTE_E2, NOTE_AS2,
  
  NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2, 
  NOTE_C3, NOTE_E2, NOTE_E2, NOTE_AS2, NOTE_E2, NOTE_E2, NOTE_B2, NOTE_C3,
  NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2,
  NOTE_C3, NOTE_E2, NOTE_E2, NOTE_AS2,
  
  NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2, 
  NOTE_C3, NOTE_E2, NOTE_E2, NOTE_AS2, NOTE_E2, NOTE_E2, NOTE_B2, NOTE_C3,
  NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2,
  NOTE_FS3, NOTE_D3, NOTE_B2, NOTE_A3, NOTE_FS3, NOTE_B2, NOTE_D3, NOTE_FS3, NOTE_A3, NOTE_FS3, NOTE_D3, NOTE_B2,
  
  NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2, 
  NOTE_C3, NOTE_E2, NOTE_E2, NOTE_AS2, NOTE_E2, NOTE_E2, NOTE_B2, NOTE_C3,
  NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2,
  NOTE_C3, NOTE_E2, NOTE_E2, NOTE_AS2,
  
  NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2, 
  NOTE_C3, NOTE_E2, NOTE_E2, NOTE_AS2, NOTE_E2, NOTE_E2, NOTE_B2, NOTE_C3,
  NOTE_E2, NOTE_E2, NOTE_E3, NOTE_E2, NOTE_E2, NOTE_D3, NOTE_E2, NOTE_E2,
  NOTE_B3, NOTE_G3, NOTE_E3, NOTE_G3, NOTE_B3, NOTE_E4, NOTE_G3, NOTE_B3, NOTE_E4, NOTE_B3, NOTE_G4, NOTE_B4
};

int durations_doom[] = {
  8, 8, 8, 8, 8, 8, 8, 8, 
  8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 2,
  
  8, 8, 8, 8, 8, 8, 8, 8, 
  8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 2,
  
  8, 8, 8, 8, 8, 8, 8, 8, 
  8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 2,
  
  8, 8, 8, 8, 8, 8, 8, 8, 
  8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8,
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16,
  
  8, 8, 8, 8, 8, 8, 8, 8, 
  8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 2,
  
  8, 8, 8, 8, 8, 8, 8, 8, 
  8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8,
  16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16
};

int melody_nokia[] = {
  NOTE_E5, NOTE_D5, NOTE_FS4, NOTE_GS4, 
  NOTE_CS5, NOTE_B4, NOTE_D4, NOTE_E4, 
  NOTE_B4, NOTE_A4, NOTE_CS4, NOTE_E4,
  NOTE_A4
};

int durations_nokia[] = {
  8, 8, 4, 4,
  8, 8, 4, 4,
  8, 8, 4, 4,
  2
};


int melody_tetris[] = {
  NOTE_E5, NOTE_B4, NOTE_C5, NOTE_D5, NOTE_C5, NOTE_B4,
  NOTE_A4, NOTE_A4, NOTE_C5, NOTE_E5, NOTE_D5, NOTE_C5,
  NOTE_B4, NOTE_C5, NOTE_D5, NOTE_E5,
  NOTE_C5, NOTE_A4, NOTE_A4, NOTE_A4, NOTE_B4, NOTE_C5,
  
  NOTE_D5, NOTE_F5, NOTE_A5, NOTE_G5, NOTE_F5,
  NOTE_E5, NOTE_C5, NOTE_E5, NOTE_D5, NOTE_C5,
  NOTE_B4, NOTE_B4, NOTE_C5, NOTE_D5, NOTE_E5,
  NOTE_C5, NOTE_A4, NOTE_A4, REST
};

int durations_tetris[] = {
  4, 8, 8, 4, 8, 8,
  4, 8, 8, 4, 8, 8,
  4, 8, 4, 4,
  4, 4, 8, 4, 8, 8,
  
  4, 8, 4, 8, 8,
  4, 8, 4, 8, 8,
  4, 8, 8, 4, 4,
  4, 4, 4, 4
};


void music_time_nokia(){
    int size = sizeof(durations_nokia) / sizeof(int);

    for (int note = 0; note < size; note++) {

      int duration = 1000 / durations_nokia[note];
      tone(buzzer, melody_nokia[note], duration);

      int pauseBetweenNotes = duration * 1.30;
      delay(pauseBetweenNotes);
      
      //stop the tone playing:
      noTone(buzzer);
    }
}

void music_time_tetris(){
    int size = sizeof(durations_tetris) / sizeof(int);

    for (int note = 0; note < size; note++) {

      int duration = 1000 / durations_tetris[note];
      tone(buzzer, melody_tetris[note], duration);

      int pauseBetweenNotes = duration * 1.30;
      delay(pauseBetweenNotes);
      
      //stop the tone playing:
      noTone(buzzer);
    }
}

void music_time_doom(){
  int size = sizeof(durations_doom) / sizeof(int);

  for (int note = 0; note < size; note++) {
    //to calculate the note duration, take one second divided by the note type.
    //e.g. quarter note = 1000 / 4, eighth note = 1000/8, etc.
    int duration = 1000 / durations_doom[note];
    tone(buzzer, melody_doom[note], duration);

    //to distinguish the notes, set a minimum time between them.
    //the note's duration + 30% seems to work well:
    int pauseBetweenNotes = duration * 1.30;
    delay(pauseBetweenNotes);
    
    //stop the tone playing:
    noTone(buzzer);
  }
}

void music_time_mario(){
    int size = sizeof(durations_mario) / sizeof(int);

    for (int note = 0; note < size; note++) {
    //to calculate the note duration, take one second divided by the note type.
    //e.g. quarter note = 1000 / 4, eighth note = 1000/8, etc.
    int duration = 1000 / durations_mario[note];
    tone(buzzer, melody_mario[note], duration);

    //to distinguish the notes, set a minimum time between them.
    //the note's duration + 30% seems to work well:
    int pauseBetweenNotes = duration * 1.30;
    delay(pauseBetweenNotes);
    
    //stop the tone playing:
    noTone(buzzer);
  }
}

void set_RGB(int red_value, int green_value, int blue_value){//Passer en params les trois valeur RGB, la led RGB affichera ensuite la couleur associee
   digitalWrite(red_RGB_pin, red_value);
   digitalWrite(green_RGB_pin, green_value);
   digitalWrite(blue_RGB_pin, blue_value);
}

void reaction_incendie(){
    incendie_en_cour = true;

    digitalWrite(led_courant_on, LOW);
    digitalWrite(led_courant_off, HIGH);
    
    Serial.println("FIRE FIRE FIRE FIRE FIRE FIRE FIRE FIRE FIRE FIRE FIRE");

    set_RGB(0,255,255);//rouge

    tone(buzzer, 500);
    delay(200);
    tone(buzzer, 600);
    delay(200);
    tone(buzzer, 500);
    delay(400);
    tone(buzzer, 600);
    delay(200);
    tone(buzzer, 500);
    delay(400);
    tone(buzzer, 600);
    delay(200);
    tone(buzzer, 500);
    delay(400);
    noTone(buzzer);

    
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
    set_RGB(0,255,0);//Rose (wifi not connected)
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
    
      set_RGB(0,0,0);//Blanc (reception message)
      
      delay(500);

      set_RGB(255,0,255);
      
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
      set_RGB(255,0,255); //vert (all good)
      // Une fois connecté, envoie du statut de base de prise (0) associe a la variable 'statut'
      client.publish("SAE301/PRISE1", "0");

      
      // Puis connection au topic pour recevoir les messages
      client.subscribe("SAE301/PRISE1");
    } else {
      set_RGB(255,255,0); //bleu (erreur MQTT)
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
      client.publish("SAE301/PRISE1", "1");
      client.publish("SAE301/PRISE1/STATUT", "1");
    }else{
      statut_boitier = 0;

      digitalWrite(led_courant_on, LOW);
      digitalWrite(led_courant_off, HIGH);

      message_redondant = true;
      client.publish("SAE301/PRISE1", "0");
      client.publish("SAE301/PRISE1/STATUT", "0");
    }
  }else{
    incendie_en_cour = false;
    set_RGB(255,0,255);
  }
}

void set_changement_statut_mqtt(char valeur){
  if (valeur == '1'){
    Serial.println("Passage boitier ON");
    statut_boitier = 1;

    digitalWrite(led_courant_on, HIGH);
    digitalWrite(led_courant_off, LOW);
    client.publish("SAE301/PRISE1/STATUT", "1");
    
  }else if (valeur == '0'){
    Serial.println("Passage boitier OFF");
    statut_boitier = '0';

    digitalWrite(led_courant_on, LOW);
    digitalWrite(led_courant_off, HIGH);
    client.publish("SAE301/PRISE1/STATUT", "0");
    
  }else if (valeur == 'H'){
    reaction_incendie();
  }else if (valeur == 'N'){
     music_time_nokia();
  }else if (valeur == 'T'){
    music_time_tetris();
  }else if(valeur == 'D'){
    music_time_doom();
  }else if(valeur == 'M'){
    music_time_mario();
  }else if (valeur == 'S'){
    if (statut_boitier == 1){
      client.publish("SAE301/PRISE1/STATUT", "1");
    }else{
      client.publish("SAE301/PRISE1/STATUT", "0");
    }
  }else{
    Serial.println("valeur troll recue");
  }
}




void setup() {
  bme.begin(adresseI2CduBME280);

  pinMode(buzzer, OUTPUT);
  
  pinMode(red_RGB_pin, OUTPUT);
  pinMode(green_RGB_pin, OUTPUT);
  pinMode(blue_RGB_pin, OUTPUT);

  pinMode(led_courant_off,OUTPUT);
  pinMode(led_courant_on, OUTPUT);
 
  pinMode(button, INPUT);
  
  Serial.begin(9600);

  setup_wifi();
  
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  
  set_RGB(255,0,255);//vert (all good)

  digitalWrite(led_courant_off, HIGH);
  digitalWrite(led_courant_on, LOW);
}



void loop() {

  if (loop_number > 1000){
    float temp = getTemp();
    float humi = getHumi();
    float pr = getPr();

    String tempstr = String(temp);
    String humistr = String(humi);
    String prstr = String(pr);
    
    client.publish("SAE301/PRISE1/TEMP", tempstr.c_str());
    client.publish("SAE301/PRISE1/HUMIDITE",humistr.c_str());
    client.publish("SAE301/PRISE1/PRESSION",prstr.c_str());
    
    loop_number = 0;
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
      set_RGB(0,255,0);
      setup_wifi();
    }

    if (!client.connected()) {// si client n'est plus connecté
      set_RGB(255,255,0);//bleu (erreur MQTT)
      reconnect(); // on retente de connecter jusqu'a recuperation du brocker
    }
    
    client.loop();
  
    delay(10);
    loop_number = loop_number + 1;

    
  }else{
      statut_bouton = digitalRead(button);
      if (statut_bouton == HIGH) {
        Serial.println("Bouton pressé, arret alerte feu");
        set_changement_statut_bouton();
        set_RGB(255,0,255);//vert (all good)
        delay(1000);
      }else{
        Serial.println("POTENTIEL INCENDIE EN COUR");
        set_RGB(0,255,255);
        delay(10);
      }
  }
}
