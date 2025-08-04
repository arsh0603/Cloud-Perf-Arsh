# Firstprj-A - Performance Analytics Dashboard

A modular full-stack application for analyzing OnTap performance data, combining a Django backend with a React frontend.

## Project Structure

```
firstprj-a/
├── firstitr/                    # Django backend application
│   ├── manage.py
│   ├── pytest.ini             # Test configuration
│   ├── requirements-test.txt   # Testing dependencies
│   ├── TEST_DOCUMENTATION.md   # Comprehensive test documentation
│   ├── firstitr/               # Django project settings
│   ├── myapp/                  # Main Django app
│   │   ├── views.py            # Modular API views (100 lines)
│   │   ├── cache_manager.py    # LRU cache implementation
│   │   ├── urls.py             # URL routing patterns
│   │   ├── services/           # Business logic services
│   │   │   ├── api_service.py      # External API communication
│   │   │   ├── stats_service.py    # Statistics processing
│   │   │   └── run_service.py      # Run data management
│   │   └── management/         # Custom Django commands
│   └── tests/                  # Comprehensive unit test suite
│       ├── conftest.py             # Test configuration and fixtures
│       ├── test_cache_manager.py   # Cache functionality tests (16 tests)
│       ├── test_api_service.py     # API service tests (9 tests)
│       ├── test_views.py           # Django view tests (5 tests)
│       ├── test_run_service.py     # Run service tests (15 tests)
│       ├── test_stats_service.py   # Stats service tests (15 tests)
│       └── test_urls.py            # URL routing tests (20 tests)
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

- **Backend**: Django (Python)
- **Frontend**: React (JavaScript)

## Features

### Performance Analytics
- **Single Run Analysis**: Detailed performance metrics for individual test runs
- **Comparison Mode**: Side-by-side comparison of two performance runs
- **Interactive Graphs**: Latency vs Throughput scatter plots with Chart.js
- **Compatibility Checking**: Automatic validation of workload/model compatibility

### Data Management
- **Smart Caching**: LRU cache for API responses and graph data
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

- Python 3
- Django
- React
- Javascript

### Backend Setup (Django)

1. **Navigate to Django project:**
   ```bash
   cd firstitr
   ```

2. Install dependencies:
   ```bash
   pip3 install django
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
   python3 manage.py runserver
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

- **`DELETE /api/cache-management/`** - Clear cache (DELETE method only)

- **`GET /api/fetch-multiple-runs/`** - Batch fetch multiple runs
  - `?run_ids=<id1>,<id2>,<id3>` - Comma-separated run IDs

### API Usage Examples

```bash
# Get cache status
curl http://localhost:8000/api/cache-status/

# Fetch single run data  
curl "http://localhost:8000/api/fetch-details/?id1=250725hbn"

# Compare two runs
curl "http://localhost:8000/api/fetch-details/?id1=250725hbn&id2=250726xyz"

# Get graph data for single run
curl "http://localhost:8000/api/fetch-graph-data/?run_id1=250725hbn"

# Clear cache
curl -X DELETE http://localhost:8000/api/cache-management/

# Fetch multiple runs
curl "http://localhost:8000/api/fetch-multiple-runs/?run_ids=250725hbn,250726xyz,250727abc"
```

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

### Testing
The project includes a comprehensive unit test suite for the Django backend:

```bash
# Run all backend unit tests
cd firstitr
DJANGO_SETTINGS_MODULE=firstitr.settings python3 -m pytest tests/ -v

# Quick test summary
DJANGO_SETTINGS_MODULE=firstitr.settings python3 -m pytest tests/ -q

# Run specific test files
DJANGO_SETTINGS_MODULE=firstitr.settings python3 -m pytest tests/test_cache_manager.py -v
```

**Test Coverage:**
- **86 unit tests** with 100% pass rate
- **6 test modules** covering all backend components
- **3-second execution** time for full suite
- **Comprehensive mocking** of external dependencies

See [TEST_DOCUMENTATION.md](firstitr/TEST_DOCUMENTATION.md) for detailed testing information.

### Backend Health Check
```bash
cd firstitr
python3 manage.py check
```

### Frontend Build Test
```bash
cd my-react-app
npm run build
```
