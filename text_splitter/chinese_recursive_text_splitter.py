import re
from typing import List, Optional, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
import PyPDF2

logger = logging.getLogger(__name__)

First_SEPARATOE = "\n\n\n\n\n\n\n\n\n\n"
Second_SEPARATOE = "\n\n\n\n\n\n\n\n"
Third_SEPARATOE = "\n\n\n\n\n\n"
def _split_text_with_regex_from_end(
        text: str, separator: str, keep_separator: bool
) -> List[str]:
    # Now that we have the separator, split the text
    if separator:
        if keep_separator:
            # The parentheses in the pattern keep the delimiters in the result.
            _splits = re.split(f"({separator})", text)
            splits = ["".join(i) for i in zip(_splits[0::2], _splits[1::2])]
            if len(_splits) % 2 == 1:
                splits += _splits[-1:]
            # splits = [_splits[0]] + splits
        else:
            splits = re.split(separator, text)
    else:
        splits = list(text)
    return [s for s in splits if s != ""]


class ChineseRecursiveTextSplitter(RecursiveCharacterTextSplitter):
    def __init__(
            self,
            separators: Optional[List[str]] = None,
            keep_separator: bool = True,
            is_separator_regex: bool = True,
            **kwargs: Any,
    ) -> None:
        """Create a new TextSplitter."""
        super().__init__(keep_separator=keep_separator, **kwargs)
        self._separators = separators or [
            First_SEPARATOE,
            Second_SEPARATOE,
            Third_SEPARATOE
            #"\n\n",
            #"\n",
            # "。|！|？",
            # "\.\s|\!\s|\?\s",
            # "；|;\s",
            # "，|,\s"
        ]
        self._is_separator_regex = is_separator_regex
        self.is_recursive = False

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Split incoming text and return chunks."""
        print(f"***********************************ChineseRecursiveTextSplitter***********************************")
        final_chunks = []
        # Get appropriate separator to use
        separator = separators[-1]
        new_separators = []
        if self.is_recursive == False:
            text = re.sub(r'(\n+前\s+言\n+)',  r"\n\n\n\n\n\n\n\n\n\n\1", text) #通过前言分块
            text = re.sub(r'(\n+\d+[^\S\n]+[^\s\.]+)', r"\n\n\n\n\n\n\n\n\n\n\1", text) #通过1 这样的
            text = re.sub(r'(手工分段\*\*\s*)', r"\n\n\n\n\n\n\n\n\n\n\1", text)  # 通过“手工分段**”
            text = re.sub(r'(\n+第\s*\S+\s*章\s+)', r"\n\n\n\n\n\n\n\n\n\n\1", text)  # 通过第 章

            text = re.sub(r'(\n+(?<!\.|[a-zA-Z0-9])[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s+(?!\.|[a-zA-Z0-9]))', r"\n\n\n\n\n\n\n\n\1", text)  # 通过\n1.2 这样的章和节来分块
            text = re.sub(r'(\n+表\s*[A-Za-z0-9]+(\.[A-Za-z0-9]+)+\s+)', r"\n\n\n\n\n\n\n\n\1", text)  # 通过表  A.4.a 
            text = re.sub(r'(\n+第\s*\S+\s*条\s+)', r"\n\n\n\n\n\n\n\n\1", text)  # 通过第 条
            text = re.sub(r'(\n+(一、|二、|三、|四、|五、|六、|七、|八、|九、|十、|十一、|十二、|十三、|十四、|十五、|十六、|十七、|十八、|十九、|二十、))', r"\n\n\n\n\n\n\n\n\1", text)  # 通过第 条
            
            text = re.sub(r'(\n+(?<!\.|[a-zA-Z0-9])[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s+(?!\.|[a-zA-Z0-9]))', r"\n\n\n\n\n\n\1", text)  # 再通过 1.2.3 
            text = text.rstrip()  # 段尾如果有多余的\n就去掉它
            self.is_recursive = True
        for i, _s in enumerate(separators):
            _separator = _s if self._is_separator_regex else re.escape(_s)
            if _s == "":
                separator = _s
                break
            if re.search(_separator, text):
                separator = _s
                new_separators = separators[i + 1:]
                break

        _separator = separator if self._is_separator_regex else re.escape(separator)
        splits = _split_text_with_regex_from_end(text, _separator, self._keep_separator)

        # Now go merging things, recursively splitting longer texts.
        _good_splits = []
        _separator = "" if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    #s = re.sub(r'(\n+[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s+)', r"\n\n\n\n\n\n\n\n\n\n\1", s)  # 再通过 1.2.3 来分块
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)
        
        final_chunks = [re.sub(r"\n{2,}", "\n", chunk.strip()) for chunk in final_chunks if chunk.strip()!=""]
        #将两行以内并且字数小于25，和下面的分块合并
        return_chunks = []
        temp_sencond = ""
        for chunk in final_chunks:
            if temp_sencond =="":
                if len(chunk.splitlines()) <= 2 and len(chunk) <= 25:
                    temp_sencond = chunk
                else:
                    return_chunks.append(chunk)
            else:
                return_chunks.append(temp_sencond + chunk)
                temp_sencond = "" 

        if temp_sencond !="":
            return_chunks.append(temp_sencond)

        return return_chunks
        #return [re.sub(r"\n{2,}", "\n", chunk.strip()) for chunk in final_chunks if chunk.strip()!=""]


if __name__ == "__main__":
 
    # 使用open的‘rb’方法打开pdf文件，使用二进制模式
    #mypdf = open('电力电缆故障测寻车技术规范.pdf',mode='rb')
    mypdf = open('/Users/wangvivi/Desktop/Opensource/Langchain-Chatchat/text_splitter/电力电缆故障测寻车技术规范.pdf',mode='rb')
    # 调用PdfFileReader函数
    pdf_document = PyPDF2.PdfReader(mypdf)
    
    # 使用PdfFileReader对象的变量，获取各个信息，如numPages属性获取PDF文档的页数
    len1 = len(pdf_document.pages)
    # print(f"文档页数:{len1}")
    
    i = 0
    text = ""
    # 调用PdfFileReader对象的getPage()方法，传入页码，取得Page对象：输出PDF文档的第一页内容
    while i < len1:   
        first_page = pdf_document.pages[i]
        # 调用Page对象的extractText()方法，返回该页文本的字符串
        text1 = first_page.extract_text()
        text += text1
        i = i+1

    #print(text)

    text_splitter = ChineseRecursiveTextSplitter(
        keep_separator=True,
        is_separator_regex=True,
        chunk_size=400,
        chunk_overlap=0
    )
    #ls = [
    #    """中国对外贸易形势报告（75页）。前 10 个月，一般贸易进出口 19.5 万亿元，增长 25.1%， 比整体进出口增速高出 2.9 个百分点，占进出口总额的 61.7%，较去年同期提升 1.6 个百分点。其中，一般贸易出口 10.6 万亿元，增长 25.3%，占出口总额的 60.9%，提升 1.5 个百分点；进口8.9万亿元，增长24.9%，占进口总额的62.7%， \n1.1 提升 1.8 个百分点。加工贸易进出口 6.8 万亿元，增长 11.8%， 占进出口总额的 21.5%，减少 2.0 个百分点。其中，出口增 长 10.4%，占出口总额的 24.3%，减少 2.6 个百分点；进口增 长 14.2%，占进口总额的 18.0%，减少 1.2 个百分点。此外， 以保税物流方式进出口 3.96 万亿元，增长 27.9%。其中，出 口 1.47 万亿元，增长 38.9%；进口 2.49 万亿元，增长 22.2%。前三季度，中国服务贸易继续保持快速增长态势。服务 进出口总额 37834.3 亿元，增长 11.6%；其中服务出口 17820.9 亿元，增长 27.3%；进口 20013.4 亿元，增长 0.5%，进口增 速实现了疫情以来的首次转正。服务出口增幅大于进口 26.8 个百分点，带动服务贸易逆差下降 62.9%至 2192.5 亿元。服 务贸易结构持续优化，知识密集型服务进出口 16917.7 亿元， 增长 13.3%，占服务进出口总额的比重达到 44.7%，提升 0.7 个百分点。 二、中国对外贸易发展环境分析和展望 全球疫情起伏反复，经济复苏分化加剧，大宗商品价格 上涨、能源紧缺、运力紧张及发达经济体政策调整外溢等风 险交织叠加。\n1.2同时也要看到，我国经济长期向好的趋势没有 改变，外贸企业韧性和活力不断增强，新业态新模式加快发 展，创新转型步伐提速。产业链供应链面临挑战。美欧等加快出台制造业回迁计 划，加速产业链供应链本土布局，跨国公司调整产业链供应 链，全球双链面临新一轮重构，区域化、近岸化、本土化、 短链化趋势凸显。疫苗供应不足，制造业“缺芯”、物流受限、 运价高企，全球产业链供应链面临压力。 全球通胀持续高位运行。能源价格上涨加大主要经济体 的通胀压力，增加全球经济复苏的不确定性。世界银行今年 10 月发布《大宗商品市场展望》指出，能源价格在 2021 年 大涨逾 80%，并且仍将在 2022 年小幅上涨。IMF 指出，全 球通胀上行风险加剧，通胀前景存在巨大不确定性。""",
    #     #"""附录A（规范性附录） 直流断路器验收标准..................................................................................................5\n附录B（资料性附录） 直流断路器验收工作记录........................................................................................29\n编制说明..............................................................................................................................................................38\nQ/GDW 12221—\n2022\nI\n前\n言\n为了规范直流断路器的验收标准，保证直流断路器的产品质量和可靠性，制定本标准。\n本标准由国家电网有限公司设备管理部提出并解释。\n本标准由国家电网有限公司科技部归口。\n本标准起草单位： 国网冀北电力有限公司。\n本标准主要起草人：李振动、武宇平、樊小伟、吕志瑞、黄晓乐、杨大伟、贺俊杰、王珣、杨敏祥、\n金海望、李涛、张晓飞、赵凯曼、覃晗、毛婷、黄彬、张国亮、黄小龙、闫玉鑫、牛铮、张雷、林林、\n于文博、李金卜、田凯哲、高宏达、柳杨、董海飞、赵媛、秦逸帆、张静岚、季一润。\n本标准首次发布。\n本标准在执行过程中的意见或建议反馈至国家电网有限公司科技部。\nQ/GDW 12221—\n2022\n5\n柔性直流系统直流断路器验收规范\n1\n范围\n本标准规定了直流断路器设备可研初设审查、厂内验收、到货验收、隐蔽工程验收、中间验收、竣工（预）验收、启动验收等七个阶段验\n收工作的内容和要求。\n本标准适用于直流6kV及以上电力系统用高压直流断路器（以下简称直流断路器）的验收工作。\n2\n规范性引用文件\n下列文件对于本文件的应用是必不可少的。凡是注日期的引用文件，仅注日期的版本适用于本文件。凡是不注日期的引用文件，其最新版本\n（包括所有的修改单）适用于本文件。\nGB/T 12022\n工业六氟化硫\nGB/T 50775\n±800kV及以下换流站换流阀施工及验收规范\nGB/T 51381\n柔性直流输电换流站设计标准\n3\n术语和定义\n下列术语和定义适用于本文件。\n3.1可研初设审查 examining feasibility study and preliminary design review\n可研初设审查是指在可研初设阶段从设备安全运行、运检便利性等方面对工程可研报告、初设文件、技术规范书等开展的审查。\n3.2\nQ/GDW 12221—\n2022\n表 A.1\n（续）\n6\n厂内验收 check and accept in the supplier′s factory/ex-factory acceptance\n厂内验收是指对设备厂内制造的关键点进行见证和出厂验收。\n3.3\n到货验收 inspection of merchandise received /site inspection\n到货验收是指设备运送到现场后进行的验收。\n3.4\n隐蔽工程验收 inspection and approval of concealed work/hidden work acceptance\n隐蔽工程验收是指对设备施工过程中本工序会被下一工序所覆盖，在随后的验收中不易查看其质量时开展验收。\n3.5\n中间验收 concealed work and intermediate acceptance\n中间验收是指在设备安装调试过程中对关键工艺、关键工序、关键部位和重点试验开展的验收。\n3.6竣工（预）验收 pre-acceptance\n竣工（预）验收是指施工单位完成三级自验收及监理初检后，对设备进行的全面验收。\n3.7\n启动验收 start-up acceptance\n启动验收是指在完成竣工（预）验收并确认缺陷全部清除后，设备正式投入运行前的验收。\n4\n验收要求及流程\n4.1\n验收条件\n验收条件的要求是：制造厂家提供的设备应符合技术条件（规范、标准、标书、应标文件等对应条款）和反事故技术措施要求，通过型式\n试验。\n4.2\n验收方法\nQ/GDW 12221—\n2022\n7\n4.2.1\n资料审查\n直流断路器资料审查是指检查包括满足直流断路器投产要求的所有资料，设备安装、试验数据应满足相关规程规范要求，安装调试前后数\n值应有比对，保持一致性，应无明显变化。\n4.2.2\n旁站见证直流断路器旁站见证是指对关键工艺、关键工序、关键部位和重点试验的见证。\n4.2.3\n现场检查\n直流断路器现场检查应包括现场设备外观和功能的检查。\n4.3\n可研初设审查\n直流断路器可研初审主要审查工程可研报告、初设文件、设备技术规范书等内容，包括：\na)\n直流断路器可研初设审查验收需由专业技术人员提前对成套设计、可研报告、初设资料等文件进行审查，并提出相关意见；\nb)\n可研初设审查阶段主要针对直流断路器选型涉及的技术参数、结构形式、安装条件进行审查、验收；\nc)\n审核直流断路器选型是否满足相关标准、反措等各项要求；\nd)\n审查时应按照附录 A中表A.1 要求执行。\n4.4\n厂内验收\n4.4.1\n关键点见证\n直流断路器关键点见证主要对设备制造过程中的重要工序进行见证，包括：\na)应对直流断路器重要组部件出厂质量证书、合格证、试验报告进行检查；\nb)\n组装期间进行关键点工序见证；\n关键点见证采用查阅制造厂家记录和现场查看方式；\nc)\n关键点见证时应按照附录 A中表A.2 要求执行。\n4.4.2\n出厂验收\n直流断路器出厂验收是对直流断路器已完成全部组部件生产和装配工作，具备出厂试验条件，出厂验收主要对设备材料、外观、出厂试验\n等内容进行验收，包括：\na)\n核查直流断路器出厂试验记录或报告；\nQ/GDW 12221—\n2022\n表 A.1\n（续）\n8\nb)\n直流断路器绝缘型式试验、运行型式试验等，试验结果应满足规范要求；\nc)\n出厂验收时应按照附录 A中表A.3 要求执行。\n4.5\n到货验收\n直流断路器到货验收主要对包装、技术资料、外观和运输过程记录等内容进行验收，包括：直流断路器开箱前，直流断路器设备区温湿度等条件应满足规范要求；\nb)\n核对到货清单、设备、备品备件、工器具、资料与合同一致；\nc)\n组部件包装防水、防潮措施良好；\nd)\n检查设备包装及外观无损伤，无异常；\ne)\n到货验收按附录 A中表A.4 要求执行。\n4.6\n隐蔽工程验收\n直流断路器隐蔽工程主要针对直流断路器光纤敷设、接线，供能变压器的引出线等内容进行验收，包括：\na)\n检查光纤槽盒内光纤敷设情况；\nb)\n检查光纤回路防火隔离情况；\nc)\n检查直流断路器本体接地情况；\nd)\n审查时按附录A中表A.5 要求执行。\n4.7\n中间验收\n直流断路器中间验收主要针对直流断路器快速机械开关、供能变压器、阀组件和MOV等内容进行验收，包括：\na)检查快速机械开关外观和二次接线端子情况；\nb)\n检查供能变压器气体性能和充气情况（如试用）；\nc)\n检查阀组件安装情况；\nd)\n检查MOV 压力释放通道、本体安装和底座等情况；\ne)\n审查时按附录A中表A.6 要求执行。\n4.8\n竣工（预）验收\n直流断路器竣工验证是指直流断路器及附件已安装调试完毕，缺陷已消除，竣工（预）验收主要是对设备外观、交接试验和技术资料等内\n容进行验收，包括：\na)\n对直流断路器外观、组部件、标识进行检查。\nQ/GDW 12221—\n2022\n9\nb)\n核查直流断路器交接试验报告和相关文件资料。\nc)\n对直流断路器开展验收工作审查时应按照附录 A中表A.7-A.9 要求执行。"""
    #     ]
    # text1 = """中国对外贸易形势报告（75页）。前 10 个月，一般贸易进出口 19.5 万亿元，增长 25.1%， 比整体进出口增速高出 2.9 个百分点，占进出口总额的 61.7%，较去年同期提升 1.6 个百分点。其中，一般贸易出口 10.6 万亿元，增长 25.3%，占出口总额的 60.9%，提升 1.5 个百分点；进口8.9万亿元，增长24.9%，占进口总额的62.7%， \n1.1 提升 1.8 个百分点。加工贸易进出口 6.8 万亿元，增长 11.8%， 占进出口总额的 21.5%，减少 2.0 个百分点。其中，出口增 长 10.4%，占出口总额的 24.3%，减少 2.6 个百分点；进口增 长 14.2%，占进口总额的 18.0%，减少 1.2 个百分点。此外， 以保税物流方式进出口 3.96 万亿元，增长 27.9%。其中，出 口 1.47 万亿元，增长 38.9%；进口 2.49 万亿元，增长 22.2%。前三季度，中国服务贸易继续保持快速增长态势。服务 进出口总额 37834.3 亿元，增长 11.6%；其中服务出口 17820.9 亿元，增长 27.3%；进口 20013.4 亿元，增长 0.5%，进口增 速实现了疫情以来的首次转正。服务出口增幅大于进口 26.8 个百分点，带动服务贸易逆差下降 62.9%至 2192.5 亿元。服 务贸易结构持续优化，知识密集型服务进出口 16917.7 亿元， 增长 13.3%，占服务进出口总额的比重达到 44.7%，提升 0.7 个百分点。 二、中国对外贸易发展环境分析和展望 全球疫情起伏反复，经济复苏分化加剧，大宗商品价格 上涨、能源紧缺、运力紧张及发达经济体政策调整外溢等风 险交织叠加。\n1.2同时也要看到，我国经济长期向好的趋势没有 改变，外贸企业韧性和活力不断增强，新业态新模式加快发 展，创新转型步伐提速。产业链供应链面临挑战。美欧等加快出台制造业回迁计 划，加速产业链供应链本土布局，跨国公司调整产业链供应 链，全球双链面临新一轮重构，区域化、近岸化、本土化、 短链化趋势凸显。疫苗供应不足，制造业“缺芯”、物流受限、 运价高企，全球产业链供应链面临压力。 全球通胀持续高位运行。能源价格上涨加大主要经济体 的通胀压力，增加全球经济复苏的不确定性。世界银行今年 10 月发布《大宗商品市场展望》指出，能源价格在 2021 年 大涨逾 80%，并且仍将在 2022 年小幅上涨。IMF 指出，全 球通胀上行风险加剧，通胀前景存在巨大不确定性。"""
    ls=[]
    ls.append(text)

    for inum, temptext in enumerate(ls):
        print(f"**************分段：{inum}")
        chunks = text_splitter.split_text(temptext)
        i = 0
        for chunk in chunks:
            print(f"**************:chunk {i}:{chunk}")
            i = i+1


    # from langchain.retrievers import BM25Retriever, EnsembleRetriever
    # from langchain.vectorstores import FAISS

    # from langchain.embeddings import HuggingFaceEmbeddings

    # model_name = "/Users/wangvivi/Downloads/bge-large-zh-v1.5"
    # model_kwargs = {'device': 'cpu'}
    # encode_kwargs = {'normalize_embeddings': False}
    # hf = HuggingFaceEmbeddings(
    #     model_name=model_name,
    #     model_kwargs=model_kwargs,
    #     encode_kwargs=encode_kwargs
    #     )
    
    # bm25_retriever = BM25Retriever.from_texts(chunks)
    # bm25_retriever.k = 2

    # faiss_vectorstore = FAISS.from_texts(chunks, hf)
    # faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": 2})

    # docs = faiss_retriever.get_relevant_documents("电力电缆故障测寻车按配置设备可以分为几类？")
    # print (f"docs:{docs}")