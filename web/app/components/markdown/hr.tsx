import type React from "react";

const Hr: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
	children,
	...props
}) => {
	return <hr {...props} className="py-2" />;
};

export default Hr;
