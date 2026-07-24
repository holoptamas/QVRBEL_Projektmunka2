# Valós idejű nyeréspredikció a League of Legends videojátékban

A projektem célja egy élő League of Legends, meccs kimenetelének folytonos predikciója. A rendszer a játék jelenlegi helyzetéről mutat adatokat és egy predikciót ad az egyik csapat győzelmi esélyeiről.

### Programnyelv/Keretrendszerek

A projektben főként Python-ban oldottam meg, a webes felületett Angular segítségével hoztam létre.

### Adatgyűjtés/Adatfeldolgozás/Analízis

Az adatok gyűjtését a RiotGamesAPI segítségével oldottam meg. Egy CSV fájlban tárolódnak a már lejátszott meccsek adatai, ezek a neurális hálónak a tanító mintái.

### Neurális háló

A neurális háló a PyTorch keretrendszert használja. Numerikus és Embedding kimeneteket is használ.

### Megjelenítés

Egy Flask szerver futtatja a neurális hálót, mely a LiveGameClientAPI-tól kapja meg a szükséges adatokat a becsléshez. Egyéb élő meccs adatok és a predikciót a szerver továbbítja a Frontend felé, amely megjeleníti a kölönböző  adatokat. 

# Real-time win prediction in the video game League of Legends

The goal of my project is to continuously predict the outcome of a live League of Legends match. The system displays data about the current state of the game and gives a prediction about the chances of one team winning.

### Programming Language/Frameworks

I mainly used Python for the project, and created the web interface using Angular.

### Data Collection/Data Processing/Analysis

I used RiotGamesAPI to collect data. The data of the matches already played is stored in a CSV file, these are the training samples of the neural network.

### Neural Network

The neural network uses the PyTorch framework. It uses both numerical and embedding outputs.

### Display

A Flask server runs the neural network, which receives the necessary data from the LiveGameClientAPI for prediction. Other live match data and the prediction are forwarded by the server to the Frontend, which displays the various data.
