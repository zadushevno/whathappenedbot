import gensim
from gensim.models import word2vec
import pymorphy2
from nltk.tokenize import wordpunct_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import pymorphy2

stops = set(stopwords.words('russian') + ['это', 'весь', 'который', 'мочь', 'свой'])

morph = pymorphy2.MorphAnalyzer()


f = 'lemmas.txt'
data = gensim.models.word2vec.LineSentence(f)

model_news = gensim.models.Word2Vec(data, vector_size=300, window=5, min_count=2)

import urllib.request
urllib.request.urlretrieve("http://rusvectores.org/static/models/rusvectores2/ruscorpora_mystem_cbow_300_2_2015.bin.gz", "ruscorpora_mystem_cbow_300_2_2015.bin.gz")

m = 'ruscorpora_mystem_cbow_300_2_2015.bin.gz'

if m.endswith('.vec.gz'):
    model = gensim.models.KeyedVectors.load_word2vec_format(m, binary=False)
elif m.endswith('.bin.gz'):
    model = gensim.models.KeyedVectors.load_word2vec_format(m, binary=True)
else:
    model = gensim.models.KeyedVectors.load(m)

cotags = {'ADJF':'A', # pymorphy2: word2vec 
'ADJS' : 'A', 
'ADVB' : 'ADV', 
'COMP' : 'ADV', 
'GRND' : 'V', 
'INFN' : 'V', 
'NOUN' : 'S', 
'PRED' : 'V', 
'PRTF' : 'A', 
'PRTS' : 'V', 
'VERB' : 'V',
'NPRO' : 'SPRO',
'NUMR' : 'NUM',
'PREP' : 'PR',
'PRCL' : 'PART',
'CONJ' : 'CONJ'}

#эта функция ищет похожее слово в модели на основе НКРЯ
def search_similar_corpora(word, w_pos, gend='masc'):
    try:
        pos = cotags[w_pos]
        lex = word + '_' + pos
        if lex in model:
            similars = model.most_similar(lex)
            for sim in similars:
                sim_lex, sim_pos = sim[0].split('_')
                if sim_pos == pos:
                    if pos == 'NOUN':
                        parse_result = morph.parse(sim_lex)
                        for ana in parse_result:
                            if ana.normal_form == sim_lex:
                                if ana.tag.gender == gend:
                                    return sim_lex
                    elif pos == 'VERB' and word[-2:] == 'ся':
                        if sim_lex[-2:] == 'ся':
                            return sim_lex
                    elif pos == 'VERB' and word[-2:] != 'ся':
                        if sim_lex[-2:] != 'ся':
                            return sim_lex
                    else:
                        return sim_lex
        return None
    except:
        return None

#эта функция ищет похожее слово в новостной модели
def search_similar(word, pos, gend='masc'):
    if word in model_news.wv.key_to_index:
        similars = model_news.wv.most_similar(word)
        for sim in similars:
            sim_pos = morph.parse(sim[0])[0].tag.POS
            if sim_pos == pos:
                if pos == 'NOUN':
                    parse_result = morph.parse(sim[0])
                    for ana in parse_result:
                        if ana.normal_form == sim[0]:
                            if ana.tag.gender == gend:
                                return sim[0]
                elif pos == 'VERB' and word[-2:] == 'ся':
                    if sim[0][-2:] == 'ся':
                        return sim[0]
                elif pos == 'VERB' and word[-2:] != 'ся':
                    if sim[0][-2:] != 'ся':
                        return sim[0]
                else:
                    return sim[0]
    return None

#эта функция изменяет слово по характеристикам другого слова
def flect(word, similar, pos):
    try:
        ana = morph.parse(word)[0]
        ana_sim = morph.parse(similar)[0]
        if pos == 'NOUN':
            number = ana.tag.number
            case = ana.tag.case
            word_to_replace = ana_sim.inflect({number, case}).word
            return word_to_replace
        if pos == 'VERB':
            number = ana.tag.number
            tense = ana.tag.tense
            person = ana.tag.person
            if person:
                word_to_replace = ana_sim.inflect({number, tense, person}).word
                return word_to_replace
            else:
                gender = ana.tag.gender
                word_to_replace = ana_sim.inflect({gender, number, tense}).word
                return word_to_replace
        if pos in ['ADJF', 'ADJS']:
            case = ana.tag.case
            gender = ana.tag.gender
            number = ana.tag.number
            if gender:
                word_to_replace = ana_sim.inflect({number, gender, case}).word
                return word_to_replace
            else:
                word_to_replace = ana_sim.inflect({number, case}).word
                return word_to_replace 
    except:
        return None
    return None