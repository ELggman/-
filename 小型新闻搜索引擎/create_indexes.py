import os
import jieba


# 使用类对象来保存每一个网页的链接、标题、正文
class Doc:
    def __init__(self):
        self.dic = {}

    # 往类对象里面添加数据
    def add(self, key, content):
        self.dic[key] = content

    # 获取类对象指定键值的数据
    def get(self, key):
        return self.dic[key]


class Index:
    inverted = {}  # 倒排索引
    forward = {}  # 正排索引，使用url作为key值，doc类对象作为value值
    idf = {}  # 记录idf值

    def __init__(self, file_path):
        self.doc_list = []
        self.read_content(file_path)
        self.create_indexes()

    # 从爬回来的的数据读取，并将其保存到Doc类对象中
    def read_content(self, file_path):
        # 获取 路径下的所有文件名，进行遍历读取数据
        for filename in os.listdir(file_path):
            try:
                with open(file_path + filename, 'r', encoding='utf-8') as fp:
                    # 爬取的数据文件保存的格式为 url、标题、正文。中间使用\t\t分隔
                    url, title, context = fp.read().split('\t\t')
            except:
                continue
            # 实例化一个Doc类对象，并将数据保存到对象中
            doc = Doc()
            doc.add('url', url)
            doc.add('title', title)
            doc.add('context', context)
            self.doc_list.append(doc)

    # 生成索引
    def create_indexes(self):
        doc_num = len(self.doc_list)

        for doc in self.doc_list:
            url = doc.get('url')
            titile = doc.get('title')
            # 使用url作为key来建立正排索引
            self.forward[url] = doc
            # 建立倒排索引
            seg_list = jieba.cut_for_search(titile)  # 对标题进行分词
            for seg in seg_list:
                # 当前词seg是否已经在倒排索引inverted的键值中
                if seg in self.inverted:
                    # 判断当前的url是否在inverted[seg]的键值中
                    if url in self.inverted[seg]:
                        # 如果在，那么seg词在该url中出现的次数加一
                        self.inverted[seg][url] += 1
                    else:
                        # 如果不在，就该url加入到inverted[seg]中，并使出现次数为1
                        self.inverted[seg][url] = 1
                else:
                    # 如果该seg词尚未存在于inverted的键值中，则将该seg加入其中，其value值为当前的url，以及出现次数1
                    self.inverted[seg] = {url: 1}
        print(f'inverted doc number:{len(self.inverted)}')


if __name__ == '__main__':
    index = Index('./content/')
    #print(index.inverted)
    print('inverted finished')
    # li = ['北京', '城市']
    # for l in li:
    #     for doc_id, fre in index.inverted[l].items():
    #         print(doc_id, fre)
    #     print('*'*20)
