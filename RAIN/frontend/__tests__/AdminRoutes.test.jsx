import { describe, it, expect } from 'vitest';
import { Routes, Route } from 'react-router-dom';
import { renderWithProviders, screen } from '../src/test-utils';
import AdminRoute from '../src/components/AdminRoute';


const AdminContent = () => <div>Admin Vsebina</div>;
const RedirectedPage = () => <div>Preusmerjen na Dashboard</div>;

describe('AdminRoute', () => {
    it('prikaže nalaganje, ko je stanje "loading"', () => {
        const providerProps = { user: null, loading: true };
        renderWithProviders(
            <Routes>
                <Route element={<AdminRoute />}>
                    <Route path="/" element={<AdminContent />} />
                </Route>
            </Routes>,
            { providerProps }
        );
        expect(screen.getByText('Nalaganje...')).toBeTruthy();
    });

    it('preusmeri na /dashboard, če uporabnik ni prijavljen', () => {
        const providerProps = { user: null, loading: false };
        renderWithProviders(
            <Routes>
                <Route element={<AdminRoute />}>
                    <Route path="/" element={<AdminContent />} />
                </Route>
                <Route path="/dashboard" element={<RedirectedPage />} />
            </Routes>,
            { providerProps }
        );
        expect(screen.getByText('Preusmerjen na Dashboard')).toBeTruthy();
        expect(screen.queryByText('Admin Vsebina')).toBeNull();
    });

    it('preusmeri na /dashboard, če uporabnik ni admin', () => {
        const providerProps = { user: { isAdmin: false }, loading: false };
        renderWithProviders(
            <Routes>
                <Route element={<AdminRoute />}>
                    <Route path="/" element={<AdminContent />} />
                </Route>
                <Route path="/dashboard" element={<RedirectedPage />} />
            </Routes>,
            { providerProps }
        );
        expect(screen.getByText('Preusmerjen na Dashboard')).toBeTruthy();
    });

    it('prikaže zaščiteno vsebino, če je uporabnik admin', () => {
        const providerProps = { user: { isAdmin: true }, loading: false };
        renderWithProviders(
            <Routes>
                <Route element={<AdminRoute />}>
                    <Route path="/" element={<AdminContent />} />
                </Route>
            </Routes>,
            { providerProps }
        );
        expect(screen.getByText('Admin Vsebina')).toBeTruthy();
    });
});