from genericpath import isfile
from ntpath import join
import os
from chatgpt_selenium_automation.handler import ChatGPTAutomation
from commit_prompt_chatter import prompt as commit_prompt
from pull_request_analysis_chatter import prompt as pull_request_analysis_prompt
from retrospective_prompt_chatter import prompt as retrospective_prompt

chrome_driver_path = r"C:\Users\halid\Desktop\chromedriver-win64\chromedriver.exe"

chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'

def read_from_text_file(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read()
    
def find_all_files(directory):
    return [f for f in os.listdir(directory) if isfile(join(directory, f))]

chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path, r"https://chatgpt.com/g/g-W59P6T40S-teamwork-helper")

files_root = "C:\\Users\\halid\\Desktop\\Master\\ChatGPT Selenium Chatter\\generated_files\\conversations"

files = find_all_files(files_root)

chatgpt.send_prompt_to_chatgpt("Summarize me chapter 8 of the book")

for i in range(len(files)):
    file_name = files_root + "\\" + files[i]
    chatgpt.send_file_to_chatgpt(file_name)

chatgpt.send_prompt_to_chatgpt("You are provided with all of the conversations. Please summarize them.")

chatgpt.quit()
    