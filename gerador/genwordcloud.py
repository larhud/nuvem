
import sys
import os
import re
import glob
import csv

from collections import Counter
from wordcloud import WordCloud, ImageColorGenerator
from django.conf import settings


def generate_words(nome_arquivo, language='pt', mask=None, color=False, font_type=None, colormap=None):
    prefix, file_extension = os.path.splitext(nome_arquivo)

    try:
        arquivo = open(nome_arquivo, 'r')
    except UnicodeDecodeError as erro:
        arquivo = open(nome_arquivo, 'r', encoding='ISO-8859-1')

    frequencia = Counter()
    for linha in arquivo.readlines():
        for key in linha.split(','):
            keyword = key.strip().capitalize()
            if keyword:
                frequencia[keyword] += 1
    arquivo.close()

    # Gera o arquivo CSV com as frequências
    csv_filename = prefix + '.csv'
    with open(csv_filename, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for item in frequencia.items():
            writer.writerow(item)

    cloud = WordCloud(width=1200, height=800, max_words=100, scale=1, background_color='white', mask=mask,
                      font_path=os.path.join(settings.FONT_PATH, font_type), colormap=colormap,
                      max_font_size=90, random_state=42)

    cloud.generate_from_frequencies(frequencia)

    if mask is not None and color:
        image_colors = ImageColorGenerator(mask)
        cloud.recolor(color_func=image_colors)

    cloud.to_file(prefix + '.png')

    image_filename = os.path.basename(prefix)
    image_filename = os.path.join(settings.MEDIA_URL, 'output', image_filename + '.png')
    return image_filename


def generate(nome_arquivo, stopwords=None, language='pt', mask=None, color=False, font_type=None, colormap=None):
    excecoes = []
    sw_filename = os.path.join(settings.BASE_DIR, 'gerador', 'stopwords-%s.txt' % language)
    if language and os.path.exists(sw_filename):
        for linha in open(sw_filename).read().lower().split('\n'):
            for palavra in linha.split(','):
                excecoes.append(palavra.strip())

    if stopwords:
        for palavra in stopwords.split(','):
            excecoes.append(palavra.strip())

    try:
        arquivo = open(nome_arquivo, 'r')
    except UnicodeDecodeError as erro:
        arquivo = open(nome_arquivo, 'r', encoding='ISO-8859-1')

    # Busca cabeçalhos e rodapés
    frequencia = Counter()
    for linha in arquivo.read().lower().split('\n'):
        if len(linha.strip()) > 3:
            frequencia[linha] += 1
    arquivo.close()

    duplicadas = {}
    for linha in frequencia.most_common():
        if linha[1] > 3:
            duplicadas[linha[0]] = 0
        else:
            break

    prefix, file_extension = os.path.splitext(nome_arquivo)
    arq_limpo = open(prefix + '.dedup', 'w', encoding='utf-8')
    frequencia = Counter()
    for linha in open(nome_arquivo, 'r').read().lower().split('\n'):
        if linha not in duplicadas:
            texto = ''
            for palavra in re.findall(r'\w+', linha):
                # Monta o texto final remove as palavras da lista de exceções e que sejam menores que 3 caracteres
                if len(palavra) > 3 and palavra not in excecoes and not palavra.isdigit():
                    frequencia[palavra] += 1
                    texto += ' ' + palavra
            if texto.strip() != '':
                arq_limpo.write(texto + '\n')
    arq_limpo.close()

    # Gera o arquivo CSV com as frequências
    csv_filename = prefix + '.csv'
    with open(csv_filename, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for item in frequencia.most_common(1000):
            writer.writerow(item)

    def black_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return "hsl(0,100%, 1%)"

    cloud = WordCloud(width=1200, height=800, max_words=100, scale=4, background_color='white', colormap=colormap,
                      mask=mask, min_font_size=5, max_font_size=150, random_state=40,
                      font_path=os.path.join(settings.FONT_PATH, font_type))

    cloud.generate_from_frequencies(frequencia)
    # cloud.recolor(color_func=black_color_func)

    if mask is not None and color:
        image_colors = ImageColorGenerator(mask)
        cloud.recolor(color_func=image_colors)

    cloud.to_file(prefix+'.png')

    # plt.imshow(cloud, interpolation="bilinear")
    # plt.axis("off")
    # plt.savefig(prefix+'.png')

    image_filename = os.path.basename(prefix)
    image_filename = os.path.join(settings.MEDIA_URL, 'output', image_filename+'.png')
    return image_filename


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = None
    if filename and os.path.isfile(filename):
        generate(filename)
    else:
        for filename in glob.glob("files/*.txt"):
            generate(filename)