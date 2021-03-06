### Start Testing_Steve ###

from builtins import print

import PyPDF2
import nltk
from nltk import FreqDist
from nltk.corpus import stopwords
import operator
from nltk import sent_tokenize, word_tokenize
from nltk import StanfordPOSTagger
import os

os.environ['JAVAHOME'] = "C:/Program Files/Java/jdk1.8.0_20/bin/java.exe"

'''
    Data extracting from Plenarprotokoll
'''
''' Globals '''
cleanList = []  # Vorhalten von Redeteilen
start_Element_Rede = 0
list_with_startelement_numbers = []  # enthält Start item aller Redetexte
list_with_startEnd_numbers = []  # enthält Start und Ende item aller Redetexte
number_of_last_element = 0
list_elements_till_first_speech = []  # enthält listenelemente bis zur ersten Rede
politican_name = ""
party_name = ""


def get_content():
    '''
    Holt den Content fuer alle Seiten eines Protokolls

    :return: page_content
    '''
    pdf_file = open('Plenarprotokoll_18_232.pdf', 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    page_content = ''
    for i in range(read_pdf.getNumPages()):
        print(i)
        pages = read_pdf.getPage(i)
        page_content += pages.extractText()
    return page_content


def split_and_analyse_content(page_content):
    '''
    Seiteninhalte des Protokolls werden zu Sätze, die wiederum zu Listenelemente werden
    entfernen von "\n" und "-" aus Listenelemente

    :param page_content:
    :return:
    '''
    list = sent_tokenize(page_content)
    print(list)
    for i in range(len(list)):
        list_element = list[i]
        list_element = list_element.replace("\n", "")
        list_element = list_element.replace("-", "")
        cleanList.append(list_element)  # liste ohne -, \n
        # print("item at index", i, ":", list_element)       # alle Listenelemente
        analyse_content_element(list_element, i)
        set_number(i)


def set_number(i):
    '''
    Setzt number of listelement

    :param i:
    '''
    global number_of_last_element
    number_of_last_element = i


def get_number():
    '''
    Gibt number of listelement
    :return:
    '''
    global number_of_last_element
    return number_of_last_element


def analyse_content_element(list_element, i):
    '''
    Nimmt das listenelement auseinander und prüft, ob ein Wechsel der Redner stattfindet oder ob es sich um ein Redeteil handelt
    + Setzen Startnummer für Rede und Speicherung in Liste
    + Einsatz von StanfordParser
    :param list_element: Übergabe aus "def content_to_dict"
    :param i: Nummerierung des Listenelements
    :return:
    '''
    temp_dict_empty_values = {'polName': '', 'partyName': ''}
    matchers = ['Das Wort', 'das Wort', 'nächste Redner', 'nächster Redner', 'nächste Rednerin', 'spricht jetzt',
                'Nächste Rednerin', 'Nächster Redner', 'Letzter Redner', 'nächste Wortmeldung']
    if any(m in list_element for m in matchers):
        print("\nWechsel Redner", i, ":", list_element)  # Listenelemente, die matchers enthalten
        start_Element_Rede = i + 1
        list_with_startelement_numbers.append(start_Element_Rede)
        print("Start_Index_Redetext: ", start_Element_Rede)
        # ''' - POS -> PartOfSpeech Verben, Nomen, ... in Listenelement mit matchers'''
        # words = word_tokenize(list_element)
        # '''extracting Named Entities - Person, Organization,...'''
        # jar = 'jars\stanford-postagger.jar'
        # model = 'jars\german-hgc.tagger'
        # pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8')
        # tagged = pos_tagger.tag(words)
        # print(tagged)
        # chunkGram = r"""Eigenname: {<NE>?}"""
        # chunkParser = nltk.RegexpParser(chunkGram)
        # namedEnt = chunkParser.parse(tagged)
        # print("chunkParser: ",namedEnt)
        # #namedEnt.draw()
        # ''' extract entity names - anhand von label - NE => Eigenname'''
        # entityPers_names_subtree = []
        # for subtree in namedEnt.subtrees(filter=lambda t: t.label() == 'Eigenname'):
        #     print(subtree)
        #     entityPers_names_subtree.append(subtree[0])
        # print('entityPers_names_subtree: ',entityPers_names_subtree)
        # entityPers_names \
        #     = []
        # name = ''
        # for ne in entityPers_names_subtree:
        #     name += ' ' + ne[0]
        # entityPers_names.append(name)
        # print("Person: ",entityPers_names)
        # print("Person:",str(name))

    # Listenelement ist entweder 'Anfang bis zur ersten Rede' oder 'Redeteil'
    else:
        Rede = []
        if len(list_with_startelement_numbers) != 0:  # wenn bereits eine Startnummer (erste Rede) vorhanden
            print("Redeteil:", i, list_element)
        else:
            global list_elements_till_first_speech
            list_elements_till_first_speech.append(list_element)  # Teile mit TOP, ZTOP,...
            print('global-> erste Zeilen: ', list_element)


def api_abgeordnetenwatch(politican_name):
    '''
    Anbindung an API-Abgeordnetenwatch um sich JSON abzugreifen und weitere Daten zur Person abzugreifen
    :param politican_name
    :return: Name, Partei usw.
    '''
    import urllib.request, json
    politican_name = politican_name.lower()
    politican_name = politican_name.replace(' ', '-')
    with urllib.request.urlopen(
                            "https://www.abgeordnetenwatch.de/api/profile/" + politican_name + "/profile.json") as url:
        data = json.loads(url.read().decode())
        politiker_name = data['profile']['personal']['first_name'] + " " + data['profile']['personal']['last_name']
        partei = data['profile']['party']
    return politican_name, partei


def get_start_and_end_of_a_speech():
    '''
    Bestimmung von Start und Ende der Reden
    :return: Liste mit Liste mit Start-und Endnummern
    '''
    print("Liste mit Startnummern: ", list_with_startelement_numbers)
    print(len(list_with_startelement_numbers))
    liste_mit_Startnummern_und_End = []
    liste_mit_Endnummern = []
    i = 0
    x = 1
    while i < len(list_with_startelement_numbers) - 1:
        liste_mit_Endnummern.insert(i, list_with_startelement_numbers[x] - 1)
        if i == len(list_with_startelement_numbers) - 2:
            liste_mit_Endnummern.append(get_number())
        i += 1
        x += 1
    print('Liste mit Endnummern: ', liste_mit_Endnummern)
    print(len(liste_mit_Endnummern))
    # Füllen mit Start und Endnummern
    i = 0
    while i <= len(list_with_startelement_numbers) - 1:
        liste_mit_Startnummern_und_End.append(list_with_startelement_numbers[i])
        liste_mit_Startnummern_und_End.append(liste_mit_Endnummern[i])
        i += 1
    print('Liste mit Start-und Endnummern: ', liste_mit_Startnummern_und_End)
    print(len(liste_mit_Startnummern_und_End))
    return liste_mit_Startnummern_und_End


def get_all_speeches(liste_mit_Startnummern_und_End):
    '''
    Befüllen der Liste "alle_Reden_einer_Sitzung" mit Reden
    :return: Liste mit Reden
    '''
    alle_Reden_einer_Sitzung = []
    x = 0
    y = 1
    start = 1
    end = len(liste_mit_Startnummern_und_End) - 1
    active = True

    while active:
        print("x: ", x)
        print("y: ", y)
        print("start: ", start)
        if start > end:
            active = False
            print("false")
        else:
            alle_Reden_einer_Sitzung.append(cleanList[liste_mit_Startnummern_und_End[x]:liste_mit_Startnummern_und_End[
                y]])  # [alle zwischen Start:Ende]
        x += 2
        y += 2
        start += 2
    print(len(alle_Reden_einer_Sitzung))
    # Ausgabe aller Reden
    for rede in alle_Reden_einer_Sitzung:
        print(rede)
    return alle_Reden_einer_Sitzung


def clean_speeches(alle_Reden_einer_Sitzung):
    '''
    Holt alle Zwischenrufe, Beifälle, Unruhe, etc. aus einer Rede
    :return: dictionary rede
    '''
    print('clean_speeches xxxxxxxxxxxxxxxxxxxxxxxx')

    import re
    # gehe jede Rede durch
    # wenn (...) kommt dann entferne diesen Teil aus Rede
    # entfernten Teil analysieren und zwischen speichern
    regex = re.compile(".*?\((.*?)\)")
    liste_dictionary_reden_einer_sitzung = []

    for rede in alle_Reden_einer_Sitzung:
        if rede:
            clean_rede = []
            liste_beifaelle = []
            liste_widersprueche = []
            liste_unruhe = []
            liste_wortmeldungen = []
            result_dictionary = {}

            for item in rede:
                # suche, schneide aus
                liste_treffer = []
                liste_treffer = re.findall(regex, item)
                clean_item = item
                for i in liste_treffer:
                    if i.__contains__('Beifall'):
                        liste_beifaelle.append(i)
                    elif i.__contains__('Widerspruch'):
                        liste_widersprueche.append(i)
                    elif i.__contains__('Unruhe'):
                        liste_unruhe.append(i)
                    else:
                        liste_wortmeldungen.append(i)
                    clean_item = clean_item.replace('(' + i + ')', '')

                clean_rede.append(clean_item)

            result_dictionary = {
                'Unruhe': liste_unruhe,
                'Rede': clean_rede,
                'Beifälle': liste_beifaelle,
                'Widerruf': liste_widersprueche,
                'Wortmeldungen': liste_wortmeldungen
            }

            liste_dictionary_reden_einer_sitzung.append(result_dictionary)
            # print(clean_rede)

    return liste_dictionary_reden_einer_sitzung


content = get_content()
names_of_entities = split_and_analyse_content(content)
start_end_nummern_liste = get_start_and_end_of_a_speech()
liste_alle_reden = get_all_speeches(start_end_nummern_liste)

redeliste = clean_speeches(liste_alle_reden)
print(redeliste)

'''ToDo: xxxxxxxxxxxxxxxxxxxxxxxxxxx   Datenbank befuellen   xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx '''

### ENDE Testing_Steve ###

### START Testing_Marc ###

from selenium import webdriver
from bs4 import BeautifulSoup


def start_scraping_with_chrome(url):
    '''
    Scrapt eine Webseite mit dem Google-Chrome-Browser anhand einer übergebenen URL
    :param url: String - URL
    :return: Selenium-Chrome-Webdriver-Objekt
    '''
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
    chrome.get(url)
    return chrome

def get_new_zp_topic(topic):
    new_topic_letters_counter = topic.index('+')
    counter = 0
    new_topic = ''

    for letter in str(topic):
        if counter <= new_topic_letters_counter:
            counter += 1
            new_topic += letter
    return new_topic

def rebuild_topic(topic, whitespaces_to_jump):
    '''
    Nimmt den Tagesordnungspunkt auseinander und gibt den 'TOP X' zurück

    :param topic: Tagesordnungspunkt (z.B. 'TOP 40 Bundeswehreinsatz im Mittelmeer')
    :param whitespaces_to_jump: Spaces die es zu überspringen gilt, bis der Tagesordnungspunktname erreicht wurde (meistens 2)
    :return: z.B. 'TOP 40 Bundeswehreinsatz im Mittelmeer' wird übergeben mit whitespaces_to_jump = 2 -> returned 'TOP 40'
    '''

    new_topic = ''
    if 'Sitzungseröffnung' in topic:
        new_topic = 'TOP'
    elif '+' in topic:
        new_topic = get_new_zp_topic(topic)
    else:
        if 'Legislaturbericht Digitale Agenda 2014 bis 2017' in topic:
            pass
        found_spaces = 0
        for letter in str(topic):
            if letter != ' ' and found_spaces < whitespaces_to_jump:
                new_topic = new_topic + letter

            elif letter == ' ' and found_spaces < whitespaces_to_jump:
                new_topic = new_topic + letter
                found_spaces = found_spaces + 1
    return new_topic.strip()


def get_topic_name_from_topic_number(top, topic):
    '''
    Entfernt die 'TOP X' Nummer aus dem Tagesordnungspunkt und gibt dann nur den/die eigentlichen Namen/Beschreibung zurück

    :param top: z.B.: 'TOP 40'
    :param topic: z.B. 'TOP 40 Bundeswehreinsatz im Mittelmeer'
    :return: Tagesordnungspunkt-Beschreibung z.B.: 'Bundeswehreinsatz im Mittelmeer'
    '''
    topic_name = topic.replace(top, '')
    topic_name = topic_name.strip()
    return topic_name


def get_alle_tops_and_alle_sitzungen_from_soup(soup):
    '''
    Holt alle Tagesordnungspunkte und die Metadaten der vorhandenen Sitzungen aus der "Wundervollen Suppe"

    :param soup: Beautiful-Soup-Objekt
    :return: Dictionary - Mit allen unbearbeiteten TOPs (Liste); Sitzungsmetadaten (Dictionary)
    '''
    dict = {'num_Sitzung': '', 'num_Wahlperiode': '', 'dat_Sitzung': '', 'top': {}}
    liste_dict = []
    liste_top = []
    alle_tops_list = []

    for item in soup.find_all('strong'):
        # print(item.get_text())
        if item.get_text().__contains__('Wahlperiode'):
            dict = {'num_Sitzung': item.get_text()[7:10], 'num_Wahlperiode': item.get_text()[21:23],
                    'dat_Sitzung': item.get_text()[38:48]}
            liste_dict.append(dict)
        if item.get_text().__contains__('TOP'):
            # print(para.get_text())
            liste_top.append(item.get_text())
        alle_tops_list.append(item.get_text())
    return {'TOPs': alle_tops_list, 'Alle_Sitzungen': liste_dict}


def get_alle_sitzungen_mit_start_und_ende_der_topic(alle_tops_list, alle_sitzungen):
    '''
    Gibt alle Sitzungen zurück samt Topics, deren Rednern, sowie die Sitzungsmetadaten. (Sitzungsnummer, Datum, Wahlperiode)
    Vereint hierbei die unbearbeiteten Topics mit den Sitzungsmetadaten.

    :param alle_tops_list: Liste - Tgesordnungspunkte
    :param alle_sitzungen: Liste - Sitzungsmetadaten
    :return: Liste
    '''
    liste_nummern_sitzungsstart = []
    liste_nummern_sitzungsende = []
    for i, j in enumerate(alle_tops_list):
        if j == '\n  TOP Sitzungseröffnung ':
            liste_nummern_sitzungsstart.append(i)
    for i, j in enumerate(alle_tops_list):
        if j == '\n  TOP Sitzungsende ':
            liste_nummern_sitzungsende.append(i)

    eine_Sitzung = []
    alle = []
    x = 0
    start = 0
    end = len(liste_nummern_sitzungsende) - 1
    active = True
    while active:
        eine_Sitzung = []
        if start > end:
            active = False
        else:
            eine_Sitzung.append(alle_tops_list[liste_nummern_sitzungsstart[x]:liste_nummern_sitzungsende[
                x]])  # [alle zwischen Start:Ende]

            alle_sitzungen[x]['top'] = eine_Sitzung
        x += 1
        start += 1
        alle.append(eine_Sitzung)

    return alle_sitzungen


def sort_topics_to_sitzung(alle_sitzungen):
    '''
    Bearbeitet die Tagesordnungspunkte, sortiert die Redner den entsprechenden Tagesordnungspunkten zu. Zuordnung der
    Sitzungs-Metadaten in die entsprechende Sitzung.

    :param alle_sitzungen:
    :return:
    '''
    dict_sitzungen = {}

    for sitzung in alle_sitzungen:
        tops = sitzung['top'][0]
        sitzungs_datum = sitzung['dat_Sitzung']
        wahlperiode = sitzung['num_Wahlperiode']
        sitzungs_nummer = sitzung['num_Sitzung']

        tops.index
        dict_rede = {}
        dict_sitzung = {}
        list_redner = []
        top_counter = -1

        top_zwischenspeicher = ''
        dict_topics = {}
        for i in range(len(tops)):

            topic = tops[i]
            topic = topic.strip()

            # print(topic)
            if topic.__contains__('TOP'):
                top_counter = top_counter + 1
                list_redner = []

                top_number_key = rebuild_topic(topic, 2)
                if top_number_key != 'TOP':
                    top_name = get_topic_name_from_topic_number(top_number_key, topic)
                    dict_topics[top_number_key] = {'Tagesordnungspunkt': top_name}

            else:
                '''
                Füge alle Redner einer Topic, der entsprechenden Topic hinzu, prüfe jedoch vorher, ob sich der jeweilige
                Redner bereits in der Liste befindet und füge ihn nur hinzu, sofern er noch darin enthalten ist.

                allready_in_list = False
                for redner in list_redner:
                    if redner == topic:
                        allready_in_list = True
                if allready_in_list == False:
                '''
                list_redner.append(topic)
            '''
            if len(list_redner) != 0:    
                if len(list_redner) > 1:
                    list_redner.remove(list_redner[0])
                    list_redner.remove(list_redner[-1])
                elif len(list_redner)< 2:
                    list_redner.remove(list_redner[0])            
            '''
            if top_number_key != 'TOP':
                dict_topics[top_number_key]['Redner'] = list_redner

        dict_sitzung = {
            'Sitzungsdatum': sitzungs_datum,
            'Wahlperiode': wahlperiode,
            'TOPs': dict_topics
        }

        dict_sitzungen['Sitzung ' + sitzungs_nummer] = dict_sitzung

    return dict_sitzungen


def delete_first_and_last_speecher_from_list(dict_sitzungen):
    for sitzung in sorted(dict_sitzungen):
        temp_speecher_dict = dict_sitzungen[sitzung]['TOPs']
        for top in sorted(temp_speecher_dict):
            if len(temp_speecher_dict[top]['Redner']) >1:
                temp_top_liste = temp_speecher_dict[top]['Redner']
                temp_top_liste.remove(temp_top_liste[0])
                temp_top_liste.remove(temp_top_liste[len(temp_top_liste) - 1])

    return dict_sitzungen

def sort_reden_eines_tops_in_tagesordnungspunkt(reden_eines_tops, tagesordnungspunkt, cleaned_sortierte_sitzungen):
    i = 0
    list_sorted_redner_temp =[]
    for redner in cleaned_sortierte_sitzungen['TOPs'][tagesordnungspunkt]['Redner']:
        dict_temp_redner = {redner: reden_eines_tops[i]}
        list_sorted_redner_temp.append(dict_temp_redner)
        i += 1
    cleaned_sortierte_sitzungen['TOPs'][tagesordnungspunkt]['Redner'] = list_sorted_redner_temp

def merge_sitzungsstruktur_mit_reden(redeliste, cleaned_sortierte_sitzung):
    laenge_der_redeliste = len(redeliste)
    tops = cleaned_sortierte_sitzung['TOPs']
    reden = redeliste


    for top in sorted(tops):
        reden_eines_tagesordnungspunkts = []
        i = 0
        anzahl_redner_in_topic = len(tops[top]['Redner'])
        print('Anzahl Redner in Tagesordnungspunkt "' + top + '" : ' + str(anzahl_redner_in_topic))

        while i < anzahl_redner_in_topic:
            reden_eines_tagesordnungspunkts.append(reden.pop(0))
            i += 1

        sort_reden_eines_tops_in_tagesordnungspunkt(reden_eines_tagesordnungspunkts, top, cleaned_sortierte_sitzung)


    for rede in reden_eines_tagesordnungspunkts:
        for list_eintrag_redner in tops[top]['Redner']:
            redner = {list_eintrag_redner:rede}
'''

def hole_reden_eines_tagesordnungspunkts(redeliste, anzahl_reden):
    reden_eines_tagesordnungspunkts = []
    counter = 0

    for rede in redeliste:
        if counter < anzahl_reden:
            counter += 1
            reden_eines_tagesordnungspunkts.append(rede)

    return reden_eines_tagesordnungspunkts
'''

chrome = start_scraping_with_chrome('http://www.bundestag.de/ajax/filterlist/de/dokumente/protokolle/-/442112/h_6810466be65964217012227c14bad20f?limit=1')
soup = BeautifulSoup(chrome.page_source, 'lxml')
alle_tops_und_alle_sitzungen = get_alle_tops_and_alle_sitzungen_from_soup(soup)

alle_tops_list = alle_tops_und_alle_sitzungen['TOPs']
alle_sitzungen = alle_tops_und_alle_sitzungen['Alle_Sitzungen']

alle_sitzungen_mit_start_und_ende_der_topic = get_alle_sitzungen_mit_start_und_ende_der_topic(alle_tops_list,
                                                                                              alle_sitzungen)

sortierte_sitzungen = sort_topics_to_sitzung(alle_sitzungen_mit_start_und_ende_der_topic)
cleaned_sortierte_sitzungen = delete_first_and_last_speecher_from_list(sortierte_sitzungen)

print('Scraping beendet')

### ENDE Testing_Marc ###

### START spaßige teil###

'''
START Test mit nur einer Sitzung
'''
sitzung_232 = cleaned_sortierte_sitzungen['Sitzung 232']

temp_speecher_dict = sitzung_232['TOPs']
temp_top_liste = []

i=0
for top in sorted(temp_speecher_dict):
    temp_top_liste.append(temp_speecher_dict[top]['Redner'])
    i = i + len(temp_speecher_dict[top]['Redner'])

print("Anzahl einsortierte Redner: " + str(i))
print("Anzahl vorhandene Reden in Redeliste: " + str(len(redeliste)))
#print(len(temp_top_liste))
#print(temp_top_liste)

merged_sitzung = merge_sitzungsstruktur_mit_reden(redeliste, sitzung_232)


'''
ENDE Test mit nur einer Sitzung
'''


def konkateniere_redeliste_zu_redestring(redeliste):
    pass


#ToDo: Redeliste zu einer zusammenhängenden Rede vereinen. -> mit Schleife konkatenieren und "\n" anhängen.


### ENDE spaßige teil###