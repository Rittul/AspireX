import React, { useState } from 'react';
import API, { createEvent } from '../../BackendConn/api';

export default function EventsForm() {
  const [form, setForm] = useState({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
    location: '',
    cover_image: ''
  });
  const [status, setStatus] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setStatus('');
    try {
      const payload = { ...form };
      // Convert date-times to ISO if not empty
      if (payload.start_time) payload.start_time = new Date(payload.start_time).toISOString();
      if (payload.end_time) payload.end_time = new Date(payload.end_time).toISOString();
      // Drop optional empty fields so backend doesn't get empty strings
      Object.keys(payload).forEach((k) => {
        if ((k === 'end_time' || k === 'location' || k === 'cover_image') && (payload[k] === '' || payload[k] == null)) {
          delete payload[k];
        }
      });
      await createEvent(payload);
      setStatus('Event created');
      setForm({ title: '', description: '', start_time: '', end_time: '', location: '', cover_image: '' });
    } catch (err) {
      setStatus(err?.response?.data?.detail || err?.response?.data || 'Failed to create event');
    }
    setSubmitting(false);
  };

  return (
    <div style={{ padding: 16 }}>
      <h3 style={{ fontSize: 20, fontWeight: 700, marginBottom: 12 }}>Publish New Event</h3>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 12, maxWidth: 600 }}>
        <input name="title" value={form.title} onChange={handleChange} placeholder="Title" required />
        <textarea name="description" value={form.description} onChange={handleChange} placeholder="Description" rows={5} required />
        <input type="datetime-local" name="start_time" value={form.start_time} onChange={handleChange} required />
        <input type="datetime-local" name="end_time" value={form.end_time} onChange={handleChange} />
        <input name="location" value={form.location} onChange={handleChange} placeholder="Location (optional)" />
        <input name="cover_image" value={form.cover_image} onChange={handleChange} placeholder="Cover Image URL (optional)" />
        <button type="submit" disabled={submitting}>{submitting ? 'Publishing...' : 'Publish Event'}</button>
        {status && <div style={{ color: status.includes('Failed') ? 'crimson' : 'green' }}>{status}</div>}
      </form>
    </div>
  );
} 