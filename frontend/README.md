# AWS Cognito User Management - Frontend

Next.js frontend application for managing AWS Cognito users.

## Features

- Microsoft Entra ID authentication
- Role-based UI (Admin, Developer)
- Account → Region → Pool selection flow
- User management interface
- Responsive design

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. Run development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Build

```bash
npm run build
npm start
```

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_ENTRA_ID_TENANT_ID` - Microsoft Entra ID tenant ID
- `NEXT_PUBLIC_ENTRA_ID_CLIENT_ID` - Microsoft Entra ID client ID
- `NEXT_PUBLIC_ENTRA_ID_AUTHORITY` - Microsoft Entra ID authority URL
- `NEXT_PUBLIC_ENTRA_ID_REDIRECT_URI` - Redirect URI after authentication

