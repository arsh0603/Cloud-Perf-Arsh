# Firstprj-A - Performance Analytics Dashboard

A modular full-stack application for analyzing NetApp performance data, combining a Django backend with a React frontend.

## Project Structure

```
firstprj-a/
├── firstitr/                    # Django backend application
│   ├── manage.py
│   ├── firstitr/               # Django project settings
│   └── myapp/                  # Main Django app
│       ├── views.py            # Modular API views (100 lines)
│       ├── cache_manager.py    # LRU cache implementation
│       ├── services/           # Business logic services
│       │   ├── api_service.py      # External API communication
│       │   ├── stats_service.py    # Statistics processing
│       │   └── run_service.py      # Run data management
│       └── management/         # Custom Django commands
└── my-react-app/               # React frontend application
    ├── src/
    │   ├── App.js             # Main app component (377 lines)
    │   ├── components/        # Modular UI components
    │   │   ├── Header.js
    │   │   ├── ModeSelector.js
    │   │   ├── RunIdInput.js
    │   │   ├── SystemStatus.js
    │   │   ├── ErrorDisplay.js
    │   │   └── LoadingIndicator.js
    │   ├── hooks/             # Custom React hooks
    │   │   └── index.js       # useRunData, useGraphData, etc.
    │   └── utils/             # Utility functions
    │       ├── api.js         # API service layer
    │       └── helpers.js     # Validation, formatting, charts
    ├── public/
    └── package.json
```

## Technologies Used

- **Backend**: Django 5.2.4 (Python) with modular service architecture
- **Frontend**: React 18+ with hooks and Chart.js integration
- **Database**: SQLite (default Django database)
- **External APIs**: NetApp performance systems (Grover, Perfweb)
- **Caching**: Custom LRU cache implementation
- **Charts**: Chart.js with react-chartjs-2 for performance visualization

## Features

### Performance Analytics
- **Single Run Analysis**: Detailed performance metrics for individual test runs
- **Comparison Mode**: Side-by-side comparison of two performance runs
- **Interactive Graphs**: Latency vs Throughput scatter plots with Chart.js
- **Compatibility Checking**: Automatic validation of workload/model compatibility

### Data Management
- **Smart Caching**: LRU cache for API responses and graph data
- **Real-time Status**: Live cache status monitoring
- **Error Handling**: Comprehensive error reporting and validation
- **Data Transformation**: Clean data formatting and processing

### Modular Architecture
- **Service Layer**: Clean separation of business logic in backend services
- **Component Library**: Reusable React components for UI elements
- **Custom Hooks**: React hooks for state management and data fetching
- **Utility Functions**: Shared validation, formatting, and chart utilities

### Performance Features
- **Throughput Units**: Toggle between bytes/sec and MB/sec display
- **Cache Analytics**: Memory usage and access pattern monitoring
- **External Links**: Direct links to Perfweb logs for detailed analysis
- **Missing Data Handling**: Graceful handling of incomplete datasets

## Getting Started

### Prerequisites

- **Python 3.8+** (tested with Python 3.13)
- **Node.js 16+** and npm
- **Git**
- Access to NetApp internal networks (for external API calls)

### Quick Start

Both servers can be started simultaneously:

```bash
# Clone the repository
git clone <repository-url>
cd Firstprj-A

# Start Django backend (Terminal 1)
cd firstitr
python3 manage.py runserver 8000

# Start React frontend (Terminal 2) 
cd my-react-app
npm install
npm start
```

### Backend Setup (Django)

1. **Navigate to Django project:**
   ```bash
   cd firstitr
   ```

2. **Install Django (if not installed):**
   ```bash
   pip install django
   ```

3. **Run system checks:**
   ```bash
   python3 manage.py check
   ```

4. **Apply migrations (if needed):**
   ```bash
   python3 manage.py migrate
   ```

5. **Start the development server:**
   ```bash
   python3 manage.py runserver 8000
   ```

### Frontend Setup (React)

1. **Navigate to React app:**
   ```bash
   cd my-react-app
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

4. **Build for production (optional):**
   ```bash
   npm run build
   ```

## API Endpoints

### Backend API (Django - Port 8000)

- **`GET /api/fetch-details/`** - Fetch run details
  - `?id1=<run_id>` - Single run analysis
  - `?id1=<run_id>&id2=<run_id>` - Comparison mode

- **`GET /api/fetch-graph-data/`** - Fetch performance graph data
  - `?run_id1=<run_id>` - Single run graph
  - `?run_id1=<run_id>&run_id2=<run_id>` - Comparison graphs

- **`GET /api/cache-status/`** - Get cache status information

- **`DELETE /api/cache-management/`** - Clear cache

- **`GET /api/fetch-multiple-runs/`** - Batch fetch multiple runs
  - `?run_ids=<id1>,<id2>,<id3>` - Comma-separated run IDs

## Usage

### Application Access
- **Django backend:** `http://localhost:8000`
- **React frontend:** `http://localhost:3000`

### Basic Workflow
1. **Select Analysis Mode:** Choose between single run or comparison analysis
2. **Enter Run IDs:** Input 9-character NetApp performance run IDs
3. **Load Data:** Fetch performance metrics and system information
4. **Generate Graphs:** Create interactive latency vs throughput visualizations
5. **Analyze Results:** Review performance data and compatibility status

### Run ID Format
- **Format:** 9 characters (e.g., `250725hbn`)
- **Structure:** YYMMDD + 3-character identifier
- **Source:** NetApp performance testing systems

## Architecture Highlights

### Modular Design
- **Backend reduced from 650 to 100 lines** (85% reduction) in main views
- **Frontend reduced from 926 to 377 lines** (59% reduction) in main component
- **Service-oriented architecture** with clear separation of concerns
- **Component-based UI** with reusable React components

### Performance Optimizations
- **LRU caching** for API responses and graph data
- **Smart data fetching** with cache-first strategy
- **Efficient state management** using React hooks
- **Modular imports** reducing bundle size

### Error Handling
- **Comprehensive validation** for run IDs and data formats
- **Graceful degradation** for missing or incomplete data
- **User-friendly error messages** with specific failure reasons
- **Compatibility checking** for workload and model types

## Development

### Project Status
- ✅ **Fully modularized** frontend and backend
- ✅ **Service layer architecture** implemented
- ✅ **Component library** created
- ✅ **Custom hooks** for state management
- ✅ **Comprehensive error handling**
- ✅ **Performance optimizations** applied

### Code Quality Metrics
- **Backend views.py:** 650 → 100 lines (85% reduction)
- **Frontend App.js:** 926 → 377 lines (59% reduction)
- **Modular services:** 6 service classes created
- **Reusable components:** 6 UI components extracted
- **Custom hooks:** 4 data management hooks

### Testing
```bash
# Backend health check
cd firstitr
python3 manage.py check

# Frontend build test
cd my-react-app
npm run build
```

## Contributing

### Development Guidelines
1. **Follow modular architecture** - Keep components and services focused
2. **Use service layer** - Business logic goes in service classes
3. **Component reusability** - Create reusable UI components
4. **Error handling** - Implement comprehensive error checking
5. **Performance first** - Consider caching and optimization

### Contribution Process
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the modular architecture patterns
4. Test both frontend and backend
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Create a Pull Request

### File Structure Guidelines
- **Backend services:** Add new business logic to appropriate service classes
- **Frontend components:** Create reusable components in `src/components/`
- **Utilities:** Add shared functions to `src/utils/helpers.js`
- **Hooks:** Create custom hooks in `src/hooks/index.js`

## Troubleshooting

### Common Issues

**Backend not starting:**
```bash
# Check Django installation
python3 -c "import django; print(django.get_version())"

# Verify project structure
cd firstitr && python3 manage.py check
```

**Frontend build errors:**
```bash
# Clear npm cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API connection issues:**
- Ensure both servers are running on correct ports
- Check network access to NetApp internal systems
- Verify run ID format (9 characters)

**Cache issues:**
- Use `DELETE /api/cache-management/` to clear cache
- Check cache status with `GET /api/cache-status/`

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Performance Analytics Dashboard

This application provides comprehensive analysis tools for NetApp performance testing results, featuring modular architecture, intelligent caching, and interactive data visualization.
