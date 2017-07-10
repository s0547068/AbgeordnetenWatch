import nltk
from nltk import FreqDist
from nltk.corpus import stopwords
import operator
from nltk import sent_tokenize, word_tokenize
import csv
import codecs


# Rede
freq_CleandedSpeech = 'Ich hasse die Universität. Wir mögen die Universität. Langsam geht mir das echt auf die Nerven.'
# deutsche Stopwords
stop_words = set(stopwords.words("german"))
# Erweiterung der Stopwords
word_list_extension = ['Dass', 'dass', 'Der', 'Die', 'Das', 'Dem', 'Den', 'Wir', 'wir', 'Ihr', 'ihr', 'Sie', 'sie',
                       'Ich', 'ich', 'Er', 'er', 'Es', 'es', 'Du', 'du', '.', ',', '-', ':']
for word in word_list_extension:
    stop_words.add(word)

token_word_list = word_tokenize(freq_CleandedSpeech)
sentence_list = sent_tokenize(freq_CleandedSpeech)
# Redetext - # herausfiltern der stopwords
clean_without_stopwords = [word for word in token_word_list if
                           not word in stop_words]

print(clean_without_stopwords)
# Zählen der Häufigkeiten
freq_Cleanded_without_stopwords = FreqDist(clean_without_stopwords)
print(freq_Cleanded_without_stopwords)
samples = (sorted(freq_Cleanded_without_stopwords.items(), key=operator.itemgetter(1), reverse=True))  # sortiertes dictionary - beginnend mit groeßter Haeufigkeit
word_samples = samples[:10]
print(word_samples)


# Wörter inkl. der Gewichtung ihrer Ausdrucksstärke
training_set_pos=[]
data_pos = codecs.open('SentiWS_training_set/SentiWS_v1.8c_Positive.txt', 'r', 'utf-8')
poswords = csv.reader(data_pos, delimiter='|')
print(poswords)
training_set_pos.append([(pos[0].lower(), 'positive') for pos in poswords])

training_set_neg=[]
data_neg = codecs.open('SentiWS_training_set/SentiWS_v1.8c_Negative.txt', 'r', 'utf-8')
negwords = csv.reader(data_neg, delimiter='|')
print(negwords)
training_set_neg.append([(neg[0].lower(), 'negative') for neg in negwords])


liste_pos = []
for tupel_training in training_set_pos:
    for word_training in tupel_training:
        liste_pos.append(word_training[0])

print(liste_pos)

for tupel in word_samples:
    for ws in tupel:
        for item in liste_pos:
            if ws[0].__contains__(item):
                item = item

print(liste_pos)



# for word[0] in word_features:


# for word in samples:
#     for x in training_set

# def find_features(clean_without_stopwords):
#     words = set(clean_without_stopwords)
#     features = {}
#     for w in training_set:
#         features[w] = (w in words)
#     return features
#
# featureset = find_features(clean_without_stopwords)
# print(featureset)




