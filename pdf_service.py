from pypdf import PdfReader


def extract_pdf_text(uploaded_file):
    """
    从 Streamlit 上传的 PDF 中提取文本，
    并为每页内容保留页码标记。
    """

    try:
        reader = PdfReader(uploaded_file)

        page_texts = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if text:

                page_texts.append(
                    f"\n\n【第 {page_number} 页】\n{text}"
                )

        full_text = "".join(page_texts)

        reference_position = full_text.lower().find(
            "\nreferences"
        )

        if reference_position != -1:
            full_text = full_text[:reference_position]

        return {
            "success": True,
            "text": full_text,
            "pages": len(reader.pages),
            "message": ""
        }

    except Exception as error:

        return {
            "success": False,
            "text": "",
            "pages": 0,
            "message": f"PDF 解析失败：{error}"
        }