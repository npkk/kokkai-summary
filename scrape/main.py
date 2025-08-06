import asyncio
from argparse import ArgumentParser

from kokkai_db.database import SessionLocal, create_tables

# libディレクトリ内のモジュールをインポート
from src.meetings.api_client import NdlApiClient
from src.meetings.crud import save_response_to_db
from src.meetings.request_schema import SpeechRequestParams


async def main():
    """
    コマンドライン引数で指定された国会回次の会議録を全ページ取得し、
    データベースに保存するメイン処理。
    """
    # コマンドライン引数の設定とパース
    parser = ArgumentParser(
        description="国会会議録データを指定された回次で取得し、DBに保存します。"
    )
    parser.add_argument(
        "--session", type=int, required=True, help="取得対象の国会回次（例: 213）"
    )
    args = parser.parse_args()

    # データベースとAPIクライアントの準備
    create_tables()
    client = NdlApiClient()
    db = SessionLocal()

    print(f"Start fetching data for session: {args.session}")

    # ページネーションのための変数を初期化
    next_record_position = 1
    total_records_fetched = 0

    try:
        # 3. 全ページ取得するまでループ
        while next_record_position:
            print(f"Fetching records from position: {next_record_position}...")

            # SpeechRequestParamsを使用してリクエストパラメータを構築
            request_params = SpeechRequestParams(
                sessionFrom=int(args.session),
                startRecord=next_record_position,
                maximumRecords=10,
            )  # type: ignore (謎エラーのため)
            api_response = await client.fetch_meeting_records(params=request_params)

            if api_response and api_response.meetingRecord:
                # 取得したデータをDBセッションに追加
                save_response_to_db(db, api_response)

                fetched_count = api_response.numberOfReturn
                total_records_fetched += fetched_count
                print(
                    f"Fetched {fetched_count} meetings. "
                    f"Total: {total_records_fetched} / {api_response.numberOfRecords}"
                )

                # 次のページの開始位置を更新
                next_record_position = api_response.nextRecordPosition
            else:
                # これ以上データがない場合はループを終了
                print("No more records found.")
                break

            # 次のAPI呼び出しまで3秒待機
            if next_record_position:
                print("Waiting for 3 seconds...")
                await asyncio.sleep(3)

        # ループ終了後、一括でコミット
        print("\nAll data fetched. Committing to the database...")
        db.commit()
        print("Successfully committed all data to the database.")

    except Exception as e:
        # エラー発生時はロールバック
        print(f"\nAn error occurred: {e}")
        db.rollback()
        print("Transaction has been rolled back.")
    finally:
        # 最終的にセッションを閉じる
        db.close()
        print("Database session closed.")


if __name__ == "__main__":
    # 非同期関数mainを実行
    asyncio.run(main())
