import markovify
import nltk
import re

#немного улучшаем markovify
class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

#создаем модель
text = open('titles.txt', encoding='utf8').read()
text_model = markovify.Text(text, well_formed = False)
