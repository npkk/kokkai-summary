import type { PropsWithChildren } from "react";
import { Link } from "react-router";

export const Header: React.FC<PropsWithChildren> = () => {
	return (
		<header className="flex gap-8 max-w-[60rem] xl:max-w-7xl w-full mx-auto pt-4 pb-4 pl-4">
			<Link className="text-xl" to="/">
				国会会議録要約システム(仮)
			</Link>
			<div className="max-md:hidden flex grow pr-4">
				<Link to="about">このサイトについて</Link>
				<div className="grow" />
				<a href="https://sigsegvvv.xyz">きつねの隠れ家</a>
			</div>
		</header>
	);
};
