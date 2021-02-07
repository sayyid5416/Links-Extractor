# Imports
import os, sys
from datetime import datetime


# Main Extraction class
class Extract_Links:

    def __init__(self):
        super().__init__()

        # TAKE User Input
        self.original_file_name = input(f'{Fore.WHITE}> Enter file name to extract links from it (Ex: file name.txt):  {Fore.LIGHTBLUE_EX}')
        self.file_to_save_extracted_links = f'Links - {self.original_file_name}.txt'
        # Data in file
        self.total_lines_num = self.total_words_num = self.total_links_num =  0
        self.links_in_the_file_list = []
        # MAIN
        self.main_extracting_fctn()


    # Main Function
    def main_extracting_fctn(self):
        try:
            self.get_data_from_file()       # Read from file
            self.write_data_to_file()       # Write to file
        except FileNotFoundError:
            print(f'{Fore.RED}=> [Error] "{self.original_file_name}" not found. Write the proper file name...')
        else:
            os.system(f'"{self.file_to_save_extracted_links}"')      # Open saved extracted links file


    def get_data_from_file(self):
        """
        Function to read data from file
        """
        # Getting data
        with open(self.original_file_name) as orig_file:
            for line in orig_file.readlines():
                self.total_lines_num += 1            # increase lines number
                for word in line.split(' '):
                    self.total_words_num += 1        # increase words number
                    if 'http' in word:
                        self.total_links_num += 1    # increase links number
                        self.links_in_the_file_list.append(word)
                        print(f'{Fore.GREEN}--- Extracted --- {word}', end='')


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
            for link in self.links_in_the_file_list:
                f_new.writelines(link)

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


################################################################### RUN
if __name__ == "__main__":
    
    # IMPORT: Third party modules
    try:
        from colorama import Fore, Style
    except Exception as e:
        # Console Properties
        os.system('color 0c')
        os.system('title [Error] Missing modules')
        input(f'=> [Error] {e}. Press Enter to exit...')
        sys.exit()
        
    # Main Program
    else:
        # Console Properties
        os.system('color 0f')
        os.system('title Extract links from a file')

        # Main Extraction
        print(f'{Fore.YELLOW + Style.BRIGHT}Note: File containing links must be in the same directory as this python file.')
        while True:
            try:
                Extract_Links()
            except:
                print(f'{Fore.RED}=> [Error] Something went wrong. Try again...')
            print('\n\n')