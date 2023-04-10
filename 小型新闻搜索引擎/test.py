from flask import Flask, request, render_template, redirect, url_for
import jieba
from search import Result
from create_indexes import Index

app = Flask(__name__, static_url_path='')


@app.route("/", methods=['POST', 'GET'])
def main():
    if request.method == 'POST' and request.form.get('query'):
        query = request.form['query']
        return redirect(url_for('search', query=query))

    return render_template('index.html')


@app.route("/search/<query>", methods=['POST', 'GET'])
def search(query):
    result = Result(index, query, 100)
    doc_list = result.get_result()
    words = list(jieba.cut_for_search(query))
    doc_list = words_highlight(doc_list,words)
    return render_template('search.html', doc_list=doc_list, value=query, length=len(doc_list))


def words_highlight(doc_list, words):
    for doc in doc_list:
        for word in words:
            title = doc[1]
            context = doc[2]
            doc[1] = title.replace(word, '<em><font color="red">{}</font></em>'.format(word))
            doc[2] = context.replace(word, '<em><font color="red">{}</font></em>'.format(word))
    return doc_list

if __name__ == "__main__":
    global index
    index = Index('./download_file/')
    app.run(host='localhost', port=722, debug=False)
    #app.run()

