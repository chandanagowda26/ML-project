from __future__ import unicode_literals
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from bs4 import BeautifulSoup
import os
import joblib
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from rouge_score import rouge_scorer
from spacy_summarization import text_summarizer
from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords
#from summarization import summarize
from nltk_summarization import nltk_summarizer
import time
import spacy
import PyPDF2
from collections.abc import Mapping
nlp = spacy.load('en_core_web_sm')
# from werkzeug import secure_filename
app = Flask(__name__)
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['pdf'])
app.config['UPLOAD_FOLDER'] = "static/"
# Web Scraping Pkg
# from urllib.request import urlopen
# from urllib3  import urlopen

# Sumy Pkg
# Sumy


def sumy_summary(docx):
    parser = PlaintextParser.from_string(docx, Tokenizer("english"))
    lex_summarizer = LexRankSummarizer()
    summary = lex_summarizer(parser.document, 3)
    summary_list = [str(sentence) for sentence in summary]
    result = ' '.join(summary_list)
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    scores = scorer.score(docx, result)
    return result, scores


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower  in ALLOWED_EXTENSIONS

# Reading Time


def readingTime(mytext):
    total_words = len([token.text for token in nlp(mytext)])
    estimatedTime = total_words/200.0
    return estimatedTime

# Fetch Text From Url


def get_text(url):
    page = urlopen(url)
    soup = BeautifulSoup(page)
    fetched_text = ' '.join(map(lambda p: p.text, soup.find_all('p')))
    return fetched_text


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sum')
def sum():
    return render_template('sum.html')


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    start = time.time()
    if request.method == 'POST':
        send_data = request.files['send_data']
    if send_data :
        filename = secure_filename(send_data.filename)
        send_data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        pdf_file_obj = open('static/' + filename, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
        x = len(pdf_reader.pages)
        rawtext=" "
        for i in range(x):
            page_obj = pdf_reader.pages[i]
            rawtext = rawtext+ page_obj.extract_text()
        final_reading_time = readingTime(rawtext)
        final_summary, score_spacy = text_summarizer(rawtext)
        summary_reading_time = readingTime(final_summary)
        end = time.time()
        final_time = end-start

        # final_reading_time = readingTime(rawtext)
        # final_summary = text_summarizer(rawtext)
        # summary_reading_time = readingTime(final_summary)
        # end = time.time()
        # final_time = end-start
    return render_template('sum.html', ctext=rawtext, final_summary=final_summary, final_time=final_time, final_reading_time=final_reading_time, summary_reading_time=summary_reading_time)

# def analyze():
# 	start = time.time()
# 	if request.method == 'POST':
# 		send_data = request.files['send_data']
#     # return render_template('index.html',ctext=rawtext,final_summary=final_summary,final_time=final_time,final_reading_time=final_reading_time,summary_reading_time=summary_reading_time)
#         # if send_data and allowed_file(send_data.filename):
#             # send_data.save(os.path.join(app.config['UPLOAD_FOLDER'],send_data.filename))
#
#
#
# 		final_reading_time = readingTime(rawtext)
# 		final_summary = text_summarizer(rawtext)
# 		summary_reading_time = readingTime(final_summary)
# 		end = time.time()
# 		final_time = end-start
#         # send_data = request.files['send_data']
    # if send_data and allowed_file(send_data.filename):
    # filename = secure_filename(send_data.filename)
    # send_data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # pdf_file_obj = open('uploads/' + filename, 'rb')
    # pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
    # page_obj = pdf_reader.getPage(0)
    # rawtext = page_obj.extractText()
    # final_reading_time = readingTime(rawtext)
    # final_summary = text_summarizer(rawtext)
    # summary_reading_time = readingTime(final_summary)
    # end = time.time()
    # final_time = end-start
    # return render_template('index.html',ctext=rawtext,final_summary=final_summary,final_time=final_time,final_reading_time=final_reading_time,summary_reading_time=summary_reading_time)

# @app.route('/analyze_url',methods=['GET','POST'])
# def analyze_url():
# 	start = time.time()
# 	if request.method=='POST':
# 		raw_url = request.form['raw_url']
# 		rawtext = get_text(raw_url)
# 		final_reading_time = readingTime(rawtext)
# 		final_summary = text_summarizer(rawtext)
# 		summary_reading_time = readingTime(final_summary)
# 		end = time.time()
# 		final_time = end-start
# 	return render_template('index.html',ctext=rawtext,final_summary=final_summary,final_time=final_time,final_reading_time=final_reading_time,summary_reading_time=summary_reading_time)


@app.route('/compare_summary')
def compare_summary():
    return render_template('compare_summary.html')

# and request.mimetype == 'multipart/form-data'
@app.route('/comparer', methods=['GET', 'POST'])
def comparer():
    start = time.time()
    if request.method == 'POST':
        send_data = request.files['send_data']
        if send_data :
            filename = secure_filename(send_data.filename)
            send_data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pdf_file_obj = open('static/' + filename, 'rb')
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
            x = len(pdf_reader.pages)
            rawtext=" "
            for i in range(x):
                page_obj = pdf_reader.pages[i]
                rawtext = rawtext+ page_obj.extract_text()
            final_reading_time = readingTime(rawtext)
            # SpaCy
            final_summary_spacy, score_spacy = text_summarizer(rawtext)
            summary_reading_time = readingTime(final_summary_spacy)
            # Gensim Summarizer
            final_summary_gensim = summarize(rawtext)
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
            scores = scorer.score(final_summary_gensim, rawtext)
            summary_reading_time_gensim = readingTime(final_summary_gensim)
            # NLTK
            final_summary_nltk, score_nltk = nltk_summarizer(rawtext)
            summary_reading_time_nltk = readingTime(final_summary_nltk)
            # Sumy
            final_summary_sumy, score_sumy = sumy_summary(rawtext)
            recal_sumy = score_sumy
            summary_reading_time_sumy = readingTime(final_summary_sumy)

            end = time.time()
            final_time = end-start
    return render_template('compare_summary.html', r_gensim=scores, r_nltk=score_nltk, r_spacy=score_spacy, r_sumy=recal_sumy, ctext=rawtext, final_summary_spacy=final_summary_spacy, final_summary_gensim=final_summary_gensim, final_summary_nltk=final_summary_nltk, final_time=final_time, final_reading_time=final_reading_time, summary_reading_time=summary_reading_time, summary_reading_time_gensim=summary_reading_time_gensim, final_summary_sumy=final_summary_sumy, summary_reading_time_sumy=summary_reading_time_sumy, summary_reading_time_nltk=summary_reading_time_nltk)


@app.route('/classify')
def classify():
    return render_template('Classification.html')


@app.route('/classi', methods=['GET', 'POST'])
def classi():
    if request.method == 'POST':
        send_data = request.files['send_data']
        if send_data :
            filename = secure_filename(send_data.filename)
            send_data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pdf_file_obj = open('static/' + filename, 'rb')
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
            x = len(pdf_reader.pages)
            rawtext=" "
            for i in range(x):
                page_obj = pdf_reader.pages[i]
                rawtext = rawtext+ page_obj.extract_text()
            clf = joblib.load("class1.sav")
            vect = joblib.load("vectorizer1.sav")
            input_data_features = vect.transform([rawtext]).toarray()
            prediction = clf.predict(input_data_features)
            for i in prediction:
                pre="The Classified Medical Speciality is " +i
    return render_template('Classification.html', c=pre)


@app.route('/about')
def about():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
