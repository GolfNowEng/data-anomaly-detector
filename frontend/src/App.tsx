import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MainLayout } from '@/components/layout';
import { Dashboard, TestsList, TestDetail, TestForm } from '@/pages';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tests" element={<TestsList />} />
            <Route path="/tests/new" element={<TestForm />} />
            <Route path="/tests/:testId" element={<TestDetail />} />
            <Route path="/tests/:testId/edit" element={<TestForm />} />
            <Route
              path="/connections"
              element={
                <div className="p-6">
                  <h1 className="text-2xl font-bold">Connections</h1>
                  <p className="text-muted-foreground mt-2">Coming soon...</p>
                </div>
              }
            />
            <Route
              path="/settings"
              element={
                <div className="p-6">
                  <h1 className="text-2xl font-bold">Settings</h1>
                  <p className="text-muted-foreground mt-2">Coming soon...</p>
                </div>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
