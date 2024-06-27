'''
Titel: Rekenhulp Sondevoeding
Auteurs: Noa van Daatselaar (s1117684), Selena Impink (s1119647),
         Eveline Verschuren (s1103140), Annika Wilbrink (s1121325)
Datum: 29-6-2022
Versienummer: 1.0
Pythonversie: 3.8.3
Djangoversie: 4.0.2
'''
import shutil

from django import forms
from .models import Sondevoeding
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
import pandas as pd
from numpy import arange
from functools import reduce
from datetime import date
from fpdf import FPDF
import os
from pathlib import Path


invoer = {
    'naam': '',
    'geboortedatum': '',
    'leeftijd': 0,
    'geslacht': '',
    'aanhef':'',
    'lengte': 0,
    'gewicht': 0,
    'rustmetabolisme': '',
    'eiwit': 0,
    'toeslag': 0,
    'voeding': '',
    'start':0,
    'stop':0,
    'vocht': 0,
    'bijzonderheden': '',
    'vandaag': '',
}

uitrekenen = {
    'bmi': 0.0,
    'eiwitbehoefte': 0,
    'energiebehoefte': 0,
}

def pdfMaken(rapport_info, voorschrift_pomp, voorschrift_portie, advies,
             res_info, res_tabel, tijden_porties, vsp2):
    '''
    Deze functie maakt drie verschillende PDF's aan: een rapport,
    een voorschrift voor pompstand en een voorschrift voor
    handmatige porties.
    :param rapport_info: een string met de informatie van de
    rekenhulppagina die in het rapport moet komen te staan.
    :param voorschrift_pomp: een string met de informatie die in het
    voorschrift van de pompstand moet komen te staan.
    :param voorschrift_portie: een string met de informatie die in het
    voorschrift van de handmatige porties moet komen te staan.
    :param advies: een string met het advies over de sondevoeding die
    in beide voorschriften moet komen te staan.
    :param res_info: een string met de informatie van de
    resultatenpagina die in het rapport moet komen te staan.
    :param res_tabel: een lijst met alle berekende informatie van alle
    sondevoedingen die in de database staan.
    :param tijden_porties: een integer die aangeeft hoeveel handmatige
    porties er gegeven moet worden.
    :param vsp2: een string met de overige informatie die in het
    voorschrift van de handmatige porties moet komen te staan.
    :return: rapnaam = bevat de path naar het rapport.
    pompnaam = bevat de path naar het voorschrift van de pomp.
    portienaam = bevat de path naar het voorschrift van de portie.
    '''
    class PDF(FPDF):
        pdf_w = 210
        pdf_h = 297

        def titel(self, titel_tekst):
            self.set_xy(0.0, 0.0)
            self.set_font('Arial', 'B', 25)
            self.set_text_color(0, 0, 0)
            self.cell(w=210.0, h=40.0, align='C', txt=titel_tekst, border=0)

        def ondertitel(self, tekst, hoogte):
            self.set_xy(18.0, 18.0)
            self.set_font('Arial', 'u', 18)
            self.set_text_color(0, 0, 0)
            self.cell(w=210.0, h=hoogte, txt=tekst, border=0)

        def ondertitel2(self, tekst, hoogte):
            self.set_xy(0, 18.0)
            self.set_font('Arial', '', 14)
            self.set_text_color(0, 0, 0)
            self.cell(w=210.0, h=hoogte, align='C', txt=tekst, border=0)

        def datum(self):
            self.set_xy(150, 40.0)
            self.set_font('Arial', '', 12)
            self.cell(w=210.0, h=0, txt="Datum: "+str(
                invoer['vandaag']), border=0)

        def tekst(self, y, pdf_info):
            self.set_xy(18.0, y)
            self.set_text_color(0,0,0)
            self.set_font('Arial', '', 12)
            self.multi_cell(0, 10, pdf_info)

        def tekst2(self, pdf_info):
            self.set_xy(18.0, 35)
            self.set_text_color(0,0,0)
            self.set_font('Arial', '', 12)
            self.multi_cell(0, 10, pdf_info)

        def tekst3(self, pdf_info):
            self.set_x(18.0)
            self.set_text_color(0,0,0)
            self.set_font('Arial', '', 12)
            self.multi_cell(0, 10, pdf_info)

        def bijzonderhedenFrame(self):
            self.set_xy(19.0, 186)
            self.multi_cell(172, 6, str(invoer['bijzonderheden']), border=1)

        def bijzonderhedenFrameLeeg(self, advies, y):
            self.set_x(19.0)
            self.multi_cell(172, 6,'\n\n\n\n\n\n\n\n\n', border=1)
            self.set_x(18.0)
            self.multi_cell(174, 5, advies)

        def tabel(self):
            self.set_x(150)
            self.set_font('Arial', '', 9)
            col1 = 0
            for row in res_tabel:
                if col1 >= 2:
                    col1 = 0
                self.set_x(18)
                for item in row:
                    if col1 == 0:
                        rapport.cell(70, 10, txt=item, border=1)
                    elif col1 == 1:
                        rapport.cell(20, 10, txt=item, border=1)
                    else:
                        rapport.cell(42.75, 10, txt=item, border=1)
                    col1 += 1
                rapport.ln(10)

        def tabelPorties(self):
            self.set_x(19)
            self.set_font('Arial', '', 12)
            voorschriftportie.cell(50, 10, txt="Portie", border=1)
            voorschriftportie.cell(50, 10, txt="Tijden", border=1)
            for i in range(tijden_porties+1):
                self.set_x(19)
                if i == 0:
                    voorschriftportie.cell(50, 10,border=1)
                    voorschriftportie.cell(50, 10, border=1)
                    voorschriftportie.ln(10)
                else:
                    voorschriftportie.cell(50, 10, txt=str(int(i)), border=1)
                    voorschriftportie.cell(50, 10, border=1)
                    voorschriftportie.ln(10)

    # Maken van de PDF folder
    cwd = os.getcwd()
    Path(cwd + '/static/pdf').mkdir(parents=True, exist_ok=True)

    # Maken van rapport
    rapnaam = 'static/pdf/rapport_' + str(
        invoer['geboortedatum']) + '_' + \
              str(invoer["naam"].replace(". ", '')).lower() + '.pdf'
    rapport = PDF(orientation='P', unit='mm', format='A4')
    rapport.add_page()
    rapport.titel("Resultaten Rekenhulp")
    rapport.ondertitel("Gegevens patiënt", 40.0)
    rapport.datum()
    rapport.tekst(45, rapport_info)
    rapport.bijzonderhedenFrame()
    rapport.add_page(orientation='L')
    rapport.ondertitel("Resultaten patiënt", 20)
    rapport.tekst2(res_info)
    rapport.tabel()
    rapport.output(rapnaam, 'F')

    # Maken voorschrift pomp
    pompnaam = 'static/pdf/voorschrift-pomp_' + str(
        invoer['geboortedatum']) + '_' + \
               str(invoer["naam"].replace(". ", '')).lower() + '.pdf'
    voorschriftpomp = PDF(orientation='P', unit='mm', format='A4')
    voorschriftpomp.add_page()
    voorschriftpomp.titel("Sondevoedingsvoorschrift")
    voorschriftpomp.ondertitel2(("voor " + str(
                          invoer['aanhef']).lower() + '. ' + str(
                          invoer['naam']) + ' ' + str(
                          invoer['geboortedatum'])), 23.0)
    voorschriftpomp.datum()
    voorschriftpomp.tekst(35, voorschrift_pomp)
    voorschriftpomp.bijzonderhedenFrameLeeg(advies, 117)
    voorschriftpomp.output(pompnaam, 'F')

    # Maken voorschrift portie
    portienaam = 'static/pdf/voorschrift-portie_' + str(
        invoer['geboortedatum']) + '_' + \
                 str(invoer["naam"].replace(". ", '')).lower() + '.pdf'
    voorschriftportie = PDF(orientation='P', unit='mm', format='A4')
    voorschriftportie.add_page()
    voorschriftportie.titel("Sondevoedingsvoorschrift")
    voorschriftportie.ondertitel2(("voor " + str(
        invoer['aanhef']).lower() + '. ' + str(
        invoer['naam']) + ' ' + str(
        invoer['geboortedatum'])), 23.0)
    voorschriftportie.datum()
    voorschriftportie.tekst(35, voorschrift_portie)
    voorschriftportie.tabelPorties()
    voorschriftportie.tekst3(vsp2)
    voorschriftportie.bijzonderhedenFrameLeeg(advies, 107)
    voorschriftportie.output(portienaam, 'F')
    return rapnaam, pompnaam, portienaam


def pdfInfo(res_tabel, voeding, vocht):
    '''
    Deze functie maakt variabelen aan met de informatie die
    weggeschreven moeten worden in de pdf's als string. Vervolgens
    wordt de functie pdfMaken() aangeroepen.
    :param res_tabel: een lijst met alle berekende informatie van alle
    sondevoedingen die in de database staan.
    :param voeding: een lijst met alle berekende informatie van de
    door de gebruiker gekozen sondevoeding.
    moet worden.
    :param vocht: een integer die de totale hoeveelheid vocht in de
    sondevoeding aangeeft.
    :return: rapnaam = bevat de path naar het rapport.
    pompnaam = bevat de path naar het voorschrift van de pomp.
    portienaam = bevat de path naar het voorschrift van de portie.
    '''
    rapport_info = "Naam: " + str(invoer['aanhef']) + '. ' + \
                   str(invoer['naam']) + \
               "\nGeboortedatum: " + str(invoer['geboortedatum']) + \
               "\nLeeftijd: " + str(invoer['leeftijd']) + \
               "\nGeslacht: " + str(invoer['geslacht']) + \
               "\nLengte: " + str(invoer['lengte']) + \
               " cm\nGewicht: " + str(invoer['gewicht']) + \
               " kg\nRustmetabolisme: " + str(invoer['rustmetabolisme']) + \
               "\nEiwitaanbeveling: " + str(invoer['eiwit']) + \
               "%\nToeslag voor activiteit en ziekte: " + str(
        invoer['toeslag']) + \
               "%\nSondevoeding: " + str(invoer['voeding']) + \
               "\nTijd sondevoeding starten: " + str(
        invoer['start']) + ".00u" + \
               "\nTijd sondevoeding stoppen: " + str(
        invoer['stop']) + ".00u" +\
               "\nVochtbehoefte per 24u: " + str(
        invoer['vocht']) + " ml\nBijzonderheden: "

    res_info = "Rustmetabolisme: " + str(invoer['rustmetabolisme']) + \
               "\nBMI: " + str(uitrekenen["bmi"]) + \
               "\nEnergiebehoefte: " + str(uitrekenen['energiebehoefte']) + \
               " kcal\nEiwitbehoefte: " + str(
        uitrekenen["eiwitbehoefte"]) + " g p/d"

    vocht_portie = int(int(invoer['vocht']) - (int(str(
        voeding[5]).split()[0])/100)*int(vocht))
    vocht_pomp =  int(int(invoer['vocht']) - ((int(str(
        voeding[1]).split()[0])/100) * int(vocht) * (int(
        invoer['stop'] - int(invoer['start'])))))
    tijden_porties = int(str(voeding[3]).split()[2])

    voorschrift_pomp = "Soort sondevoeding: " + str(voeding[0]) + \
                       "\nHoeveelheid sondevoeding: " + str(voeding[5]) + \
                       "\nPompstand: " + str(voeding[1]) + \
                       "\nTijd pomp starten: " + str(invoer['start']) + \
                       ".00u" +  \
                       "\nTijd pomp stoppen: " + str(invoer['stop']) + \
                       ".00u" + \
                       "\nHoeveelheid vocht bij te spuiten door de sonde: " + \
                       str(vocht_pomp) +\
                       " ml\nTotale hoeveelheid vocht: " + str(
                        invoer['vocht']) + " ml\nBijzonderheden: "

    voorschrift_portie = "Soort sondevoeding: " + str(voeding[0]) + \
                         "\nHoeveelheid sondevoeding: " + str(voeding[5]) + \
                         "\nGrootte van porties: " + str(voeding[3]) + \
                         "\nTijden handmatige porties: "
    vsp2 = "Hoeveelheid vocht bij te spuiten door de sonde: " + str(vocht_portie) +\
                         " ml\nTotale hoeveelheid vocht: " + str(invoer['vocht']) + \
                         " ml\nBijzonderheden: "

    advies = "\n\nBewaaradvies: fles geopend met dop erop: 24 uur in koelkast. " \
            "Sondevoeding op kamertemperatuur toedienen. Koude sondevoeding " \
            "kan klachten veroorzaken. \n\nBij het aan- en afkoppelen van de " \
            "sondevoeding de sonde doorspuiten met 20 ml lauw water om " \
            "verstopping te voorkomen.\n\nAandacht voor mondhygiëne."

    rapnaam, pompnaam, portienaam = pdfMaken(rapport_info, voorschrift_pomp,
                                             voorschrift_portie, advies,
                                             res_info, res_tabel,
                                             tijden_porties, vsp2)
    return rapnaam, pompnaam, portienaam


def leeftijdBerekenen(born):
    '''
    Deze functie zet eerst de geboortedatum om in dd-mm-jjjj format en
    voegt deze toe aan de globale dictionary 'invoer'. Dit wordt ook
    gedaan voor de huidige datum. Vervolgens wordt de leeftijd berekent
    aan de hand van de ingevoerde geboortedatum en huidige datum.
    :param born: de ingevoerde geboortedatum in jjjj-mm-dd format.
    :return: de berekende leeftijd als integer.
    '''
    dag = born[8:10]
    maand = born[5:7]
    jaar = born[:4]
    invoer['geboortedatum'] = str(dag + '-' + maand + '-' + jaar)
    today = date.today()
    invoer['vandaag'] = str(str(today)[8:10] + '-' + str(today)[5:7] + '-' + str(today)[:4])
    birth = date(int(jaar), int(maand), int(dag))
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def energieBehoefte(eb):
    '''
    Deze functie berekent de energiebehoefte van de patiënt aan de
    hand van het gekozen rustmetabolsime. Bij H&B wordt de
    Harris-Benedict formule gebruikt en bij WHO de World Health
    Organization formule. Nadat een van de formules gebruikt is,
    wordt de energiebehoefte door 100 gedeeld en wordt dit
    vermenigvuldigt met de ingevulde toeslag voor activiteit en ziekte.
    Dit wordt vervolgens toegevoegd aan de al berekende
    energiebehoefte. Totslot wordt dit afgerond en toegevoegd aan de
    dictionary 'uitrekenen'.
    :param eb: integer die de variabele 'eb' definieerd
    :return:
    '''
    global invoer, uitrekenen
    if invoer['rustmetabolisme'] == 'H&B':
        if invoer['geslacht'] == 'man':
            eb = 66.4730 + (13.7516 * invoer['gewicht']) + (5.0033 * invoer['lengte']) - (6.7550 * invoer['leeftijd'])
        else:
            eb = 655.0955 + (9.5634 * invoer['gewicht']) + (1.8496 * invoer['lengte']) - (4.6756 * invoer['leeftijd'])
    else:
        if invoer['leeftijd'] >= 18 and invoer['leeftijd'] < 30:
            if invoer['geslacht'] == 'man':
                eb = ((15.4 * invoer['gewicht']) - (27 * (invoer['lengte']/100))) + 717
            else:
                eb = ((13.3 * invoer['gewicht']) + (334 * (invoer['lengte']/100))) + 35
        elif invoer['leeftijd'] >= 30 and invoer['leeftijd'] <= 60:
            if invoer['geslacht'] == 'man':
                eb = ((11.3 * invoer['gewicht']) - (16 * (invoer['lengte']/100))) + 901
            else:
                eb = ((8.7 * invoer['gewicht']) - (25 * (invoer['lengte']/100))) + 865
        elif invoer['leeftijd'] > 60:
            if invoer['geslacht'] == 'man':
                eb = ((8.8 * invoer['gewicht']) + (1128 * (invoer['lengte']/100))) - 1071
            else:
                eb = ((9.2 * invoer['gewicht']) + (637 * (invoer['lengte']/100))) - 302
    eb += ((eb/100) * invoer['toeslag'])
    uitrekenen['energiebehoefte'] = int(round(eb))


def eiwitBehoefte(ewb):
    '''
    Deze functie berekent de eiwitbehoefte van de patiënt. Als de BMI
    van de patiënt tussen de 20 en 30 zit, dan wordt het gewicht
    vermenigvuldigt met de ingevoerde eiwitaanbeveling. Als de BMI
    lager is dan 20 wordt de ingevoerde eiwitaanbeveling
    vermenigvuldigt met de lengte in het kwadraat en met 20. Als de BMI
    hoger is dan 30 wordt de ingevoerde eiwitaanbeveling
    vermenigvuldigt met de lengte in het kwadraat en met 27,5. Totslot
    wordt de berekende eiwitbehoefte afgerond en toegevoegd aan de
    dictionary 'uitrekenen'.
    :param ewb: integer die de variabele 'ewb' definieerd
    :return:
    '''
    global invoer, uitrekenen
    if uitrekenen['bmi'] >= 20 and uitrekenen['bmi'] <= 30:
        ewb = invoer['gewicht'] * invoer['eiwit']
    elif uitrekenen['bmi'] < 20:
        ewb = invoer['eiwit'] * (invoer['lengte']/100) * (invoer['lengte']/100) * 20
    elif uitrekenen['bmi'] > 30:
        ewb = invoer['eiwit'] * (invoer['lengte']/100) * (invoer['lengte']/100) * 27.5
    uitrekenen['eiwitbehoefte'] = int(round(ewb))


def berekeningen():
    '''
    Deze functie berekent de BMI en roept functies aan die de leeftijd,
    energiebehoefte en eiwitbehoefte berekenen.
    :return:
    '''
    global invoer, uitrekenen
    uitrekenen['bmi'] = float(round(int(invoer['gewicht']) /
                                    (int(invoer['lengte']) *
                                     int(invoer['lengte'])) * 10000, 1))
    leeftijd = leeftijdBerekenen(invoer['geboortedatum'])
    invoer['leeftijd'] = int(leeftijd)
    energieBehoefte(0)
    eiwitBehoefte(0)


def rekenhulpVoorblad(request):
    '''
    Deze functie kijkt of er op de knop 'Submit' is gedrukt. Als dit
    het geval is dan worden alle ingevoerde gegevens opgehaald en
    opgeslagen in de dictionary 'invoer'. Vervolgens wordt de gebruiker
    doorverwezen naar de resultaten pagina.
    :param request: object WSGIRequest, bevat de form methode en de
    path van de pagina.
    :return: HttpResponseRedirect = een HttpResponseRedirect terug naar
    de juiste URL.
    render = de functie geeft de request terug.
    '''
    global invoer
    if request.method == 'POST':
        if request.POST.get('submit'):
            invoer['naam'] = str(request.POST.get('naam'))
            invoer['geboortedatum'] = request.POST.get('datum')
            invoer['geslacht'] = str(request.POST.get('geslacht'))
            if invoer['geslacht'] == 'man':
                invoer['aanhef'] = 'dhr'
            else:
                invoer['aanhef'] = 'mw'
            invoer['lengte'] = int(request.POST.get('lengte'))
            invoer['gewicht'] = int(request.POST.get('gewicht'))
            invoer['rustmetabolisme'] = str(request.POST.get('rust'))
            invoer['eiwit'] = float(request.POST.get('eiwit'))
            invoer['toeslag'] = int(request.POST.get('toeslag'))
            invoer['voeding'] = str(request.POST.get('voeding'))
            invoer['start'] = int(request.POST.get('start'))
            invoer['stop'] = int(request.POST.get('stop'))
            invoer['vocht'] = int(request.POST.get('vocht'))
            invoer['bijzonderheden'] = str(request.POST.get('bijzonderheden'))
            berekeningen()
            return HttpResponseRedirect('/resultaten/')
    return render(request, 'rekenhulp.html')


def sondevoeding_berekening(info_sondevoeding, eiwitbehoefte, energiebehoefte, aantal_uren):
    """"
    In deze functie worden de pompstand, handmatige porties, uitkomst
    energie, uitkomst eiwit de hoeveelheid sondevoeding en het verschil
    berekent aan de hand van de ingevoerde uren, de berekende
    energiebehoefte en eiwitbehoefte. Voor porties wordt voor elke
    sondevoeding berekent welke portie tussen 200, 250 en 300 ml het
    dichtst bij de energieboehoefte zit en hoe vaak deze portie dan op
    een dag gegeven moet worden. Voor pompstand wordt berekent welke
    stand tussen 21 en 100 ml met de beschikbare uren die opgegeven
    zijn, het dichtst bij de energieboehoefte zit. De hoeveelheid
    sondevoeding wordt berekent door de portiegrootte te
    vermenigvuldigen met het aantal porties. Voor uitkomst energie en
    uitkomst eiwit wordt de uitkomst van de som pompstand en portie
    gebruikt. Hierbij worden de eiwitbehoefte en energiebehoefte
    opgeteld. Voor het verschil worden de uitkomsten van de sommen
    pompstand en energie gebruikt. De beste opties en de andere
    uitkomsten die erbij horen worden in de variable data gezet.
    :param info_sondevoeding: Een dictionary met de sondevoedingen en
    hun energie, eiwit en vocht per 100 ml
    :param eiwitbehoefte:  De berekende eiwitbehoefte als integer
    :param energiebehoefte: De berekende energiebehoefte als integer
    :param aantal_uren:  De berekende uren als integer
    :return: data = Een lijst met per sondevoeding de berekende
    waarden, pompstand, handmatige porties, uitkomst energie,
    uitkomst eiwit, hoeveelheid sondevoeding en het verschil.
    """
    data = []
    uitkomst_portie_energie = ''
    uitkomst_portie_eiwit = ''
    uitkomst_pompstand_energie = ''
    uitkomst_pompstand_eiwit = ''
    for x in info_sondevoeding.keys():
        beste_uitkomst_portie = []
        beste_uitkomst_pompstand = []
        lijst_uitkomsten_pompstand = []
        beste_uitkomst_pompstand_eiwit = []
        lijst_uitkomsten_pompstand_eiwit = []
        lijst_porties = []
        lijst_ip = []
        lijst_porties_eiwit = []
        lijst_ip_eiwit = []

        for i in range(2, 9):
            lijst_uitkomsten = []
            lijst_uitkomsten_eiwit = []
            lijst_uitkomsten.append((energiebehoefte - (info_sondevoeding[x][0] * i * 2)))
            lijst_uitkomsten_eiwit.append(eiwitbehoefte - (info_sondevoeding[x][1] * i * 2))

            lijst_uitkomsten.append((energiebehoefte - (info_sondevoeding[x][0] * i * 2.5)))
            lijst_uitkomsten_eiwit.append(eiwitbehoefte - (info_sondevoeding[x][1] * i * 2.5))

            lijst_uitkomsten.append((energiebehoefte - (info_sondevoeding[x][0] * i * 3)))
            lijst_uitkomsten_eiwit.append(eiwitbehoefte - (info_sondevoeding[x][1] * i * 3))

            beste_uitkomst_portie.append(reduce(lambda x, y: x if abs(y) > abs(x) else y, lijst_uitkomsten))

            portie = lijst_uitkomsten.index(min(lijst_uitkomsten, key=abs))
            if portie == 0:
                lijst_porties.append(200)
            elif portie == 1:
                lijst_porties.append(250)
            elif portie == 2:
                lijst_porties.append(300)

            beste_portie = beste_uitkomst_portie.index(min(beste_uitkomst_portie, key=abs))
            lijst_ip_eiwit.append(lijst_uitkomsten_eiwit[portie])


        lijst_ip.append(lijst_porties[beste_portie])
        for i in arange(0.21, 1.01, 0.01):
            lijst_uitkomsten_pompstand.append((energiebehoefte - (info_sondevoeding[x][0] * aantal_uren * i)))
            lijst_uitkomsten_pompstand_eiwit.append(eiwitbehoefte - (info_sondevoeding[x][1] * aantal_uren * i))

            beste_uitkomst_pompstand.append(
                reduce(lambda x, y: x if abs(y) > abs(x) else y, lijst_uitkomsten_pompstand))
        pompstand = str(int(beste_uitkomst_pompstand.index(min(beste_uitkomst_pompstand, key=abs))) + 21)
        beste_uitkomst_pompstand_eiwit.append(lijst_uitkomsten_pompstand_eiwit[beste_uitkomst_pompstand.index(min(beste_uitkomst_pompstand, key=abs))])

        p_d = beste_uitkomst_portie.index(min(beste_uitkomst_portie, key=abs)) + 2
        lijst_porties_eiwit.append(lijst_ip_eiwit[beste_uitkomst_portie.index(min(beste_uitkomst_portie, key=abs))])
        verschil = abs(beste_uitkomst_portie[beste_uitkomst_portie.index(min(beste_uitkomst_portie, key=abs))]) \
            + abs(*lijst_porties_eiwit) + abs(*beste_uitkomst_pompstand_eiwit) + abs(beste_uitkomst_pompstand[beste_uitkomst_pompstand.index(min(beste_uitkomst_pompstand, key=abs))])

        if int(beste_uitkomst_portie[beste_uitkomst_portie.index(min(beste_uitkomst_portie, key=abs))]) < 0 :
            uitkomst_portie_energie = str(int(abs(beste_uitkomst_portie[beste_uitkomst_portie.index(min(beste_uitkomst_portie, key=abs))]))
                    + int(energiebehoefte)) + ' kcal'
        elif int(beste_uitkomst_portie[beste_uitkomst_portie.index(min(beste_uitkomst_portie, key=abs))]) > 0 :
            uitkomst_portie_energie = str(int(-abs(beste_uitkomst_portie[beste_uitkomst_portie.index(min(beste_uitkomst_portie, key=abs))]))
                    + int(energiebehoefte)) + ' kcal'
        if int(*lijst_porties_eiwit) < 0 :
            uitkomst_portie_eiwit = str(int(abs(*lijst_porties_eiwit)) + int(eiwitbehoefte)) + ' g'
        elif int(*lijst_porties_eiwit) > 0:
            uitkomst_portie_eiwit = str(int(-abs(*lijst_porties_eiwit)) + int(eiwitbehoefte)) + ' g'
        if beste_uitkomst_pompstand[beste_uitkomst_pompstand.index(min(beste_uitkomst_pompstand, key=abs))] < 0:
            uitkomst_pompstand_energie = str(int(abs(beste_uitkomst_pompstand[beste_uitkomst_pompstand.index(min(beste_uitkomst_pompstand, key=abs))]))
                    + int(energiebehoefte)) + ' kcal'
        elif beste_uitkomst_pompstand[beste_uitkomst_pompstand.index(min(beste_uitkomst_pompstand, key=abs))] > 0:
            uitkomst_pompstand_energie = str(int(-abs(beste_uitkomst_pompstand[beste_uitkomst_pompstand.index(min(beste_uitkomst_pompstand, key=abs))]))
                    + int(energiebehoefte)) + ' kcal'
        if int(*beste_uitkomst_pompstand_eiwit) < 0:
            uitkomst_pompstand_eiwit = str(int(abs(*beste_uitkomst_pompstand_eiwit)) + int(eiwitbehoefte)) + ' g'
        elif int(*beste_uitkomst_pompstand_eiwit) > 0:
            uitkomst_pompstand_eiwit = str(int(-abs(*beste_uitkomst_pompstand_eiwit)) + int(eiwitbehoefte)) + ' g'
        uitkomst_pompstand = uitkomst_pompstand_energie + ' ' + uitkomst_pompstand_eiwit
        uitkomst_portie = uitkomst_portie_energie + ' ' + uitkomst_portie_eiwit
        porties_p_d = str(int(*[porties for porties in lijst_ip])) + ' ml ' + str(p_d) + ' porties p/d '
        hoeveelheid_sonde = str(int(*[porties for porties in lijst_ip]) * int(p_d)) + ' ml'
        data.append([x, pompstand, uitkomst_pompstand, porties_p_d, uitkomst_portie, hoeveelheid_sonde, verschil])
    return data


def resultaten(request):
    """
    In deze functie wordt de functie sondevoeding_bereking()
    aangeroepen om de data te verkrijgen voor de dataframe. Als de
    data is verkregen wordt de dataframe gemaakt. Vervolgens wordt
    de dataframe gesorteerd op de kolom 'verschil' en wordt de kolom
    gedropt. Vervolgens wordt de gebruiker doorverwezen naar de
    resultaten pagina. Als op de knop 'maak PDF' wordt geklikt, wordt
    de directory static/pdf/ verwijderd en wordt de functie
    pdf_info() aangeroepen.
    :param request: object WSGIRequest, bevat de form methode en de
    path van de pagina.
    :return: render = de functie combineert de template met een
    dictionary en geeft de request terug. De dictionary bevat de
    variabelen:'rust' de rustmetabolisme als string, 'bmi' de berekende
    BMI als float, 'energiebehoefte' de berekende energiebehoefte als
    integer, 'eiwitbehoefte' de berekende eiwitbehoefte als integer,
    'selection' de resultaten tabel, 'rapnaam' de path naar het
    rapport, 'pompnaam' de path naar het voorschrift voor de pomp en
    'portienaam' de path naar het voorschrift voor de portie.
    render = de functie combineert de template met een
    dictionary en geeft de request terug. De dictionary bevat de
    variabelen:'rust' de rustmetabolisme als string, 'bmi' de berekende
    BMI als float, 'energiebehoefte' de berekende energiebehoefte als
    integer, 'eiwitbehoefte' de berekende eiwitbehoefte als integer
    en 'selection' de resultaten tabel.
    """
    global uitrekenen
    info_sondevoeding = {}
    sondevoedingen = Sondevoeding.objects.all()
    for sondevoeding in sondevoedingen:
        info_sondevoeding[str(sondevoeding.Soort)] = [int(sondevoeding.Energie), float(sondevoeding.Eiwit), int(sondevoeding.Vocht)]
    eiwitbehoefte = int(uitrekenen['eiwitbehoefte'])
    energiebehoefte = int(uitrekenen['energiebehoefte'])
    aantal_uren = int(invoer['stop']) - int(invoer['start'])
    data = sondevoeding_berekening(info_sondevoeding, eiwitbehoefte, energiebehoefte, aantal_uren)
    df = pd.DataFrame(data, columns=['Soort', 'Pompstand', 'Totale energie en eiwit pomp', 'Handmatige porties',
                                     'Totale energie en eiwit portie', 'Hoeveelheid Sondevoeding', 'verschil'])
    df = df.sort_values(by=['verschil'])
    df = df.drop(['verschil'], axis=1)
    col_names = []
    for name in df:
        col_names.append(name)
    res_tabel = [col_names]
    for ind in df.index:
        res_tabel.append([df['Soort'][ind], df['Pompstand'][ind],
                          df['Totale energie en eiwit pomp'][ind],
                          df['Handmatige porties'][ind],
                          df['Totale energie en eiwit portie'][ind],
                          df['Hoeveelheid Sondevoeding'][ind]])
    if request.method == "POST":
        if invoer['naam'] != '':
            if 'maakPDF' in request.POST:
                if os.path.isdir('static/pdf/'):
                    shutil.rmtree('static/pdf/')
                inx = int(request.POST.get('maakPDF')) + 1
                rapnaam, pompnaam, portienaam = pdfInfo(res_tabel,
                                                        res_tabel[inx],
                                                        info_sondevoeding[res_tabel[inx][0]][2])
                return render(request, 'resultaten.html', {
                    'rust': invoer['rustmetabolisme'],
                    'bmi': uitrekenen['bmi'],
                    'eiwit': eiwitbehoefte,
                    'energie': energiebehoefte,
                    'selection': res_tabel[1:],
                    'rapnaam': rapnaam,
                    'pompnaam': pompnaam,
                    'portienaam': portienaam,
                })
    return render(request, 'resultaten.html', {
        'rust': invoer['rustmetabolisme'],
        'bmi': uitrekenen['bmi'],
        'eiwit': eiwitbehoefte,
        'energie': energiebehoefte,
        'selection': res_tabel[1:],
    })


def sondevoedingen(request):
    """
    In deze functie wordt de tabel 'Sondevoeding' opgehaald
    uit de database.
    :param request: object WSGIRequest, bevat de form methode
    en de path van de pagina.
    :return: render = de functie combineert de template met een
    dictionairy en geeft de request terug. De dictionary
    bevat de variabele 'tabel' de sondevoeding tabel.
    """
    tabel = Sondevoeding.objects.all()
    return render(request, 'sondevoeding.html', {
        'tabel': tabel,
    })


class Sondevoeding_form(forms.ModelForm):
    class Meta:
        model = Sondevoeding
        exclude = []


def toevoegen(request):
    """
    In deze functie wordt de toevoegen pagina gerenderd. De
    ondertitel wordt veranderd naar 'Toevoegen'. Het formulier
    van de Sondevoeding wordt opgehaald via
    Sondevoeding_form(request.POST). Wanneer de functie voor het
    eerst wordt aangeroepen, zal de return render uitgevoerd worden
    en verschijnt er een leeg formulier op de pagina. Als het
    formulier correct wordt ingevuld (is_valid()), wordt het object
    toegevoegd aan de database. De gebruiker wordt dan doorverwezen
    naar de sondevoedingen pagina.
    :param request: object WSGIRequest, bevat de form methode
    en de path van de pagina.
    :return: render = de functie combineert de template met een
    dictionairy en geeft de request terug. De dictionairy bevat de
    variabele 'form' het formulier en de variabele 'ondertitel' de
    ondertitel: 'Toevoegen'.
    redirect = functie, verwijst de gebruiker door naar de
    sondevoedingen pagina.
    """
    ondertitel = "Toevoegen"
    form = Sondevoeding_form(request.POST)
    if form.is_valid():
        form.save()
        return redirect('/sondevoedingen/')
    return render(request, 'sondevoeding_toevoegen.html', {
        "form": form,
        'ondertitel': ondertitel,
        })


def bewerken(request, soort):
    """
    In deze functie wordt de toevoegen pagina gerenderd als
    aanpassen pagina. De ondertitel wordt veranderd naar
    'Aanpassen'. Het object wat bij het soort Sondevoeding hoort,
    wordt opgehaald en meegegeven aan het formulier wanneer er nog
    niet op een knop is gedrukt. Als er wel op de 'opslaan' knop is
    gedrukt, worden de ingevulde gegevens opgehaald en
    gecontroleerd. Als deze voldoen (is_valid()), wordt het object
    bijgewerkt en opgeslagen in de database. De gebruiker wordt dan
    doorverwezen naar de sondevoedingen.
    :param request: object WSGIRequest, bevat de form methode
    en de path van de pagina.
    :param soort: bevat de soort Sondevoeding die bewerkt gaat
    worden.
    :returns: render = de functie combineert de template met een
    dictionairy en geeft de request terug. De dictionairy bevat de
    variabele 'form' het formulier en de variabele 'ondertitel' de
    ondertitel: 'Aanpassen'.
    redirect = functie, verwijst de gebruiker door naar de
    sondevoedingen pagina.
    """
    ondertitel = "Aanpassen"
    voeding = Sondevoeding.objects.get(Soort=soort)

    if request.method == 'POST':
        form = Sondevoeding_form(request.POST, instance=voeding)
        if form.is_valid():
            form.save()
            return redirect('/sondevoedingen/')
    else:
        form = Sondevoeding_form(instance=voeding)
    return render(request, 'sondevoeding_toevoegen.html', {
        'form': form,
        'ondertitel': ondertitel,
    })


def delete(request, soort):
    """
    In deze functie wordt de meegegeven param opgezocht in
    tabel 'Sondevoeding' en verwijderd uit de database.
    :param request: object WSGIRequest, bevat de form methode
    en de path van de pagina.
    :param soort: Sondevoeding soortnaam
    :return: een HttpResponseRedirect terug naar de juiste URL.
    """
    record = Sondevoeding.objects.get(Soort=soort)
    record.delete()
    return redirect('/sondevoedingen/')

