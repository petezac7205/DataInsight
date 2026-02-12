import { render, screen } from '@testing-library/react';
import App from './App';

test('renders DataInsight hero heading', () => {
  render(<App />);
  const heading = screen.getByText(/Turn CSV data into visuals in one smooth scroll/i);
  expect(heading).toBeTruthy();
});
