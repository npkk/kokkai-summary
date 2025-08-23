import type React from "react";

const P: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
	children,
	...props
}) => {
	return (
		<p {...props} className="py-0.5">
			{children}
		</p>
	);
};

export default P;
