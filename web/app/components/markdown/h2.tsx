import type React from "react";

const H2: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
	children,
	...props
}) => {
	return (
		<h2 {...props} className="text-xl font-bold py-4">
			{children}
		</h2>
	);
};

export default H2;
