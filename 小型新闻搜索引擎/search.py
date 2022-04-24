# 带有正文与搜索词余弦相似度的搜索
import jieba
import re
import numpy
from operator import itemgetter
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from create_indexes import Index


class Sim:
    def __init__(self, keywords, doc_list):
        self.keywords = keywords
        self.doc_list = doc_list
        self.tfidf = TFIDF()

    def cos(self, weight):
        vec1 = weight[0]
        cos_dict = {}
        for i in range(1, len(weight)):
            vec2 = weight[i]
            fenzi = sum(vec1 * vec2)
            fenmu1 = numpy.sqrt(sum(vec1 ** 2))
            fenmu2 = numpy.sqrt(sum(vec2 ** 2))
            cos = fenzi / (fenmu1 * fenmu2)
            cos_dict[i] = cos
        cos_dict = sorted(cos_dict.items(), key=itemgetter(1), reverse=True)
        # print(cos_dict)
        docs_list = []
        for cos in cos_dict:
            docs_list.append(cos[0])
        return docs_list

    def sim(self):
        words = ""
        seg_list = jieba.cut(self.keywords, cut_all=False)
        words += (" ".join(seg_list))
        # 用于保存每一篇正文与搜索关键词的相似度
        doc_dic = {}
        context_list = []
        context_list.append(words)
        for i, doc in enumerate(self.doc_list):
            context = doc.get('context')
            context = self.tfidf.fenci(context)
            context_list.append(context)
            doc_dic[i + 1] = doc
        # print(doc_dic)
        weight = self.tfidf.tfidf(context_list)
        # 返回向量相似度逆序排序结果，列表中每一个元素是一个元组，元组两个元素分别是 doc编号，以及向量相似度
        cos_list = self.cos(weight)
        docs_list = [doc_dic[i] for i in cos_list]
        return docs_list


class Search:
    def __init__(self, indexes):
        self.indexes = indexes

    def search(self, keywords):
        seg_list = []  # 用于保存对keyword_list中的关键词进行分词后的关键词
        # 将查询关键词以空格分割开
        keywords_list = keywords.split()

        for word in keywords_list:
            # 将分词后生成的列表加在seg_list上
            seg_list.extend(jieba.cut_for_search(word))
        url_list = []  # 用于保存与分词后的关键词相关的url
        for seg in seg_list:
            if seg in self.indexes.inverted:
                for url in self.indexes.inverted[seg]:
                    url_list.append(url)
        # doc_list保存的是 根据url_list中保存的url对应的doc对象
        doc_list = [self.indexes.forward[url] for url in url_list]
        sim = Sim(keywords, doc_list)
        doc_list = sim.sim()
        return doc_list


class TFIDF:

    def fenci(self, str):
        result = []
        seg_list = jieba.cut(str)
        for seg in seg_list:
            seg = ''.join(seg.split())
            # if seg !=',' and seg!='，' and seg != '?' and seg != '？' and seg != '\n' and seg !='\n\n' and seg != '':
            if seg not in ",`~!@#$%^&*()-_+={}[]|';:.?><，。？《》【】、：":
                result.append(seg)
        result = ' '.join(result)
        return result

    def tfidf(self, doc):
        vectorizer = CountVectorizer()
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(vectorizer.fit_transform(doc))
        word = vectorizer.get_feature_names_out()
        # print(word)
        weight = tfidf.toarray()
        tfidfdict = {}
        for i in range(len(weight)):
            for j in range(len(word)):
                getWord = word[j]
                getValue = weight[i][j]
                if getValue != 0:
                    if tfidfdict.__contains__(getWord):
                        tfidfdict[getWord] += float(getValue)
                    else:
                        tfidfdict.update({getWord: getValue})
        # print(tfidfdict)
        # sorted_tdidf = sorted(tfidfdict.items(), key=lambda d: d[1], reverse=True)
        # print(sorted_tdidf)
        # print(tfidfdict)
        # return weight
        return weight


class create_extract:
    def __init__(self, str, len, keywords):
        self.str = str
        self.len = len
        self.keywords = keywords

    def fenci(self):
        result = []
        seg_list = jieba.cut(self.str)
        for seg in seg_list:
            seg = ''.join(seg.split())
            # if seg !=',' and seg!='，' and seg != '?' and seg != '？' and seg != '\n' and seg !='\n\n' and seg != '':
            if seg not in ",`~!@#$%^&*()-_+={}[]|';:.?><，。？《》【】、：":
                result.append(seg)
        return result

    def tfidf(self, doc):
        vectorizer = CountVectorizer()
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(vectorizer.fit_transform(doc))
        word = vectorizer.get_feature_names_out()
        # print(word)
        weight = tfidf.toarray()
        tfidfdict = {}
        for i in range(len(weight)):
            for j in range(len(word)):
                getWord = word[j]
                getValue = weight[i][j]
                if getValue != 0:
                    if tfidfdict.__contains__(getWord):
                        tfidfdict[getWord] += float(getValue)
                    else:
                        tfidfdict.update({getWord: getValue})
        # print(tfidfdict)
        # sorted_tdidf = sorted(tfidfdict.items(), key=lambda d: d[1], reverse=True)
        # print(sorted_tdidf)
        # print(tfidfdict)
        # return weight
        return tfidfdict

    def get_pos(self, words):
        pos_list = []  # 关键词在文本中的位置
        for word in words:
            word_list = [i.start() for i in re.finditer(word, self.str)]
            pos_list.extend(word_list)
        pos_list.sort()
        return pos_list

    def get_text(self, pos_list):
        x = self.len  # 分割长度
        result = []
        for i in pos_list:
            text = self.str[i:i + x]
            result.append(text)
        # print(result)
        return result

    def get_score(self, words, tfidf_dict, text_list):
        score_dic = {}
        for i, line in enumerate(text_list):
            if i not in score_dic:
                score_dic[i] = 0
            score = 0
            for word in words:
                try:
                    count = [i.start() for i in re.finditer(word, self.str)]
                    score += tfidf_dict[word] * len(count)
                except:
                    continue
            score_dic[i] = score
        # 对字典的按照value值降序排列
        score_dic = sorted(score_dic.items(), key=itemgetter(1), reverse=True)
        return score_dic

    def process(self):
        # 对查询关键词进行分词处理，处理后保存到一个列表words当中
        words = ""
        seg_list = jieba.cut(self.keywords, cut_all=False)
        words += (" ".join(seg_list))
        words = words.split()
        # do 为分词之后返回的列表
        do = self.fenci()
        # 获取该文本中每个词的的tfidf值，数据类型为一个字典
        tfidf_dict = self.tfidf(do)
        # 获取words在正文中出现的位置
        pos_list = self.get_pos(words)
        # 如果在正文中存在关键词
        if len(pos_list) != 0:
            text_list = self.get_text(pos_list)
        else:
            text_list = self.get_text([50])
        # 窗口打分
        score_list = self.get_score(words, tfidf_dict, text_list)
        # 获取分值最高的窗口并返回
        max_text = text_list[score_list[0][0]]
        # print(max_text)
        return max_text


class Result:
    def __init__(self, index, keywords, len):
        self.keywords = keywords
        self.len = len
        # self.index = Index(path)
        # self.search = Search(self.index)
        self.search = Search(index)
        self.doc_list = self.search.search(self.keywords)

    def get_result(self):
        total_result = []
        for doc in self.doc_list:
            data = []
            url = doc.get('url')
            title = doc.get('title')
            context = doc.get('context')
            data.append(url)
            data.append(title)

            extract = create_extract(context, self.len, self.keywords)
            max_text = extract.process()
            data.append(max_text)
            total_result.append(data)
        return total_result


if __name__ == '__main__':
    pass
    # index = Index('./content/')
    # search = Search(index)
    # doc_list = search.search('北京城市')
    # for doc in doc_list:
    #     # print('doc')
    #     url = doc.get('url')
    #     title = doc.get('title')
    #     context = doc.get('context')
    #     extract = create_extract(context, 50, '北京城市')
    #     extract.process()

    # index = Index('./content/')
    # result = Result(index, '詹姆斯', 100)
    # doc_list = result.get_result()
    # for doc in doc_list:
    #     print(doc[0], doc[1], doc[2])
