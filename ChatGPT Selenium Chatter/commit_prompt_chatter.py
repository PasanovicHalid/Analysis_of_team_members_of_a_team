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
    chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path, r"https://chatgpt.com/g/g-GJGOsEZzs-teamwork-github-helper")

    files_root = "C:\\Users\\halid\\Desktop\\Master\\ChatGPT Selenium Chatter\\generated_files\\commit_consistancy"

    files = find_all_files(files_root)

    chatgpt.send_prompt_to_chatgpt("Summarize me chapter 8 of the book")

    for i in range(len(files)):
        file_name = files_root + "\\" + files[i]
        chatgpt.send_file_to_chatgpt(file_name)

        if i == len(files) - 1:
            chatgpt.send_prompt_to_chatgpt("This is the overview of the commit history.")
        else:
            chatgpt.send_prompt_to_chatgpt("Analyse these commits.")

    chatgpt.send_prompt_to_chatgpt("Sumarize everything about the commits.")

    chatgpt.save_conversation("commit_conversation.txt")

    chatgpt.quit()

if __name__ == "__main__":
    prompt()