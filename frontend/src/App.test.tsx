import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';

// Mock the API module
vi.mock('./hooks/useShipments', () => ({
  useShipments: () => ({
    data: [
      {
        id: '1',
        title: 'Test Shipment',
        destination: 'Test City',
        eta: '2024-12-31',
        status: 'pending',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ],
    isLoading: false,
    error: null,
  }),
  useCreateShipment: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useUpdateShipment: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useDeleteShipment: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useToggleShipmentStatus: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('App', () => {
  it('renders the shipments manager title', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );
    
    expect(screen.getByText('Shipments Manager')).toBeInTheDocument();
  });

  it('renders the new shipment button', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );
    
    expect(screen.getByText('New Shipment')).toBeInTheDocument();
  });

  it('displays shipment data', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );
    
    expect(screen.getByText('Test Shipment')).toBeInTheDocument();
    expect(screen.getByText('Test City')).toBeInTheDocument();
  });
});
