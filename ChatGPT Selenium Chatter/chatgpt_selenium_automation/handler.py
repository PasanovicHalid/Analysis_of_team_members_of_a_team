import os
import socket
import threading
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ChatGPTAutomation:

    def __init__(self, chrome_path, chrome_driver_path, url=None):
        """
        This constructor automates the following steps:
        1. Open a Chrome browser with remote debugging enabled at a specified URL.
        2. Prompt the user to complete the log-in/registration/human verification, if required.
        3. Connect a Selenium WebDriver to the browser instance after human verification is completed.

        :param chrome_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        :param chrome_driver_path: file path to chromedriver.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        """

        self.chrome_path = chrome_path
        self.chrome_driver_path = chrome_driver_path

        free_port = self.find_available_port()
        self.launch_chrome_with_remote_debugging(free_port, url)
        time.sleep(5)
        #self.wait_for_human_verification()
        self.driver = self.setup_webdriver(free_port)
        self.cookie = self.get_cookie()

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
            chrome_cmd = f"{self.chrome_path} --remote-debugging-port={port} {url}"
            os.system(chrome_cmd)

        chrome_thread = threading.Thread(target=open_chrome)
        chrome_thread.start()

    def setup_webdriver(self, port):
        """  Initializes a Selenium WebDriver instance, connected to an existing Chrome browser
             with remote debugging enabled on the specified port"""

        chrome_options = webdriver.ChromeOptions()
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

        input_box = self.driver.find_element(by=By.XPATH, value='//textarea[contains(@id, "prompt-textarea")]')
        self.driver.execute_script(f"arguments[0].value = `{prompt}`;", input_box)
        input_box.send_keys(Keys.RETURN)
        input_box.submit()
        self.check_response_ended()

    def send_file_to_chatgpt(self, file_name):
        """ Sends a file to ChatGPT and waits for 20 seconds for the response """

        input_box = self.driver.find_element(by=By.XPATH, value='//input[@type="file"]')
        self.driver.execute_script("arguments[0].value = '';", input_box)
        input_box.send_keys(file_name)
        self.check_response_ended()

        start_time = time.time()
        while len(self.driver.find_elements(by=By.TAG_NAME, value="circle")) > 1:
            time.sleep(0.5)
            # Exit the while loop after 60 seconds anyway
            if time.time() - start_time > 60:
                break
        time.sleep(2)

    def check_response_ended(self):
        """ Checks if ChatGPT response ended """
        start_time = time.time()
        time.sleep(1)
        while len(self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base')[-1].find_elements(
                by=By.CSS_SELECTOR, value='button[data-testid="send-button"]')) < 1:
            time.sleep(2)
            # Exit the while loop after 60 seconds anyway
            if time.time() - start_time > 60:
                break
        time.sleep(4)  # the length should be =4, so it's better to wait a moment to be sure it's really finished

    def return_chatgpt_conversation(self):
        """
        :return: returns a list of items, even items are the submitted questions (prompts) and odd items are chatgpt response
        """

        user_questions = self.driver.find_elements(by=By.CSS_SELECTOR, value='div[data-message-author-role="user"]')
        chatgpt_responses = self.driver.find_elements(by=By.CSS_SELECTOR, value='div[data-message-author-role="assistant"]')
        
        full_conversation = []

        for i in range(len(user_questions)):
            full_conversation.append(user_questions[i])
            full_conversation.append(chatgpt_responses[i])
        
        return full_conversation

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

        directory_name = "generated_files\\conversations"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        delimiter = "-" * 50
        chatgpt_conversation = self.return_chatgpt_conversation()
        with open(os.path.join(directory_name, file_name), 'w', encoding="utf-8") as file:
            for i in range(0, len(chatgpt_conversation), 2):
                file.write(
                    f"prompt: \n{chatgpt_conversation[i].text}\n\nresponse: \n{chatgpt_conversation[i + 1].text}\n\n{delimiter}\n\n",)

    def return_last_response(self):
        """ :return: the text of the last chatgpt response """

        response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value='div[data-message-author-role="assistant"]')
        return response_elements[-1].text

    @staticmethod
    def wait_for_human_verification():
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
        try:
            self.driver.quit()
        except Exception as inst:
            return
