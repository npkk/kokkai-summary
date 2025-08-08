def clean_summary_text(summary_text: str) -> str:
    """
    要約テキストから「## 会議名」の前の行を削除する
    """
    position = summary_text.find("## 会議名")
    if position != -1:
        return summary_text[position:]
    return summary_text
