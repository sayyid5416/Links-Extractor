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
choiceDict :dict[str, tuple[str, str]] = {
    '1': ('Web links', '(http/https)'),
    '2': ('FTP links', '(ftp)'),
    '3': ('MAIL links', '(mailto)'),
    '4': ('All types of links', ''),
    '5': ('Web-Crawl', '(all links)'),
    '6': ('About', '')
}
choicesText = ''
for a, b in choiceDict.items():
    choicesText += f' {a} - {b[0]} {b[1]}\n'



class Extract_Links:

    def __init__(self):
        super().__init__()
        try:
            # User choices
            print(Fore.WHITE, end='')
            self.userChoice = self.getUserChoice()
            print(f'{Fore.RESET}', end='')
            
            # Main Action
            match self.userChoice:
                case '6':   self.show_about_data()
                case _:     self.mainExtraction()
        
        except FileNotFoundError:
            print(f'{Fore.RED}=> [Error] Source not found. Write proper file name...')
                
        except Exception as e:
            print(f'{Fore.RED}=> [Error] {e}, Try again...')
    
    def getUserChoice(self):
        """
        This function shows user the choices and returns dict and the user choice
        """
        # Printing choices
        print(app_name.center(os.get_terminal_size().columns))
        print(choicesText)
        
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
                self.sourcePath = self.takeUserInput('Enter web-address (Ex: github.com/hussain5416)', [('\\', '/')], web=True)
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
        dirPath = os.path.join(winshell.desktop(), 'Extracted Links')
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
        with open(fileLocation, 'a+', encoding='utf-8') as f:
            # Heading
            currentTime = datetime.now().strftime(r'%d/%b/%Y   %I:%M %p')
            f.write("•" * 84)
            f.write(f'\n● Links extracted from "{self.sourcePath}"\n● {currentTime}\n\n')
            
            # Summary
            summaryData = [f'{a} {b}' for a, b in summary.items()]
            summaryStr = '\n'.join(summaryData + ['\n'])
            f.write(summaryStr)
            
            # Links
            for i, link in enumerate(extractedLinks, start=1):
                print(f'{Fore.GREEN}{i} -- Extracted -- {link}')
                f.write(f'    {i} - {link}\n')

            # Footer
            f.write("‾" * 100)
            f.write('\n\n\n')
            
        # Print summary
        print(
            f'{Fore.BLUE}{summaryStr}'
            f'{Fore.YELLOW}=> Data saved to "{fileLocation}"'
        )

    def show_about_data(self):
        print(
            f'{Fore.GREEN}'
            "App Name: Links Extractor\n" \
            "Creator: Hussain Abbas\n" \
            f"App Webpage: {github_link}\n"
        )
        update_check = self.takeUserInput('Check for updates? (y/n) ')
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
