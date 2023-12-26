import re
from typing import List, Optional, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

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
            # "\n\n",
            # "\n",
            # "。|！|？",
            # "\.\s|\!\s|\?\s",
            # "；|;\s",
            # "，|,\s"
        ]
        self._is_separator_regex = is_separator_regex
        self.is_recursive = False

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Split incoming text and return chunks."""
        final_chunks = []
        # Get appropriate separator to use
        separator = separators[-1]
        new_separators = []
        if self.is_recursive == False:
            text = re.sub(r'(\n+前\s+言\n+)',  r"\n\n\n\n\n\n\n\n\n\n\1", text) #通过前言分块
            text = re.sub(r'(\n+\d+[^\S\n]+[^\s\.]+)', r"\n\n\n\n\n\n\n\n\n\n\1", text) #通过1 这样的
            text = re.sub(r'(手工分段\*\*\s*)', r"\n\n\n\n\n\n\n\n\n\n\1", text)  # 通过“手工分段**”
            text = re.sub(r'(\n+第\s*\S+\s*章\s+)', r"\n\n\n\n\n\n\n\n\n\n\1", text)  # 通过第 章

            text = re.sub(r'(\n+[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s+(?!\.|[a-zA-Z0-9]))', r"\n\n\n\n\n\n\n\n\1", text)  # 通过\n1.2 这样的章和节来分块
            text = re.sub(r'(\n+表\s*[A-Za-z0-9]+(\.[A-Za-z0-9]+)+\s+)', r"\n\n\n\n\n\n\n\n\1", text)  # 通过表  A.4.a 
            text = re.sub(r'(\n+第\s*\S+\s*条\s+)', r"\n\n\n\n\n\n\n\n\1", text)  # 通过第 条
            text = re.sub(r'(\n+(一、|二、|三、|四、|五、|六、|七、|八、|九、|十、|十一、|十二、|十三、|十四、|十五、|十六、|十七、|十八、|十九、|二十、))', r"\n\n\n\n\n\n\n\n\1", text)  # 通过第 条
            
            text = re.sub(r'(\n+[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s+)', r"\n\n\n\n\n\n\1", text)  # 再通过 1.2.3 
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
            #print(f"***s:{s},len:{self._length_function(s)}")
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    #print(f"***_merge_splits(s)")
                    merged_text = self._merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                    #print(f"***final_chunks.append(s)")
                else:
                    #s = re.sub(r'(\n+[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s+)', r"\n\n\n\n\n\n\n\n\n\n\1", s)  # 再通过 1.2.3 
                    #print(f"***下一级_split_text(s)")
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)

        final_chunks = [re.sub(r"\n{2,}", "\n", chunk.strip()) for chunk in final_chunks if chunk.strip()!=""]
        #将两行并且字数小于25，和下面的分块合并
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
    text_splitter = ChineseRecursiveTextSplitter(
        keep_separator=True,
        is_separator_regex=True,
        chunk_size=300,
        chunk_overlap=30
    )
    ls = [
        """6   进出等电位
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
7.4   绝缘工具在使用前， 应使用 2500V 及以上兆欧表进行分段检测（电极宽 2cm，极间宽 2cm），阻值 不低于 700MΩ。""",
        ]
    # text = """"""
    for inum, text in enumerate(ls):
        print(inum)
        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            print(f"分段：{chunk}")
