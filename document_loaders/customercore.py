import re

from unstructured.nlp.patterns import (
    DOUBLE_PARAGRAPH_PATTERN_RE,
    E_BULLET_PATTERN,
    PARAGRAPH_PATTERN,
    PARAGRAPH_PATTERN_RE,
    UNICODE_BULLETS_RE,
)
from unstructured.cleaners.core import group_bullet_paragraph

def custom_group_broken_paragraphs(
    text: str,
    line_split: re.Pattern = PARAGRAPH_PATTERN_RE,
    paragraph_split: re.Pattern = DOUBLE_PARAGRAPH_PATTERN_RE,
) -> str:
    """Groups paragraphs that have line breaks for visual/formatting purposes.
    For example:

    '''The big red fox
    is walking down the lane.

    At the end of the lane
    the fox met a bear.'''

    Gets converted to

    '''The big red fox is walking down the lane.
    At the end of the land the fox met a bear.'''
    """
    paragraphs = paragraph_split.split(text)
    clean_paragraphs = []
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
        # NOTE(robinson) - This block is to account for lines like the following that shouldn't be
        # grouped together, but aren't separated by a double line break.
        #     Apache License
        #     Version 2.0, January 2004
        #     http://www.apache.org/licenses/

        #para_split = line_split.split(paragraph)

        # pytesseract converts some bullet points to standalone "e" characters
        if UNICODE_BULLETS_RE.match(paragraph.strip()) or E_BULLET_PATTERN.match(paragraph.strip()):
            tempList = group_bullet_paragraph(paragraph)
            clean_paragraphs.extend(tempList)
            #print(f"new 11111:{tempList}")
        else:
            tempList = re.sub(PARAGRAPH_PATTERN, " ", paragraph)
            clean_paragraphs.append(tempList)
            #print(f"new 333333:{tempList}")

    return "\n\n".join(clean_paragraphs)


# str1 = "手工分段**绝缘装置（10）  工作斗在额定载荷下起升至最大平台高度，制动后15 min, 工作斗下沉量应不超过该工况最大 平台高度的0.3%。"
# str2 = "手工分段**操控系统（12） 电气系统的要求如下："
# custom_group_broken_paragraphs(str1)
# custom_group_broken_paragraphs(str2)

