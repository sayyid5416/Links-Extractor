# Imports
import os, sys, subprocess, re, threading, requests
from datetime import datetime
from colorama.ansi import Style

app_version = '1.5'
github_link = 'https://github.com/hussain5416/extract_links'

# Console properties
if __name__ == "__main__":
    os.system('color 07')
    os.system(f'title Extract links from a file [v{app_version}] -- {github_link}')



# Main Extraction class
class Extract_Links:

    def __init__(self):
        super().__init__()
        self.webcrawl = False
        
        try:
            # User Choice
            print(Fore.WHITE, end='')
            print(f'Links Extractor v{app_version}'.title().center(os.get_terminal_size().columns))
            choices_dict = {
                '1': ('Web links', '(http/https)'),
                '2': ('FTP links', '(ftp)'),
                '3': ('MAIL links', '(mailto)'),
                '4': ('All types of links', ''),
                '5': ('Web-Crawl', '')
            }
            for key, val in choices_dict.items():
                print('', key, '-', val[0], val[1])
            
            self.user_choice = input(
                f'{Fore.WHITE}> Enter your choice ({"/".join(choices_dict.keys())}) {Fore.LIGHTBLUE_EX}'
            )
            while not self.user_choice in choices_dict.keys():
                self.user_choice = input(
                    f'{Fore.WHITE}> Enter your choice ({"/".join(choices_dict.keys())}) {Fore.LIGHTBLUE_EX}'
                )
            print()
            
            # Files name
            if self.user_choice in ['1', '2', '3', '4']:
                # Get the file name
                self.old_file_name = input(
                    f'{Fore.WHITE}> Enter file name to extract links from it (relative/absolute path): {Fore.LIGHTBLUE_EX}'
                ).replace(
                    '/',
                    '\\'
                ).removeprefix('"').removesuffix('"').removeprefix("'").removesuffix("'")
                
                # Extracted links file name
                file_name = self.old_file_name
                if '\\' in file_name:
                    file_name = file_name.split('\\')[-1]        # get only last name, if '\' in 'file_name'
                self.new_file_name = f'{choices_dict[self.user_choice][0]} - {file_name}.txt'
            
            # Web Crawling
            elif self.user_choice == '5':
                # webpage
                self.webcrawl = True
                self.webpage = input(
                    f'{Fore.WHITE}> Enter WEB-Page address to extract links from it (Ex: github.com/hussain5416): {Fore.LIGHTBLUE_EX}'
                ).replace(
                    '\\',
                    '/'
                ).removeprefix('"').removesuffix('"').removeprefix("'").removesuffix("'")
                
                # Extracted links file name
                text = self.webpage
                for i in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                    text = text.replace(i, '-')
                self.new_file_name = f'{choices_dict[self.user_choice][0]} - {text}.txt'
                
                # Getting source code of webpage
                source_code = requests.get(self.webpage).text
                with open('TEMP_FILE', 'w') as temp_file:           #todo Move this temp file os temporary directory
                    for i in source_code:
                        try:
                            temp_file.write(i)
                        except UnicodeError:
                            pass
                self.old_file_name = 'TEMP_FILE'
                self.user_choice = '4'
                
            # Main function
            self.main_extracting_fctn(
                self.user_choice,
                self.old_file_name,
                self.new_file_name
            )
            
        except:
            print(f'{Fore.RED}=> [Error] Something went wrong. Try again...')
        

    def main_extracting_fctn(self, usr_choice, orig_file_location, extracted_file_location):
        try:
            self.get_data_from_file(
                orig_file_location, 
                usr_choice
            )                                           # Read from file
            
            orig_file_name = orig_file_location
            if self.webcrawl:
                orig_file_name = self.webpage
                
            self.write_data_to_file(
                orig_file_name, 
                extracted_file_location
            )                                           # Write to file
            
        except FileNotFoundError:
            print(
                f'{Fore.RED}=> [Error] "{orig_file_location}" not found. Write the proper file name...'
            )
            
        else:
            # Open saved extracted links file
            General_Class.open_file(
                file_to_open=extracted_file_location
            )


    def get_data_from_file(self, orig_file_location, usr_choice):
        """
        Function to get data from file
        """
        
        # PROPER Function
        def  fctn(self, data_in_file):
            
            # Extracting links from file
            def extract_links_proper(regex_string:str):
                """
                This function returns a 'LIST' of matching items, based on the passed 'REG-EX'
                """
                
                extracted_list = General_Class.non_duplicated_list(
                    re.findall(
                        regex_string,
                        data_in_file,
                        re.IGNORECASE
                    )
                )

                return extracted_list
            
            web_links = extract_links_proper(
                r'(https?://[^(\s<>)]+)'                    # http[s]://anything_until (' ', <, >)
            )
            ftp_list = extract_links_proper(
                r'(ftp://[^(\s<>)]+)'                       # ftp://anything_until (' ', <, >)
            )
            mail_links = extract_links_proper(
                r'(mailto: *[^(\s<>)]+)',                   # mailto:[whitespaces]anything_until (' ', <, >)
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
            self.extracted_items_list = user_choice_dict[usr_choice][1]
            
            # Additional data
            self.additional_items_dict = {}
            self.additional_items_dict.update(
                {
                    user_choice_dict[usr_choice][0]: len(user_choice_dict[usr_choice][1])
                }
            )
            if usr_choice == '4':
                self.additional_items_dict.update(
                    {
                        '        • Web links:': len(web_links),
                        '        • FTP links:': len(ftp_list),
                        '        • Mail links:': len(mail_links)
                    }
                )
            self.additional_items_dict.update(
                {
                    '◆ Words:': len(data_in_file.split(' ')),
                    '◆ Lines:': len(data_in_file.split('\n'))
                }
            )
            
        
        # Getting data (try & except block: To solve encoding issues)
        try:
            with open(orig_file_location, encoding='utf-8') as f:
                fctn(self, f.read())
        except:
            with open(orig_file_location) as f:
                fctn(self, f.read())


    def write_data_to_file(self, orig_file_name, extracted_file_location):
        """
        Function to write data to a new file
        """
        
        with open(extracted_file_location, 'a+', encoding='utf-8') as f_new:
            
            # Heading
            f_new.writelines("•" * 84)
            f_new.writelines(
                f'\n● Links extracted from "{orig_file_name}"\n'
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
            
            # Conclusion
            print(
                f'{Fore.BLUE}{conclusion}\n'
                f'{Fore.YELLOW}=> Data saved to "{extracted_file_location}"'
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

# Import: Third party modules
try:
    from colorama import Fore

# Installing missing imports
except:
    # Asks permission
    if input(f'=> [Error] Some modules missing. Install missing modules? (y/n) ') == 'y':
        
        # Modules to install
        modules_list = [
            'colorama'
        ]                       
        
        # Process
        print('\n')
        print('*' * 50)
        try:                                            # Installing
            General_Class.import_modules(modules_list)
        except Exception as e:                          # Error catching
            input(f'=> [Error]: {e}. Press enter to exit...')
            sys.exit()
        else:                                           # Importing
            from colorama import Fore
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
