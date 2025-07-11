import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter, Link } from 'react-router-dom';
import { Button } from './src/components/ui/button';
import { it } from 'vitest';

// Quick debug test
function DebugTest() {
  console.log('=== DEBUG TEST START ===');
  
  const { container } = render(
    <BrowserRouter>
      <Button asChild>
        <Link to="/test">Navigate</Link>
      </Button>
    </BrowserRouter>
  );
  
  console.log('Container HTML:', container.innerHTML);
  console.log('=== DEBUG TEST END ===');
  
  return null;
}

it('debug button asChild', () => {
  DebugTest();
});
