import os
import sys
import time
import subprocess
import webbrowser
from chatgpt_selenium_automation.handler import ChatGPTAutomation

def main():
    if len(sys.argv) < 2:
        print("Please provide the filename as an argument.")
        exit(1)

    filename = sys.argv[1]
    with open(filename, "r") as file:
        source_code = file.read()

    cmd = f"git --no-pager diff {filename}"
    proc = subprocess.run(cmd, shell=True, text=True, capture_output=True, encoding="utf-8")
    diff = proc.stdout

# Create an instance
    chatgpt = ChatGPTAutomation()

    prompt = f""" 아래는 소스 파일의 내용과, 그 중 변경된 부분의 diff입니다. 전체 코드 컨텍스트를 고려하여 변경 사항에 대한 코드 리뷰를 요청합니다. 변경 사항이 일으킬 수 있는 잠재적인 버그와 기존 코드와 충돌을 일으킬 가능성, 혹은 더 나은 구현 방법이 있는지 검토해주세요.  또한, 성능, 가독성, 유지보수성을 개선할 수 있는지에 대한 의견을 부탁드립니다.

    소스 파일 {filename}:

    {source_code}

    변경된 부분의 diff:

    {diff}

    리뷰 요청 사항:
    * 변경 사항이 기존 코드와 잘 통합되는지 검토해주세요.
    * 변경된 코드에 버그 가능성이 있는지 확인해주세요.
    * 성능, 가독성, 유지보수성에 대한 개선점을 제안해주세요.
    * 변경 사항을 더 최적화할 수 있는 방법이 있다면 알려주세요.
    """

    chatgpt.send_prompt_to_chatgpt(prompt)
    print(chatgpt.return_last_response())
    chatgpt.quit()

if __name__ == "__main__":
    main()
