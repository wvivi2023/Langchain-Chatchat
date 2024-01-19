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
  
    FIRST_TITLE = r'((?<!.)\d+[^\S\n]+[^\s\.]+\S+)'
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
           
    Second_TITLE = r'((?<!.)[0-9]+\s*\.\s*[0-9]+[^\S\n]+[^\s\.]+(?!\.|[a-zA-Z0-9]))'
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
   
    Second_TITLE = r'((?<!.)[0-9]+\s*\.\s*[0-9]+[^\S\n]+[^\s\.]+(?!\.|[a-zA-Z0-9]))|(?<!.)(表\s*[A-Za-z0-9]+(\s*\.\s*[A-Za-z0-9]+)*\s+)'
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
   
    Third_TITLE = r'((?<!.)[0-9]+\s*\.\s*[0-9]+\s*\.\s*[0-9]+[^\S\n]+[^\s\.]+(?!\.|[a-zA-Z0-9]))|((?<!.)表\s*[A-Za-z0-9]+(\s*\.\s*[A-Za-z0-9]+)*\s+)'
    TITLE_PUNCT_RE = re.compile(Third_TITLE)
    if TITLE_PUNCT_RE.search(first_line) is not None:
        return True
            
    return False
    
#给三级被分开的内容 增加二级标题
def zh_second_title_enhance(docs: Document) -> Document:
    title = None
    print(f"zh_second_title_enhance ....")
    if len(docs) > 0:
        for doc in docs:
            print(f"zh_second_title_enhance: {doc}")
            second_title = get_second_level_title(doc.page_content)
            if second_title:
                title = second_title
                print(f"title: {title}")
            elif title:
                print(f"title is not none")
                temp_third_content = is_third_level_content(doc.page_content)
                if temp_third_content:
                    print(f"is_third_level_content : {temp_third_content}")
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
            first_title = get_fist_level_title(doc.page_content)
            if first_title:
                title = first_title
            elif title:
                temp_second_content = is_second_level_content(doc.page_content)
                if temp_second_content:
                    doc.page_content = f"{title} {doc.page_content}"
                else:
                    title = None
        return docs
    else:
        print("zh_first_title_enhance 文件不存在")


if __name__ == "__main__":
    str =  """8.1.3  采购过程\n为统筹资产管理相关的采购需求，统一设备采购标准，保障采购的产品和服务的质量，应策划、实 施和控制电网实物资产相关的采购过程。采购过程包括招标采购、仓储配送及到货验收等。对产品和服 务的采购以及供应商的选择等，应按照 8.3 外包的要求进行管理。策划、实施和控制时应满足：\na)  应统计和分析建设、运维阶段的设备质量信息，如设备缺陷信息、故障信息及使用寿命等，用 于指导设备采购标准的制定。应系统性评估企业的采购需求以及内外部机会，确定采购策略， 从而降低企业的整体成本，发挥企业的内外部优势，如实施战略采购、超市化采购等；\nb)  库存物资应进行统一管理，建立包含不同业务形成的实物库存的台账，如利用 ERP 系统建立库 存物资“一本账 ”，准确反映实体仓库内库存实物信息。应根据合同交付和物资使用的要求， 统一进行物资配送的调度和协调，以满足安全、准时、快捷、服务优质等要求；\nc)  应综合考虑设备的价值、重要性、复杂性等因素，确定监造设备范围（如变压器、换流变、串\nQ/GDW 12219—2022\n联补偿装置、换流阀等）和监造方式（如驻厂监造、关键点见证等）；物资抽检应覆盖所有供 应商及所有物资类别；现场验收应按照策划的方式进行。应保留监造、抽检和现场验收相关的 文件和过程控制记录。' metadata={'source': '/home/bns001/Langchain-Chatchat_0.2.9/knowledge_base/test/content/资产全寿命周期管理体系实施指南.docx'}
title: 为统筹资产管理相关的采购需求，统一设备采购标准，保障采购的产品和服务的质量，应策划、实 施和控制电网实物资产相关的采购过程。采购过程包括招标采购、仓储配送及到货验收等。对产品和服 务的采购以及供应商的选择等，应按照 8.3 外包的要求进行管理。策划、实施和控制时应满足：
"""
    title = is_third_level_content(str)
    print(title)
    #title = get_second_level_title(str)
    #print(title)
    #zh_second_title_enhance()