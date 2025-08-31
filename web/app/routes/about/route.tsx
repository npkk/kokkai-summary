export default function About() {
	return (
		<main className="p-4">
			{/* meta */}
			<title>このサイトについて - 国会会議録要約システム(仮)</title>
			<meta
				name="description"
				content="国会の会議録を要約しているシステムです。"
			/>
			<meta property="og:title" content="国会会議録要約システム(仮)" />
			<meta property="og:locale" content="ja_JP" />
			<meta
				property="og:description"
				content="国会の会議録を要約しているシステムです。"
			/>
			<meta
				property="og:url"
				content="https://kokkai-summary.sigsegvvv.xyz/about"
			/>

			{/* main */}
			<div className="pb-8">
				<h2 className="text-2xl">このサイトについて</h2>
				<p className="mt-2">
					国会の会議録を要約し、公開しているWebサイトです。
					<br />
					要約にはGemini APIを使用しています。
					現在従量課金が発生しない範囲で作成しています。
				</p>
			</div>
			{/* 
				Release Note 
				TODO: MDXを入れてこの辺雑に書き足せるようにしておきたい
			*/}
			<div className="pb-8">
				<h2 className="text-2xl">リリースノート</h2>
				<ul className="list-disc list-inside pl-4">
					<li>
						v0.1.0
						<ul className="list-disc list-inside pl-4">
							<li>
								<a href="https://kokkai-summary.sigsegvvv.xyz">
									https://kokkai-summary.sigsegvvv.xyz
								</a>
								として公開しました。
							</li>
						</ul>
					</li>
				</ul>
				<ul className="list-disc list-inside pl-4">
					<li>
						v0.1.1
						<ul className="list-disc list-inside pl-4">
							<li>ヘッダーを追加しました。</li>
							<li>metaタグを修正しました。</li>
							<li>パンくずリストを追加しました。</li>
							<li>サイト全体のデザインを修正しました。</li>
						</ul>
					</li>
				</ul>
			</div>
		</main>
	);
}
