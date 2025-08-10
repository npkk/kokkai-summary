import type React from 'react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="p-4 bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100 min-h-screen">
      {children}
    </div>
  );
};