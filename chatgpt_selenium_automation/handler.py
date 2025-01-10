import os
import time
import socket
import platform
import threading

from selenium import webdriver
from selenium.webdriver.common.by import By


class ChatGPTAutomation:

    def __init__(self):
        """
        This constructor automates the following steps:
        1. Open a Chrome browser with remote debugging enabled at a specified URL.
        2. Prompt the user to complete the log-in/registration/human verification, if required.
        3. Connect a Selenium WebDriver to the browser instance after human verification is completed.

        :param chrome_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        :param chrome_driver_path: file path to chromedriver.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        """

        system = platform.system()

        if system == "Windows":
            self.chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'
            self.chrome_driver_path = rf"C:\Users\{os.getlogin()}\local\workspace\chromedriver.exe"
        elif system == "Darwin":  # macOS
            self.chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        else:
            return None

        url = r"https://chat.openai.com"
        free_port = self.find_available_port()
        self.launch_chrome_with_remote_debugging(free_port, url)
        self.driver = self.setup_webdriver(free_port)
        # self.driver.minimize_window()
        self.cookie = self.get_cookie()
        self.wait_for_human_verification()

    @staticmethod
    def find_available_port():
        """ This function finds and returns an available port number on the local machine by creating a temporary
            socket, binding it to an ephemeral port, and then closing the socket. """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def launch_chrome_with_remote_debugging(self, port, url):
        """ Launches a new Chrome instance with remote debugging enabled on the specified port and navigates to the
            provided url """

        def open_chrome():
            # headless = '' if len(sys.argv) > 1 and sys.argv[1] == '-h' else '--headless=new'
            headless = ''
            chrome_cmd = f"{self.chrome_path} --remote-debugging-port={port} --user-data-dir=remote-profile {headless} {url}"
            os.system(chrome_cmd)

        chrome_thread = threading.Thread(target=open_chrome)
        chrome_thread.start()

    def setup_webdriver(self, port):
        """  Initializes a Selenium WebDriver instance, connected to an existing Chrome browser
             with remote debugging enabled on the specified port"""

        chrome_options = webdriver.ChromeOptions()
        user_agent = "'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'"
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.binary_location = self.chrome_driver_path
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def get_cookie(self):
        """
        Get chat.openai.com cookie from the running chrome instance.
        """
        cookies = self.driver.get_cookies()
        cookie = [elem for elem in cookies if elem["name"] == '__Secure-next-auth.session-token'][0]['value']
        return cookie

    def send_prompt_to_chatgpt(self, prompt):
        """ Sends a message to ChatGPT and waits for 20 seconds for the response """

        input_box = self.driver.find_element(by=By.XPATH, value='//div[contains(@id, "prompt-textarea")]/p')
        self.driver.execute_script(f"arguments[0].innerText = `{prompt}`;", input_box)
        self.driver.find_element(by=By.XPATH, value="//button[@aria-label='Send prompt']").click()
        self.check_response_ended()

    def check_response_ended(self):
        """ Checks if ChatGPT response ended """
        time.sleep(1)
        start_time = time.time()
        while len(self.driver.find_elements(by=By.XPATH, value="//button[@aria-label='Stop streaming']")) > 0:
            time.sleep(0.5)
            if time.time() - start_time > 30:
                break
        time.sleep(1)

    def return_chatgpt_conversation(self):
        """
        :return: returns a list of items, even items are the submitted questions (prompts) and odd items are chatgpt response
        """

        return self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base > div.text-base')[:-1]

    def save_conversation(self, file_name):
        """
        It saves the full chatgpt conversation of the tab open in chrome into a text file, with the following format:
            prompt: ...
            response: ...
            delimiter
            prompt: ...
            response: ...

        :param file_name: name of the file where you want to save
        """

        directory_name = "conversations"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        delimiter = "|^_^|"
        chatgpt_conversation = self.return_chatgpt_conversation()
        with open(os.path.join(directory_name, file_name), "a") as file:
            for i in range(0, len(chatgpt_conversation), 2):
                file.write(
                    f"prompt: {chatgpt_conversation[i].text}\nresponse: {chatgpt_conversation[i + 1].text}\n\n{delimiter}\n\n")

    def return_last_response(self):
        """ :return: the text of the last chatgpt response """

        return self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base > div.text-base')[-2].text

    def wait_for_human_verification(self):
        time.sleep(2)
        login = self.driver.find_elements(by=By.XPATH, value="//div[text()='Log in']")

        if len(login) == 0:
            if (self.driver.title != "Just a moment..."):
                return

        print("You need to manually complete the log-in or the human verification if required.")

        while True:
            user_input = input(
                "Enter 'y' if you have completed the log-in or the human verification, or 'n' to check again: ").lower().strip()

            if user_input == 'y':
                print("Continuing with the automation process...")
                break
            elif user_input == 'n':
                print("Waiting for you to complete the human verification...")
                time.sleep(5)  # You can adjust the waiting time as needed
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def quit(self):
        """ Closes the browser and terminates the WebDriver session."""
        print("Closing the browser...")
        self.driver.close()
        self.driver.quit()
