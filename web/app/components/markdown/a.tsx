import type React from "react";

const A: React.FC<React.AnchorHTMLAttributes<HTMLAnchorElement>> = ({
	children,
	...props
}) => {
	return <a {...props}>{children}</a>;
};

export default A;
