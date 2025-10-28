import type { Config } from "tailwindcss";import type { Config } from "tailwindcss";

import animatePlugin from "tailwindcss-animate";import animatePlugin from "tailwindcss-animate";



const config: Config = {const config: Config = {

  darkMode: ["class"],    darkMode: ["class"],

  content: [    content: [

    "./src/pages/**/*.{ts,tsx}",    "./src/pages/**/*.{ts,tsx}",

    "./src/components/**/*.{ts,tsx}",    "./src/components/**/*.{ts,tsx}",

    "./src/app/**/*.{ts,tsx}",	darkMode: ["class"],

  ],	content: [

  theme: {  theme: {

    extend: {  	extend: {

      fontFamily: {  		fontFamily: {

        sans: ["Inter", "sans-serif"],  			sans: [

      },  				'Inter',

      borderRadius: {		extend: {

        lg: "var(--radius)",  			]

        md: "calc(var(--radius) - 2px)",				sans: ["Inter", "sans-serif"],

        sm: "calc(var(--radius) - 4px)",  			sm: 'calc(var(--radius) - 4px)'

      },  		},

      colors: {				lg: "var(--radius)",

        background: "hsl(var(--background))",				md: "calc(var(--radius) - 2px)",

        foreground: "hsl(var(--foreground))",				sm: "calc(var(--radius) - 4px)",

        card: {  			card: {

          DEFAULT: "hsl(var(--card))",  				DEFAULT: 'hsl(var(--card))',

          foreground: "hsl(var(--card-foreground))",				background: "hsl(var(--background))",

        },				foreground: "hsl(var(--foreground))",

        popover: {				card: {

          DEFAULT: "hsl(var(--popover))",					DEFAULT: "hsl(var(--card))",

          foreground: "hsl(var(--popover-foreground))",					foreground: "hsl(var(--card-foreground))",

        },				},

        primary: {				popover: {

          DEFAULT: "hsl(var(--primary))",					DEFAULT: "hsl(var(--popover))",

          foreground: "hsl(var(--primary-foreground))",					foreground: "hsl(var(--popover-foreground))",

        },				},

        secondary: {				primary: {

          DEFAULT: "hsl(var(--secondary))",					DEFAULT: "hsl(var(--primary))",

          foreground: "hsl(var(--secondary-foreground))",					foreground: "hsl(var(--primary-foreground))",

        },				},

        muted: {				secondary: {

          DEFAULT: "hsl(var(--muted))",					DEFAULT: "hsl(var(--secondary))",

          foreground: "hsl(var(--muted-foreground))",					foreground: "hsl(var(--secondary-foreground))",

        },				},

        accent: {				muted: {

          DEFAULT: "hsl(var(--accent))",					DEFAULT: "hsl(var(--muted))",

          foreground: "hsl(var(--accent-foreground))",					foreground: "hsl(var(--muted-foreground))",

        },				},

        destructive: {				accent: {

          DEFAULT: "hsl(var(--destructive))",					DEFAULT: "hsl(var(--accent))",

          foreground: "hsl(var(--destructive-foreground))",					foreground: "hsl(var(--accent-foreground))",

        },				},

        border: "hsl(var(--border))",				destructive: {

        input: "hsl(var(--input))",					DEFAULT: "hsl(var(--destructive))",

        ring: "hsl(var(--ring))",					foreground: "hsl(var(--destructive-foreground))",

        chart: {				},

          1: "hsl(var(--chart-1))",				border: "hsl(var(--border))",

          2: "hsl(var(--chart-2))",				input: "hsl(var(--input))",

          3: "hsl(var(--chart-3))",				ring: "hsl(var(--ring))",

          4: "hsl(var(--chart-4))",				chart: {

          5: "hsl(var(--chart-5))",					1: "hsl(var(--chart-1))",

        },					2: "hsl(var(--chart-2))",

      },					3: "hsl(var(--chart-3))",

    },					4: "hsl(var(--chart-4))",

  },					5: "hsl(var(--chart-5))",

  plugins: [animatePlugin],				},

};			},

		},

export default config;export default config;

	},
	plugins: [animatePlugin],


