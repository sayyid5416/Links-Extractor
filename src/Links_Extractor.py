# Imports
import os, re, threading, requests
from datetime import datetime
from colorama import Fore
from colorama.ansi import Style


app_name = 'Links Extractor'
github_link = 'github.com/hussain5416/extract_links'


# Console properties
if __name__ == "__main__":
    os.system('color 07')
    os.system(f'title {app_name} - {github_link}')


def take_user_input(question_text:str, replace_tuple_list=[]):
    """
    This function asks user input and returns the modified text
    """    
    
    x = input(
        f'{Fore.WHITE}> {question_text}: {Fore.LIGHTBLUE_EX}'
    )
    
    if replace_tuple_list != []:
        for rep_tuple in replace_tuple_list:
            x.replace(
                rep_tuple[0],
                rep_tuple[1]
            )

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
                replace_tuple_list=rep_list
            )
            if self.webcrawl:
                if '://' not in self.source_location:
                    self.source_location = f'https://{self.source_location}'        # Add https://, if not present
            
            # File name for extracted links
            file_name = self.source_location
            for i in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                file_name = file_name.replace(i, '-')
            self.new_file_location = f'{choices_dict[self.user_choice][0]} - {file_name}.txt'   # TODO Change location to 'desktop' folder
                
            ## Main links extraction function
            self.main_extracting_fctn()
            
        except Exception as e:
            print(
                f'{Fore.RED}=> [Error 1] {e}, Try again...'
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
        print(app_name.center(os.get_terminal_size().columns))
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
                
        except Exception as e:
            print(
                f'{Fore.RED}=> [Error 2] {e}, Try again...'
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


class General_Class:
    """
    This class contains general methods
    """        

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



############################################################################################## Run Main Program
if __name__ == "__main__":
    print(Style.BRIGHT, end='')
    while True:
        Extract_Links()
        print('\n\n')
