# Roska Radiadores Frontend

Angular 17 standalone application for Roska Radiadores management system.

## Features

- Angular 17 with standalone components
- Signals for reactive state management
- JWT authentication
- Lazy-loaded feature modules
- SCSS styling with CSS custom properties
- Responsive design

## Project Structure

```
frontend/src/app/
├── core/                     # Singleton services and guards
│   ├── auth/                # Authentication services, guards, interceptors
│   ├── api/                 # API services
│   ├── permissions/         # Permission services and directives
│   └── navigation/          # Navigation/menu services
├── shared/                   # Shared components, directives, pipes
│   ├── components/          # Reusable UI components
│   ├── directives/          # Custom directives
│   ├── pipes/               # Custom pipes
│   └── utils/               # Helper functions
├── features/                 # Feature modules (lazy-loaded)
│   ├── auth/                # Authentication pages
│   ├── dashboard/           # Dashboard
│   ├── users/               # User management
│   ├── roles/               # Role management
│   └── profile/             # User profile
└── app.config.ts            # Application configuration
```

## Setup

### Prerequisites

- Node.js 20+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm start
```

3. Open http://localhost:4200

## Development

### Build

```bash
npm run build
```

### Run tests

```bash
npm test
```

### Lint

```bash
npm run lint
```

## Docker

```bash
# From project root
docker-compose up frontend
```

## Environment Configuration

Edit `src/environments/environment.ts` for development settings.
Edit `src/environments/environment.production.ts` for production settings.

## Architecture

- **Standalone Components**: All components are standalone (no NgModules)
- **Signals**: Using Angular Signals for reactive state management
- **Lazy Loading**: Feature modules are lazy-loaded for better performance
- **Path Aliases**: Configured TypeScript path aliases for cleaner imports:
  - `@core/*` → `src/app/core/*`
  - `@shared/*` → `src/app/shared/*`
  - `@features/*` → `src/app/features/*`
  - `@environments/*` → `src/environments/*`

## API Integration

The frontend connects to the Django REST API at `http://localhost:8000/api` by default.

Authentication is handled via JWT tokens stored in localStorage.

## License

Proprietary
