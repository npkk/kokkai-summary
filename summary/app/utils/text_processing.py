def clean_summary_text(summary_text: str) -> str:
    """
    要約テキストから「## 決議された事項」の前の行を削除する
    """
    position = summary_text.find("## 決議された事項")
    if position != -1:
        return summary_text[position:]
    return summary_text
