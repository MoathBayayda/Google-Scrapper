import platform
import subprocess
import sys
ascii_art = """

        ┏┓      ┓   ┳┓    ┓   ┏┓              ┏    ┏┓      ┓   ┓
        ┃┓┏┓┏┓┏┓┃┏┓ ┃┃┏┓┏┓┃┏┏ ┗┓┏┏┓┏┓┏┓┏┓┏┓┏┓ ┃┏┓┏┓┃ ┏┓┏┓╋┏┣┓┏┓┃
        ┗┛┗┛┗┛┗┫┗┗ ━┻┛┗┛┛ ┛┗┛━┗┛┗┛ ┗┻┣┛┣┛┗ ┛ ━┗┛ ┗ ┗┛┗┻┣┛┗┗┛┗┗┻┛
               ┛                     ┛ ┛               ┛        






"""

madeBy = """


"""
# import requests

import threading
import os
from colorama import Fore, Style
import requests
# from selenium.common.exceptions import ElementNotVisibleException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as webdriver
# from selenium import webdriver
from bs4 import BeautifulSoup
import time
import warnings
import random
import whisper
from anti_useragent  import UserAgent
# from selenium.webdriver.support.wait import WebDriverWait

# Suppress warnings
warnings.filterwarnings("ignore")

# Initialize Whisper model

model = whisper.load_model("base")

dorks_dir = ""
dorks_files_paths = []
max_number_of_threads = 0
number_of_pages = 0
is_headless = False
search_engines = []
available_search_engines = ['google', 'ask', 'bing']
is_stopped = False
driver = None
url_per_m = 0
progress = 0
total_dorks = 0
dorks_finished = 0
current_search_engine = ''
current_search_engine_order = 0
total_generated_urls = 0


# Configure headless browser options

# options.headless = False

# prefs = {"download.default_directory": "./recaptcha_audios"}

# options.add_experimental_option("prefs", prefs)

# options.add_argument("--headless=new")

# options.add_argument(f"--proxy-server=ecarumpx:sg038b7jf5xa@185.199.229.156:7492")

# driver = webdriver.Chrome(
#     service=Service(ChromeDriverManager().install()),
#     options=options
# )


# Function to transcribe audio from URL

def clear_terminal():
    # Determine the command based on the platform
    try:
        if platform.system() == "Windows":
            command = "cls"
        else:
            command = "clear"

        # Use subprocess to call the appropriate command
        subprocess.call(command, shell=True)
        if sys.platform.startswith("win"):
            # For Windows
            _ = sys.stdout.write("\033[H\033[2J")
        else:
            # For Linux and Mac
            _ = sys.stdout.write("\033c")
        sys.stdout.flush()
    except:
        sys.stdout.write(Fore.RED + Style.BRIGHT + "\n>Stopping ...\n")
        sys.stdout.write(Fore.RED + Style.BRIGHT + "Check files paths\n")
        is_aborted = True
        exit()

def set_viewport_size(driver, width, height):
    # window_size = driver.execute_script("""
    #     return [window.outerWidth - window.innerWidth + arguments[0],
    #       window.outerHeight - window.innerHeight + arguments[1]];
    #     """, width, height)
    driver.set_window_size(width, height)


def transcribe(url):
    with open('./recaptcha_audios/rec.mp3', 'wb') as f:
        f.write(requests.get(url).content)
        f.close()
    time.sleep(2)

    result = model.transcribe('./recaptcha_audios/rec.mp3')
    rec_text = result["text"].strip()
    os.remove('./recaptcha_audios/rec.mp3')
    return rec_text


# Function to click reCAPTCHA checkbox
def click_checkbox(driver):
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='reCAPTCHA']"))
    driver.find_element(By.ID, "recaptcha-anchor-label").click()
    driver.switch_to.default_content()


# Function to request audio version of reCAPTCHA
def request_audio_version(driver):
    driver.switch_to.default_content()
    driver.switch_to.frame(
        driver.find_element(By.XPATH, ".//iframe[@title='recaptcha challenge expires in two minutes']"))
    driver.find_element(By.ID, "recaptcha-audio-button").click()
    time.sleep(5)


# Function to solve audio reCAPTCHA
def solve_audio_captcha(driver):
    text = transcribe(driver.find_element(By.ID, "audio-source").get_attribute('src'))
    for letter in text:
        driver.find_element(By.ID, "audio-response").send_keys(letter)
        time.sleep(0.3)
    driver.find_element(By.ID, "recaptcha-verify-button").click()


# Main function to perform Google search and handle reCAPTCHA if necessary

def googleSearcherByTab(page, options, driver, dork_to_search, result_file_name):
    global total_generated_urls

    for i in range(0, page):
        try:

            ua = UserAgent()

            user_agent = ua.random

            options.add_argument(f'--user-agent={user_agent}')

            search_url = f"https://www.google.com/search?q={dork_to_search}&start={i}"

            set_viewport_size(driver, random.randint(800, 1440), random.randint(400, 900))

            driver.get(search_url)

            time.sleep(1)

            html = driver.page_source

            soup = BeautifulSoup(html)

            recaptcha_elements = soup.find_all('iframe', {'title': 'reCAPTCHA'})

            if recaptcha_elements:
                time.sleep(5)
                click_checkbox(driver)
                time.sleep(2)
                request_audio_version(driver)
                time.sleep(3)
                solve_audio_captcha(driver)

            else:
                try:
                    with open(result_file_name, 'a') as generated_urls_file:
                        # TODO add public filterer
                        links = soup.find_all('div', class_="yuRUbf")

                        for link in links:
                            generated_urls_file.write(link.a.get('href') + "\n")
                            total_generated_urls += 1

                        generated_urls_file.close()

                except Exception as e:
                    print(f"{Fore.RED + Style.BRIGHT}\n\nError opening result url, {e}")
                    return



        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}\n\nError searching dork, {e}")
            return


def googleScrapper():
    global max_number_of_threads, dorks_files_paths, is_stopped
    global dorks_finished, driver, is_headless

    options = Options()
    if is_headless:
        options.add_argument("--headless=new")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.accept_insecure_certs = True
    options.enable_downloads = True

    seleniumwire_options = {
        "proxy": {
            "http": "http://ecarumpx:sg038b7jf5xa@185.199.229.156:7492",
        },
    }

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        # seleniumwire_options=seleniumwire_options,
        options=options
    )

    for i in range(1, max_number_of_threads):
        driver.execute_script("window.open('');")

    for dork_file_path in dorks_files_paths:
        try:
            with open(dork_file_path, 'r') as dork_file:

                dorks = dork_file.read().split("\n")

                dorks_counter = 0

                threads_dorks = []

                dork_file_max_threads = max_number_of_threads
                if len(dorks) < max_number_of_threads:
                    dork_file_max_threads = len(dorks)
                while dorks_counter < len(dorks):

                    if dorks_counter % dork_file_max_threads != 0 or dorks_counter == 0:
                        threads_dorks.append(dorks[dorks_counter].strip())

                    else:
                        for page in range(0, number_of_pages):

                            for tab_index in range(0, dork_file_max_threads):
                                ua = UserAgent()

                                user_agent = ua.random

                                options.add_argument(f'--user-agent={user_agent}')

                                driver.switch_to.window(driver.window_handles[tab_index])

                                # googleSearcherByTab(page, options, driver, threads_dorks[tab_index],
                                #                     f"./result/google/{str(dorks_counter - dork_file_max_threads + tab_index)}.txt")
                                googleSearcherByTab(page, options, driver, threads_dorks[tab_index],
                                                    f"./result/google/{"url_"+os.path.basename(dork_file_path).split('/')[-1]}")

                        threads_dorks = []

                        dorks_finished += dork_file_max_threads
                    dorks_counter += 1
                else:
                    if len(dorks) % dork_file_max_threads != 0:
                        remaining_dorks_counter = 0

                        while remaining_dorks_counter < len(dorks) % dork_file_max_threads:

                            for page in range(0, number_of_pages):
                                ua = UserAgent()

                                user_agent = ua.random

                                options.add_argument(f'--user-agent={user_agent}')

                                driver.switch_to.window(driver.window_handles[tab_index])

                                googleSearcherByTab(page, options, driver, dorks[dorks_counter + remaining_dorks_counter],
                                                    f"./result/google/{str(dorks_counter + remaining_dorks_counter)}.txt")
                                dorks_finished += 1

        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}\n\nError opening dork file")
            driver.quit()
            is_stopped = True
            return

    driver.quit()


def searchEnginesRoot():
    global search_engines
    global url_per_m, progress, total_dorks, dorks_finished, current_search_engine_order, total_generated_urls, current_search_engine

    for search_engine in search_engines:
        match search_engine:

            case "google":
                current_search_engine = 'Google'
                googleScrapper()

        current_search_engine_order += 1


def loggerThread():
    global url_per_m, progress, total_dorks, dorks_finished, current_search_engine_order, total_generated_urls
    global is_stopped, search_engines

    loading_symbols = ['|', '/', '-', '\\']
    loading_symbols_counter = 0
    while not is_stopped:
        progress = ((dorks_finished / total_dorks) * 100)// 1

        print(Fore.GREEN + ascii_art)
        print(Fore.GREEN + madeBy)

        print(f"{Fore.GREEN}[{Fore.BLUE + loading_symbols[loading_symbols_counter]}{Fore.GREEN}] Generating urls ...")
        print(f"{Fore.GREEN}Total dorks : {Fore.BLUE + str(total_dorks)}")
        print(
            f"{Fore.GREEN}Current search engine order : {Fore.BLUE + str(current_search_engine_order)}{Fore.GREEN}/{Fore.BLUE}{len(search_engines)}")
        print(f"{Fore.GREEN}Progress : {Fore.BLUE + str(progress)} %")
        print(f"{Fore.GREEN}Dorks finished in current search engine : {Fore.BLUE + str(dorks_finished)}")
        print(f"{Fore.GREEN}Total generated urls : {Fore.BLUE + str(total_generated_urls)}")
        print(f"{Fore.GREEN}Url per minute : {Fore.BLUE + str(url_per_m)}")

        move_up = "\033[F" * 24
        print(move_up, end='\r')

        loading_symbols_counter += 1
        if loading_symbols_counter >= len(loading_symbols):
            loading_symbols_counter = 0


def urlPMCalc():
    global url_per_m, total_generated_urls, is_stopped

    while not is_stopped:
        current_url_per_m = url_per_m
        time.sleep(60)
        url_per_m = url_per_m - current_url_per_m
    pass


def totallDorksCalc():
    global total_dorks, dorks_files_paths
    try:
        for dorks_file_path in dorks_files_paths:
            with open(dorks_file_path, 'r') as dorks_file:
                total_dorks += len(dorks_file.read().split("\n"))
                dorks_file.close()
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}\n\nError opening dorks file, {e}")
        return


def main():
    global search_engines, dorks_dir, max_number_of_threads, number_of_pages, is_headless, search_engines

    global dorks_files_paths, is_stopped

    try:
        print(Fore.GREEN + ascii_art)
        print(Fore.GREEN + madeBy)

        print(Fore.GREEN + "> Enter the directory of the dorks, example : c:\\users\\dorks")
        print(Fore.GREEN + "> *Note* only .txt files are supported")

        dorks_dir = input(f"{Fore.GREEN + Style.BRIGHT}> ")

        print(Fore.GREEN + "> Enter max number of threads to be used")
        max_number_of_threads = int(input(f"{Fore.GREEN + Style.BRIGHT}> "))

        print(Fore.GREEN + "> Enter number of pages to search")
        number_of_pages = int(input(f"{Fore.GREEN + Style.BRIGHT}> "))

        print(Fore.GREEN + "> Do you want to see browser? enter y as yes or n as no")
        is_headless_prompt = input(f"{Fore.GREEN + Style.BRIGHT}> ")

        if is_headless_prompt == "y" or is_headless_prompt == "Y":
            is_headless = False
        elif is_headless_prompt == "n" or is_headless_prompt == "N":
            is_headless = True
        else:
            print(f"\n\n{Fore.RED + Style.BRIGHT}Enter a valid answer, exiting ...\n\n")
            return -1

        print(Fore.GREEN + "> Enter search engines to use from the following: google, being, ask.")
        print(Fore.GREEN + "> Note example input: -all , utilize all search engines")
        print(Fore.GREEN + "> Note example input:-google -bing -ask. -search engine name from the previous list")

        search_engines_answer = input(f"{Fore.GREEN + Style.BRIGHT}> ").split("-")

        search_engines_answer.remove('')

        if len(search_engines_answer) == 1 and search_engines_answer[0] == 'all':
            search_engines = available_search_engines
        else:
            for search_engine in search_engines_answer:
                if search_engine.strip() not in available_search_engines:
                    print(f"\n\n{Fore.RED + Style.BRIGHT}> Enter a valid answer\n\n")
                    return -1
            search_engines = search_engines_answer

        if len(search_engines) == 0:
            print(f"\n\n{Fore.RED + Style.BRIGHT}> Please validate your input\n\n")
            return -1

        for dork_file_path in os.listdir(dorks_dir):
            if dork_file_path.split(".")[1] == "txt":
                dorks_files_paths.append(os.path.join(dorks_dir, dork_file_path))

        if len(dorks_files_paths) == 0:
            print(f"\n\n{Fore.RED + Style.BRIGHT}> Dorks folder is empty\n\n")
            return -1

        print(f"{Fore.GREEN}Loading dorks ...")

        logger_thread = threading.Thread(target=loggerThread)
        total_dorks_calc_thread = threading.Thread(target=totallDorksCalc)
        url_p_m_calc_thread = threading.Thread(target=urlPMCalc)

        clear_terminal()

        total_dorks_calc_thread.start()
        total_dorks_calc_thread.join()

        logger_thread.start()
        url_p_m_calc_thread.start()

        searchEnginesRoot()




    except Exception as e:
        print(f"\n\n{Fore.RED + Style.BRIGHT}Error occurred, check your input {e}\n\n")
        is_stopped = True


if __name__ == "__main__":
    try:

        # key = get_random_bytes(16)  # 16 bytes = 128 bits
        # print(key.hex())  # Print the key in hexadecimal format

        main()

    except KeyboardInterrupt:
        print(f"\n{Fore.RED + Style.BRIGHT}Program interrupted by user. Exiting...")
        is_stopped = True
        if driver:
            driver.quit()
        sys.exit(0)  # Gracefully exit the program

    except Exception as e:
        print(f"\n\n{Fore.RED + Style.BRIGHT}exiting ... {e}\n\n")
        is_stopped = True

# choco install ffmpeg
