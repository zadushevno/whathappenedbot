from wordcloud import WordCloud
import matplotlib.pyplot as plt
f = 'lemmas.txt'
text = f.read()
wordcloud = WordCloud(
    background_color ='white',
    width = 800,
    height = 800, 
).generate(text)

plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud)
plt.axis("off") 
plt.title('Облако слов')
plt.show()