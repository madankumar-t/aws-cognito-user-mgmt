# Frontend Architecture & Folder Structure
## AWS Cognito User Management Application

**Document Version:** 1.0  
**Date:** 2024

---

## 1. Frontend Folder Structure

```
frontend/
├── src/
│   ├── app/                         # Next.js App Router
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Home/login page
│   │   ├── dashboard/
│   │   │   ├── layout.tsx           # Dashboard layout
│   │   │   ├── page.tsx             # Dashboard home
│   │   │   ├── accounts/
│   │   │   │   └── page.tsx         # Account selection
│   │   │   ├── regions/
│   │   │   │   └── page.tsx         # Region selection
│   │   │   ├── pools/
│   │   │   │   └── page.tsx         # Pool selection
│   │   │   └── users/
│   │   │       ├── page.tsx         # User list
│   │   │       └── [username]/
│   │   │           └── page.tsx     # User detail
│   │   └── api/                     # API routes (if needed)
│   │
│   ├── components/                  # React components
│   │   ├── auth/
│   │   │   ├── LoginButton.tsx
│   │   │   ├── LogoutButton.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── UserProfile.tsx
│   │   ├── accounts/
│   │   │   ├── AccountList.tsx
│   │   │   ├── AccountCard.tsx
│   │   │   └── AccountSelector.tsx
│   │   ├── regions/
│   │   │   ├── RegionList.tsx
│   │   │   └── RegionSelector.tsx
│   │   ├── pools/
│   │   │   ├── PoolList.tsx
│   │   │   ├── PoolCard.tsx
│   │   │   └── PoolSelector.tsx
│   │   ├── users/
│   │   │   ├── UserList.tsx
│   │   │   ├── UserTable.tsx
│   │   │   ├── UserDetail.tsx
│   │   │   ├── UserDetailModal.tsx
│   │   │   ├── CreateUserForm.tsx
│   │   │   ├── UserActions.tsx
│   │   │   └── UserStatusBadge.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Breadcrumbs.tsx
│   │   └── common/
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorBoundary.tsx
│   │       ├── Toast.tsx
│   │       ├── ToastContainer.tsx
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Select.tsx
│   │       ├── Modal.tsx
│   │       ├── Table.tsx
│   │       └── Pagination.tsx
│   │
│   ├── lib/                         # Libraries and utilities
│   │   ├── auth/
│   │   │   ├── msalConfig.ts        # MSAL configuration
│   │   │   ├── msalInstance.ts      # MSAL instance
│   │   │   └── useAuth.ts           # Auth hook
│   │   ├── api/
│   │   │   ├── client.ts            # Axios instance
│   │   │   ├── accounts.ts          # Account API calls
│   │   │   ├── pools.ts             # Pool API calls
│   │   │   ├── users.ts             # User API calls
│   │   │   └── types.ts             # API types
│   │   └── utils/
│   │       ├── constants.ts         # Constants
│   │       ├── helpers.ts           # Helper functions
│   │       └── formatters.ts        # Data formatters
│   │
│   ├── store/                       # State management (Zustand)
│   │   ├── authStore.ts             # Authentication state
│   │   ├── accountStore.ts          # Selected account/region/pool
│   │   └── userStore.ts             # User list state
│   │
│   ├── hooks/                       # Custom React hooks
│   │   ├── useAccounts.ts
│   │   ├── usePools.ts
│   │   ├── useUsers.ts
│   │   ├── useToast.ts
│   │   └── useDebounce.ts
│   │
│   └── types/                       # TypeScript types
│       ├── auth.ts
│       ├── account.ts
│       ├── pool.ts
│       ├── user.ts
│       └── api.ts
│
├── public/                          # Static assets
│   ├── images/
│   └── icons/
│
├── styles/                          # Global styles
│   └── globals.css
│
├── next.config.js                   # Next.js configuration
├── tailwind.config.js               # Tailwind CSS configuration
├── tsconfig.json                    # TypeScript configuration
├── package.json                     # Dependencies
├── .env.example                     # Environment variables template
├── .gitignore
└── README.md
```

---

## 2. Component Architecture

### 2.1 Authentication Flow

```
1. User visits application
   ↓
2. Check for valid token in store
   ↓
3. If no token:
   - Show login page
   - User clicks "Sign in with Microsoft"
   - Redirect to Microsoft Entra ID
   ↓
4. User authenticates
   ↓
5. Redirect back with authorization code
   ↓
6. Exchange code for JWT token
   ↓
7. Store token securely
   ↓
8. Extract roles from token
   ↓
9. Redirect to dashboard
```

### 2.2 Account Selection Flow

```
1. Dashboard loads
   ↓
2. Fetch available accounts (GET /api/v1/accounts)
   ↓
3. Display account list
   ↓
4. User selects account
   ↓
5. Store in accountStore
   ↓
6. Navigate to region selection
   ↓
7. User selects region
   ↓
8. Store in accountStore
   ↓
9. Fetch pools (GET /api/v1/accounts/{id}/regions/{region}/pools)
   ↓
10. Display pool list
   ↓
11. User selects pool
   ↓
12. Store in accountStore
   ↓
13. Navigate to user management
```

### 2.3 User Management Flow

```
1. User management page loads
   ↓
2. Fetch users (GET /api/v1/pools/{pool_id}/users)
   ↓
3. Display user table
   ↓
4. User actions (role-dependent):
   - Admin: Create, Edit, Enable/Disable, Set Password, etc.
   - Developer: View only
   ↓
5. On action:
   - Show loading state
   - Call API
   - Show success/error toast
   - Refresh user list
```

---

## 3. Key Components

### 3.1 Authentication Components

**`LoginButton.tsx`**
- Triggers MSAL login
- Handles redirect flow
- Shows loading state

**`ProtectedRoute.tsx`**
- Wraps protected pages
- Checks authentication
- Redirects to login if not authenticated
- Checks role permissions

**`UserProfile.tsx`**
- Displays current user info
- Shows roles
- Logout button

### 3.2 Account Selection Components

**`AccountList.tsx`**
- Fetches and displays accounts
- Handles account selection
- Loading and error states

**`AccountCard.tsx`**
- Individual account card
- Account name, ID
- Selection indicator

**`RegionSelector.tsx`**
- Dropdown or grid of regions
- Region selection handler

**`PoolList.tsx`**
- Fetches and displays pools
- Pool selection handler
- Search and filter

### 3.3 User Management Components

**`UserList.tsx`**
- Main user management page
- Integrates UserTable, CreateUserForm
- Handles user actions

**`UserTable.tsx`**
- Data table with pagination
- Sortable columns
- Search functionality
- Row actions (role-dependent)

**`UserDetailModal.tsx`**
- Modal with user details
- All user attributes
- Action buttons (Admin only)

**`CreateUserForm.tsx`**
- Form for creating users
- Validation
- Submit handler

**`UserActions.tsx`**
- Action buttons component
- Role-aware rendering
- Confirmation dialogs

### 3.4 Layout Components

**`Header.tsx`**
- Application header
- Logo, navigation
- User profile, logout

**`Sidebar.tsx`**
- Navigation sidebar
- Breadcrumbs
- Context-aware navigation

**`Footer.tsx`**
- Application footer
- Version info, links

---

## 4. State Management

### 4.1 Zustand Stores

**`authStore.ts`**
```typescript
interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  roles: string[];
  token: string | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  getAccessToken: () => Promise<string | null>;
}
```

**`accountStore.ts`**
```typescript
interface AccountState {
  selectedAccount: Account | null;
  selectedRegion: string | null;
  selectedPool: Pool | null;
  setAccount: (account: Account) => void;
  setRegion: (region: string) => void;
  setPool: (pool: Pool) => void;
  clearSelection: () => void;
}
```

**`userStore.ts`**
```typescript
interface UserState {
  users: User[];
  loading: boolean;
  error: string | null;
  pagination: Pagination;
  fetchUsers: (poolId: string, params?: FetchParams) => Promise<void>;
  refreshUsers: () => Promise<void>;
}
```

---

## 5. API Integration

### 5.1 API Client Setup

**`lib/api/client.ts`**
- Axios instance with base URL
- Request interceptor: Add JWT token
- Response interceptor: Handle errors, refresh token
- Error handling

### 5.2 API Functions

**`lib/api/accounts.ts`**
- `getAccounts()` - List accounts
- `assumeRole(accountId, region)` - Assume role

**`lib/api/pools.ts`**
- `getPools(accountId, region)` - List pools
- `getPoolDetails(poolId)` - Get pool info

**`lib/api/users.ts`**
- `getUsers(poolId, params)` - List users
- `getUser(poolId, username)` - Get user details
- `createUser(poolId, userData)` - Create user
- `updateUserStatus(poolId, username, enabled)` - Enable/disable
- `setPassword(poolId, username, password)` - Set password
- `resetPassword(poolId, username)` - Reset password
- `forcePasswordReset(poolId, username)` - Force reset

---

## 6. Styling

### 6.1 Tailwind CSS

- Utility-first CSS framework
- Custom theme configuration
- Responsive design
- Dark mode support (optional)

### 6.2 Component Library

- shadcn/ui components
- Custom components built on top
- Consistent design system

---

## 7. Type Safety

### 7.1 TypeScript Types

All API responses, requests, and state are typed:
- `types/auth.ts` - Authentication types
- `types/account.ts` - Account types
- `types/pool.ts` - Pool types
- `types/user.ts` - User types
- `types/api.ts` - API response types

---

## 8. Error Handling

### 8.1 Error Boundaries

- React Error Boundary component
- Catches React errors
- Displays fallback UI
- Logs errors

### 8.2 API Error Handling

- Axios interceptors catch errors
- Toast notifications for user feedback
- Retry logic for transient failures
- 401 errors trigger re-authentication

---

## 9. Performance Optimization

### 9.1 Code Splitting

- Next.js automatic code splitting
- Dynamic imports for heavy components
- Route-based splitting

### 9.2 Caching

- React Query for API caching (optional)
- Local storage for account selection
- Token caching in memory

### 9.3 Optimization Techniques

- Debounced search inputs
- Pagination for large lists
- Lazy loading
- Memoization for expensive computations

---

## 10. Security

### 10.1 Token Storage

- JWT stored in memory (preferred) or httpOnly cookies
- Never in localStorage (XSS risk)
- Automatic token refresh

### 10.2 XSS Prevention

- React automatically escapes content
- No `dangerouslySetInnerHTML` usage
- Input sanitization

### 10.3 CSRF Protection

- SameSite cookies
- CORS configuration
- Token-based authentication

---

## 11. Testing Strategy

### 11.1 Unit Tests

- Jest + React Testing Library
- Test individual components
- Mock API calls

### 11.2 Integration Tests

- Test user flows
- E2E tests with Playwright (optional)

---

## 12. Dependencies

### 12.1 Core Dependencies

- `next` - Next.js framework
- `react` - React library
- `react-dom` - React DOM
- `@azure/msal-browser` - MSAL for authentication
- `axios` - HTTP client
- `zustand` - State management
- `tailwindcss` - CSS framework

### 12.2 Development Dependencies

- `typescript` - TypeScript
- `@types/react` - React types
- `eslint` - Linting
- `prettier` - Code formatting
- `jest` - Testing framework
- `@testing-library/react` - React testing utilities

---

**Document Control**

- **Version**: 1.0
- **Last Updated**: 2024

