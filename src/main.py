# Imports
import os


app_name = 'Links Extractor'
github_link = 'https://github.com/sayyid5416/Links-Extractor'


# Console properties
if __name__ == "__main__":
    os.system('color 07')
    os.system(f'title {app_name}')


# Imports
import re, threading, webbrowser, time, sys
from datetime import datetime
from typing import Callable
from colorama import Fore
import requests


def pp(text:str, fore=Fore.WHITE, end:str='\n'):
    return print(f'{fore}{text}', end=end)


def get_desktop_path():
    desktop = os.path.join(
        os.environ.get('USERPROFILE', '/'), 
        'Desktop'
    )
    if not os.path.exists(desktop):
        os.mkdir(desktop)
    return desktop

def get_saving_directory():
    return os.path.join(get_desktop_path(), 'Extracted Links')



# Settings
config = 'config-file'
RAW, ORIGINAL = 'ENABLED', 'DISABLED'

def set_settings(setting=''):
    """ Sets a new setting """
    if not os.path.exists(config):
        setting = ORIGINAL
    if setting:
        with open(config, 'w') as f:
            f.write(setting)
            return True
    return False

def get_current_settings() -> str :
    """ Returns: current settings """
    set_settings()
    with open(config, 'r') as f:
        return f.read()

def switch_raw_setting():
    """ Enable / Disable raw settings """
    newVal = RAW if get_current_settings() == ORIGINAL else ORIGINAL
    set_settings(newVal)
    pp(f'[Raw formatting {newVal}]', Fore.BLUE)


# Choices dict
def get_choices() -> dict[str, tuple[str, str]] :
    return {
        '1': ('Web links', '(http/https)'),
        '2': ('FTP links', '(ftp)'),
        '3': ('MAIL links', '(mailto)'),
        '4': ('All types of links', ''),
        '5': ('Web-Crawl', '(all links)'),
        '6': ('About', ''),
        'raw': ('Enable/Disable raw formatting of links', f'({get_current_settings()})')
    }
    

def get_choices_str():
    valsStr = ''
    for a, b in get_choices().items():
        valsStr += f' {a:3} -  {b[0]} {b[1]}\n'
    return valsStr

choiceDict = get_choices()




def D_error_catcher(func:Callable):
    """ Decorator to catch errors """
    def wrapper(*args, **kwargs):
        try:        
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            pp(f'<ctrl+c>', Fore.BLUE)
            pp('[Exited]', Fore.GREEN)
            print(Fore.WHITE)
            sys.exit()
        except FileNotFoundError:   
            pp('=> [Error] Source not found. Write proper file name...', Fore.RED)
        except Exception as e:      
            pp(f'=> [Error] {e}, Try again...', Fore.RED)
    return wrapper




class Extract_Links:

    @D_error_catcher
    def __init__(self):
        # User choices
        pp('', Fore.WHITE, end='')
        self.userChoice = self.getUserChoice()
        
        # Main Action
        match self.userChoice:
            case '6':   self.show_about_data()
            case 'raw': switch_raw_setting()
            case _:     self.mainExtraction()
    
    
    def getUserChoice(self):
        """ Show user the choices and returns dict and the user choice """
        # Printing choices
        print(app_name.center(os.get_terminal_size().columns))
        print(get_choices_str())
        
        # Asking for user choice
        question = f'Enter your choice ({"/".join(choiceDict)})'
        choice = self.takeUserInput(question)
        while choice not in choiceDict:
            choice = self.takeUserInput(question)
        print()
        
        return choice
    
    
    def mainExtraction(self):
        """ Main Links extraction """
        # Ask for source location -> Get its data
        match self.userChoice:
            case '5':                                                                                       # Web
                self.sourcePath = self.takeUserInput('Enter web-address (Ex: github.com/sayyid5416)', [('\\', '/')], web=True)
                sourceData = requests.get(self.sourcePath).text
            case _:                                                                                         # Local-file
                self.sourcePath = self.takeUserInput('Enter relative/absolute file-path', [('/', '\\')])
                try:
                    with open(self.sourcePath, encoding='utf-8') as f:  sourceData = f.read()
                except Exception:
                    with open(self.sourcePath) as f:                    sourceData = f.read()
        
        # Extract links
        retData = self.get_extractedLinks(sourceData)
        
        # Save data -> open saved file
        fileLocation = self.get_filePath()
        self.saveToFile(fileLocation, retData[0], retData[1])
        threading.Thread(target=lambda: os.system(f'""{fileLocation}""'), daemon=True).start()


    ## -------------------------------------------- Others -------------------------------------------- ##
    @staticmethod
    def takeUserInput(question:str, replaceList=[], web:bool=False):
        """ Asks user input & Returns: modified text """    
        # Input
        x = input(f'{Fore.WHITE}> {question}: {Fore.LIGHTBLUE_EX}')
        
        # Modifications
        if replaceList:
            for i in replaceList:
                x = x.replace(i[0], i[1])
        if web and '://' not in x:
            x = 'https://' + x

        return x

    def get_filePath(self):
        """ Returns: File location where extracted links would be saved """
        # File Name
        fileName = self.sourcePath
        for i in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            fileName = fileName.replace(i, '-')
        fileName = f'{choiceDict[self.userChoice][0]} - {fileName}.txt'
        
        # Parent directory
        dirPath = get_saving_directory()
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
            
        # File path
        return os.path.join(dirPath, fileName)
    
    def get_extractedLinks(self, sourceData:str):
        """
        Returns: (`extracted-links`, `extraction-summary`)
        """
        def getLinks(regex:str) -> set[str] :
            return set(re.findall(regex, sourceData, re.IGNORECASE))
        
        # Extracting links from file
        webLinks   = getLinks(r'(https?://[^("\s<>)]+)')               # http[s]://anything_until (' ', <, >)
        ftpLinks   = getLinks(r'(ftp://[^("\s<>)]+)')                  # ftp://anything_until (' ', <, >)
        mailLinks  = getLinks(r'(mailto: *[^("\s<>)]+)')               # mailto:[whitespaces]anything_until (' ', <, >)

        # Extracted links
        if self.userChoice == '5': self.userChoice = '4'
        match self.userChoice:
            case '1':   text, linksList = '◆ Web links:', webLinks
            case '2':   text, linksList = '◆ FTP links:', ftpLinks
            case '3':   text, linksList = '◆ Mail links:', mailLinks
            case '4':   text, linksList = '◆ All links:', webLinks.union(ftpLinks, mailLinks)
            case _  :   raise ValueError('Wrong inputs')
        
        # Extraction summary
        summaryDict = {text: len(linksList)}
        if self.userChoice == '4':
            summaryDict.update({'        • Web links:'  : len(webLinks)})
            summaryDict.update({'        • FTP links:'  : len(ftpLinks)})
            summaryDict.update({'        • Mail links:' : len(mailLinks)})
        summaryDict.update({'◆ Words:': len(sourceData.split(' '))})
        summaryDict.update({'◆ Lines:': len(sourceData.split('\n'))})
        return linksList, summaryDict

    def saveToFile(self, fileLocation, extractedLinks:set[str], summary:dict[str, int]):
        """
        Function to write extracted links to a new file
        """
        rawEnabled = bool(get_current_settings() == RAW)
        with open(fileLocation, 'a+', encoding='utf-8') as f:
            # Summary
            currentTime = datetime.now().strftime(r'%d/%b/%Y   %I:%M %p')
            summaryData = [f'{a} {b}' for a, b in summary.items()]
            summaryStr = '\n'.join(summaryData + ['\n'])
            f.write("•" * 84)
            if rawEnabled: 
                f.write("\n----- RAW FORMAT -----")
            f.write(f'\n● Links extracted from "{self.sourcePath}"\n● {currentTime}\n\n')
            f.write(summaryStr)
            
            # Links
            for i, link in enumerate(extractedLinks, start=1):
                threading.Thread(
                    target=lambda: pp(f'{i} -- Extracted -- {link}', Fore.GREEN)
                ).start()
                if rawEnabled:  f.write(f'{link}\n')
                else:           f.write(f'    {i} - {link}\n')
            f.writelines(['‾'*100, '\n\n\n'])
        
        # Summary
        pp(summaryStr, Fore.BLUE)
        pp(f'=> Data saved to "{fileLocation}"', Fore.YELLOW)

    def show_about_data(self):
        data = {
            'app name': 'Links Extractor',
            'saving directory': get_saving_directory(),
            'creator': 'https://t.me/sayyid5416',
            'app webpage': github_link,
        }
        statement = ''
        for a, b in data.items():
            statement += f'{Fore.GREEN}{a.title():20} : {Fore.BLUE}{b}\n'
        print(statement)
        pp('Press <ctrl+c> any time to exit the app\n', Fore.CYAN)

        update_check = self.takeUserInput('Check for updates? (y/n) ')
        pp('', Fore.GREEN, end='')
        if update_check.lower() in ['y', 'yes']:
            threading.Thread(
                target=lambda: webbrowser.open(
                    f'{github_link}/releases/latest'
                )
            ).start()
            pp('[Opening the app update page....]\n\n', Fore.GREEN)
            time.sleep(2)
        else:
            pp('[Skipped]', Fore.GREEN)





############################################################################################## Run Main Program
if __name__ == "__main__":
    while True:
        Extract_Links()
        print('\n\n')
