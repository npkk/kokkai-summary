import type React from "react";

const H3: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
	children,
	...props
}) => {
	return (
		<h3 {...props} className="text-lg font-bold py-2">
			{children}
		</h3>
	);
};

export default H3;
