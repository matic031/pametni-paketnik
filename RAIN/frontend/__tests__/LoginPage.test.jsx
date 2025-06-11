// __tests__/LoginPage.test.jsx

import { describe, it, expect, vi, beforeEach } from 'vitest'; // <-- Dodan beforeEach
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../src/test-utils';
import LoginPage from '../src/pages/LoginPage';

// Mock useNavigate
const mockedNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockedNavigate,
    };
});

describe('LoginPage', () => {
    // =============================================================
    // ============>          TUKAJ JE POPRAVEK          <============
    // Ta blok se bo izvedel pred vsakim 'it' blokom v tej datoteki.
    // Poskrbi, da so vsi mocki "sveži" za vsak test posebej.
    // =============================================================
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('pravilno renderira obrazec za prijavo', () => {
        const providerProps = { login: vi.fn() };
        renderWithProviders(<LoginPage />, { providerProps });

        expect(screen.getByRole('heading', { name: /prijava/i })).toBeTruthy();
        expect(screen.getByPlaceholderText(/vnesite uporabniško ime/i)).toBeTruthy();
        expect(screen.getByPlaceholderText(/vnesite geslo/i)).toBeTruthy();
        expect(screen.getByRole('button', { name: /prijava/i })).toBeTruthy();
    });

    it('kliče login funkcijo in preusmeri ob uspešni prijavi (navaden uporabnik)', async () => {
        const mockLogin = vi.fn().mockResolvedValue({ success: true, user: { isAdmin: false } });
        const providerProps = { login: mockLogin };

        renderWithProviders(<LoginPage />, { providerProps });

        await userEvent.type(screen.getByPlaceholderText(/vnesite uporabniško ime/i), 'testuser');
        await userEvent.type(screen.getByPlaceholderText(/vnesite geslo/i), 'password123');
        await userEvent.click(screen.getByRole('button', { name: /prijava/i }));

        await waitFor(() => {
            expect(mockLogin).toHaveBeenCalledWith('testuser', 'password123');
            expect(mockedNavigate).toHaveBeenCalledWith('/dashboard', expect.any(Object));
        });
    });

    it('kliče login funkcijo in preusmeri na admin ploščo (admin uporabnik)', async () => {
        const mockLogin = vi.fn().mockResolvedValue({ success: true, user: { isAdmin: true } });
        const providerProps = { login: mockLogin };

        renderWithProviders(<LoginPage />, { providerProps });

        await userEvent.type(screen.getByPlaceholderText(/vnesite uporabniško ime/i), 'admin');
        await userEvent.type(screen.getByPlaceholderText(/vnesite geslo/i), 'adminpass');
        await userEvent.click(screen.getByRole('button', { name: /prijava/i }));

        await waitFor(() => {
            expect(mockLogin).toHaveBeenCalledWith('admin', 'adminpass');
            expect(mockedNavigate).toHaveBeenCalledWith('/admin/dashboard', expect.any(Object));
        });
    });

    it('prikaže napako ob neuspešni prijavi', async () => {
        const mockLogin = vi.fn().mockResolvedValue({ success: false, message: 'Napačno geslo' });
        const providerProps = { login: mockLogin };

        renderWithProviders(<LoginPage />, { providerProps });

        await userEvent.type(screen.getByPlaceholderText(/vnesite uporabniško ime/i), 'testuser');
        await userEvent.type(screen.getByPlaceholderText(/vnesite geslo/i), 'wrongpassword');
        await userEvent.click(screen.getByRole('button', { name: /prijava/i }));

        // Počakamo, da se prikaže sporočilo o napaki
        expect(await screen.findByText('Napačno geslo')).toBeTruthy();
        // Preverimo, da preusmeritev NI bila klicana v TEM testu
        expect(mockedNavigate).not.toHaveBeenCalled();
    });
});