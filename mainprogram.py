# pip install openpyxl beautifulsoup4 requests pandas
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

def scrape_property(chemical_name, property): # 修改自chatgpt，自己擴充成可以查詢各種property
    url = f"https://en.wikipedia.org/wiki/{chemical_name}"  # 資料源：維基百科
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # 嘗試從表格中提取「化學特性」字樣
            table = soup.find("table", {"class": "infobox"})
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    if property in row.text.lower():
                        lines = row.text.strip().split("\n")
                        return lines[-1]  # 返回最後一行
            
            # 如果表格中未找到，從段落中查找
            paragraphs = soup.find_all("p")
            for para in paragraphs:
                if property in para.text.lower():
                    lines = para.text.strip().split("\n")
                    return lines[-1]
            
            return f"No {property} information found."
        else:
            return f"Error: Failed to fetch page. Status Code: {response.status_code}"
    except Exception as e:
        return f"An exception occurred: {str(e)}"


# 移除輸出內容中的[?] # chatgpt寫的
def remove_brackets(text):
    if isinstance(text, str):  # 確保處理的是字串
        return re.sub(r"\[.*?\]", "", text).strip()
    return text  # 如果不是字串，直接返回原內容


# 使用者介面 # 都是自己寫的
# 改成使用者在vscode介面輸入藥品的化學式，再存成性質的第一欄
print("請輸入藥品的化學式(chemical formula)，若該藥品是水合物請去掉水合的部分(如SnCl2•2H2O請輸入SnCl2)")
print("每行輸入一個化學式，輸入end結束：")
chemical_name=[]
while True:
    line = input()
    if line.lower() == "end":
        break
    chemical_name.append(line)
if not chemical_name:
    print("未輸入任何化學式，程式結束")
    exit()

# 將輸入的化學式存入dataframe 以存入檔案 # chatgpt寫的
data = pd.DataFrame({"chemical formula": chemical_name})

# 欲查詢的性質 # 都是自己寫的
print("藥品性質查詢組合")
print("1(solubility):\tIUPAC name + molar mass + solubility in water + appearance")
print("2(m.p./b.p.):\tIUPAC name + molar mass + m.p. + b.p. + appearance")
print("3(1+2):\tIUPAC name + molar mass + solubility in water + m.p. + b.p. + appearance")
print("4(customized)")

setlist={1:["iupac name","molar mass", "solubility in water", "appearance"],
         2:["iupac name","molar mass", "melting point", "boiling point", "appearance"],
         3:["iupac name","molar mass", "solubility in water", "melting point", "boiling point", "appearance"]}

try:
    setnumber = int(input("請輸入數字(1234)以選擇你想查詢的藥品性質："))
    #property_searched=setlist[setnumber]

    if setnumber in [1, 2, 3]:
        property_searched = setlist[setnumber]

    elif setnumber == 4:
        property_searched = []
        print("請以小寫輸入想查詢的化合物性質，每行一個性質，輸入end結束：")
        while True:
            line = input()
            if line.lower() == "end":
                break
            property_searched.append(line)

    else:
        print("輸入錯誤，請輸入1, 2, 3 或 4！")

except KeyError or ValueError:
    print("輸入錯誤，請輸入1, 2, 3 或 4！")


# 用forloop存入檔案 # 都是自己寫的
for i in property_searched:
    new_list = []
    for j in chemical_name:
        new_list.append(scrape_property(j, i))
    
    if len(new_list) != len(data):  # 檢查新列表長度是否與現有資料行數一致
        raise ValueError("新列表的長度與原始資料行數不一致！")
    else:
        data[i] = new_list  # 將新列表加入資料框


# 移除[]並輸出為 Excel 文件 # 修改自chatgpt
data_cleaned = data.applymap(remove_brackets)
output_file = 'updated.xlsx'
data_cleaned.to_excel(output_file, index=False, engine='openpyxl')  # 不輸出索引列
print(f"資料已處理並儲存為 {output_file}")
