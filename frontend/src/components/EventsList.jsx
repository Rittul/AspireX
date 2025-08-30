import React, { useEffect, useMemo, useState } from 'react';
import { fetchEvents } from '../BackendConn/api';
import ServicesNavbar from './ServicesNavbar';
import './CSS/Events.css';
import { FiCalendar, FiMapPin, FiClock, FiSearch } from 'react-icons/fi';

function getStatus(startIso, endIso) {
  const now = new Date();
  const start = startIso ? new Date(startIso) : null;
  const end = endIso ? new Date(endIso) : null;
  if (start && now < start) return { label: 'Upcoming', variant: 'upcoming' };
  if (end && now <= end) return { label: 'Ongoing', variant: 'ongoing' };
  return { label: 'Ended', variant: 'ended' };
}

function EventCard({ ev }) {
  const status = getStatus(ev.start_time, ev.end_time);
  return (
    <div className="event-card">
      <div className="event-cover">
        {ev.cover_image ? (
          <img src={ev.cover_image} alt={ev.title} />
        ) : (
          <div className="event-cover-fallback" />
        )}
        <span className={`event-badge event-badge-${status.variant}`}>{status.label}</span>
      </div>
      <div className="event-content">
        <div className="event-title">{ev.title}</div>
        <div className="event-meta">
          <span className="event-meta-item">
            <FiCalendar /> {new Date(ev.start_time).toLocaleString()}
          </span>
          {ev.location && (
            <span className="event-meta-item">
              <FiMapPin /> {ev.location}
            </span>
          )}
        </div>
        {ev.description && (
          <div className="event-desc">{ev.description}</div>
        )}
        <div className="event-footer">
          <div className="event-organizer">
            <div className="event-organizer-avatar">
              {(ev.organizer_name || 'A').slice(0, 2).toUpperCase()}
            </div>
            <div className="event-organizer-name">{ev.organizer_name || ev.organizer_type}</div>
          </div>
          <div className="event-duration">
            <FiClock />
            {ev.end_time ? (
              <span>
                {Math.max(1, Math.ceil((new Date(ev.end_time) - new Date(ev.start_time)) / (1000 * 60)))}m
              </span>
            ) : (
              <span>—</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="event-card skeleton">
      <div className="event-cover" />
      <div className="event-content">
        <div className="skeleton-line" style={{ width: '70%' }} />
        <div className="skeleton-line" style={{ width: '50%', marginTop: 8 }} />
        <div className="skeleton-line" style={{ width: '90%', marginTop: 14 }} />
        <div className="skeleton-line" style={{ width: '60%', marginTop: 6 }} />
      </div>
    </div>
  );
}

export default function EventsList() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [search, setSearch] = useState('');
  const [includePast, setIncludePast] = useState(false);
  const [mineOnly, setMineOnly] = useState(false);
  const [ordering, setOrdering] = useState('start_time'); // or -created_at

  const isAuthenticated = useMemo(() => {
    return !!(localStorage.getItem('Mentortoken') || localStorage.getItem('token'));
  }, []);

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (search) params.search = search;
      if (includePast) params.include_past = 'true';
      if (mineOnly) params.organizer = 'me';
      if (ordering) params.ordering = ordering;
      const data = await fetchEvents(params);
      setEvents(Array.isArray(data) ? data : []);
    } catch (e) {
      setError('Failed to load events');
    }
    setLoading(false);
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <ServicesNavbar />
      <div className="events-page">
        <div className="events-hero">
          <div className="events-hero-title">Discover Events</div>
          <div className="events-hero-subtitle">Expert sessions, workshops, and more from our mentor community.</div>
          {isAuthenticated && (
            <a className="events-cta" href="/mentor/dashboard">Publish an Event</a>
          )}
        </div>

        <div className="events-controls">
          <div className="events-search">
            <FiSearch />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search events by title, description, or location"
              onKeyDown={e => { if (e.key === 'Enter') load(); }}
            />
            <button onClick={load}>Search</button>
          </div>
          <div className="events-filters">
            <label className="events-switch">
              <input type="checkbox" checked={includePast} onChange={e => setIncludePast(e.target.checked)} />
              <span>Include past</span>
            </label>
            {isAuthenticated && (
              <label className="events-switch">
                <input type="checkbox" checked={mineOnly} onChange={e => setMineOnly(e.target.checked)} />
                <span>My events</span>
              </label>
            )}
            <select value={ordering} onChange={e => setOrdering(e.target.value)}>
              <option value="start_time">Sort: Soonest</option>
              <option value="-created_at">Sort: Newest</option>
              <option value="created_at">Sort: Oldest</option>
            </select>
            <button className="events-apply" onClick={load}>Apply</button>
          </div>
        </div>

        {loading ? (
          <div className="events-grid">
            {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : error ? (
          <div className="events-error">{error}</div>
        ) : events.length === 0 ? (
          <div className="events-empty">
            <img src="/empty.svg" alt="No events" onError={e => (e.currentTarget.style.display = 'none')} />
            <div className="events-empty-title">No events to show</div>
            <div className="events-empty-subtitle">Try adjusting filters or check back later.</div>
          </div>
        ) : (
          <div className="events-grid">
            {events.map(ev => <EventCard key={ev.id} ev={ev} />)}
          </div>
        )}
      </div>
    </>
  );
} 