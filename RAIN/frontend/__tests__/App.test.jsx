import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../src/App';

describe('App', () => {
    it('renders app title', () => {
        render(<App />);
        const titleElement = screen.getByRole('heading', {
            level: 1,
            name: /pametni paketnik/i
        });
        expect(titleElement).toBeDefined();
        expect(titleElement.textContent).toMatch(/pametni paketnik/i);
    });
});
