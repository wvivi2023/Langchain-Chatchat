from typing import List
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from configs import PDF_OCR_THRESHOLD,logger
from document_loaders.ocr import get_ocr
#PDF_OCR_THRESHOLD= (0.6,0.6)
#from ocr import get_ocr
import tqdm
import re

class RapidOCRPDFLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        def pdf2text(filepath):
            import fitz # pyMuPDF里面的fitz包，不要与pip install fitz混淆
            import numpy as np
            ocr = get_ocr()
            doc = fitz.open(filepath)
            resp = ""

            b_unit = tqdm.tqdm(total=doc.page_count, desc="RapidOCRPDFLoader context page index: 0")
            for i, page in enumerate(doc):
                b_unit.set_description("RapidOCRPDFLoader context page index: {}".format(i))
                b_unit.refresh()
                print(f"****page:{i+1}****")
                text = page.get_text("")
                text_lines = text.strip().split("\n")
                logger.debug(f"文字内容：{text_lines}")

                img_list = page.get_image_info(xrefs=True)
                ocr_result = []
                for img in img_list:
                    if xref := img.get("xref"):
                        bbox = img["bbox"]
                        # 检查图片尺寸是否超过设定的阈值
                        if ((bbox[2] - bbox[0]) / (page.rect.width) < PDF_OCR_THRESHOLD[0]
                            or (bbox[3] - bbox[1]) / (page.rect.height) < PDF_OCR_THRESHOLD[1]):
                            continue
                        pix = fitz.Pixmap(doc, xref)
                        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, -1)
                        result, _ = ocr(img_array)
                        if result:
                            ocr_result = [line[1] for line in result]
                            logger.debug(f"图片内容：{ocr_result}")
                            #resp += "\n".join(ocr_result)

                if (len(ocr_result)>0):
                    resp += "\n".join(ocr_result)
                else:
                    if text_lines:
                        # 假设页码在最后一行
                        if text_lines[-1].isdigit():
                            text = "\n".join(text_lines[:-1])
                            logger.debug(f"******去除了页码")
                    resp += text + "\n"

                # 更新进度
                b_unit.update(1)
            
            resp = re.sub(r'((?<!.)\d+(?!\.|[a-zA-Z0-9]))', r"\1 ", resp) 
            resp = re.sub(r'((?<!.)[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+(?!\.|[a-zA-Z0-9]))', r"\1 ", resp) 
            resp = re.sub(r'((?<!.)[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+\s*\.\s*[a-zA-Z0-9]+(?!\.|[a-zA-Z0-9]))', r"\1 ", resp) 
            return resp

        text = pdf2text(self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(text=text, **self.unstructured_kwargs)


if __name__ == "__main__":
    loader = RapidOCRPDFLoader(file_path="/Users/wangvivi/Desktop/Work/思极GPT/数字化部/图片版pdf数据/变电站集中监控验收技术导则.pdf")
    #loader = RapidOCRPDFLoader(file_path="/Users/wangvivi/Desktop/Work/思极GPT/数字化部/原PDF文档/设备/AQ80012007.pdf")
    #loader = RapidOCRPDFLoader(file_path="/Users/wangvivi/Desktop/Work/思极GPT/数字化部/原PDF文档/设备/DL4081991.pdf")
    #loader = RapidOCRPDFLoader(file_path="/Users/wangvivi/Desktop/Work/思极GPT/数字化部/原PDF文档/设备/AQ80032007.pdf")
    docs = loader.load()
    print(docs)
