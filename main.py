from chatgpt_selenium_automation.handler import ChatGPTAutomation

chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'
chrome_driver_path = r"C:\Users\luftaquila\local\workspace\chromedriver.exe"

# Create an instance
chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path)

prompt = "저녁 메뉴 추천"
chatgpt.send_prompt_to_chatgpt(prompt)

print("send done")

# Retrieve the last response from ChatGPT
response = chatgpt.return_chatgpt_conversation()

print(response)

for i in response:
    print(i.text)
    print("------------------")

print(chatgpt.return_last_response())

chatgpt.quit()
