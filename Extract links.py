# Imports
import os, sys, subprocess, re, threading
from datetime import datetime

app_version = '1.3'

# Console properties
if __name__ == "__main__":
    os.system('color 07')
    os.system(f'title Extract links from a file [v{app_version}]')



# Main Extraction class
class Extract_Links:

    def __init__(self):
        super().__init__()
        
        try:
            # Original file
            self.original_file_name = input(f'{Fore.WHITE}> Enter file name to extract links from it (Ex: file name.html): {Fore.LIGHTBLUE_EX}').replace(
                '/',
                '\\'
            ).removeprefix('"').removesuffix('"').removeprefix("'").removesuffix("'")

            # File to save
            file_name = self.original_file_name
            if '\\' in file_name:
                file_name = file_name.split('\\')[-1]
            self.file_to_save_extracted_links = f'Links - {file_name}.txt'
            
            # Init: Additional Data
            self.total_lines_num = self.total_words_num = self.total_links_num =  0
            
            # MAIN
            self.main_extracting_fctn()
            
        except:
            print(f'{Fore.RED}=> [Error] Something went wrong. Try again...')
        

    # Main Function
    def main_extracting_fctn(self):
        try:
            self.get_data_from_file()       # Read from file
            self.write_data_to_file()       # Write to file
        except FileNotFoundError:
            print(f'{Fore.RED}=> [Error] "{self.original_file_name}" not found. Write the proper file name...')
        else:
            # Open saved extracted links file
            self.open_file(self.file_to_save_extracted_links)


    def get_data_from_file(self):
        """
        Function to read data from file
        """
        
        # PROPER Function
        def  fctn(self, a):
            data_in_file = a
            
            # Links list
            list_of_all_links = re.findall(
                r'(https?://[^\s]+)',
                data_in_file
            )                                   # List of all links present in the file
            self.extracted_links_list = []      # List for links after duplicate removal
            check_list = []                     # List for main links
            
            # Duplicate removal
            for link in list_of_all_links:
                main_link = str(link).removeprefix(str(link).split('://')[0])   # Link w/o 'http' like things
                if main_link not in check_list:
                    check_list.append(main_link)
                    self.extracted_links_list.append(link)      # Addding item to main list :: if its main_link was not added
                        
            # Additional data
            self.total_links_num = len(self.extracted_links_list)        # Total links
            self.total_words_num = len(data_in_file.split(' '))          # Total words
            self.total_lines_num = len(data_in_file.split('\n'))         # Total lines
        
        
        # Getting data
        try:
            with open(self.original_file_name, encoding='utf-8') as orig_file:
                fctn(self, orig_file.read())
        except:
            with open(self.original_file_name) as orig_file:
                fctn(self, orig_file.read())


    def write_data_to_file(self):
        """
        Function to write data to file
        """
        with open(self.file_to_save_extracted_links, 'a+', encoding='utf-8') as f_new:
            # Heading
            f_new.writelines(
                f'● Links extracted from "{self.original_file_name}"\n'
                f'● {self.get_current_date_and_time()}\n\n'
            )

            # Links
            for num, link in enumerate(self.extracted_links_list, start=1):
                print(f'{Fore.GREEN}{num} -- Extracted -- {link}')
                f_new.writelines(f'{num} - {link}\n')

            # Conclusion
            conclusion = (
                f'> Links found: {self.total_links_num}\n'
                f'> Total words: {self.total_words_num}\n'
                f'> Total lines: {self.total_lines_num}'
            )

            f_new.writelines(f'{conclusion}\n')
            f_new.writelines("````````````````````````````````````````````````````````````````````````````````````````````````````\n\n\n")

            print(
                f'{Fore.BLUE}{conclusion}\n'
                f'{Fore.YELLOW}=> Data saved to "{self.file_to_save_extracted_links}"'
            )


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
            target=lambda : os.system(f'"{file_to_open}"'),
        )
        file_thread.setDaemon(True)
        file_thread.start()
    
    

# General class
class General_Class:
    
    def __init__(self) -> None:
        """
        This class contains general methods
        """        
        pass

    
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
    while True:
        Extract_Links()
        print('\n\n')
