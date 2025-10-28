'use client';
import { useState } from 'react';
import { apiPost } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export default function Reset() {
  const [email, setEmail] = useState('');

  const submit = async (e:any) => {
    e.preventDefault();
    try {
      await apiPost('/auth/request-reset', { email });
      alert('If that email exists, you will receive reset instructions.');
    } catch (err:any) {
      alert(err.message);
    }
  };

  return (
    <form onSubmit={submit} className="flex flex-col gap-3 max-w-sm mx-auto mt-20">
      <Input placeholder="Email" value={email} onChange={(e:any)=>setEmail(e.target.value)} />
      <Button type="submit">Request reset</Button>
    </form>
  );
}
