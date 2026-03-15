# AI Tourism Recommendation Frontend

A modern React web application for the AI Tourism Recommendation System built with Vite, Tailwind CSS, and Axios.

## Features

- **Modern UI**: Beautiful gradient design with glass morphism effects
- **Responsive**: Mobile-first design that works on all devices
- **Real-time Search**: Search for tourist destinations by city
- **Smart Cards**: Display results with icons, ratings, and metadata
- **Loading States**: Smooth animations during API calls
- **Error Handling**: User-friendly error messages
- **AI Indicator**: Shows when ML model or live data is used

## Project Structure

```
frontend/
├── index.html              # HTML entry point
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind CSS config
├── postcss.config.js       # PostCSS config
├── README.md               # This file
└── src/
    ├── main.jsx            # React entry point
    ├── App.jsx             # Main application component
    ├── index.css           # Global styles
    ├── api.js              # API service (Axios)
    └── components/
        ├── SearchBar.jsx   # Search input component
        └── PlaceCard.jsx   # Place result card
```

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL

Edit `src/api.js` and replace the API URL with your Google Cloud Run endpoint:

```javascript
const API_BASE_URL = 'https://your-api-url.run.app';
```

Or use environment variables by creating a `.env` file:

```env
VITE_API_URL=https://your-api-url.run.app
```

### 3. Run Development Server

```bash
npm run dev
```

The app will open at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` folder.

## Deploy to Vercel

### Option 1: Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```

   Follow the prompts:
   - Set up and deploy? **Yes**
   - Which scope? Select your account
   - Link to existing project? **No** (first time)
   - Project name? `tourism-frontend` (or your choice)

4. **Set Environment Variable** (for API URL):
   ```bash
   vercel env add VITE_API_URL
   ```
   Enter your Cloud Run URL when prompted.

5. **Redeploy with env vars**:
   ```bash
   vercel --prod
   ```

### Option 2: Vercel Dashboard (GitHub Integration)

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com) and sign in
3. Click "Add New Project"
4. Import your GitHub repository
5. Configure:
   - Framework Preset: **Vite**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
6. Add Environment Variable:
   - Name: `VITE_API_URL`
   - Value: `https://your-api-url.run.app`
7. Click **Deploy**

### Option 3: Manual Deploy

```bash
cd frontend
npm run build
vercel dist --prod
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   React + Vite  │────▶│   Google Cloud   │────▶│   ML Model /    │
│   (This App)    │     │   Run (FastAPI)  │     │   Overpass API  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Customization

### Colors

Edit `tailwind.config.js` to customize the color palette:

```javascript
colors: {
  primary: { ... },    // Blues
  secondary: { ... },  // Purples
}
```

### API Timeout

Edit `src/api.js` to change the request timeout:

```javascript
const api = axios.create({
  timeout: 30000,  // 30 seconds
});
```

## Troubleshooting

### CORS Errors

If you see CORS errors, ensure your FastAPI backend has CORS enabled:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Not Found

Make sure your Cloud Run API URL is correct and the service is running:

```bash
# Test your API directly
curl https://your-api-url.run.app/health
```

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Deployment**: Vercel

## License

MIT
