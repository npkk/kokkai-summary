import type React from "react";

const Li: React.FC<React.LiHTMLAttributes<HTMLLIElement>> = ({
	children,
	...props
}) => {
	return (
		<li {...props} className="text-base pl-4">
			{children}
		</li>
	);
};

export default Li;
