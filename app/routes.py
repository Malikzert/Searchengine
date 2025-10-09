from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.forms import SearchForm
from app.bm25 import BM25Engine
import os
import string
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

main = Blueprint('main', __name__)

# Load semua dataset
dataset_paths = [
    os.path.join(os.path.dirname(__file__), '..', 'dataset', 'Summarized_Kompas.csv'),
    os.path.join(os.path.dirname(__file__), '..', 'dataset', 'Summarized_CNN.csv'),
    os.path.join(os.path.dirname(__file__), '..', 'dataset', 'Summarized_Turnbackhoax.csv'),
    os.path.join(os.path.dirname(__file__), '..', 'dataset', 'Summarized_Detik.csv'),
]
bm25 = BM25Engine(dataset_paths)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()

    # Ambil semua kata dari judul berita non-hoax
    stop_factory = StopWordRemoverFactory()
    stopwords = set(stop_factory.get_stop_words())
    punct_table = str.maketrans('', '', string.punctuation)

    judul_series = bm25.df_full[bm25.df_full['hoax'].astype(str) == '0']['judul'].str.lower()
    tokens = (
        judul_series
        .str.translate(punct_table)
        .str.split()
        .explode()
        .loc[lambda x: x.str.isalpha()]
        .loc[lambda x: ~x.isin(stopwords)]
    )
    all_keywords = tokens.drop_duplicates().tolist()

    if form.validate_on_submit():
        query = form.query.data
        return redirect(url_for('main.result', query=query, page=1))

    return render_template('index.html', form=form)


@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/result', methods=['GET'])
def result():
    query = request.args.get('query', '').strip()
    sumber_filter = request.args.get('sumber', '').strip().lower()
    limit_param = request.args.get('limit', '10').strip()  # ← ambil limit
    page = int(request.args.get('page', 1))

    if not query:
        return redirect(url_for('main.index'))

    all_results = bm25.search(query)

    if sumber_filter:
        all_results = [
            item for item in all_results
            if item.get('sumber', '').lower() == sumber_filter
        ]

    total_results = len(all_results)

    suggested = None
    if total_results == 0:
        suggested = bm25.suggest_keyword(query)
        if suggested and suggested != query:
            all_results = bm25.search(suggested)
            if sumber_filter:
                all_results = [
                    item for item in all_results
                    if item.get('sumber', '').lower() == sumber_filter
                ]
            total_results = len(all_results)

    if total_results == 0:
        abort(404)

    # Perhitungan jumlah per halaman berdasarkan limit
    if limit_param.lower() == 'semua':
        per_page = total_results
    else:
        try:
            per_page = int(limit_param)
        except ValueError:
            per_page = 10  # fallback

    total_pages = (total_results + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    page_results = all_results[start:end]

    return render_template(
        'result.html',
        query=query,
        suggested=suggested,
        page=page,
        page_results=page_results,
        total_results=total_results,
        total_pages=total_pages,
        limit=limit_param  # ← untuk mempertahankan dropdown aktif
    )



@main.route('/detail/<int:item_id>')
def detail(item_id):
    query = request.args.get('query', '').strip()

    if not query:
        return redirect(url_for('main.index'))

    all_results = bm25.search(query)

    if 0 <= item_id < len(all_results):
        item = all_results[item_id]
        return render_template('detail.html', item=item, query=query)
    else:
        abort(404)

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
