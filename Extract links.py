# Imports
import os, sys, subprocess, re, threading
from datetime import datetime

def import_third_party_modules():                                                               #improve unify
    """
    Function to install third party modules
    """
    
    global modules_list, Fore, Style, requests
    
    # Modules to install
    modules_list = [
        'colorama',
        'requests'
    ]

    from colorama import Fore
    from colorama.ansi import Style
    import requests


app_version = '1.5'
github_link = 'https://github.com/hussain5416/extract_links'


# Console properties
if __name__ == "__main__":
    os.system('color 07')
    os.system(f'title Extract links from a file [v{app_version}] -- {github_link}')



def take_user_input(question_text:str, remove_quotes=False, replace_tuple_list=[]):
    """
    This function asks user input and returns the modified text
    """    
    
    x = input(
        f'{Fore.WHITE}> {question_text}: {Fore.LIGHTBLUE_EX}'
    )
    
    if remove_quotes:
        x.removeprefix('"').removesuffix('"').removeprefix("'").removesuffix("'")
    
    if replace_tuple_list != []:
        for rep_tuple in replace_tuple_list:
            x.replace(
                rep_tuple[0],
                rep_tuple[1]
            )

    return x



# Main Extraction class
class Extract_Links:

    def __init__(self):
        super().__init__()
        self.webcrawl = False
        
        try:
            # User choices
            choices_dict, self.user_choice = self.asks_user_choice()
            
            # Local file Crawling
            ques = 'Enter file name to extract links from it (relative/absolute path)'
            rep_list = [('/', '\\')]
            
            # Web Crawling
            if self.user_choice == '5':
                ques = 'Enter WEB-Page address to extract links from it (Ex: github.com/hussain5416)'
                rep_list = [('\\', '/')]
                self.webcrawl = True
                
            # Old location user input
            self.source_location = take_user_input(
                question_text=ques,
                remove_quotes=True,
                replace_tuple_list=rep_list
            )
            if self.webcrawl:
                if '://' not in self.source_location:
                    self.source_location = f'https://{self.source_location}'        # Add https://, if not present
            
            # File name for extracted links
            file_name = self.source_location
            for i in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                file_name = file_name.replace(i, '-')
            self.new_file_location = f'{choices_dict[self.user_choice][0]} - {file_name}.txt'
                
            ## Main links extraction function
            self.main_extracting_fctn()
            
        except:
            print(
                f'{Fore.RED}=> [Error] Something went wrong. Try again...'
            )
    
    
    def asks_user_choice(self):
        """
        This function shows user the choices and returns dict and the user choice
        """        
        
        # Choices dict
        choice_dict = {
            '1': ('Web links', '(http/https)'),
            '2': ('FTP links', '(ftp)'),
            '3': ('MAIL links', '(mailto)'),
            '4': ('All types of links', ''),
            '5': ('Web-Crawl', '(all links)')
        }
        
        # Printing choices
        print(Fore.WHITE, end='')
        print(f'Links Extractor v{app_version}'.title().center(os.get_terminal_size().columns))
        for key, val in choice_dict.items():
            print('', key, '-', val[0], val[1])
        
        # Asking for user choice
        choice_question = f'Enter your choice ({"/".join(choice_dict.keys())})'
        choice = take_user_input(choice_question)
        while not choice in choice_dict.keys():
            choice = take_user_input(choice_question)
        print()
        
        return choice_dict, choice
    

    def main_extracting_fctn(self):
        
        try:    
            ## Getting data from source location
            if self.webcrawl:
                self.data_to_parse = requests.get(
                    self.source_location
                ).text                                                              # Source code of webpage
                self.user_choice = '4'                                                      # for extracting all links
            else:                                                                   # Data from file
                try:                                                                        # solve encoding issues
                    with open(self.source_location, encoding='utf-8') as f:
                        self.data_to_parse = f.read()
                except:
                    with open(self.source_location) as f:
                        self.data_to_parse = f.read()
                        
            self.extract_links_from_string()                    # Extract links
            self.write_data_to_file()                           # Write links to a file
            
        except FileNotFoundError:
            print(
                f'{Fore.RED}=> [Error] "{self.source_location}" not found. Write the proper file name...'
            )
            
        else:
            # Open saved extracted links file
            General_Class.open_file(
                file_to_open=self.new_file_location
            )


    def extract_links_from_string(self):
        """
        This function extracts links from source location based on user choice
        """            
        
        # Extracting links from file
        def extract_links_proper(regex_string:str):
            """
            This function returns a 'LIST' of matching items, based on the passed 'REG-EX'
            """
            
            extracted_list = General_Class.non_duplicated_list(
                re.findall(
                    regex_string,
                    self.data_to_parse,
                    re.IGNORECASE
                )
            )

            return extracted_list
        
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
        user_choice_dict = {
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
        self.extracted_items_list = user_choice_dict[self.user_choice][1]
        
        # Additional data
        self.additional_items_dict = {}
        self.additional_items_dict.update(
            {
                user_choice_dict[self.user_choice][0]: len(user_choice_dict[self.user_choice][1])
            }
        )
        if self.user_choice == '4':
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
        
        with open(self.new_file_location, 'a+', encoding='utf-8') as f_new:
            
            # Heading
            f_new.writelines("•" * 84)
            f_new.writelines(
                f'\n● Links extracted from "{self.source_location}"\n'
                f'● {General_Class.get_current_date_and_time()}\n\n'
            )
            
            # Conclusion
            conclusion = '\n'.join(
                [f'{key} {val}' for key, val in self.additional_items_dict.items()]
            )
            f_new.writelines(f'{conclusion}\n\n')
            
            # Links
            for num, link in enumerate(self.extracted_items_list, start=1):
                print(f'{Fore.GREEN}{num} -- Extracted -- {link}')
                f_new.writelines(f'    {num} - {link}\n')

            f_new.writelines("‾" * 100)
            f_new.writelines('\n\n\n')
            
        # Print conclusion
        print(
            f'{Fore.BLUE}{conclusion}\n'
            f'{Fore.YELLOW}=> Data saved to "{self.new_file_location}"'
        )



# General class
class General_Class:
    """
    This class contains general methods
    """        

    @staticmethod
    def import_modules(list_of_modules):
        """
        This function install the modules

        Args:
            list_of_modules (list): These modules will be installed, if not present
        """
        
        # Start
        print('=> Modules installation started <=\n')
        
        # Installing modules
        for module in list_of_modules:
            subprocess.run(
                f'pip install {module}'
            )
        
        # Success
        print('\n=> All modules installed successfully <=')

    
    @staticmethod
    def get_current_date_and_time():
        """
        Returns: string: customised date and time
        """
        # Current Date
        months_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        day_today = datetime.now().day
        if day_today < 10:
            day_today = f'0{day_today}'
        current_date = f'{day_today}/{months_list[datetime.now().month - 1]}/{datetime.now().year}'
        
        # Current Time (12hr format)
        hour = datetime.now().hour
        minute = datetime.now().minute
        time_stamp = 'am'                   # AM
        if hour >= 12:                      # PM
            time_stamp = 'pm'
            if hour != 12:
                hour = hour - 12
        if minute < 10:
            minute = f'0{minute}'
        current_time = f'{hour}:{minute} {time_stamp}'
        
        return f'{current_date}   {current_time}'


    @staticmethod
    def open_file(file_to_open):
        """
        This function launches a file using subprocess module
            - Threading is used to keep the app functional
        """
        
        file_thread = threading.Thread(
            target=lambda : os.system(f'""{file_to_open}""'),
        )
        file_thread.setDaemon(True)
        file_thread.start()
    
    
    @staticmethod
    def non_duplicated_list(original_list):
        """
        This function returns a list after removing all the duplicates
        """

        new_list = []
        [new_list.append(item) for item in original_list if item not in new_list]
        
        return new_list


################################################################### Third party modules

# TRY: Importing Third party modules
# EXCEPT: Installing & importing missing imports
try:
    import_third_party_modules()
except:
    # Asks permission
    if input(f'=> [Error] Some modules missing. Install missing modules? (y/n) ') == 'y':
        # Process
        print('\n')
        print('*' * 50)
        try:                                                            # Installing
            General_Class.import_modules(modules_list)
        except Exception as e:                                          # Error catching
            input(f'=> [Error]: {e}. Press enter to exit...')
            sys.exit()
        else:                                                           # Importing
            import_third_party_modules()
            input('> Press Enter to continue...')
        print('*' * 50)
        print('\n\n')

    else:
        sys.exit()
        

################################################################### RUN

# Main Program
if __name__ == "__main__":
    print(Style.BRIGHT, end='')
    while True:
        Extract_Links()
        print('\n\n')
