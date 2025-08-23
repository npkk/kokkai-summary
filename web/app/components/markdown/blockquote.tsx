import type React from "react";

const Blockquote: React.FC<
	React.BlockquoteHTMLAttributes<HTMLQuoteElement>
> = ({ children, ...props }) => {
	return <blockquote {...props}>{children}</blockquote>;
};

export default Blockquote;
