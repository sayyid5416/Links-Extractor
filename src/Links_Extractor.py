# Imports
import os

app_name = 'Links Extractor'
github_link = 'https://github.com/hussain5416/Links-Extractor'


# Console properties
if __name__ == "__main__":
    os.system('color 07')
    os.system(f'title {app_name}')


# Imports
import re, threading, requests, winshell, webbrowser, time
from datetime import datetime
from colorama import Fore



# Choices dict
choiceDict = {
    '1': ('Web links', '(http/https)'),
    '2': ('FTP links', '(ftp)'),
    '3': ('MAIL links', '(mailto)'),
    '4': ('All types of links', ''),
    '5': ('Web-Crawl', '(all links)'),
    '6': ('About', '')
}


def takeUserInput(question:str, replaceList=[]):
    """
    This function asks user input and returns the modified text
    """    
    
    x = input(f'{Fore.WHITE}> {question}: {Fore.LIGHTBLUE_EX}')
    
    if replaceList:
        for i in replaceList:
            x = x.replace(i[0], i[1])

    return x





class Extract_Links:
    """
    Main Links Extraction class
    """    

    def __init__(self):
        super().__init__()
        self.webcrawl = False
        
        try:
            # User choices
            print(Fore.WHITE, end='')
            self.userChoice = self.asks_user_choice()
            print(f'{Fore.RESET}', end='')
            
            if self.userChoice == '6':
                self.show_about_data()
            else:
                # Web Crawling | Local file Crawling
                if self.userChoice == '5':
                    ques = 'Enter WEB-Page address to extract links from it (Ex: github.com/hussain5416)'
                    rep_list = [('\\', '/')]
                    self.webcrawl = True
                else:
                    ques = 'Enter file name to extract links from it (relative/absolute path)'
                    rep_list = [('/', '\\')]
                    
                # Old location user input
                self.dataSource = takeUserInput(ques, rep_list)
                if self.webcrawl:
                    if '://' not in self.dataSource:
                        self.dataSource = f'https://{self.dataSource}'
                
                # 
                self.fileLocation = self.get_filePath()
                self.main_extracting_fctn()
        
        except Exception as e:
            print(f'{Fore.RED}=> [Error 1] {e}, Try again...')
    
    def asks_user_choice(self):
        """
        This function shows user the choices and returns dict and the user choice
        """
        # Printing choices
        choices = ''
        for a, b in choiceDict.items():
            choices += f' {a} - {b[0]} {b[1]}\n'
        print(app_name.center(os.get_terminal_size().columns))
        print(choices)
        
        # Asking for user choice
        question = f'Enter your choice ({"/".join(choiceDict)})'
        choice = takeUserInput(question)
        while choice not in choiceDict:
            choice = takeUserInput(question)
        print()
        
        return choice
    
    def get_filePath(self):
        """
        - RETURNS the file location of NEW FILE, for extracted links
        - Creates parent folder - if missing
        """
        # File Name
        fileName = self.dataSource
        for i in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            fileName = fileName.replace(i, '-')
        fileName = f'{choiceDict[self.userChoice][0]} - {fileName}.txt'
        
        # Parent directory
        dirPath = os.path.join(winshell.desktop(), 'Extracted Links')
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
            
        # File location
        return os.path.join(dirPath, fileName)
    
    def main_extracting_fctn(self):
        try:
            # Getting data from source location
            if self.webcrawl:
                dataToParse = requests.get(self.dataSource).text                    # From Webpage
                self.userChoice = '4'
            else:                                                                   # From local file
                try:
                    with open(self.dataSource, encoding='utf-8') as f:
                        dataToParse = f.read()
                except Exception as e:
                    with open(self.dataSource) as f:
                        dataToParse = f.read()
            
            # Extract links
            retData = self.extractLinks(dataToParse)
            if retData is None: raise ValueError('Wrong inputs')
            self.saveToFile(retData[0], retData[1])
            
        except FileNotFoundError:
            print(f'{Fore.RED}=> [Error] "{self.dataSource}" not found. Write the proper file name...')
                
        except Exception as e:
            print(f'{Fore.RED}=> [Error] {e}, Try again...')
            
        else:
            # Open saved file
            threading.Thread(
                target=lambda: os.system(f'""{self.fileLocation}""'),
                daemon=True
            ).start()


    ## -------------------------------------------- Others -------------------------------------------- ##
    def extractLinks(self, dataToParse:str):
        """
        Returns: (`extracted-links`, `extracted-items-summary`)
        """
        def getLinks(regex:str) -> list[str] :
            return list(
                set(
                    re.findall(regex, dataToParse, re.IGNORECASE)
                )
            )
        
        # Extracting links from file
        webLinks   = getLinks(r'(https?://[^("\s<>)]+)')               # http[s]://anything_until (' ', <, >)
        ftpLinks   = getLinks(r'(ftp://[^("\s<>)]+)')                  # ftp://anything_until (' ', <, >)
        mailLinks  = getLinks(r'(mailto: *[^("\s<>)]+)')               # mailto:[whitespaces]anything_until (' ', <, >)

        # Extracted links
        match self.userChoice:
            case '1':   text, linksList = '◆ Web links:', webLinks
            case '2':   text, linksList = '◆ FTP links:', ftpLinks
            case '3':   text, linksList = '◆ Mail links:', mailLinks
            case '4':   text, linksList = '◆ All links:', webLinks + ftpLinks + mailLinks
            case _  :   text, linksList = None, None
        
        # Extraction summary
        if text and linksList:
            summaryDict = {text: len(linksList)}
            if self.userChoice == '4':
                summaryDict.update({'        • Web links:'  : len(webLinks)})
                summaryDict.update({'        • FTP links:'  : len(ftpLinks)})
                summaryDict.update({'        • Mail links:' : len(mailLinks)})
            summaryDict.update({'◆ Words:': len(dataToParse.split(' '))})
            summaryDict.update({'◆ Lines:': len(dataToParse.split('\n'))})
            return linksList, summaryDict

    def saveToFile(self, extractedLinks:list[str], summary:dict[str, int]):
        """
        Function to write extracted links to a new file
        """
        with open(self.fileLocation, 'a+', encoding='utf-8') as f:
            # Heading
            currentTime = datetime.now().strftime(r'%d/%b/%Y   %I:%M %p')
            f.write("•" * 84)
            f.write(
                f'\n● Links extracted from "{self.dataSource}"\n'
                f'● {currentTime}\n\n'
            )
            
            # Conclusion
            conclusionData = [f'{a} {b}' for a, b in summary.items()]
            conclusion = '\n'.join(conclusionData + ['\n'])
            f.write(conclusion)
            
            # Links
            for i, link in enumerate(extractedLinks, start=1):
                print(f'{Fore.GREEN}{i} -- Extracted -- {link}')
                f.write(f'    {i} - {link}\n')

            f.write("‾" * 100)
            f.write('\n\n\n')
            
        # Print conclusion
        print(
            f'{Fore.BLUE}{conclusion}'
            f'{Fore.YELLOW}=> Data saved to "{self.fileLocation}"'
        )

    def show_about_data(self):
        print(
            f'{Fore.GREEN}'
            "App Name: Links Extractor\n" \
            "Creator: Hussain Abbas\n" \
            f"App Webpage: {github_link}\n"
        )
        update_check = takeUserInput('Check for updates? (y/n) ')
        print(f'{Fore.GREEN}', end='')
        if update_check.lower() in ['y', 'yes']:
            threading.Thread(
                target=lambda: webbrowser.open(
                    f'{github_link}/releases/latest'
                )
            ).start()
            print('[Opening the app update page....]\n\n')
            time.sleep(2)
        else:
            print('[Skipped]')


    
    


############################################################################################## Run Main Program
if __name__ == "__main__":
    while True:
        Extract_Links()
        print('\n\n')
