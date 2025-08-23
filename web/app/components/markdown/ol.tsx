import type React from "react";

const Ol: React.FC<React.OlHTMLAttributes<HTMLOListElement>> = ({
	children,
	...props
}) => {
	return <ol {...props}>{children}</ol>;
};

export default Ol;
