
# -*- coding: utf-8 -*-
import csv
import os
import datetime
from requests_html import HTMLSession
import utils
import scraperwiki


# morph.io requires this db filename, but scraperwiki doesn't nicely
# expose a way to alter this. So we'll fiddle our environment ourselves
# before our pipeline modules load.
os.environ['SCRAPERWIKI_DATABASE_NAME'] = 'sqlite:///data.sqlite'


def get_dados_from_page(data_referencia):
    url = 'http://celepar7.pr.gov.br/sima/cotdiat.asp'
    params = {
        'data': data_referencia.strftime('%Y-%m-%d')
    }

    session = HTMLSession()
    response = session.get(url, params=params)
    
    if (response.status_code != 200):
        get_dados_from_page(data_referencia)
        print(response.status_code)
    return response


def extract_data(response, data_referencia, no_produto, tr_desc):
    tabela = response.html.find('.mytable', first=True)
    try:
        vr_real = tabela.xpath(".//tr["+str(tr_desc+1)+"]/td[21]/font/text()")[0].strip()
        vr_real = float(vr_real)
    except Exception:
        vr_real = None

    try:
        no_indicador = tabela.xpath(".//tr["+str(tr_desc)+"]/td[1]/font/text()")[0].strip().replace('  ',' ')
    except Exception:
        no_indicador = ''

    return {
        'dt_referencia': data_referencia,
        'no_produto': no_produto,
        'no_indicador': no_indicador,
        'vr_real': vr_real
    }


def main():
    base_file_name = 'precos_deral_base.csv'
    path_file_base = os.path.join('bases', base_file_name)
    ultima_data_base = utils.get_ultima_data_disponivel_base(path_file_base)
    print('última data base:', ultima_data_base)

    # base inicial com dados desde 2010
    start_date = ultima_data_base
    #start_date = datetime.date(2010, 1, 1)
    end_date = datetime.date.today()
    dates_2010_2018 = [ start_date + datetime.timedelta(n) for n in range(int ((end_date - start_date).days))]

    for data_referencia in dates_2010_2018:
        print(data_referencia)
        
        # só insere datas que ainda não estão na base
        if ultima_data_base >= data_referencia:
            continue

        # se não é dia de semana        
        if not utils.isbizday(data_referencia):
            continue

        rows = []
        
        response = get_dados_from_page(data_referencia)

        for index, dado in enumerate(get_dados()):
            index
            dados_site = extract_data(response, data_referencia, dado['no_produto'], dado['tr_desc'])
            rows.append(dados_site)

        for row in rows:
            # faz o append no csv da base
            with open(path_file_base, 'a', newline='', encoding='utf8') as baseFile:            
                fieldnames = ['dt_referencia', 'no_produto', 'no_indicador', 'vr_real']
                writer = csv.DictWriter(baseFile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(row)
                # print('Dado inserido no arquivo base:', path_file_base, row_inserted)

    print('Registros deral importados com sucesso')
    return True


def get_dados():
    dados = [
        { 'no_produto': 'algodão', 'tr_desc': 2},
        { 'no_produto': 'arroz em casca', 'tr_desc': 5},
        { 'no_produto': 'arroz agulhinha', 'tr_desc': 8},
        { 'no_produto': 'café em coco', 'tr_desc': 11},
        { 'no_produto': 'feijão carioca', 'tr_desc': 14},
        { 'no_produto': 'feijão preto', 'tr_desc': 17},
        { 'no_produto': 'milho', 'tr_desc': 20},
        { 'no_produto': 'soja', 'tr_desc': 23},
        { 'no_produto': 'trigo', 'tr_desc': 26},
        { 'no_produto': 'boi', 'tr_desc': 29},
        { 'no_produto': 'frango vivo', 'tr_desc': 32},
        { 'no_produto': 'erva-mate', 'tr_desc': 35},
        { 'no_produto': 'suíno', 'tr_desc': 38},
        { 'no_produto': 'vaca', 'tr_desc': 41},
        { 'no_produto': 'café beneficiado', 'tr_desc': 44},
        { 'no_produto': 'mandioca', 'tr_desc': 47}
    ]
    
    return dados


if __name__ == '__main__':
    main()
    
# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

# import lxml.html
#
# # Read in a page
# html = scraperwiki.scrape("http://foo.com")
#
# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".
