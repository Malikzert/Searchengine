from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import pandas as pd
import math
import os
from urllib.parse import urlparse
import difflib 

class BM25Engine:
    def __init__(self, csv_paths, k1=1.5, b=0.75):
        if isinstance(csv_paths, str):
            csv_paths = [csv_paths]

        dfs = []
        for path in csv_paths:
            df = pd.read_csv(path).fillna("")
            dfs.append(df)

        df = pd.concat(dfs, ignore_index=True)

        # Simpan kolom penting
        self.df_full = df[[
            'url', 'judul', 'tanggal', 'isi_berita',
            'Narasi', 'Clean Narasi', 'hoax', 'summary'
        ]].fillna("")

        # Tambahkan kolom sumber berdasarkan domain URL
        self.df_full['sumber'] = self.df_full['url'].apply(self.extract_sumber)

        self.k1 = k1
        self.b = b

        self.documents = self.df_full['Clean Narasi'].tolist()
        self.N = len(self.documents)

        self.vectorizer = CountVectorizer()
        self.doc_term_matrix = self.vectorizer.fit_transform(self.documents)
        self.doc_len = self.doc_term_matrix.sum(axis=1)
        self.avgdl = self.doc_len.mean()

        self.df_term = np.bincount(self.doc_term_matrix.indices, minlength=self.doc_term_matrix.shape[1])
        self.idf = np.log((self.N - self.df_term + 0.5) / (self.df_term + 0.5) + 1)
        all_titles = " ".join(self.df_full['judul'].astype(str)).lower()
        self.title_keywords = list(set(all_titles.split()))
    def extract_sumber(self, url):
        try:
            domain = urlparse(url).netloc.lower()
            if 'kompas' in domain:
                return 'kompas'
            elif 'cnnindonesia' in domain or 'cnn' in domain:
                return 'cnn'
            elif 'turnbackhoax' in domain:
                return 'turnbackhoax'
            elif 'detik' in domain:
                return 'detik'
            else:
                return 'lainnya'
        except:
            return 'lainnya'

    def search(self, query, top_n=None):
        query_vec = self.vectorizer.transform([query])
        query_indices = query_vec.indices

        scores = []
        for i in range(self.N):
            score = 0.0
            doc_vec = self.doc_term_matrix[i]
            dlen = self.doc_len[i, 0]

            for idx in query_indices:
                f = doc_vec[0, idx]
                idf = self.idf[idx]
                denom = f + self.k1 * (1 - self.b + self.b * dlen / self.avgdl)
                score += idf * f * (self.k1 + 1) / (denom + 1e-6)

            if score > 0:
                scores.append((i, score))

        ranked = sorted(scores, key=lambda x: x[1], reverse=True)
        if top_n is not None:
            ranked = ranked[:top_n]

        return [
            {
                "judul": self.df_full.iloc[i]['judul'],
                "isi_berita": self.df_full.iloc[i]['isi_berita'],
                "narasi": self.df_full.iloc[i]['Narasi'],
                "clean_narasi": self.df_full.iloc[i]['Clean Narasi'],
                "hoax": self.df_full.iloc[i]['hoax'],
                "summary": self.df_full.iloc[i]['summary'],
                "url": self.df_full.iloc[i]['url'],
                "tanggal": self.df_full.iloc[i]['tanggal'],
                "sumber": self.df_full.iloc[i]['sumber'],
                "score": round(score, 2)
            }
            for i, score in ranked
        ]
    def suggest_keyword(self, query):
        query_words = query.lower().split()
        suggestions = []
        for word in query_words:
            match = difflib.get_close_matches(word, self.title_keywords, n=1, cutoff=0.7)
            if match:
                suggestions.append(match[0])
        if suggestions and suggestions != query_words:
            return ' '.join(suggestions)
        return None
