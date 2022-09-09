#!/usr/bin/env python
# coding: utf-8

import sys
# !{sys.executable} sudo -m pip install --upgrade pip
# !{sys.executable} sudo -m pip install fake-useragent

# Bossa Muffin Scrapping net1901.org Program v1 - 07/09/2022
import lib_display as ds
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import csv
from time import time

class Arguments:
    """
    Classdocs
    """
    def __init__(self, num_department, id_theme, user_tag):
        self.nb_args: int = self._checkArgs()
        self.arg_1 = num_department
        self.arg_2 = id_theme
        self.arg_3 = user_tag
        # Then we match with arg in the command line
        self._selectArgs()

    def _selectArgs(self):
        """
        :return: void
        """
        if self.nb_args < 4:
            self.arg_3 = self._enterTheTag()

        if self.nb_args >= 2:
            self.arg_1 = sys.argv[1]

        if self.nb_args >= 3:
            self.arg_2 = sys.argv[2]

        if self.nb_args >= 4:
            self.arg_3 = sys.argv[3]

    def _showArgs(self):
        """
        :return: print view in shell
        """
        print(f"You give {self.nb_args} args to run the script ;"
              f"\nThe final args to execute the program are : "
              f"\n\t 1) Num of the FR department : {self.arg_1}"
              f"\n\t 2) Id theme of the association : {self.arg_2}"
              f"\n\t 3) A subjective tag to name the files of this current call {self.arg_3}")


    def _checkArgs(self):
        """
        :return: int = number of agrs
        """
        nb_args = len(sys.argv)
        if nb_args > 4:
            print("Param error !")
            print(f"\tusage : python3 {__file__} [intValue (FR country number, default : 47 = Lot-et-Garonne) "
                  f"[intValue (theme id, default : 134 = chasse)]"
                  f"[intValue (current call tag, default : 1)]")
            exit("Try again with 3 int args")

        for strParam in sys.argv[1:]:
            try:
                param = int(strParam)
            except ValueError:
                print("Bad parameter value %s" % strParam, file=sys.stderr)
                exit("Try again with 3 int args")

        return nb_args


    def _enterTheTag(self):
        """
        :return: int = a int tag from the user to name the filenames
        """
        tag = "version"
        user_validation = ""

        while user_validation != 'y':
            if user_validation == 'q':
                exit("Ok! bye, bye :)")

            tag = input("Enter an integer to tag the file names of your result (or press q:quit) > ")

            try:
                tag = int(tag)
                user_validation = input(f"Your tag is : {tag}, are you agree with that ? "
                                        f"(press y:yes, or other:no, or q:quit) > ")

            except ValueError:
                if tag == 'q':
                    exit("Ok! bye, bye :)")
                else:
                    print("Error : Your input isn't an integer ")

        return tag

class Scrap:
    """
    Classdocs
    """

    # Give the paths which interests me
    PATH = ["https://www.net1901.org", "/associations.html"]
    OUT_DIR = "scrapped"
    DELAY = True

    def __init__(self, num_department=47, id_theme=134, tag=1):
        """
        :param num_department: int
        :param id_theme: int
        :param salt: int to tag each different call of this class (generate different files and dir names)
        """
        self.URL = self.PATH[0]
        self.TARGET = self.PATH[1]
        self.payload = {
            'go': 1,
            'num_dpt': num_department,
            'id_theme': id_theme,
            'page': 1
        }
        self.tag = tag
        self.header = self._getUserAgent()

        # Open a session with the website
        self.CURRENT_SESSION = requests.Session()

        # Init a dict for stock the request responses
        self.responses = {}

        # Soup string
        self.soups = {}

        # Pages counter
        self.page = 0

    def _getPage(self, url, get_params):
        """
        Import the page results from the given URL and datas in get method by payload
        :param url_target:
        :param get_params:
        :return: the get http request answer
        """

        with self.CURRENT_SESSION.get(url, params=get_params, headers=self.header) as res:
            return res

    def _getUserAgent(self):
        """
        Make a credible user agent to our web request
        :return: user-agent for a http request header
        """
        ua = UserAgent().random

        return {'user-agent': ua}

    def getAllPages(self):
        """
        Scrap all html pages of this theme in this department
        :return: Void
        """
        status = 200

        while status == 200:
            # Don't flood the server !!!!
            print("Ready to scrap the page n°", self.payload['page'])
            if self.DELAY:
                ds.countdown(3)
            self.responses[self.payload['page']] = self._getPage(self.URL + self.TARGET, self.payload)

            # The imported code is put in a soup object, easy to work on
            self.soups[self.payload['page']] = BeautifulSoup(self.responses[self.payload['page']].text, 'html.parser')
            status = self.responses[self.payload['page']].status_code

            if status == 200:
                print("> Page scrapped")
            else:
                print("> Scrapping error")

            # Now, we scrap a new page
            self.payload['page'] += 1

    def _createPreFileName(self, prefixe="theme", midfixe="dpt", suffixe="page"):
        """
        Creat a filename scheme
        :param midfixe:
        :param suffixe:
        :return: str
        """

        return f"{prefixe}_{str(self.payload['id_theme'])}_{midfixe}_{str(self.payload['num_dpt'])}_{suffixe}_"

    def saveSoupsInFiles(self):
        """
        Save the results in txt files in order to not flood the web server
        We'll work on these files
        """
        for i in range(1, self.payload['page']):
            with open(f"{self.OUT_DIR}/{self._createPreFileName() + str(i)}_v{self.tag}.txt", 'w') as outfile:
                outfile.write(str(self.soups[i]))

    def _waitOneOrTwoSecond(self, cursor: int):
        """
        Wait to prevent flooding the server
        :return: Void
        """
        if cursor % 2 == 0:
            ds.countdown(1, p_show=False)
        else:
            ds.countdown(2, p_show=False)


    def getAllItemsInPagesByScrappedFiles(self):
        """
        Scrap the page of each search result (ex : associations) find in the main page (results of the main search).
        These web pages are soup files yet
        :return: tab_results -> list[dict] (the result to write in a csv file)
        """
        tab_results = []
        tab_results.append({'site': self.URL + self.TARGET})
        nb_files_in_out_dir = self.payload['page']
        k = 1

        for i in range(1, nb_files_in_out_dir):

            with open(f"{self.OUT_DIR}/{self._createPreFileName() + str(i)}_v{self.tag}.txt", 'r') as infile:
                self.soups[i] = BeautifulSoup(infile.read(), 'html.parser')

                for assoc in self.soups[i].find_all(class_="list-group-item", href=True):
                    result = {
                        'Nom': "",
                        'Rue': "",
                        'CP': "",
                        'Ville': "",
                        'Objet': "",
                        'RNA': "",
                        'Lien': ""
                    }

                    try:
                        result['Nom'] = assoc.find('h4', class_="list-group-item-heading").text
                    except:
                        pass

                    try:
                        result['Ville'] = assoc.find('p', class_="list-group-item-text").text.split(' / ')[0]
                    except:
                        pass

                    try:
                        result['Lien'] = assoc['href']
                    except:
                        pass
                    
                    # Don't flood the server !!!!
                    if self.DELAY:
                        self._waitOneOrTwoSecond(k)
                    result = self._getAllItemsInItemPage(result)
                    tab_results.append(result)
                    print(f"{k} : {result['Nom']} > OK")
                    k += 1

        return tab_results

    def _getAllItemsInItemPage(self, result):
        """
        Scrap the page of on item (ex : associations) find in the main page (result of the main search)
        :param result:
        :return: result -> list (a line in the tab_results to write in the final csv file)
        """
        scrap_assoc = self._getPage(self.URL + result['Lien'], "")

        if scrap_assoc.status_code == 200:
            soup_assoc = BeautifulSoup(scrap_assoc.text, 'html.parser')

            try:
                result['Rue'] = soup_assoc.find('span', attrs={'itemprop': "streetAddress"}).text
                result['Rue'] = result['Rue'].replace(",", " ")
            except:
                pass

            try:
                result['CP'] = soup_assoc.find('span', attrs={'itemprop': "postalCode"}).text
            except:
                pass
            try:
                text_temp = soup_assoc.find('div', class_="well").text.split("Objet : ")[1]
                result['Objet'] = text_temp.split("R.N.A : ")[0].replace(",", "/")
                result['RNA'] = text_temp.split("R.N.A : ")[1].split("Activités : ")[0]
            except:
                pass

        return result

    def writeDictInCsvFile(self, tab_results):
        """
        Put data in the csv file
        :param tab_results:
        :return: file_name -> str (just the name of the file where is the final datas)
        """
        file_name = self._createPreFileName(suffixe="results") + str(self.tag) + ".csv"
        file_csv = open(f"{file_name + str(self.tag)}.csv", 'w', newline='')

        with file_csv:
            header = ['Nom', 'Rue', 'CP', 'Ville', 'Objet', 'RNA', 'Lien']
            writer = csv.DictWriter(file_csv, fieldnames=header)
            writer.writeheader()

            for assoc in tab_results[1:]:
                writer.writerow(assoc)

        return file_name


if __name__ == "__main__":
    # Prepare the argues for the scrapping class
    num_department = 47
    id_theme = 134
    tag = 1

    args = Arguments(num_department, id_theme, tag)

    start_time = time()

    # To scrap net1901.org
    scrap = Scrap(num_department=args.arg_1, id_theme=args.arg_2, tag=args.arg_3)
    scrap.getAllPages()
    scrap.saveSoupsInFiles()
    tab_results = scrap.getAllItemsInPagesByScrappedFiles()
    out_csv_file = scrap.writeDictInCsvFile(tab_results)

    stop_time = time()
    elapsed = (start_time - stop_time) * 1000

    print(f"Scrapping of {scrap.URL + scrap.TARGET} is completed in {elapsed:.2}s")
    print(f"Find the data in  {out_csv_file}")
    exit("End")
