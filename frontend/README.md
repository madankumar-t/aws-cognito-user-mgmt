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
# Create .env.local file in frontend/ directory
# Add the following variables:

# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_ENTRA_TENANT_ID=your-tenant-id-here
# NEXT_PUBLIC_ENTRA_CLIENT_ID=your-client-id-here

# See ENV_SETUP.md for detailed instructions
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

Create a `.env.local` file in the `frontend/` directory with:

- `NEXT_PUBLIC_API_URL` - Backend API URL (e.g., `http://localhost:8000`)
- `NEXT_PUBLIC_ENTRA_TENANT_ID` - Microsoft Entra ID tenant ID (from Azure Portal)
- `NEXT_PUBLIC_ENTRA_CLIENT_ID` - Microsoft Entra ID client ID (from Azure Portal)

**See `ENV_SETUP.md` for detailed setup instructions and where to find these values.**

