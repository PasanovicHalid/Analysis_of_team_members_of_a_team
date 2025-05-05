from genericpath import isfile
from ntpath import join
import os
from chatgpt_selenium_automation.handler import ChatGPTAutomation

chrome_driver_path = r"C:\Users\halid\Desktop\chromedriver-win64\chromedriver.exe"

chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'

def read_from_text_file(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read()
    
def find_all_files(directory):
    return [f for f in os.listdir(directory) if isfile(join(directory, f))]

def prompt():
    # Create an instance
    chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path, r"https://chatgpt.com/g/g-wVvYLVCm5-teamwork-pull-request-helper")

    files_root = "C:\\Users\\halid\\Desktop\\Master\\ChatGPT Selenium Chatter\\generated_files\\pull_request_handling"

    files = find_all_files(files_root)

    chatgpt.send_prompt_to_chatgpt("Now you will be provided with batches of pull requests. Analyze the batch of pull requests.")

    for i in range(len(files)):
        file_name = files_root + "\\" + files[i]
        chatgpt.send_file_to_chatgpt(file_name)

        if i == len(files) - 1:
            chatgpt.send_prompt_to_chatgpt("This is the overview of the pull request history.")
        else:
            chatgpt.send_prompt_to_chatgpt("Analyse these pull requests.")

    chatgpt.send_prompt_to_chatgpt("Sumarize everything about the pull requests.")

    chatgpt.save_conversation("pull_request_conversation.txt")

    # Close the browser and terminate the WebDriver session
    chatgpt.quit()

if __name__ == "__main__":
    prompt()