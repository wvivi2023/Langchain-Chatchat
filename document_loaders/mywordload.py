from typing import List
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from docx import Document as docxDocument
from docx.document import Document as _Document
from docx.table import _Cell
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

class RapidWordLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        def iter_block_items(parent):
            """
            Yield each paragraph and table child within *parent*, in document order.
            Each returned value is an instance of either Table or Paragraph.
            """
            #Document
            if isinstance(parent, _Document):
                parent_elm = parent._element.body
            elif isinstance(parent, _Cell):
                parent_elm = parent._element
            else:
                raise ValueError("something's not right")

            for child in parent_elm.iterchildren():
                if isinstance(child, CT_P):
                    yield Paragraph(child, parent)
                elif isinstance(child, CT_Tbl):
                    yield Table(child, parent)

        def read_table(table):
            # 获取表格列标题
            headers = [cell.text.strip() for cell in table.rows[0].cells]
            # 存储表格数据的字符串
            table_string = ""

            # 遍历表格行
            for row_index, row in enumerate(table.rows[1:], 2):  # 从第二行开始遍历，因为第一行是标题
                row_data = []

                # 遍历行中的单元格
                for cell_index, cell in enumerate(row.cells, 1):
                    cell_text = cell.text.strip()
                    row_data.append(f'"{headers[cell_index - 1]}": "{cell_text}"')

                # 将每一行的数据连接为字符串，用逗号分隔
                row_string = ", ".join(row_data)
                # 将每一行的字符串添加到总的表格字符串中
                table_string += f"{{{row_string}}}\n"

            return table_string
        
        def word2text(filepath):
            resp = ""
            try:
                doc = docxDocument(filepath)
                for block in iter_block_items(doc):
                    if isinstance(block,Paragraph):
                        resp += (block.text + "\n\n")
                    elif isinstance(block, Table):
                        resp += read_table(block) + "\n"
            except ValueError:
                print(f"Error:input invalid parameter")
            except Exception as e:
                print(f"word2text error:{e}")
            return resp    
        
        text = word2text(self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(text=text, **self.unstructured_kwargs)


if __name__ == "__main__":
    loader = RapidWordLoader(file_path="/Users/wangvivi/Desktop/MySelf/AI/Test/国家电网公司供电企业组织机构规范标准.docx")
    docs = loader.load()
    print(docs)
