const API_URL = import.meta.env.VITE_API_URL;

// 新しいリトライ関数
async function fetchWithRetry(
	url: string,
	options: RequestInit,
	retries = 3,
	delay = 2000,
): Promise<Response> {
	for (let i = 0; i < retries; i++) {
		try {
			const response = await fetch(url, options);
			// サーバーエラー（5xx系）など、リトライすべきエラーの場合に再試行
			if (!response.ok && response.status >= 500 && i < retries - 1) {
				await new Promise((resolve) => setTimeout(resolve, delay));
				continue;
			}
			return response;
		} catch (error) {
			if (i < retries - 1) {
				// TypeError: Failed to fetch のようなネットワークエラーの場合
				await new Promise((resolve) => setTimeout(resolve, delay));
				continue;
			}
			throw error; // 最後の試行でも失敗したらエラーをスロー
		}
	}
	// この行には到達しないはずだが、型チェックのためにエラーをスロー
	throw new Error("Fetch failed after multiple retries.");
}

export async function graphqlRequest<T>(
	query: string,
	variables?: Record<string, unknown>,
): Promise<T> {
	// fetchをfetchWithRetryに置き換える
	const response = await fetchWithRetry(API_URL, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			query,
			variables,
		}),
	});

	if (!response.ok) {
		// fetchWithRetry内でリトライされるため、ここでのエラーはリトライしても無駄なもの
		throw new Error(`HTTP error! status: ${response.status}`);
	}

	const result = await response.json();

	if (result.errors) {
		throw new Error(
			result.errors.map((err: { message: string }) => err.message).join(", "),
		);
	}

	return result.data;
}
