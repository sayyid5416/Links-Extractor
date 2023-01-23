# Imports
import os


# App data 
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
from generalpy import Settings as gSettings
from colorama import *
import requests




## ----------------------------------------------- Prints ------------------------------------------------ ##
def pp(text:str, fore=Fore.WHITE, back=Back.RESET, end:str='\n'):
    return print(
        f'{fore}{back}{text}{Back.RESET}{Fore.RESET}',
        end=end
    )

def pp_info(text):
    return pp(
        text,
        Fore.GREEN
    )

def pp_info_2(text):
    return pp(
        text,
        Fore.CYAN
    )

def pp_error(text):
    return pp(
        text,
        Fore.WHITE,
        Back.RED
    )

def pp_input(text):
    return pp(
        text,
        Fore.LIGHTBLUE_EX
    )

def pp_question(text):
    return input(
        f'{Fore.WHITE}{Back.BLUE}{Style.BRIGHT}> {text}:{Style.RESET_ALL}{Back.RESET}{Fore.LIGHTBLUE_EX} '
    )
    



## ----------------------------------------------- General ----------------------------------------------- ##
def D_error_catcher(func:Callable):
    """ Decorator to catch errors """
    def wrapper(*args, **kwargs):
        try:
            return func(
                *args,
                **kwargs
            )
        except KeyboardInterrupt:
            pp_input(f'<ctrl+c>')
            pp_info('[Exited]\n\n')
            sys.exit()
        except FileNotFoundError:
            pp_error('=> [Error] Source not found. Write proper file name...')
        except Exception as e:
            pp_error(f'=> [Error] {e}, Try again...')
    return wrapper


def multi_replace(
    text: str,
    old: list[str] | list[tuple[str, str]],
    new: str='-',
    count: int=-1
):
    """ Returns `text` after replacing all items of `old` with `new`
    - If `old = list[tuple[str, str]]`: 
        - `new` would be ignored.
        - second item of tuple would replace first item
    - `count`: 
        - Maximum number of occurrences to replace. 
        - Default = -1 : means replace all occurrences.
    """
    for i in old:
        if isinstance(i, str):
            text = text.replace(
                i,
                new, 
                count
            )
        else:
            text = text.replace(
                i[0],
                i[1],
                count
            )
    return text


def get_desktop_path():
    """ Returns: Desktop path, create if not exist """
    desktop = os.path.join(
        os.environ.get(
            'USERPROFILE',
            '/'
        ), 
        'Desktop'
    )
    if not os.path.exists(desktop):
        os.makedirs(desktop)
    return desktop


def get_saving_directory():
    """ Returns: Path of directory where extracted links will be saved , create if not exist """
    dirPath =  os.path.join(
        get_desktop_path(),
        'Extracted Links'
    )
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    return dirPath




## ----------------------------------------------- Program ----------------------------------------------- ##
class Settings(gSettings):
    """ Handles all settings related functions """
    
    def get_setting_str(self, setting: str):
        """ Returns: `Enabled/Disabled` based on the `setting` """
        return "ENABLED" if self.get_setting(
            setting
        ) else "DISABLED"



class Choices:
    """ Handles choices related data """
    
    def __init__(self, settingsInstance:Settings) -> None:
        # Settings
        rawSetting = settingsInstance.get_setting_str('raw')
        
        # Choices
        self._choices :dict[str, tuple[str, str]] = {
            '1': (
                '[File] Web links', 
                '(http/https)'
            ),
            '2': (
                '[File] FTP links',
                '(ftp)'
            ),
            '3': (
                '[File] MAIL links',
                '(mailto)'
            ),
            '4': (
                '[File] All types of links',
                ''
            ),
            'web': (
                '[Web ] All types of links', 
                ''
            ),
            'about': (
                'About this app',
                ''
            ),
            'raw': (
                'Enable/Disable raw formatting of links', 
                f'({rawSetting})'
            )
        }
    
    def __str__(self) -> str:
        """ Returns: Proper formatted string of all choices """
        choicesStr = ''
        for a, b in self._choices.items():
            choicesStr += f'• {a:5} : {b[0]} {b[1]}\n'
        return choicesStr

    def get(self):
        """ Returns: All available choices """
        return self._choices
    
    def get_val(self, choice: str, default: tuple[str, str] | None=None):
        """ Returns: Value of `choice` from all choices
        - Returns: `default` if `choice` is not available in choices
        """
        return self._choices.get(
            choice,
            default if default else (None, None)
        )
    
    def have(self, choice:str):
        """ Returns: `True` if choice is available in choices """
        return choice in self._choices



class Extract_Links:
    """ Handles Links extraction """  

    @D_error_catcher
    def __init__(self, availableChoices:Choices, settingsInstance:Settings):
        # Args
        self.availableChoices = availableChoices
        self.settingsInstance = settingsInstance
        
        # User choices
        pp(
            app_name.center(
                os.get_terminal_size().columns
            ),
            end='\n\n'
        )
        self.userChoice = self.getUserChoice()
        
        # Main Action
        match self.userChoice:
            case 'about':   self.show_about_data()
            case 'raw':     self.switch_raw_setting()
            case _:         self.mainExtraction()
    
    def getUserChoice(self):
        """ Show user the choices and returns dict and the user choice """
        # Printing choices
        print(self.availableChoices)
        
        # Asking for user choice
        while True:
            choice = self.takeUserInput(
                f'Enter your choice ({"/".join(self.availableChoices.get())})'
            )
            if self.availableChoices.have(choice):
                print()
                return choice
        
    def mainExtraction(self):
        """ Main Links extraction """
        # Ask for source location -> Get its data
        match self.userChoice:
            case 'web':                                                                                         # Web
                self.sourcePath = self.takeUserInput(
                    'Enter web-address (Ex: github.com/sayyid5416)', 
                    [
                        (
                            '\\',
                            '/'
                        )
                    ],
                    web=True
                )
                sourceData = requests.get(
                    self.sourcePath
                ).text
            case _:                                                                                             # Local-file
                self.sourcePath = self.takeUserInput(
                    'Enter relative/absolute file-path',
                    [
                        (
                            '/',
                            '\\'
                        )
                    ]
                )
                try:
                    with open(self.sourcePath, encoding='utf-8') as f:
                        sourceData = f.read()
                except Exception:
                    with open(self.sourcePath) as f:
                        sourceData = f.read()
        
        # Extract links
        retData = self.get_extractedLinks(sourceData)
        
        # Save data -> open saved file
        self.saveToFile(
            retData[0],
            retData[1]
        )
        threading.Thread(
            target=lambda: os.system(
                f'""{self.get_filePath()}""'
            ),
            daemon=True
        ).start()


    ## -------------------------------------------- Others -------------------------------------------- ##
    @staticmethod
    def takeUserInput(question: str, replaceList: list[tuple[str, str]]=[], web: bool=False):
        """ Asks user input & Returns: modified text """    
        # Input
        x = multi_replace(
            text=pp_question(
                question
            ),
            old=replaceList
        )                                                                       # Also replace items according to replaceList
        if web and '://' not in x:
            x = 'https://' + x

        return x

    def get_filePath(self):
        """ Returns: File location where extracted links would be saved """
        # File Name
        fileName = multi_replace(
            self.sourcePath,
            old=[
                '\\',
                '/',
                ':',
                '*',
                '?',
                '"',
                '<',
                '>',
                '|'
            ],
            new='-'
        )
        fileName = str(
            self.availableChoices.get_val(
                self.userChoice
            )[0]
        ) + f' - {fileName}.txt'
        
        # File path
        return os.path.join(
            get_saving_directory(),
            fileName
        )
    
    def get_extractedLinks(self, sourceData:str):
        """ Returns: `(extracted-links, extraction-summary)` """
        _userChoice = self.userChoice
        
        def getLinks(regex:str) -> set[str] :
            return set(
                re.findall(
                    regex,
                    sourceData,
                    re.IGNORECASE
                )
            )
        
        # Extracting links from file
        webLinks   = getLinks(r'(https?://[^("\s<>)]+)')               # http[s]://anything_until (' ', <, >)
        ftpLinks   = getLinks(r'(ftp://[^("\s<>)]+)')                  # ftp://anything_until (' ', <, >)
        mailLinks  = getLinks(r'(mailto: *[^("\s<>)]+)')               # mailto:[whitespaces]anything_until (' ', <, >)

        # Extracted links
        match _userChoice:
            case '1':
                text = '◆ Web links:'
                linksList = webLinks
            case '2':
                text = '◆ FTP links:'
                linksList = ftpLinks
            case '3':
                text = '◆ Mail links:'
                linksList = mailLinks
            case '4' | 'web':
                text = '◆ All links:'
                linksList = webLinks.union(
                    ftpLinks,
                    mailLinks
                )
            case _  :   
                raise ValueError(
                    'Wrong inputs'
                )
        
        # Extraction summary
        summaryDict = {
            text: len(linksList)
        }
        if _userChoice in ['4', 'web']:
            summaryDict.update(
                {
                    '        • Web links:'  : len(webLinks)
                }
            )
            summaryDict.update(
                {
                    '        • FTP links:'  : len(ftpLinks)
                }
            )
            summaryDict.update(
                {
                    '        • Mail links:' : len(mailLinks)
                }
            )
        summaryDict.update(
            {
                '◆ Words:': len(
                    sourceData.split(
                        ' '
                    )
                )
            }
        )
        summaryDict.update(
            {
                '◆ Lines:': len(
                    sourceData.split(
                        '\n'
                    )
                )
            }
        )
        
        return linksList, summaryDict

    def saveToFile(self, extractedLinks:set[str], summary:dict[str, int]):
        """
        Function to write extracted links to a new file
        """
        fileLocation = self.get_filePath()
        rawEnabled = self.settingsInstance.get_setting('raw')
        with open(fileLocation, 'a+', encoding='utf-8') as f:
            # Summary
            currentTime = datetime.now().strftime(
                r'%d/%b/%Y   %I:%M %p'
            )
            summaryData = [
                f'{a} {b}' for a, b in summary.items()
            ]
            summaryStr = '\n'.join(
                summaryData + [
                    '\n'
                ]
            )
            f.write("•" * 84)
            if rawEnabled: 
                f.write("\n----- RAW FORMAT -----")
            f.write(f'\n● Links extracted from "{self.sourcePath}"\n● {currentTime}\n\n')
            f.write(summaryStr)
            
            # Links
            for i, link in enumerate(extractedLinks, start=1):
                threading.Thread(
                    target=lambda: pp_info(
                        f'[{i}] {link}'
                    )
                ).start()
                if rawEnabled:
                    f.write(f'{link}\n')
                else:
                    f.write(f'    [{i}] {link}\n')
            f.writelines(
                [
                    '‾' * 100, 
                    '\n\n\n'
                ]
            )
        
        # Summary
        pp_info_2(summaryStr)
        pp_info(f'=> Data saved to "{fileLocation}"')

    def show_about_data(self):
        data = {
            'app name': app_name,
            'saving directory': get_saving_directory(),
            'settings file': self.settingsInstance.settings_file_path,
            'creator': os.path.split(
                github_link
            )[0],
            'app webpage': github_link,
        }
        statement = ''
        for a, b in data.items():
            statement += f'{Fore.GREEN}• {a.title():17} : {Fore.LIGHTBLUE_EX}{b}\n'
        print(statement, end='')
        pp_info_2(f'{" " * 15} (Press <ctrl+c> any time to exit the app)\n')

        update_check = self.takeUserInput(
            'Check for updates? (y/n) '
        )
        if update_check.lower() in [
            'y', 
            'yes'
        ]:
            threading.Thread(
                target=lambda: webbrowser.open(
                    f'{github_link}/releases/latest'
                )
            ).start()
            pp_info('[Opening the app update page....]\n\n')
            time.sleep(2)
        else:
            pp_info('[Skipped]')

    def switch_raw_setting(self):
        """ Enable / Disable raw settings """
        oldRawSetting = self.settingsInstance.get_setting('raw')
        newRawSetting = not oldRawSetting
        self.settingsInstance.update_setting(
            'raw',
            newRawSetting
        )
        pp_info(
            f'[Raw formatting {self.settingsInstance.get_setting_str("raw")}]'
        )






############################################################################################## Run Main Program
if __name__ == "__main__":
    # Initiate settings
    defaultSettings = {
        'raw': False
    }
    settingsDir = os.path.join(
        os.environ.get(
            'LOCALAPPDATA', 'App-Data'
        ),
        app_name.replace(' ', '-')
    )
    settingsInst = Settings(
        default_settings=defaultSettings,
        settings_directory=settingsDir,
        settings_file_name=f"{app_name.lower().replace(' ', '-')}.json"
    )
    
    # Program
    while True:
        choicesInst = Choices(
            settingsInstance=settingsInst
        )
        Extract_Links(
            availableChoices=choicesInst,
            settingsInstance=settingsInst
        )
        print('\n\n')
