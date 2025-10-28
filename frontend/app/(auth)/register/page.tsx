'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiPost } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();

  const submit = async (e:any) => {
    e.preventDefault();
    try {
      await apiPost('/auth/register', { email, password });
      router.push('/en/login');
    } catch (err:any) {
      alert(err.message);
    }
  };

  return (
    <form onSubmit={submit} className="flex flex-col gap-3 max-w-sm mx-auto mt-20">
      <Input placeholder="Email" value={email} onChange={(e:any)=>setEmail(e.target.value)} />
      <Input type="password" placeholder="Password" value={password} onChange={(e:any)=>setPassword(e.target.value)} />
      <Button type="submit">Register</Button>
    </form>
  );
}
