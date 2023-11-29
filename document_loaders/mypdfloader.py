from typing import List
from langchain.document_loaders.unstructured import UnstructuredFileLoader
import tqdm
import os

class RapidOCRPDFLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        def pdf2text(filepath):
            import fitz # pyMuPDF里面的fitz包，不要与pip install fitz混淆
            from rapidocr_onnxruntime import RapidOCR
            import numpy as np
            ocr = RapidOCR()
            doc = fitz.open(filepath)
            resp = ""

            file_name_without_extension, file_extension = os.path.splitext(filepath)

            b_unit = tqdm.tqdm(total=doc.page_count, desc="RapidOCRPDFLoader context page index: 0")
            outputfile = file_name_without_extension + "_scan.txt"
            # 打开文件以写入模式
            with open(outputfile, 'w') as file:
        
                for i, page in enumerate(doc):

                    # 更新描述
                    b_unit.set_description("RapidOCRPDFLoader context page index: {}".format(i))
                    # 立即显示进度条更新结果
                    b_unit.refresh()
                    # TODO: 依据文本与图片顺序调整处理方式
                    text = page.get_text("")
                    file.write(f"\n**********文字,页码：{i}")
                    file.write(text)
                    resp += text + "\n"


                    img_list = page.get_images()
                    for img in img_list:
                        pix = fitz.Pixmap(doc, img[0])
                        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, -1)
                        result, _ = ocr(img_array)
                        if result:
                            ocr_result = [line[1] for line in result]
                            file.write(f"\n*****图片****，页码：{i}")
                            file.write(ocr_result)
                            resp += "\n".join(ocr_result)

                    # 更新进度
                    b_unit.update(1)
                return resp

        text = pdf2text(self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(text=text, **self.unstructured_kwargs)


if __name__ == "__main__":
    loader = RapidOCRPDFLoader(file_path="../tests/samples/ocr_test.pdf")
    docs = loader.load()
    print(docs)
