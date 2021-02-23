# Imports
import os, sys, subprocess, re, threading
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
        
        try:
            # User Choice
            print(Fore.WHITE, end='')
            print(f'Links Extractor v{app_version}'.title().center(os.get_terminal_size().columns))
            extraction_dict = {
                '1': ('Web links', '(http/https)'),
                '2': ('FTP links', '(ftp)'),
                '3': ('MAIL links', '(mailto)'),
                '4': ('All types of links', '')
            }
            for key, val in extraction_dict.items():
                print('', key, '-', val[0], val[1])
            
            self.user_choice = input(
                f'{Fore.WHITE}> Enter your choice ({"/".join(extraction_dict.keys())}) {Fore.LIGHTBLUE_EX}'
            )
            while not self.user_choice in extraction_dict.keys():
                self.user_choice = input(
                    f'{Fore.WHITE}> Enter your choice ({"/".join(extraction_dict.keys())}) {Fore.LIGHTBLUE_EX}'
                )
            print()
            
            # Files name
            if self.user_choice in ['1', '2', '3', '4']:
                # Get the file name
                self.original_file_name = input(
                    f'{Fore.WHITE}> Enter file name to extract links from it (relative/absolute path): {Fore.LIGHTBLUE_EX}'
                ).replace(
                    '/',
                    '\\'
                ).removeprefix('"').removesuffix('"').removeprefix("'").removesuffix("'")
                
                # Extracted links file name
                file_name = self.original_file_name
                if '\\' in file_name:
                    file_name = file_name.split('\\')[-1]        # get only last name, if '\' in 'file_name'
                self.file_to_save_extracted_links = f'{extraction_dict[self.user_choice][0]} - {file_name}.txt'
            
            # Main function
            self.main_extracting_fctn()
            
        except:
            print(f'{Fore.RED}=> [Error] Something went wrong. Try again...')
        

    def main_extracting_fctn(self):
        try:
            self.get_data_from_file(self.user_choice)       # Read from file
            self.write_data_to_file()       # Write to file
        except FileNotFoundError:
            print(f'{Fore.RED}=> [Error] "{self.original_file_name}" not found. Write the proper file name...')
        else:
            # Open saved extracted links file
            General_Class.open_file(
                file_to_open=self.file_to_save_extracted_links
            )


    def get_data_from_file(self, usr_choice):
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
            with open(self.original_file_name, encoding='utf-8') as orig_file:
                fctn(self, orig_file.read())
        except:
            with open(self.original_file_name) as orig_file:
                fctn(self, orig_file.read())


    def write_data_to_file(self):
        """
        Function to write data to a new file
        """
        
        with open(self.file_to_save_extracted_links, 'a+', encoding='utf-8') as f_new:
            
            # Heading
            f_new.writelines("•" * 84)
            f_new.writelines(
                f'\n● Links extracted from "{self.original_file_name}"\n'
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
                f'{Fore.YELLOW}=> Data saved to "{self.file_to_save_extracted_links}"'
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
