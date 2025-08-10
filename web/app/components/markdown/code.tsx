import type React from "react";

const Code: React.FC<React.HTMLAttributes<HTMLElement>> = ({
	children,
	...props
}) => {
	return <code {...props}>{children}</code>;
};

export default Code;
