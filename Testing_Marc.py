"""
@author: Steve
"""
import PyPDF2
import datetime
import sys
import operator

from nltk import FreqDist
from nltk.corpus import stopwords

from nltk import sent_tokenize, word_tokenize
from nltk import StanfordPOSTagger

import xlrd
from nltk import ne_chunk

'''
    Data extracting from Plenarprotokoll
'''
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("log/console-output/output_log.txt'", 'w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        #Diese Methode wird für die Python3-Kopatibilität benötigt
        pass

''' get content fuer alle Seiten im Protokoll '''
def getContent():
    pdf_file = open('Plenarprotokoll_18_232.pdf', 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    page_content = ''
    for i in range(read_pdf.getNumPages()):
        print(i)
        pages = read_pdf.getPage(i)
        page_content += pages.extractText()
    return page_content
'''
- function fuer content-splitt und vorhalten in Liste
- Dabei entfernen von "\n" und "-" aus Listenelemente
- zusätzliche Speicherung in txt-file
'''
def contentToList(page_content):
    list = sent_tokenize(page_content)
    # list = page_content.split(' ')
    print(list)
    cleanList = []
    list_with_startelement_numbers = [] # enthält Start item aller Redetexte
    list_with_startEnd_numbers = []     # enthält Start und Ende item aller Redetexte
    # hallo ihr
    # meine dfsdkfsdfsd

    for i in range(len(list)):
        list_element = list[i]
        list_element = list_element.replace("\n", "")
        list_element = list_element.replace("-", "")
        cleanList.append(list_element) # liste ohne -, \n
        #print("item at index", i, ":", list_element)       # alle Listenelemente

        start_Element_Rede = 0

        '''analysiere Struktur list_element'''
        ''' nachdem Präsident Lammert das Wort übergibt, beginnt eine Rede'''
        matchers = ['Das Wort','das Wort']
        if any(m in list_element for m in matchers):
            print("item at index", i, ":", list_element)    # Listenelemente, die matchers enthalten
            start_Element_Rede = i + 1
            list_with_startelement_numbers.append(start_Element_Rede)
            print("Start_Index_Redetext: ", start_Element_Rede)

            '''- POS -> PartOfSpeech Verben, Nomen, ... in Listenelement mit matchers'''
            words = word_tokenize(list_element)

            '''extracting Named Entities - Person, Organization,...'''
            jar = 'jars/stanford-postagger.jar'
            model = 'jars/german-hgc.tagger'
            pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8')
            text = pos_tagger.tag(pos_tagger)
            print(text)

            namedEnt = ne_chunk(tagged)
            print(namedEnt)
            #namedEnt.draw()


            def extract_entity_names(namedEnt):
                entityPers_names = []
                if hasattr(namedEnt, 'label') and namedEnt.label:
                    if namedEnt.label() == 'PERSON': #or namedEnt.label() == 'ORGANIZATION':
                        entityPers_names.append(' '.join([child[0] for child in namedEnt]))
                    else:
                        for child in namedEnt:
                            entityPers_names.extend(extract_entity_names(child))
                return entityPers_names
            entityPerson_names = []
            entityPerson_names.extend(extract_entity_names(namedEnt))
            # Print all entity names
            print("Person: " + str(entityPerson_names))

            ''' Excel-sheet with all politicans '''
            workbook = xlrd.open_workbook('mdb.xls')
            worksheet = workbook.sheet_by_name('Tabelle1')
            # Value of 1st row and 1st column
            value_of_first_col_Names = []
            value_of_second_col_Party = []
            first_col_Names = worksheet.col_values(0)
            second_col_Party = worksheet.col_values(1)
            print(first_col_Names)
            print(second_col_Party)

            matchers = first_col_Names
            politican_name = ""
            party_name = ""
            for i in range(len(entityPerson_names)):
                list_element = entityPerson_names[i]
                for m in range(len(matchers)):
                    matcher_element = matchers[m]
                    if matcher_element in list_element:
                        print("listen_eintrag", i, ": ", list_element)
                        print("excel_eintrag_name", m, ": ", matcher_element)
                        print("excel_eintrag_partei", m, ": ", second_col_Party[m])
                        politican_name = matcher_element
                        party_name = second_col_Party[m]

                        ''' Eintrag in DB Name + Partei'''

            ''' Anbindung API-Abgeordnetenwatch - JSON Data-Extract'''
            # import urllib.request, json
            # politican_name = politican_name.lower()
            # print(politican_name)
            # politican_name = politican_name.replace(' ','-')
            # print(politican_name)
            # with urllib.request.urlopen("https://www.abgeordnetenwatch.de/api/profile/"+politican_name+"/profile.json") as url:
            #     data = json.loads(url.read().decode())
            #     print(data)
            #     print(data['profile']['personal']['first_name']+ " " +data['profile']['personal']['last_name'])
            #     print(data['profile']['party'])

            ''' Eintrag in DB Name + Partei'''

    print("Liste mit Startnummern: ", list_with_startelement_numbers)
    # jede zweite Startnummer (= Ende) um 1 mindern für Ende einer Rede
    # [start:end:stop]
    # print(list_with_startelement_numbers[1::2])
    for value in range(1, len(list_with_startelement_numbers), 2):
        list_with_startelement_numbers[value] = list_with_startelement_numbers[value]-1
        #print(list_with_startelement_numbers)
    list_with_startEnd_numbers = list_with_startelement_numbers      # list_with_startEnd_numbers enthält Start und Ende item(Nummern) aller Redetexte
    print("Liste mit Start + Endnummern: ", list_with_startEnd_numbers)

    for item in range(len(cleanList)):
        element = cleanList[item]
        #print("item at index", item, ":", element)

    alle_Reden = []
    x = 0
    y = 1
    start = 1
    print(len(list_with_startEnd_numbers))
    end = len(list_with_startEnd_numbers)-1
    active = True
    while active:
        print("x: ", x)
        print("y: ", y)
        print("start: ", start)
        if start > end:
            active = False
            print("false")
        else:
            alle_Reden.append(cleanList[list_with_startEnd_numbers[x]:list_with_startEnd_numbers[y]])  # [alle zwischen Start:Ende]
            #print("weiter")
            #print("start: ", start)
        x += 2
        y += 2
        start += 2

    # Ausgabe aller Reden
    for rede in alle_Reden:
        print(rede)
        print("\n")



        #textFile.write(list_element+"\n")





''' xxxxxxxxxxxxxxxxxxxxxxxxxxx   Dictionary befuellen   xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx '''
#start with an empty list
dl_protocol = []

# make a new dic for datarow and add them to the list
datarow = {'tag':'',
       'top':'',
       'thema':'',
       'politiker': '',
       'partei': '',
       'redetext':''
       }
dl_protocol.append(datarow)
print(dl_protocol)
# Show all information about each datarow.
for datarows in dl_protocol:
    for k, v in datarow.items():
        print(k + ": " + v)
    print("\n")

# neues dic für jeden neuen Datensatz

datarow['tag']


''' xxxxxxxxxxxxxxxxxxxxxxxxxxx   Datenbank befuellen   xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx '''









''' xxxxxxxxxxxxxxxxxxxxxxxxx   Analyse Redetext - Haufigkeit und lexikalische Diversitaet   xxxxxxxxxxxxxxxxxxxxxxxxxxxx '''

def clean_and_getFrequenz(wordlist):
    words = word_tokenize(str(wordlist))
    # RedeText enthealt noch  „!“, „,“, „.“ und Doppelungen und so weiter
    print("Anzahl aller Woerter und Zeichen: " + str(len(words)))
    # saebern des RedeTextes von Zeichen !!! ABER !!! doppelte Woerter lassen, da die Haeufigkeit spaeter gezaehlt werden soll
    cleaned_speech = [word for word in words if word.isalpha()]
    print("Anzahl aller Woerter - AUCH DOPPELTE ohne Zeichen: " + str(len(cleaned_speech)))
    return cleaned_speech

def count_and_viz_seldom_frequently(freq_CleandedSpeech):
    # 30 haeufigsten und seltensten Woerter einer gesaeuberten Rede
    dc_sort = (sorted(freq_CleandedSpeech.items(), key= operator.itemgetter(1), reverse = True))   # sortiertes dictionary - beginnend mit groeßter Haeufigkeit
    print(dc_sort[:30])                         # 30 haeufigsten Woerter (Wort: Anzahl)
    print([str(w[0]) for w in dc_sort[:30]])    # 30 haeufigsten Woerter (nur Wort)
    print(dc_sort[-30:])                        # 30 seltensten Woerter (Wort: Anzahl)
    print([str(w[0]) for w in dc_sort[-30:]])   # 30 seltensten Woerter (nur Wort)

    # Wir koennen uns auch eine kummulative Verteilungsfunktion grafisch anzeigen lassen. Dazu können wir die plot()-Methode
    # auf dem fdist1-Objekt anwenden. Dazu muss jedoch das Modul matplotlib installiert sein!
    freq_CleandedSpeech.plot(30, cumulative=True)

def lex_div_with_and_without_stopwords(wordlist, cleaned_speech):
    ###### Lexikalische Diversität eines Redners - Vielzahl von Ausdrucksmöglichkeiten #######
    # Die Diversität ist ein Maß für die Sprachvielfalt. Sie ist definiert als Quotient der „verschiedenen Wörter“ dividiert durch die „Gesamtanzahl von Wörtern“ eines Textes.

    # Redetext mit stop words
    freq_CleandedSpeech_with_stopwords = FreqDist(cleaned_speech)           # methode FreqDist() - Ermittlung der Vorkommenshaeufigkeit der Woerter im gesaeuberten RedeText
    print(freq_CleandedSpeech_with_stopwords)
    #freq_CleandedSpeech_with_stopwords.tabulate()                           # most high-frequency parts of speech
    count_and_viz_seldom_frequently(freq_CleandedSpeech_with_stopwords)     # Visualisieren der haufigsten und seltensten Woerter inclusive stopwords

    complete_text_with_doubles = list(freq_CleandedSpeech_with_stopwords)        # noch doppelte Woerter enthalten
    diff_words = set(complete_text_with_doubles)                                 # "diff_words" enthaelt keine doppelten Woerter mehr
    diversity_with_stopwords = len(diff_words) / float(len(complete_text_with_doubles))

    # Redetext ohne stop words
    stop_words = set(stopwords.words("german"))
    print("\n" + "STOPWORDS: " + "\n" + str(stop_words) + "\n")

    clean_without_stopwords = [word for word in cleaned_speech if not word in stop_words]                       # herausfiltern der stopwords
    freq_Cleanded_without_stopwords =  FreqDist(clean_without_stopwords)                                        # Neuzuweisung: methode FreqDist() - Ermittlung der Vorkommenshaeufigkeit der Woerter im gesaeuberten RedeText ohne stopwords
    #freq_Cleanded_without_stopwords.tabulate()                                                                  # most high-frequency parts of speech
    complete_text_with_doubles_without_stopwords = list(freq_Cleanded_without_stopwords)
    diff_words_without_doubles = set(complete_text_with_doubles_without_stopwords)                              # "diff_words_without_doubles" enthaelt keine doppelten Woerter mehr
    diversity_without_stopwords = len(diff_words_without_doubles) / float(len(complete_text_with_doubles_without_stopwords))

    print(freq_Cleanded_without_stopwords)
    count_and_viz_seldom_frequently(freq_Cleanded_without_stopwords)  # Visualisieren der haufigsten und seltensten Woerter ohne stopwords

    name = "Redner: " + 'xxxxxxxxxxxxxxxxxxxx'
    print(name)
    print("different words:    {0:8d}".format(len(diff_words)))                                     # Anzahl unterschiedlich einmalig genutzter Woerter
    print("words:              {0:8d}".format(len(wordlist)))                                       # Anzahl genutzter Woerter
    print("lexical diversity with stopwords:  {0:8.2f}".format(diversity_with_stopwords))           # Prozentsatz fuer die Sprachvielfalt mit stopwords
    print("lexical diversity without stopwords:  {0:8.2f}".format(diversity_without_stopwords))     # Prozentsatz fuer die Sprachvielfalt ohne stopwords

sys.stdout = Logger()
content = getContent()
wordlist = contentToList(content)
cleaned_Speech = clean_and_getFrequenz(wordlist)
lex_div_with_and_without_stopwords(wordlist, cleaned_Speech)
