# AspireX System Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CLIENT LAYER (Browser)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐               │
│  │ Public Pages   │  │ Student Portal │  │ Mentor Portal  │               │
│  ├────────────────┤  ├────────────────┤  ├────────────────┤               │
│  │ • Home         │  │ • Dashboard    │  │ • Dashboard    │               │
│  │ • About        │  │ • Browse       │  │ • Students     │               │
│  │ • Contact      │  │   Mentors      │  │   Management   │               │
│  │ • Events       │  │ • Chat         │  │ • Chat         │               │
│  └────────────────┘  │ • Community    │  │ • Community    │               │
│                      │ • Profile      │  │ • Sessions     │               │
│  React 19.1.0 SPA   │ • Booking      │  │ • Analytics    │               │
│  + Vite + Tailwind  └────────────────┘  └────────────────┘               │
│                                                                              │
└──────────────┬───────────────────────────────────────┬───────────────────────┘
               │                                       │
               │ HTTPS/REST API (Axios)                │ WebSocket (WS/WSS)
               │ Authorization: Token <token>          │ Socket.io Client
               │                                       │
┌──────────────▼───────────────────────────────────────▼───────────────────────┐
│                        APPLICATION LAYER (Django)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      Django Backend (Python 3.10+)                    │  │
│  │                      Framework: Django 5.2 + DRF 3.16                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌────────────────────────┐           ┌──────────────────────────────┐     │
│  │   REST API Layer       │           │   WebSocket Layer            │     │
│  │  (Django REST Framework)│          │  (Django Channels 4.2.2)     │     │
│  ├────────────────────────┤           ├──────────────────────────────┤     │
│  │ • Authentication       │           │ • ChatConsumer               │     │
│  │   - Token Auth         │           │ • Real-time messaging        │     │
│  │   - Google OAuth       │           │ • Online status updates      │     │
│  │ • Student APIs         │           │ • Typing indicators          │     │
│  │ • Mentor APIs          │           │ • Message read receipts      │     │
│  │ • Chat APIs            │           │                               │     │
│  │ • Community APIs       │           │ Protocol: WebSocket          │     │
│  │ • Events APIs          │           │ URL: /ws/chat/<id>/<id>/     │     │
│  │ • Payment APIs         │           └──────────────────────────────┘     │
│  └────────────────────────┘                                                 │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      Business Logic Layer                             │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │ • Multi-user Authentication (Student/Mentor)                          │  │
│  │ • Session Booking & Payment Processing (Razorpay Integration)         │  │
│  │ • Notification System (Email + In-app)                                │  │
│  │ • File Upload Handler (Cloudinary/Supabase/S3)                        │  │
│  │ • Permission & Authorization (DRF Permissions)                        │  │
│  │ • Signal Handlers (post_save for auto ID generation)                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────┬────────────────────────────┬──────────────────────────────────┘
               │                            │
               │                            │ Channel Layer
               │                            │ (Message Broker)
               ▼                            ▼
┌──────────────────────────┐    ┌─────────────────────────┐
│   PRIMARY DATABASE       │    │   REDIS CACHE &         │
│   (PostgreSQL/SQLite)    │    │   MESSAGE BROKER        │
├──────────────────────────┤    ├─────────────────────────┤
│                          │    │                         │
│ Tables:                  │    │ • Session storage       │
│ • student               │    │ • WebSocket messages    │
│ • mentor                │    │ • Channel layer         │
│ • studentdetail         │    │ • Temporary cache       │
│ • mentordetail          │    │                         │
│ • conversation          │    │ Port: 6379              │
│ • message               │    │ Version: 6.2.0          │
│ • post (community)      │    │                         │
│ • comment               │    └─────────────────────────┘
│ • like                  │
│ • event                 │
│ • notification          │
│ • contactmessage        │
│ • newslettersubscriber  │
│                          │
│ ORM: Django ORM          │
│ Migrations: Django       │
└──────────────────────────┘
               │
               │
┌──────────────▼──────────────────────────────────────────────────────────────┐
│                       EXTERNAL SERVICES LAYER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │  File Storage   │  │ Payment Gateway │  │ Authentication  │            │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤            │
│  │ • Cloudinary    │  │ • Razorpay      │  │ • Google OAuth  │            │
│  │   (Static files)│  │   - Order       │  │   2.0           │            │
│  │ • Supabase      │  │     Creation    │  │   - Client ID   │            │
│  │   Storage       │  │   - Payment     │  │   - Callback    │            │
│  │ • AWS S3        │  │     Verify      │  │                 │            │
│  │   (Alternative) │  │   - Webhooks    │  │ • Token Auth    │            │
│  │                 │  │                 │  │   (Built-in)    │            │
│  │ CDN: Cloudinary │  │ Version: 1.4.2  │  │                 │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                                  │
│  │ Email Service   │  │ Analytics       │                                  │
│  ├─────────────────┤  ├─────────────────┤                                  │
│  │ • Gmail SMTP    │  │ • Vercel        │                                  │
│  │   Port: 587     │  │   Analytics     │                                  │
│  │   TLS: Enabled  │  │ • Speed         │                                  │
│  │                 │  │   Insights      │                                  │
│  │ • Notifications │  │                 │                                  │
│  │ • Verification  │  │ • Custom Events │                                  │
│  └─────────────────┘  └─────────────────┘                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                          DEPLOYMENT INFRASTRUCTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────┐  ┌────────────────────────────────┐    │
│  │       FRONTEND (Vercel)        │  │     BACKEND (Render)           │    │
│  ├────────────────────────────────┤  ├────────────────────────────────┤    │
│  │ • React Build (Vite)           │  │ • Gunicorn WSGI Server         │    │
│  │ • Static Site Hosting          │  │ • Daphne ASGI Server           │    │
│  │ • Edge Network CDN             │  │   (for WebSockets)             │    │
│  │ • Auto SSL/TLS                 │  │ • Auto SSL/TLS                 │    │
│  │ • Environment Variables        │  │ • Environment Variables        │    │
│  │                                │  │ • PostgreSQL Managed DB        │    │
│  │ URL:                           │  │                                │    │
│  │ https://aspire-x.vercel.app    │  │ URL:                           │    │
│  │                                │  │ https://aspirexbackend         │    │
│  │ Deploy: Git Push (main branch) │  │         .onrender.com          │    │
│  └────────────────────────────────┘  │                                │    │
│                                      │ Deploy: Git Push (main branch) │    │
│                                      └────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. User Authentication Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │         │  Django  │         │ Database │         │  Google  │
│ (React)  │         │ Backend  │         │(Postgres)│         │  OAuth   │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │                    │
     │  1. POST /auth/    │                    │                    │
     │     login/         │                    │                    │
     ├───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │ 2. Query user      │                    │
     │                    ├───────────────────>│                    │
     │                    │                    │                    │
     │                    │ 3. User data       │                    │
     │                    │<───────────────────┤                    │
     │                    │                    │                    │
     │                    │ 4. Validate        │                    │
     │                    │    password        │                    │
     │                    │                    │                    │
     │ 5. Token + User    │                    │                    │
     │<───────────────────┤                    │                    │
     │                    │                    │                    │
     │ 6. Store token     │                    │                    │
     │    in localStorage │                    │                    │
     │                    │                    │                    │
     │  OR                │                    │                    │
     │                    │                    │                    │
     │  7. Google OAuth   │                    │                    │
     │     redirect       │                    │                    │
     ├───────────────────>│ 8. Redirect to     │                    │
     │                    │    Google          │                    │
     │                    ├───────────────────────────────────────>│
     │                    │                    │                    │
     │                    │ 9. Auth code       │                    │
     │                    │<───────────────────────────────────────┤
     │                    │                    │                    │
     │                    │ 10. Exchange       │                    │
     │                    │     for tokens     │                    │
     │                    ├───────────────────────────────────────>│
     │                    │                    │                    │
     │                    │ 11. User info      │                    │
     │                    │<───────────────────────────────────────┤
     │                    │                    │                    │
     │                    │ 12. Create/update  │                    │
     │                    │     user           │                    │
     │                    ├───────────────────>│                    │
     │                    │                    │                    │
     │ 13. Token + User   │                    │                    │
     │<───────────────────┤                    │                    │
     │                    │                    │                    │
```

### 2. Real-time Chat Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│ Student  │         │  Django  │         │  Redis   │         │  Mentor  │
│ Client   │         │ Channels │         │  Broker  │         │  Client  │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │                    │
     │ 1. WS Connect      │                    │                    │
     │    /ws/chat/S1/M1/ │                    │                    │
     ├───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │ 2. Join channel    │                    │
     │                    │    "chat_S1_M1"    │                    │
     │                    ├───────────────────>│                    │
     │                    │                    │                    │
     │ 3. Connected       │                    │                    │
     │<───────────────────┤                    │                    │
     │                    │                    │                    │
     │                    │                    │ 4. WS Connect      │
     │                    │                    │    /ws/chat/S1/M1/ │
     │                    │                    │<───────────────────┤
     │                    │                    │                    │
     │                    │ 5. Join channel    │                    │
     │                    │<───────────────────┤                    │
     │                    │                    │                    │
     │                    │                    │ 6. Connected       │
     │                    │                    ├───────────────────>│
     │                    │                    │                    │
     │ 7. Send message    │                    │                    │
     │    {"text": "Hi"}  │                    │                    │
     ├───────────────────>│                    │                    │
     │                    │                    │                    │
     │                    │ 8. Save to DB      │                    │
     │                    │    (Message model) │                    │
     │                    │                    │                    │
     │                    │ 9. Broadcast to    │                    │
     │                    │    channel         │                    │
     │                    ├───────────────────>│                    │
     │                    │                    │                    │
     │                    │                    │ 10. Forward msg    │
     │                    │                    ├───────────────────>│
     │                    │                    │                    │
     │ 11. Echo back      │                    │                    │
     │<───────────────────┤                    │                    │
     │                    │                    │                    │
```

### 3. Payment Processing Flow

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Student  │    │  React   │    │  Django  │    │ Razorpay │    │  Mentor  │
│          │    │ Frontend │    │ Backend  │    │   API    │    │          │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │              │              │              │              │
     │ 1. Click     │              │              │              │
     │   "Book      │              │              │              │
     │    Session"  │              │              │              │
     ├─────────────>│              │              │              │
     │              │              │              │              │
     │              │ 2. POST      │              │              │
     │              │    /mentor/  │              │              │
     │              │    create-   │              │              │
     │              │    order/    │              │              │
     │              ├─────────────>│              │              │
     │              │              │              │              │
     │              │              │ 3. Create    │              │
     │              │              │    Razorpay  │              │
     │              │              │    order     │              │
     │              │              ├─────────────>│              │
     │              │              │              │              │
     │              │              │ 4. Order ID  │              │
     │              │              │    & details │              │
     │              │              │<─────────────┤              │
     │              │              │              │              │
     │              │ 5. Order     │              │              │
     │              │    details   │              │              │
     │              │<─────────────┤              │              │
     │              │              │              │              │
     │ 6. Open      │              │              │              │
     │    Razorpay  │              │              │              │
     │    checkout  │              │              │              │
     │<─────────────┤              │              │              │
     │              │              │              │              │
     │ 7. Enter     │              │              │              │
     │    payment   │              │              │              │
     │    details   │              │ 8. Process   │              │
     │──────────────┼──────────────┼─────────────>│              │
     │              │              │              │              │
     │              │              │ 9. Payment   │              │
     │              │              │    success   │              │
     │              │              │<─────────────┤              │
     │              │              │              │              │
     │ 10. Payment  │              │              │              │
     │     ID +     │              │              │              │
     │     signature│              │              │              │
     │<─────────────┤              │              │              │
     │              │              │              │              │
     │              │ 11. POST     │              │              │
     │              │     /mentor/ │              │              │
     │              │     verify-  │              │              │
     │              │     payment/ │              │              │
     │              ├─────────────>│              │              │
     │              │              │              │              │
     │              │              │ 12. Verify   │              │
     │              │              │     signature│              │
     │              │              │     (HMAC)   │              │
     │              │              │              │              │
     │              │              │ 13. Update   │              │
     │              │              │     session  │              │
     │              │              │     status   │              │
     │              │              │              │              │
     │              │              │ 14. Send     │              │
     │              │              │     email    │              │
     │              │              │     notif    │              │
     │              │              ├──────────────┼──────────────>│
     │              │              │              │              │
     │              │ 15. Success  │              │              │
     │              │<─────────────┤              │              │
     │              │              │              │              │
     │ 16. Show     │              │              │              │
     │     success  │              │              │              │
     │<─────────────┤              │              │              │
     │              │              │              │              │
```

## Component Breakdown

### Backend Components

1. **API Layer** (`backend/backend/urls.py`)
   - URL routing and endpoint definitions
   - REST API versioning
   - WebSocket routing

2. **Authentication** (`unified_auth/`)
   - Custom multi-user authentication backend
   - Token generation and validation
   - Google OAuth integration
   - Permission classes

3. **Student Module** (`student/`)
   - Student model and manager
   - Profile management
   - Session booking
   - Dashboard APIs

4. **Mentor Module** (`mentor/`)
   - Mentor model and manager
   - Availability management
   - Session pricing and scheduling
   - Payment integration

5. **Chat Module** (`chat/`)
   - Real-time messaging via WebSockets
   - Conversation management
   - Message persistence
   - Customer service messaging

6. **Community Module** (`community/`)
   - Post creation and management
   - Like/comment functionality
   - Content moderation
   - View tracking

7. **Events Module** (`events/`)
   - Event creation by mentors/admins
   - Event listing and filtering
   - Registration management

### Frontend Components

1. **Routing** (`src/routes/`)
   - Public routes
   - Protected routes (auth required)
   - Role-based route guards

2. **Authentication** (`src/components/AuthContext.jsx`)
   - Context provider for auth state
   - Token management
   - User role detection

3. **Student Portal** (`src/Student/`)
   - Dashboard
   - Mentor browsing
   - Session booking
   - Profile management

4. **Mentor Portal** (`src/Mentor/`)
   - Dashboard with analytics
   - Student management
   - Session scheduling
   - Earnings tracking

5. **Chat Interface** (`src/components/Chat/`)
   - Real-time messaging UI
   - WebSocket connection handling
   - Message threading
   - Typing indicators

6. **Community Feed** (`src/components/Community/`)
   - Post creation form
   - Feed display with infinite scroll
   - Like/comment interactions

## Security Architecture

### Authentication & Authorization

1. **Token-based Authentication**
   - JWT-like tokens (DRF Token Auth)
   - Tokens stored in localStorage
   - Token sent in `Authorization: Token <token>` header
   - Automatic token refresh

2. **CORS Protection**
   - Whitelist allowed origins
   - Credentials included in requests
   - Preflight request handling

3. **CSRF Protection**
   - CSRF tokens for state-changing operations
   - Trusted origins configuration
   - Cookie-based CSRF tokens

4. **Password Security**
   - Django's built-in password hashing (PBKDF2)
   - Password validation rules
   - Minimum length, complexity requirements

5. **SQL Injection Prevention**
   - Django ORM parameterized queries
   - No raw SQL without parameterization

6. **XSS Prevention**
   - React's automatic escaping
   - Content Security Policy headers
   - Sanitization of user inputs

### Data Privacy

1. **Environment Variables**
   - Sensitive data in `.env` files (not committed)
   - Production secrets in hosting dashboards
   - Encryption at rest (managed by hosting providers)

2. **HTTPS/TLS**
   - All production traffic over HTTPS
   - Automatic SSL certificates (Vercel/Render)
   - Secure WebSocket (WSS) in production

3. **File Upload Security**
   - File type validation
   - Size limits (10MB default)
   - Virus scanning (TODO)
   - CDN signed URLs

## Monitoring & Observability

### Logging
- Django logging framework
- Request/response logging
- Error tracking (console logs)
- TODO: Sentry integration

### Performance Monitoring
- Vercel Speed Insights (frontend)
- Vercel Analytics (user behavior)
- Django Debug Toolbar (development)
- TODO: New Relic APM

### Health Checks
- `/api/` endpoint (alive check)
- `/api/site-status/` (maintenance mode check)
- Database connection monitoring
- Redis connection monitoring

---

## Scalability Considerations

### Current Limitations
- Single server instance (Render free tier)
- Single Redis instance (no clustering)
- Synchronous request handling (Gunicorn workers)
- SQLite in development (file-based)

### Scaling Path
1. **Horizontal Scaling**: Multiple Render instances with load balancer
2. **Database Scaling**: PostgreSQL read replicas, connection pooling
3. **Redis Clustering**: Multi-node Redis for WebSocket scaling
4. **CDN**: Cloudflare for edge caching
5. **Async Processing**: Celery for background tasks
6. **Microservices**: Split payment, chat, notifications into separate services

---

*This architecture document is subject to updates as the platform evolves.*
