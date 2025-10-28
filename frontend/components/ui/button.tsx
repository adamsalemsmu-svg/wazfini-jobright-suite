import React from 'react';

export const Button = ({ children, ...props }: any) => {
  return (
    <button
      {...props}
      className="px-4 py-2 bg-sky-600 text-white rounded hover:bg-sky-700 disabled:opacity-50"
    >
      {children}
    </button>
  );
};
