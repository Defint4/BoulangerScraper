import concurrent.futures
import requests
from bs4 import BeautifulSoup
from AddCsv import CSVWriter

class Boulanger():
    
    def __init__(self):
        proxy_host = "192.168.126.136"
        proxy_port = 3128                   #proxy privé
        proxy_login = "defint"
        proxy_pass = "root"
        self.url = 'https://www.boulanger.com/c/'
        self.proxies = {
            'https': f"http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}",
            'http': f"http://{proxy_login}:{proxy_pass}@{proxy_host}:{proxy_port}"
        }
        
        
        
        
    def get_html(self,pagename=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        proxies = self.proxies
        try : 
            url = self.url + pagename
        except:
            url = self.url
            
        try:
            response = requests.get(url, headers=headers, proxies=proxies)
            
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
                        title = "\n".join([ligne.strip() for ligne in title.split("\n") if ligne.strip() != ""])
                        price = article.find('p', {'class': 'price__amount'}).text.strip().replace(',', '.').replace('€', '')
                        desc = article.find('ul', {'class': 'keypoints'}).text.strip()
                        desc = "\n".join([ligne.strip() for ligne in desc.split("\n") if ligne.strip() != ""])
                        data.append({'Titre': title, 'Prix': price, 'Description': desc})
                        
                    except:
                        continue
                
                return data

    def scrape(self, nbpages):
        for pagename in self.all_pages():
            data = []
            try : 
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(self.scrape_page, pagename + f'?numPage={i+1}') for i in range(nbpages)]     
                    for future in concurrent.futures.as_completed(futures):
                        result = future.result()
                        if result:
                            data.extend(result)
                
            except Exception as e:
                print(f"L'erreur est : {e}")
                continue
            writer = CSVWriter(f'{pagename}.csv', ['Titre', 'Prix', 'Description'])
            writer.writeCsv(data)
    
        
        
        
        
#exemple d'utilisation : 
#--------------------------------------------
nbpages = 2                       #nombre de page à scraper
scraper = Boulanger()               
scraper.scrape(nbpages)
#--------------------------------------------