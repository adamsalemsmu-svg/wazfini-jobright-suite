import React from 'react';

export const Input = (props: any) => (
  <input
    {...props}
    className={`border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sky-300 ${props.className ?? ''}`}
  />
);
