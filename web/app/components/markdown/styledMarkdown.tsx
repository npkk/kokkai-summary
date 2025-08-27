import ReactMarkdown from "react-markdown";
import type React from "react";

const A: React.FC<React.AnchorHTMLAttributes<HTMLAnchorElement>> = ({
	children,
	...props
}) => {
	return <a {...props}>{children}</a>;
};

const Blockquote: React.FC<
	React.BlockquoteHTMLAttributes<HTMLQuoteElement>
> = ({ children, ...props }) => {
	return <blockquote {...props}>{children}</blockquote>;
};

const Code: React.FC<React.HTMLAttributes<HTMLElement>> = ({
	children,
	...props
}) => {
	return <code {...props}>{children}</code>;
};

const H1: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
	children,
	...props
}) => {
	return <h1 {...props}>{children}</h1>;
};

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

const Hr: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
	children,
	...props
}) => {
	return <hr {...props} className="my-2" />;
};

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

const Ol: React.FC<React.OlHTMLAttributes<HTMLOListElement>> = ({
	children,
	...props
}) => {
	return <ol {...props}>{children}</ol>;
};

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

interface StyledMarkdownProps {
  children: string;
}

export const StyledMarkdown: React.FC<StyledMarkdownProps> = ({ children }) => {
  return (
    <ReactMarkdown
      components={{
        h1: H1,
        h2: H2,
        h3: H3,
        hr: Hr,
        p: P,
        a: A,
        ul: Ul,
        ol: Ol,
        li: Li,
        blockquote: Blockquote,
        code: Code,
      }}
    >
      {children}
    </ReactMarkdown>
  );
};