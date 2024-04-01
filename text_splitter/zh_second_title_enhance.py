from langchain.docstore.document import Document
import re

def get_fist_level_title(
        text: str,
) -> bool:
    # 文本长度为0,肯定不是title
    if len(text) == 0:
        print("Not a title. Text is empty or longer than 25.")
        return ""
    
    splitlines = text.splitlines()
    first_line = splitlines[0]
    # 文本中有标点符号，就不是title
    ENDS_IN_PUNCT_PATTERN = r"[^\w\s]\Z"
    ENDS_IN_PUNCT_RE = re.compile(ENDS_IN_PUNCT_PATTERN)
    if ENDS_IN_PUNCT_RE.search(first_line) is not None:
        return ""
    FIRST_TITLE = r'((?<!.)\d+[^\S\n]+[^\s\.]+(?!\.|[a-zA-Z0-9])|((?<!.)第\s*\S+\s*章\s+\S+))'
    TITLE_PUNCT_RE = re.compile(FIRST_TITLE)
    if TITLE_PUNCT_RE.search(first_line) is not None:
        return first_line
    return ""

#return the 2nd level title
def get_second_level_title(
        text: str,
) -> str:
    # 文本长度为0的话，肯定不是title
    lenght = len(text)
    if lenght == 0:
        print("Not a title. Text is empty or longer than 25.")
        return ""
    
    splitlines = text.splitlines()
    first_line = splitlines[0]
    # 文本中有标点符号，就不是title
    # ENDS_IN_PUNCT_PATTERN = r"[^\w\s]\Z"
    # ENDS_IN_PUNCT_RE = re.compile(ENDS_IN_PUNCT_PATTERN)
    # if ENDS_IN_PUNCT_RE.search(first_line) is not None:
    #    return ""

    #3 ****
    #3.1 *****
    #3.1.1 *****
    #另一个分块
    #3.1.2 ***** 所以二级目录可能在第二行 和第一行     
    Second_TITLE = r'((?<!.)[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+[^\S\n]+[^\s\.]+(?!\.|[a-zA-Z0-9])|(?<!.)第\s*\S+\s*条\s+|(?<!.)第\s*\S+\s*条(:|：)|(?<!.)(一、|二、|三、|四、|五、|六、|七、|八、|九、|十、|十一、|十二、|十三、|十四、|十五、|十六、|十七、|十八、|十九、|二十、))'
    TITLE_PUNCT_RE = re.compile(Second_TITLE)
    if TITLE_PUNCT_RE.search(first_line) is not None:
        return first_line
    else:
        if len(splitlines)>1:
            Second_line = splitlines[1]
            if TITLE_PUNCT_RE.search(Second_line) is not None:
                return Second_line
    return ""

#judge if it is 2nd level content
def is_second_level_content(
        text: str,
) -> bool:
    # 文本长度为0的话，肯定不是title
    if len(text) == 0:
        print("Not a title. Text is empty.")
        return False
    
    splitlines = text.splitlines()
    first_line = splitlines[0]
   
    Second_TITLE = r'((?<!.)[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+[^\S\n]+[^\s\.]+(?!\.|[a-zA-Z0-9]))|(?<!.)(表\s*[A-Za-z0-9]+(\s*\.\s*[A-Za-z0-9]+)*\s+)|(?<!.)第\s*\S+\s*条\s+|(?<!.)第\s*\S+\s*条(:|：)|(?<!.)(一、|二、|三、|四、|五、|六、|七、|八、|九、|十、|十一、|十二、|十三、|十四、|十五、|十六、|十七、|十八、|十九、|二十、)'
    TITLE_PUNCT_RE = re.compile(Second_TITLE)
    if TITLE_PUNCT_RE.search(first_line) is not None:
        return True
            
    return False

#judge if it is 3rd level content
def is_third_level_content(
        text: str,
) -> bool:
    # 文本长度为0的话，肯定不是title
    if len(text) == 0:
        print("Not a title. Text is empty.")
        return False
    
    splitlines = text.splitlines()
    first_line = splitlines[0]
   
    Third_TITLE = r'((?<!.)[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+[^\S\n]+[^\s\.]+(?!\.|[a-zA-Z0-9]))|((?<!.)表\s*[A-Za-z0-9]+(\s*\.\s*[A-Za-z0-9]+)*\s+)|((?<!.)（一）|（二）|（三）|（四）|（五）|（六）|（七）|（八）|（九）|（十）|（十一）|（十二）|（十三）|（十四）|（十五）|（十六）|（十七）|（十八）|（十九）|（二十）)|((?<!.)(\(一\)|\(二\)|\(三\)|\(四\)|\(五\)|\(六\)|\(七\)|\(八\)|\(九\)|\(十\)|\(十一\)|\(十二\)|\(十三\)|\(十四\)|\(十五\)|\(十六\)|\(十七\)|\(十八\)|\(十九\)|\(二十\)))'
    TITLE_PUNCT_RE = re.compile(Third_TITLE)
    if TITLE_PUNCT_RE.search(first_line) is not None:
        return True
            
    return False

def get_third_level_title(
        text: str,
) -> str:
    # 文本长度为0的话，肯定不是title
    if len(text) == 0:
        print("Not a title. Text is empty or longer than 25.")
        return ""
    
    splitlines = text.splitlines()
    first_line = splitlines[0]
    # 文本中有标点符号，就不是title
    # ENDS_IN_PUNCT_PATTERN = r"[^\w\s]\Z"
    # ENDS_IN_PUNCT_RE = re.compile(ENDS_IN_PUNCT_PATTERN)
    # if ENDS_IN_PUNCT_RE.search(first_line) is not None:
    #    return ""
    
    #3 ****
    #3.1 *****
    #3.1.1 *****
    #3.1.1.1 *****
    #另一个分块
    #3.1.1.2 ***** 所以三级级目录可能在第三行  和第二行及第一行  
    Third_TITLE = r'((?<!.)[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+[^\S\n]+[^\s\.]+(?!\.|[a-zA-Z0-9]))'
    TITLE_PUNCT_RE = re.compile(Third_TITLE)
    if TITLE_PUNCT_RE.search(first_line) is not None:
        return first_line
    else:
        if len(splitlines)>1:
            Second_line = splitlines[1]
            if TITLE_PUNCT_RE.search(Second_line) is not None:
                return Second_line
            else:
               if len(splitlines)>2:
                    Second_line = splitlines[2]
                    if TITLE_PUNCT_RE.search(Second_line) is not None:
                        return Second_line
        
    return ""

#judge if it is 4th level content
def is_fourth_level_content(
        text: str,
) -> bool:
    # 文本长度为0的话，肯定不是title
    if len(text) == 0:
        print("Not a title. Text is empty.")
        return False
    
    splitlines = text.splitlines()
    first_line = splitlines[0]
   
    Third_TITLE = r'((?<!.)[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+[^\S\n]+[^\s\.]+(?!\.|[a-zA-Z0-9]))'
    TITLE_PUNCT_RE = re.compile(Third_TITLE)
    if TITLE_PUNCT_RE.search(first_line) is not None:
        return True
            
    return False

#给四级被分开的内容 增加三级标题
def zh_third_title_enhance(docs: Document) -> Document:
    title = None
    #print(f"zh_third_title_enhance ....")
    if len(docs) > 0:
        for doc in docs:
            #print(f"zh_third_title_enhance: {doc}")
            third_title = get_third_level_title(doc.page_content)
            if third_title:
                title = third_title
                #print(f"title: {title}")
            elif title:
                #print(f"title is not none")
                temp_fourth_content = is_fourth_level_content(doc.page_content)
                if temp_fourth_content:
                    #print(f"is_fourth_level_content : {temp_fourth_content}")
                    doc.page_content = f"{title} {doc.page_content}"
                else:
                    title = None
            #print(f"final title: {title}")
        return docs
    else:
        print("zh_third_title_enhance 文件不存在")

#给三级被分开的内容 增加二级标题
def zh_second_title_enhance(docs: Document) -> Document:
    title = None
    if len(docs) > 0:
        for doc in docs:
            #print(f"zh_second_title_enhance: {doc}")
            second_title = get_second_level_title(doc.page_content)
            if second_title:
                title = second_title
                #print(f"title: {title}")
            elif title:
                #print(f"title is not none")
                temp_third_content = is_third_level_content(doc.page_content)
                if temp_third_content:
                    #print(f"is_third_level_content : {temp_third_content}")
                    doc.page_content = f"{title} {doc.page_content}"
                else:
                    title = None
            print(f"final title: {title}")
        return docs
    else:
        print("zh_second_title_enhance 文件不存在")

#给二级被分开的内容 增加一级标题
def zh_first_title_enhance(docs: Document) -> Document:
    title = None
    if len(docs) > 0:
        for doc in docs:
            #print(f"zh_first_title_enhance: {doc}")
            first_title = get_fist_level_title(doc.page_content)
            if first_title:
                title = first_title
                #print(f"title: {title}")
            elif title:
                temp_second_content = is_second_level_content(doc.page_content)
                if temp_second_content:
                    #print(f"is_second_level_content : {temp_second_content}")
                    doc.page_content = f"{title} {doc.page_content}"
                else:
                    title = None
        #print(f"final title: {title}")
        return docs
    else:
        print("zh_first_title_enhance 文件不存在")


if __name__ == "__main__":
    str =  """1 总  则\n1.1 本导则是编制和审查城市电力网(以下简称城网)规划的指导性文件，其 适用范围为国家电网公司所属的各网省公司、城市供电公司。\n1.2 城网是城市行政区划内为城市供电的各级电压电网的总称。城网是电力系  统的主要负荷中心，作为城市的重要基础设施之一，与城市的社会经济发展密切  相关。各城市应根据《中华人民共和国城市规划法》和《中华人民共和国电力法》 的相关规定，编制城网规划，并纳入相应的城市总体规划和各地区详细规划中。\n1.3 城网规划是城市总体规划的重要组成部分，应与城市的各项发展规划相互 配合、同步实施，做到与城市规划相协调，落实规划中所确定的线路走廊和地下 通道、变电站和配电室站址等供电设施用地。\n1.4 城网规划的目的是通过科学的规划，建设网络坚强、结构合理、安全可靠、 运行灵活、节能环保、经济高效的城市电网，不断提高城网供电能力和电能质量， 以满足城市经济增长和社会发展的需要。 ' metadata={'source': '/home/bns001/Langchain-Chatchat_0.2.9/knowledge_base/test/content/资产全寿命周期管理体系实施指南.docx'}"""
    title = get_fist_level_title(str)
    print(title)



    #zh_second_title_enhance()