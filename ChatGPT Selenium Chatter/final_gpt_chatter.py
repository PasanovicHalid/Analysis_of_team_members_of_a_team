from genericpath import isfile
from ntpath import join
import os
from chatgpt_selenium_automation.handler import ChatGPTAutomation
from commit_prompt_chatter import prompt as commit_prompt
from pull_request_analysis_chatter import prompt as pull_request_analysis_prompt
from retrospective_prompt_chatter import prompt as retrospective_prompt
from trello_prompt_chatter import prompt as trello_prompt

chrome_driver_path = r"C:\Users\halid\Desktop\chromedriver-win64\chromedriver.exe"

chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'

def read_from_text_file(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read()
    
def find_all_files(directory):
    return [f for f in os.listdir(directory) if isfile(join(directory, f))]

retrospective_prompt()
pull_request_analysis_prompt()
trello_prompt()
commit_prompt()

chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path, r"https://chatgpt.com/g/g-t0k4YKG8U-teamwork-finalizer")

files_root = "C:\\Users\\halid\\Desktop\\Master\\ChatGPT Selenium Chatter\\generated_files\\conversations"

files = find_all_files(files_root)

for i in range(len(files)):
    file_name = files_root + "\\" + files[i]
    chatgpt.send_file_to_chatgpt(file_name)

chatgpt.send_prompt_to_chatgpt("You are provided with all of the conversations. Analyze the conversations and find all the positive behaviors of the team")

chatgpt.send_prompt_to_chatgpt("Analyze the conversations and find all the negative behaviors of the team")

chatgpt.send_prompt_to_chatgpt(f"""Task Description:
Please create two tables based on the analysis of Shared Cognition within software engineering teams:

Positive Behaviors Table:
List all positive behaviors.
Describe how each positive behavior has positively affected Shared Cognition

Negative Behaviors Table:

List all negative behaviors.
Provide suggestions on how to improve or eliminate each negative behavior.

These tables will help teams understand and enhance their collaborative efforts by clearly identifying beneficial practices and addressing detrimental ones.""")

chatgpt.quit()
    