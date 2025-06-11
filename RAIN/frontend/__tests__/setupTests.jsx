import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Razširi expect z jest-dom matcherji


// Po vsakem testu počisti DOM
afterEach(() => {
    cleanup();
});