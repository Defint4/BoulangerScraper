#version 2.0 qui scrappe les pages de produits

import multiprocessing
import requests
from bs4 import BeautifulSoup
from functools import lru_cache


class BoulangerScraper():
    
    def __init__(self):
        proxy_host = "10.2.41.11"
        proxy_port = 3128                   #proxy privé
        proxy_login = "defint"
        proxy_pass = "root"
        self.url = 'https://www.boulanger.com/c/'
        self.proxies = {
            'https': f"http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}",
            'http': f"http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}"
        }
        
    @lru_cache(maxsize=None)    
    def get_html(self,pagename=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        proxies = self.proxies
        if pagename : 
            url = self.url + pagename
            if 'ref' in url:
                url = url.replace('/c/','')
        else:
            url = self.url
            
        
        
            
        try:
            response = requests.get(url, headers=headers) #, proxies=proxies
            
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Une erreur s'est produite lors de la récupération du contenu : {e}")
            return None
        
    def all_pages(self):
        html = self.get_html()
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            pagenames=[]
            for pagename in soup.find_all('li', {'class': 'navigation__item'}):
                try :
                    pagename = pagename.find('a',{'class': 'navigation__link--level1'}).get('href')
                    pagename = pagename.split("/")[-1]
                    pagenames.append(pagename)
                except:
                    continue
            return pagenames
        
        
        
    def get_links(self,pagename):    
        html = self.get_html(pagename)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            for page in soup.find_all('div', {'class': 'category-menu__category'}):
                try:
                    link = page.find('a').get('href')
                    link = link.split("/")[-1]
                    links.append(link)
                except:
                    continue
            return links
        
    def scrape_page(self, pagename):
        pages = self.get_links(pagename)
        for i in range(len(pages)):
            html = self.get_html(pages[i])
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                data = []
                for article in soup.find_all('div', {'class': 'product-item__row'}):
                    try:
                        title = article.find('h2').text.strip()
                        title = '\n'.join([ligne.strip() for ligne in title.split('\n') if ligne.strip() != ''])
                        price = article.find('p', {'class': 'price__amount'}).text.strip().replace(',', '.').replace('€', '')
                        desc = article.find('ul', {'class': 'keypoints'})
                        if desc:
                            desc = desc.prettify()
                            desc = "\n".join([ligne.strip() for ligne in desc.split("\n") if ligne.strip() != ""])
                        else:
                            desc = ''
                        link = article.find('a',{'class': 'product-item__title'}).get('href')
                        article_html = self.get_html(link)
                        if article_html:
                            article_soup = BeautifulSoup(article_html, 'html.parser')
                            details = article_soup.find('ul', {'class': 'product-features__list'})
                            # print(details)
                            if details:
                                details = details.prettify()
                                details = "\n".join([ligne.strip() for ligne in details.split("\n") if ligne.strip() != ""])
                            else:
                                details = 'Aucun détail'
                            data.append({'Titre': title, 'Prix(€)': price, 'Description': desc, 'Détails': details, 'Lien': self.url.replace('/c/','')+link})
                            
                    except:
                        continue
                return data


    def scrape(self, nbpages):
        for pagename in self.all_pages():
            data = []
            try:
                pool = multiprocessing.Pool()
                results = pool.map(self.scrape_page, [pagename + f'?numPage={i+1}' for i in range(nbpages)])
                pool.close()
                pool.join()

                for result in results:
                    if result:
                        data.extend(result)

            except Exception as e:
                print(f"L'erreur est : {e}")
                continue
            writer = CSVWriter(f'{pagename}.csv', ['Titre', 'Prix(€)', 'Description','Détails','Lien'])
            writer.writeCsv(data)

    
    
    
if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()

    from AddCsv import CSVWriter    
    #exemple d'utilisation : 
    #--------------------------------------------
    nbpages = 1                     #nombre de page à scraper
    scraper = BoulangerScraper()               
    scraper.scrape(nbpages)
    #--------------------------------------------