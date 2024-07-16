import './globals.css';
import type { ReactNode } from 'react';

type Props = {
  children: ReactNode;
};

const RootLayout: React.FC<Props> = ({ children }) => {
  return (
    <html lang="en">
      <head>
        <title>PClone - Clone your Pre-built PC</title>
      </head>
      <body className="bg-gradient-to-br from-[#2A2F4F] to-[#1C1E2F] min-h-screen flex justify-center items-center">
        {children}
      </body>
    </html>
  );
};

export default RootLayout;