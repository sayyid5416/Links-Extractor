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
                # Local file Crawling
                ques = 'Enter file name to extract links from it (relative/absolute path)'
                rep_list = [('/', '\\')]
                
                # Web Crawling
                if self.userChoice == '5':
                    ques = 'Enter WEB-Page address to extract links from it (Ex: github.com/hussain5416)'
                    rep_list = [('\\', '/')]
                    self.webcrawl = True
                    
                # Old location user input
                self.dataSource = takeUserInput(ques, rep_list)
                if self.webcrawl:
                    if '://' not in self.dataSource:
                        self.dataSource = f'https://{self.dataSource}'        # Add https://, if not present
                
                # NEW FILE - for extracted links
                self.fileLocation = self.get_extracted_file_location(choiceDict)
                    
                ## Main links extraction function
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
    
    def get_extracted_file_location(self, choices_dict):
        """
        - RETURNS the file location of NEW FILE, for extracted links
        - Creates parent folder - if missing
        """        
        
        # New File Name
        file_name = self.dataSource
        for i in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            file_name = file_name.replace(i, '-')
        new_f_name = f'{choices_dict[self.userChoice][0]} - {file_name}.txt'
        
        # Parent Folder location
        new_folder_location = os.path.join(
            winshell.desktop(),
            'Extracted Links'
        )
        if not os.path.exists(new_folder_location):
            os.makedirs(new_folder_location)
            
        # New File location
        new_file_loctn = os.path.join(
            new_folder_location,
            new_f_name
        )
        
        return new_file_loctn
    
    def main_extracting_fctn(self):
        
        try:
            ## Getting data from source location
            if self.webcrawl:
                self.data_to_parse = requests.get(
                    self.dataSource
                ).text                                                              # Source code of webpage
                self.userChoice = '4'                                                      # for extracting all links
            else:                                                                   # Data from file
                try:                                                                        # solve encoding issues
                    with open(self.dataSource, encoding='utf-8') as f:
                        self.data_to_parse = f.read()
                except:
                    with open(self.dataSource) as f:
                        self.data_to_parse = f.read()
                        
            self.extract_links_from_string()                    # Extract links
            self.write_data_to_file()                           # Write links to a file
            
        except FileNotFoundError:
            print(
                f'{Fore.RED}=> [Error] "{self.dataSource}" not found. Write the proper file name...'
            )
                
        except Exception as e:
            print(
                f'{Fore.RED}=> [Error 2] {e}, Try again...'
            )
            
        else:
            # Open saved extracted links file
            threading.Thread(
                target=lambda : os.system(f'""{self.fileLocation}""'),
                daemon=True
            ).start()

    def extract_links_from_string(self):
        """
        This function extracts links from source location based on user choice
        """            
        
        # Extracting links from file
        def extract_links_proper(regex_string:str) -> list[str] :
            """
            This function returns a 'LIST' of matching items, based on the passed 'REG-EX'
            """
            return list(
                set(
                    re.findall(regex_string, self.data_to_parse, re.IGNORECASE)
                )
            )
        
        web_links = extract_links_proper(
            r'(https?://[^("\s<>)]+)'                    # http[s]://anything_until (' ', <, >)
        )
        ftp_list = extract_links_proper(
            r'(ftp://[^("\s<>)]+)'                       # ftp://anything_until (' ', <, >)
        )
        mail_links = extract_links_proper(
            r'(mailto: *[^("\s<>)]+)',                   # mailto:[whitespaces]anything_until (' ', <, >)
        )

        # User choice :: Links & Additional data
        user_choice_dict :dict[str, tuple[str, list[str]]] = {
            '1': (
                '◆ Web links:',
                web_links
            ),
            
            '2': (
                '◆ FTP links:',
                ftp_list
            ),
            
            '3': (
                '◆ Mail links:',
                mail_links
            ),
            
            '4': (
                '◆ All Links:',
                web_links + ftp_list + mail_links
            ),
        }
        
        # Links to extract
        self.extracted_items_list = user_choice_dict[self.userChoice][1]
        
        # Additional data
        self.additional_items_dict = {}
        self.additional_items_dict.update(
            {
                user_choice_dict[self.userChoice][0]: len(user_choice_dict[self.userChoice][1])
            }
        )
        if self.userChoice == '4':
            self.additional_items_dict.update(
                {
                    '        • Web links:': len(web_links),
                    '        • FTP links:': len(ftp_list),
                    '        • Mail links:': len(mail_links)
                }
            )
        self.additional_items_dict.update(
            {
                '◆ Words:': len(self.data_to_parse.split(' ')),
                '◆ Lines:': len(self.data_to_parse.split('\n'))
            }
        )

    def write_data_to_file(self):
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
            conclusionData = [f'{a} {b}' for a, b in self.additional_items_dict.items()]
            conclusion = '\n'.join(conclusionData + ['\n'])
            f.write(conclusion)
            
            # Links
            for i, link in enumerate(self.extracted_items_list, start=1):
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
