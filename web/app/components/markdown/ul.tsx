import type React from "react";

const Ul: React.FC<React.HTMLAttributes<HTMLUListElement>> = ({
	children,
	...props
}) => {
	return (
		<ul {...props} className="list-disc list-inside">
			{children}
		</ul>
	);
};

export default Ul;
