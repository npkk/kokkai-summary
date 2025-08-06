import json
import re


def convert_kaiji_data(input_file="kaiji.json", output_file="master_data.json"):
    """
    kaiji.jsonを読み込み、指定された形式に変換してmaster_data.jsonに出力する。
    """
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            original_data = json.load(f)

        master_data = []
        # 西暦(YYYY)と月、日を直接抽出する正規表現
        date_pattern = re.compile(
            r"\((\d{4})\)年(\d+)月(\d+)日～.*\((\d{4})\)年(\d+)月(\d+)日"
        )

        for item in original_data.get("data", []):
            session_code = item.get("code")
            name_full = item.get("name")

            if not session_code or not name_full:
                continue

            # 修正点1: 名前の部分を正しく抽出 (例: "第218回 臨時会")
            name_parts = name_full.split(" ")
            session_name = " ".join(name_parts[:2])

            start_date_iso = None
            end_date_iso = None

            # 修正点2: 西暦を考慮した正規表現で日付を抽出
            date_match = date_pattern.search(name_full)
            if date_match:
                s_year, s_month, s_day, e_year, e_month, e_day = date_match.groups()
                start_date_iso = f"{s_year}-{int(s_month):02d}-{int(s_day):02d}"
                end_date_iso = f"{e_year}-{int(e_month):02d}-{int(e_day):02d}"

            transformed_item = {
                "session": int(session_code),
                "name": session_name,
                "start_date": start_date_iso,
                "end_date": end_date_iso,
            }
            master_data.append(transformed_item)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(master_data, f, ensure_ascii=False, indent=4)

        print(f"Successfully converted {input_file} to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_file}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    convert_kaiji_data()
