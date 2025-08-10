import type React from "react";

const H1: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
	children,
	...props
}) => {
	return <h1 {...props}>{children}</h1>;
};

export default H1;
