
from server.knowledge_base.kb_service.faiss_kb_service import FaissKBService
from server.knowledge_base import KnowledgeFile

if __name__ == '__main__':
    from pprint import pprint

    #kb_file = KnowledgeFile(filename="test.txt", knowledge_base_name="samples")
    # kb_file = KnowledgeFile(filename="国网安徽信通公司安全准入实施要求_修订.docx", knowledge_base_name="test")
    # docs = kb_file.file2docs()
    # pprint(docs[-1])
    # docs = kb_file.file2text()
    # pprint(docs[-1])

    faissService = FaissKBService("test")
    faissService.add_doc(KnowledgeFile("国网安徽信通公司安全准入实施要求_修订.docx", "test"))
    # faissService.delete_doc(KnowledgeFile("README.md", "test"))
    # faissService.do_drop_kb()
    print(faissService.search_docs("准入手续的内容是什么？"))


