from typing import List
from langchain.document_loaders.unstructured import UnstructuredFileLoader
#from document_loaders.ocr import get_ocr
from ocr import get_ocr


class RapidOCRLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        def img2text(filepath):
            resp = ""
            ocr = get_ocr()
            result, _ = ocr(filepath)
            if result:
                ocr_result = [line[1] for line in result]
                resp += "\n".join(ocr_result)
            return resp

        text = img2text(self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(text=text, **self.unstructured_kwargs)


if __name__ == "__main__":
    #loader = RapidOCRLoader(file_path="/Users/wangvivi/Desktop/Code/ocrtest/images/id_card.JPG")
    #loader = RapidOCRLoader(file_path="/Users/wangvivi/Desktop/Code/ocrtest/images/id_card.JPG")
    #loader = RapidOCRLoader(file_path="/Users/wangvivi/Desktop/Code/ocrtest/images/20230726163834.png")
    loader = RapidOCRLoader(file_path="/Users/wangvivi/Desktop/Code/ocrtest/images/QQ截图20230726163813.png")
    #loader = RapidOCRLoader(file_path="/Users/wangvivi/Desktop/Code/ocrtest/images/fapiao.jpg")
    docs = loader.load()
    print(docs)
