import time

from bs4 import BeautifulSoup
import re
import string
import os
import pandas as pd
import numpy as np
from keybert import KeyBERT
from pytrends.request import TrendReq
from mysql_config import MY_SQL

class Extract:
    def __init__(self):
        self.snp_list = []
        self.ticker_cik_dict = {}
        self.cik_ticker_dict ={}
        self.ticker_list = []
        self.keywords_list = []
        self.trends_df = None
        self.keywords_col_list = []
        self.MYSQL_GOOGLE_TRENDS = 'keywords_google_trend_data'
        self.my_sql = MY_SQL

    ########################################### M A I N ########################################################
    def keyword_extraction(self):
        #read and extract mdna sections
        self._read_snp_500_list()
        self._read_cik_list()
        self._save_mdna_section()
        self._extract_using_keybert()
        self._get_google_trends_results()
        self._add_google_trend_results_to_db()

        ##preprocess text in mdna txts


        #extract keywords from the reports
        #다만, mdna에 없는 연도의 경우,


    ###########################################################################################################
    def _read_snp_500_list(self):
        def _read_snp_500_list(self):
            # THESE ARE THE TICKERS THAT HAD ERRORS...
            # ['ANTM', 'BRK.B', 'BF.B', 'DISCA', 'FB', 'MAA', 'REG', 'VIAC']

            f = open('snp500_list.txt', 'r', encoding='UTF-8')
            list = []
            for line in f:
                n = line.split(',')
                list.append(n[0])
            self.snp_list = list[1:]

    def _read_cik_list(self):
        for line in open('cik_ticker.csv', 'r', encoding='UTF-8'):
            row = line.split('|')
            ticker = row[1]
            cik = row [0]
            self.ticker_cik_dict[ticker] = cik
            self.cik_ticker_dict[cik] = ticker
            self.ticker_list.append(ticker)

    def _load_10k_reports(self):
        pass

    def _check_comp_code(self):
        tickers = ['AMZN', 'AAPL', 'TSLA']
        for tic in tickers:

            print(self.cik_ticker_dict[tic])

    def _get_mdna_section(self, report_file_path):
        report = open(report_file_path, encoding='UTF8').read()

        if '<html>' in report:
            is_html = True
        else:
            is_html = False

        # Extract only 10k from the whole report
        # doc = report[report.lower().index('<document>')+len('<document>'):report.lower().index('</document>')]
        doc = report

        if not is_html:
            doc = doc.replace('\n', '\n<new line>')

        # Clean file
        cleantext = BeautifulSoup(doc, "lxml").getText(separator=u' ')

        cleantext = cleantext.replace('item', '\nitem')
        cleantext = cleantext.replace('Item', '\nItem')
        cleantext = cleantext.replace('ITEM', '\nITEM')

        # Getting business section from cleaned file
        s, s1, s2 = 0, 0, 0
        e, e1, e2 = 0, 0, 0

        text = ""
        flag_business_toc = 0

        lines = cleantext.splitlines()

        for i, line in enumerate(lines):
            line = re.sub("\.", "", line)
            temp_split_line = line.lower().split()
            # print(i, temp_split_line)

            if "item" in temp_split_line and "7" in temp_split_line and "management" in line.lower() \
                    and "discussion and analysis" in line.lower() and len(temp_split_line) <= 15:
                # found item business once before
                if flag_business_toc == 1:
                    # print("\t\ts2:", i, line[:200])
                    s2 = i
                    flag_business_toc += 1

                else:
                    # print("\t\ts1:", i, line[:200])
                    s1 = i
                    flag_business_toc += 1

            if "item" in temp_split_line and "8" in temp_split_line and "financial" in temp_split_line \
                    and "statements" in temp_split_line and len(temp_split_line) <= 15:
                if flag_business_toc == 2:
                    e2 = i
                    # print("\t\te2:", i, line[:200])
                    break

                else:
                    # print("\t\te1:", i, line[:200])
                    e1 = i

        # If we couldnt find anythin
        if s1 == 0 and s2 == 0:
            return ''

        # fetched some text
        if e2 - s2 > 20:
            s, e = s2, e2
            text = "".join(line for line in lines[s2:e2 + 1] if "table of content" not in line.lower())

        # fetched some text
        elif e1 - s1 > 20:
            s, e = s1, e1
            text = "".join(line for line in lines[s1:e1 + 1] if "table of content" not in line.lower())

        if not text:
            if s1 - e1 < 10:
                md_title = lines[s1].strip().rstrip(string.digits)[15:]
                fs_title = lines[e1].strip().rstrip(string.digits)[15:]

                cleantext = cleantext.replace(md_title, md_title + '\n')
                cleantext = cleantext.replace(fs_title, fs_title + '\n')

                # Getting business section from cleaned file
                s, s1, s2 = 0, 0, 0
                e, e1, e2 = 0, 0, 0

                text = ""
                flag_business_toc = 0

                lines = cleantext.splitlines()

                for i, line in enumerate(lines):
                    line = re.sub("\.", "", line)
                    temp_split_line = line.lower().split()
                    # print(i, temp_split_line)

                    if "item" in temp_split_line and "7" in temp_split_line and "management" in line.lower() \
                            and "discussion and analysis" in line.lower() and len(temp_split_line) <= 15:
                        # found item business once before
                        if flag_business_toc == 1:
                            # print("\t\ts2:", i, line[:200])
                            s2 = i
                            flag_business_toc += 1

                        else:
                            # print("\t\ts1:", i, line[:200])
                            s1 = i
                            flag_business_toc += 1

                    if "item" in temp_split_line and "8" in temp_split_line and "financial" in temp_split_line \
                            and "statements" in temp_split_line and len(temp_split_line) <= 15:
                        if flag_business_toc == 2:
                            e2 = i
                            # print("\t\te2:", i, line[:200])
                            break

                        else:
                            # print("\t\te1:", i, line[:200])
                            e1 = i

                # fetched some text
                if e2 - s2 > 20:
                    s, e = s2, e2
                    text = "".join(line for line in lines[s2:e2 + 1] if "table of content" not in line.lower())

                # fetched some text
                elif e1 - s1 > 20:
                    s, e = s1, e1
                    text = "".join(line for line in lines[s1:e1 + 1] if "table of content" not in line.lower())

                text = text.replace(md_title, md_title + '\n', 1)

        if not is_html:
            text = text.replace('\n<new line>', ' ')

        return text

    def _save_mdna_section(self):
        filing_path = './10k_reports'
        mdna_path = './mdna_dataset'
        mdna_stats_path = './mdna_stats.txt'

        mdna_stats = open(mdna_stats_path, 'w', encoding='UTF8')
        mdna_stats.write('cik\tticker\tyear\n')

        cik_folders = os.listdir(filing_path)
        for cik in cik_folders:
            ticker = self.cik_ticker_dict[cik]
            if not os.path.exists(mdna_path + '/' + cik):
                os.makedirs(mdna_path + '/' + cik)

            years = os.listdir(filing_path + '/' + cik)

            for year in years:
                year_text = year.split('.')[0]
                report_path = filing_path + '/' + cik + '/' + year
                mdna_text = self._get_mdna_section(report_path)

                if mdna_text:
                    print('Writing: ' + str(cik) + '    ' + str(year))
                    with open(mdna_path + '/' + cik + '/' + year, 'w', encoding='UTF8') as f:
                        f.write(mdna_text)

                    mdna_stats.write(cik + '\t' + ticker + '\t' + year_text + '\n')
                else:
                    print('Not Found: ' + str(cik) + '    ' + str(year))
                    continue
                # print('MD&A section not found for ' + cik + ' for year ' + year)

    # def _preprocess_txt_one_by_one(self, text):
    #     #only put preprocessiong related codes here
    #     #given single set of text
    #     tokens = [word for sent in nltk.sent_tokenize(text)
    #           for word in nltk.word_tokenize(sent)]
    #
    #     stopwords_list = stopwords.words('english')
    #     tokens = [token for token in tokens if token not in stopwords_list]
    #     tokens = [word for word in tokens if len(word) >= 2]
    #     tokens = [word.lower() for word in tokens]
    #     lmtzr = WordNetLemmatizer()
    #     tokens = [lmtzr.lemmatize(word) for word in tokens]
    #     tokens = [lmtzr.lemmatize(word, 'v') for word in tokens]
    #     stemmer = PorterStemmer()
    #     tokens = [stemmer.stem(word) for word in tokens]
    #
    #     return tokens

    def _extract_using_keybert(self):
        #note that we only extract from the latest reports
        mdna_path = './mdna_dataset'
        cik_list = os.listdir(mdna_path)
        key_path = './keyword_dataset'
        # kw_model = KeyBERT('distilbert-base-nil-mean_tokens')
        kw_model = KeyBERT()

        for cik in cik_list:
            if not os.path.exists(key_path + '/' + cik):
                os.makedirs(key_path + '/' + cik)

            years = os.listdir(mdna_path + '/' + cik)
            latest_year = years[-1]

            report_path = mdna_path + '/' + cik + '/' + latest_year
            report = open(report_path, encoding='UTF-8').read()
            # print('Company: ', cik, ' Year: ', latest_year)
            keywords = kw_model.extract_keywords(report, stop_words='english', top_n=5)

            self._add_to_keywords_list(keywords)

            # print(keywords)
            # print('\n')

    def _add_to_keywords_list(self, keywords):
        tmp =[]
        tmp.append(keywords)
        for t in tmp:
            self.keywords_list.append(t[0][0])

    def _get_google_trends_results(self):
        data_df = pd.DataFrame()
        pytrends = TrendReq(hl='en-US', tz=360)
        for word in self.keywords_list:
            _keyword = [word]
            #cat은 카테고리를 의미
            #geo는 지역
            #한달단위로 줄것임
            pytrends.build_payload(kw_list=_keyword, cat=0, timeframe='2017-01-01 2022-07-01', geo='US')
            tmp = pytrends.interest_over_time()

            if 'isPartial' in tmp.columns:
                tmp = tmp.drop(['isPartial'], axis=1)

            data_df = pd.concat([data_df, tmp], axis=1)
            time.sleep(15)

        self.trends_df = data_df

    def _make_columns_list_by_keywords(self):
        base = ['date']
        for key in self.keywords_list:
            name = key + '_ratio'
            self.keywords_col_list.append(name)

    def _make_change_ratios_to_trends_df(self):
        tmp_df = pd.DataFrame(columns=self.keywords_col_list)
        for key in self.keywords_col_list:
            target_col = key+'_ratio'
            tmp_df[target_col] = np.zeros(len(self.trends_df))
            tmp_df.loc[1:, target_col] = (self.trends_df[key][1:].values -
                                          self.trends_df[key][:-1].values) / self.trends_df[key][:-1].values
        return tmp_df

    def _add_google_trend_results_to_db(self):
        df = self._make_change_ratios_to_trends_df()
        df.to_sql(self.MYSQL_GOOGLE_TRENDS, self.my_sql, if_exists='append', index=False)
        #수치 그대로도 넣되, 상대적 변화율을 넣는것이 핵심

