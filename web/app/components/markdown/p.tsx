import type React from "react";

const P: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
	children,
	...props
}) => {
	return <p {...props}>{children}</p>;
};

export default P;
