import Link from 'next/link';

export default function Home() {
  return (
    <div className="max-w-3xl mx-auto mt-24 text-center">
      <h1 className="text-3xl font-bold">Wazifni</h1>
      <p className="mt-4">Frontend MVP connected to the FastAPI backend.</p>
      <div className="mt-6 flex justify-center gap-4">
        <Link href="/en/login" className="text-sky-600">Login</Link>
        <Link href="/en/register" className="text-sky-600">Register</Link>
      </div>
    </div>
  );
}
