import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthContext } from './components/AuthContext';

const renderWithProviders = (ui, { providerProps, ...renderOptions }) => {
    return render(
        <AuthContext.Provider value={providerProps}>
            <MemoryRouter>
                {ui}
            </MemoryRouter>
        </AuthContext.Provider>,
        renderOptions
    );
};

export * from '@testing-library/react';
export { renderWithProviders };