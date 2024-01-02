from langchain.docstore.document import Document
import re

def get_fist_level_title(
        text: str,
) -> bool:
    # 文本长度为0的话或长度大于25，肯定不是title
    if len(text) == 0 and len (text)>= 25:
        print("Not a title. Text is empty or longer than 25.")
        return ""
    
    splitlines = text.splitlines()
    first_line = splitlines[0]
    # 文本中有标点符号，就不是title
    ENDS_IN_PUNCT_PATTERN = r"[^\w\s]\Z"
    ENDS_IN_PUNCT_RE = re.compile(ENDS_IN_PUNCT_PATTERN)
    if ENDS_IN_PUNCT_RE.search(first_line) is not None:
        return ""
  
    FIRST_TITLE = r'((?<!\.|[a-zA-Z0-9]|\S)\d+[^\S\n]+[^\s\.]+\S+)'
    TITLE_PUNCT_RE = re.compile(FIRST_TITLE)
    if TITLE_PUNCT_RE.search(first_line) is not None:
        return first_line
    return ""

#return the 2nd level title
def get_second_level_title(
        text: str,
) -> str:
    # 文本长度为0的话，肯定不是title
    if len(text) == 0 and len (text)>= 25:
        print("Not a title. Text is empty or longer than 25.")
        return ""
    
    splitlines = text.splitlines()
    first_line = splitlines[0]
    # 文本中有标点符号，就不是title
    ENDS_IN_PUNCT_PATTERN = r"[^\w\s]\Z"
    ENDS_IN_PUNCT_RE = re.compile(ENDS_IN_PUNCT_PATTERN)
    if ENDS_IN_PUNCT_RE.search(first_line) is not None:
       return ""
           
    Second_TITLE = r'((?<!\.|[a-zA-Z0-9]|\S)[0-9]+\s*\.\s*[0-9]+[^\S\n]+[^\s\.]+(?!\.|[a-zA-Z0-9]))'
    TITLE_PUNCT_RE = re.compile(Second_TITLE)
    if TITLE_PUNCT_RE.search(first_line) is not None:
        return first_line
    else:
        if len(splitlines)>1:
            Second_line = splitlines[1]
            if TITLE_PUNCT_RE.search(Second_line) is not None:
                return Second_line
    return ""

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
   
    Third_TITLE = r'((?<!\.|[a-zA-Z0-9]|\S)\s*[0-9]+\s*\.\s*[0-9]+\s*\.\s*[0-9]+[^\S\n]+[^\s\.]+(?!\.|[a-zA-Z0-9]))'
    TITLE_PUNCT_RE = re.compile(Third_TITLE)
    if TITLE_PUNCT_RE.search(first_line) is not None:
        return True
            
    return False
    
#给三级被分开的内容 增加二级标题
def zh_second_title_enhance(docs: Document) -> Document:
    title = None
    if len(docs) > 0:
        for doc in docs:
            second_title = get_second_level_title(doc.page_content)
            if second_title:
                title = second_title
            elif title:
                temp_third_content = is_third_level_content(doc.page_content)
                if temp_third_content:
                    doc.page_content = f"{title} {doc.page_content}"
                else:
                    title = None
        return docs
    else:
        print("文件不存在")


if __name__ == "__main__":
    str =  """6   进出等电位
6.1   直线塔进出等电位
6.1.1   对于直线塔， 作业人员不得从横担或绝缘子串垂直进出等电位， 可采用吊篮（吊椅、吊梯） 法、 绝缘软梯法等方式进出等电位。
6.1.2   等电位作业人员进出等电位时与接地体及带电体的各电气间隙距离（包括安全距离、组合间隙） 均应满足表 1 、3 要求。
6.1.3    吊篮（吊椅、吊梯）必须用吊拉绳索稳固悬吊； 吊篮（吊椅、吊梯）的移动速度必须用绝缘滑 车组严格控制， 做到均匀、慢速； 固定吊拉绳索的长度， 应准确计算或实际丈量， 保证等电位作业人员 即将进入等电位时人体最高部位不超过导线侧均压环。
6.2   耐张塔进出等电位
6.2.1   在耐张塔进出等电位时，作业人员可采用沿耐张绝缘子串方法或其它方法进出等电位。
6.2.2   等电位作业人员沿绝缘子串移动时， 手与脚的位置必须保持对应一致， 且人体和工具短接的绝 缘子片数应符合 5.2.2 的要求。
6.2.3   等电位作业人员所系安全带，应绑在手扶的绝缘子串上，并与等电位作业人员同步移动。
6.2.4   等电位作业人员在进出等电位时，应在移动至距离带电体 3  片绝缘子时进行电位转移，方可进 行后续操作。
6.2.5   带电作业人员与接地体及带电体的各电气间隙距离（包括安全距离、组合间隙）和经人体或工 具短接后的良好绝缘子片数均应满足表 4 要求，否则不能沿耐张绝缘子串进出等电位。
7   作业中的注意事项
7.1   等电位作业人员在带电作业过程中时，应避免身体动作幅度过大。
7.2   等电位作业人员与地电位作业人员之间传递物品应采用绝缘工具，绝缘工具的有效长度，应满足 表 2 的规定。
7.3   屏蔽服装应无破损和孔洞， 各部分应连接良好、可靠。发现破损和毛刺时应送有资质的试验单位 进行屏蔽服装电阻和屏蔽效率测量，测量结果满足本标准 5.3.1 条的要求后，方可使用。
7.4   绝缘工具在使用前， 应使用 2500V 及以上兆欧表进行分段检测（电极宽 2cm，极间宽 2cm），阻值 不低于 700MΩ。"""
    title = is_third_level_content(str)
    print(title)
    title = get_second_level_title(str)
    print(title)
    #zh_second_title_enhance()