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
    chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path, r"https://chatgpt.com/g/g-roxqZbzS3-teamwork-trello-helper")

    files_root = "C:\\Users\\halid\\Desktop\\Master\\ChatGPT Selenium Chatter\\generated_files\\trello_actions"

    files = find_all_files(files_root)

    for i in range(len(files)):
        file_name = files_root + "\\" + files[i]
        chatgpt.send_file_to_chatgpt(file_name)

        chatgpt.send_prompt_to_chatgpt("Find me positive and negative behaviors in these Trello card action history.")
            

    chatgpt.send_prompt_to_chatgpt("Please summarize all the provided Trello actions comprehensively")

    chatgpt.save_conversation("trello_conversation.txt")

    chatgpt.quit()

if __name__ == "__main__":
    prompt()