# Sondevoeding rekenhulp

Sondevoeding rekenhulp is een web-based tool voor de diëtist. De diëtist vult een aantal waarden van de patiënt in. Aan de hand hiervan produceert de tool een rapport met informatie over de behoeftes van de patiënt. De diëtist kan zelf de te gebruiken sondevoeding kiezen. Sondevoedingen kunnen daarnaast toegevoegd, bewerkt of verwijderd worden door de gebruiker. 

## Eisen

De web-based tool is gemaakt en getest op een Windows systeem. 
 - Beeldscherm resolutie: 1366 x 768
 - Schaal: 100%

 Sondevoeding rekenhulp maakt gebruik van de tool fpdf. 

## Installatie
De tool fpdf wordt via de terminal geïnstalleerd met de volgende commando:
```bash
python -m pip install fpdf
```

## Opstarten
Het opstarten van de applicatie kan via pythonanywhere en via anaconda.

### pythonanywhere
Navigeer naar de URL: https://rekenhulp.pythonanywhere.com/

### anaconda
Open een termminal. Navigeer naar het project. Voer de volgende commandos uit in de terminal: 
```bash
cd rekenhulp 
python manage.py runserver
```

Navigeer naar de URL: http://localhost:8000/.  

## Rapport
Sondevoeding rekenhulp kan drie rapporten produceren:
 - rapport_['geboortedatum']_['naam'].pdf --> Sondevoeding rekenhulp rapport
 - voorschrift-portie_['geboortedatum']_['naam'].pdf --> Sondevoedingvoorschrift porties
 - voorschrift-pomp_['geboortedatum']_['naam'].pdf --> Sondevoedingvoorschrift pomp

In de blokhaken [] staan de gegevens van de patiënt. 

## Auteurs
 - Annika Wilbrink (s1121325@student.hsleiden.nl)
 - Eveline Verschuren (s1103140@student.hsleiden.nl) 
 - Noa van Daatselaar (s1117684@student.hsleiden.nl) 
 - Selena Impink (s1119674@student.hsleiden.nl) 

