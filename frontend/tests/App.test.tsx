import { screen } from '@testing-library/react';
import { customRender } from './test-utils';
import React from 'react';

function App() {
    return <h1>Hello, ReViewPoint!</h1>;
}

describe('App', () => {
    it('renders the heading', () => {
        // Example usage of customRender and userTemplate
        customRender(<App />);
        // You can use userTemplate in your tests as needed
        expect(screen.getByText('Hello, ReViewPoint!')).toBeInTheDocument();
    });
});
