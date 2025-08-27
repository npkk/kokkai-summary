export default function About() {
	return (
		<div className="p-4">
			<h1 className="text-2xl font-bold">このサイトについて</h1>
			<p className="mt-2">
				国会の会議録を要約し、公開しているWebサイトです。
				<br />
				要約にはGemini APIを使用しています。
				現在従量課金が発生しない範囲で作成しています。
			</p>
		</div>
	);
}
